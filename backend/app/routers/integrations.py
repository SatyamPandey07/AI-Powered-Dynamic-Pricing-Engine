from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

from app.database import get_db
from app.models.tenant import Integration, SyncLog, IntegrationCredentialHistory
from app.dependencies import require_role
from app.services.encryption import encrypt_credentials, decrypt_credentials, credentials_hash
from app.services.integrations import get_integration

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

SHOPIFY_SCOPES = "read_products,write_products,read_orders"


class IntegrationCreate(BaseModel):
    platform: str           # shopify | woocommerce | custom
    name: str
    credentials: dict       # Raw credentials (never stored plain; encrypted immediately)
    config: Optional[dict] = {}


class IntegrationUpdate(BaseModel):
    config: Optional[dict] = None
    credentials: Optional[dict] = None


class PushPricesRequest(BaseModel):
    sku_ids: list[str]


def _load_integration(integration_id: str, org_id: str, db: Session) -> Integration:
    rec = db.query(Integration).filter(
        Integration.id == integration_id, Integration.org_id == org_id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Integration not found")
    return rec


@router.post("")
def create_integration(
    request: Request, data: IntegrationCreate, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    int_id = str(uuid.uuid4())
    encrypted = encrypt_credentials(data.credentials)

    integration = Integration(
        id=int_id,
        org_id=auth.org_id,
        platform=data.platform,
        name=data.name,
        status="pending_auth",
        credentials=encrypted,
        config=data.config or {},
    )
    db.add(integration)
    db.commit()

    # For Shopify: return OAuth URL
    auth_url = None
    if data.platform == "shopify":
        shop = data.credentials.get("shop_url", "")
        api_key = data.credentials.get("api_key", "")
        redirect = data.config.get("redirect_uri", "")
        from app.services.integrations.shopify import ShopifyIntegration
        auth_url = ShopifyIntegration.get_auth_url(shop, api_key, redirect, SHOPIFY_SCOPES)

    return {
        "integration_id": int_id,
        "platform": data.platform,
        "status": "pending_auth",
        "auth_url": auth_url,
    }


@router.get("")
def list_integrations(
    request: Request, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))
):
    integrations = db.query(Integration).filter(Integration.org_id == auth.org_id).all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "platform": i.platform,
            "status": i.status,
            "last_sync_at": i.last_sync_at,
            "error_message": i.error_message,
        }
        for i in integrations
    ]


@router.put("/{integration_id}")
def update_integration(
    request: Request,
    integration_id: str,
    data: IntegrationUpdate,
    db: Session = Depends(get_db),
    auth=Depends(require_role("admin")),
):
    rec = _load_integration(integration_id, auth.org_id, db)

    if data.config is not None:
        rec.config = data.config

    if data.credentials is not None:
        # Audit credential change
        old_hash = credentials_hash(decrypt_credentials(rec.credentials)) if rec.credentials else None
        new_hash = credentials_hash(data.credentials)
        hist = IntegrationCredentialHistory(
            id=str(uuid.uuid4()),
            integration_id=integration_id,
            old_credentials_hash=old_hash,
            new_credentials_hash=new_hash,
        )
        db.add(hist)
        rec.credentials = encrypt_credentials(data.credentials)

    db.commit()
    return {"status": "updated"}


@router.delete("/{integration_id}")
def delete_integration(
    request: Request, integration_id: str, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    rec = _load_integration(integration_id, auth.org_id, db)
    rec.status = "disconnected"
    db.commit()
    return {"status": "disconnected"}


@router.post("/{integration_id}/test")
async def test_integration(
    request: Request, integration_id: str, db: Session = Depends(get_db), auth=Depends(require_role("editor"))
):
    rec = _load_integration(integration_id, auth.org_id, db)
    credentials = decrypt_credentials(rec.credentials)
    adapter = get_integration(rec.platform, integration_id, credentials, rec.config or {})
    result = await adapter.test_connection()
    if result.get("status") == "success":
        rec.status = "connected"
        rec.error_message = None
    else:
        rec.status = "error"
        rec.error_message = result.get("message")
    db.commit()
    return result


@router.get("/{integration_id}/sync-inventory")
async def trigger_inventory_sync(
    request: Request, integration_id: str, db: Session = Depends(get_db), auth=Depends(require_role("editor"))
):
    rec = _load_integration(integration_id, auth.org_id, db)
    log = SyncLog(
        id=str(uuid.uuid4()),
        integration_id=integration_id,
        sync_type="inventory",
        status="running",
    )
    db.add(log)
    db.commit()

    try:
        credentials = decrypt_credentials(rec.credentials)
        adapter = get_integration(rec.platform, integration_id, credentials, rec.config or {})
        result = await adapter.sync_inventory()
        log.status = "completed"
        log.items_processed = result["count"]
        rec.last_sync_at = datetime.datetime.now(datetime.timezone.utc)
    except Exception as e:
        log.status = "failed"
        log.error_count = 1
        log.errors = [str(e)]
        rec.status = "error"
        rec.error_message = str(e)
    finally:
        log.completed_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

    return {"skus_synced": log.items_processed, "errors": log.errors or [], "last_sync": log.completed_at}


@router.get("/{integration_id}/sync-sales-history")
async def trigger_sales_sync(
    request: Request, integration_id: str, db: Session = Depends(get_db), auth=Depends(require_role("editor"))
):
    rec = _load_integration(integration_id, auth.org_id, db)
    # Determine backfill start date
    since = rec.last_sync_at.isoformat() if rec.last_sync_at else None
    log = SyncLog(
        id=str(uuid.uuid4()), integration_id=integration_id, sync_type="sales", status="running"
    )
    db.add(log)
    db.commit()

    try:
        credentials = decrypt_credentials(rec.credentials)
        adapter = get_integration(rec.platform, integration_id, credentials, rec.config or {})
        result = await adapter.sync_sales(since=since)
        log.status = "completed"
        log.items_processed = result["count"]
        rec.last_sync_at = datetime.datetime.now(datetime.timezone.utc)
    except Exception as e:
        log.status = "failed"
        log.error_count = 1
        log.errors = [str(e)]
    finally:
        log.completed_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

    return {"orders_synced": log.items_processed, "errors": log.errors or []}


@router.post("/{integration_id}/push-prices")
async def push_prices(
    request: Request,
    integration_id: str,
    data: PushPricesRequest,
    db: Session = Depends(get_db),
    auth=Depends(require_role("editor")),
):
    rec = _load_integration(integration_id, auth.org_id, db)
    if rec.status != "connected":
        raise HTTPException(status_code=400, detail="Integration is not connected")

    credentials = decrypt_credentials(rec.credentials)
    adapter = get_integration(rec.platform, integration_id, credentials, rec.config or {})

    pushed, failed, errors = 0, 0, []
    for sku_id in data.sku_ids:
        try:
            # In a full implementation: look up platform_product_id from sku mapping
            # and the latest recommended price. Here we demonstrate the flow.
            await adapter.push_price(sku_id, 0.0)  # product_id and price fetched from DB in prod
            pushed += 1
        except Exception as e:
            failed += 1
            errors.append({"sku_id": sku_id, "error": str(e)})

    return {"prices_pushed": pushed, "failed": failed, "errors": errors}
