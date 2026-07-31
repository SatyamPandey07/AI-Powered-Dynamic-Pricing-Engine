from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid
import secrets

from app.database import get_db
from app.models.tenant import Webhook, WebhookDelivery
from app.dependencies import require_role
from app.services.webhooks import trigger_webhook_event

router = APIRouter(prefix="/api/webhooks", tags=["outbound_webhooks"])

class WebhookCreate(BaseModel):
    endpoint_type: str
    target_url: str
    events_subscribed: Optional[List[str]] = []
    
class WebhookUpdate(BaseModel):
    target_url: Optional[str] = None
    events_subscribed: Optional[List[str]] = None
    active: Optional[bool] = None

@router.post("/register")
def register_webhook(
    request: Request, data: WebhookCreate, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    wh_id = str(uuid.uuid4())
    signing_secret = secrets.token_urlsafe(32)
    
    webhook = Webhook(
        id=wh_id,
        org_id=auth.org_id,
        endpoint_type=data.endpoint_type,
        target_url=data.target_url,
        events_subscribed=data.events_subscribed,
        signing_secret=signing_secret,
        active=True
    )
    db.add(webhook)
    db.commit()
    
    return {
        "webhook_id": wh_id,
        "event_type": data.endpoint_type,
        "signing_secret": signing_secret,
        "status": "active"
    }

@router.get("")
def list_webhooks(
    request: Request, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))
):
    webhooks = db.query(Webhook).filter(Webhook.org_id == auth.org_id).all()
    return [
        {
            "webhook_id": w.id,
            "event_type": w.endpoint_type,
            "target_url": w.target_url,
            "status": "active" if w.active else "inactive",
            "events_subscribed": w.events_subscribed
        }
        for w in webhooks
    ]

@router.put("/{webhook_id}")
def update_webhook(
    request: Request, webhook_id: str, data: WebhookUpdate, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.org_id == auth.org_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    if data.target_url is not None:
        webhook.target_url = data.target_url
    if data.events_subscribed is not None:
        webhook.events_subscribed = data.events_subscribed
    if data.active is not None:
        webhook.active = data.active
        
    db.commit()
    return {"status": "updated"}

@router.delete("/{webhook_id}")
def delete_webhook(
    request: Request, webhook_id: str, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.org_id == auth.org_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    webhook.active = False
    db.commit()
    return {"status": "stopped"}

@router.get("/{webhook_id}/deliveries")
def list_deliveries(
    request: Request, webhook_id: str, db: Session = Depends(get_db), auth=Depends(require_role("editor"))
):
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.org_id == auth.org_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    deliveries = db.query(WebhookDelivery).filter(WebhookDelivery.webhook_id == webhook_id).order_by(WebhookDelivery.created_at.desc()).limit(50).all()
    
    return {
        "deliveries": [
            {
                "delivery_id": d.id,
                "attempt": d.attempt_number,
                "timestamp": d.created_at,
                "status": d.status,
                "response_code": d.response_code,
                "response_body": d.response_body
            }
            for d in deliveries
        ]
    }

@router.post("/{webhook_id}/retry")
def retry_webhook_delivery(
    request: Request, webhook_id: str, delivery_id: str, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.org_id == auth.org_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    delivery = db.query(WebhookDelivery).filter(WebhookDelivery.id == delivery_id, WebhookDelivery.webhook_id == webhook_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
        
    delivery.status = "pending"
    delivery.next_retry_at = None
    db.commit()
    
    from app.worker import attempt_webhook_delivery
    attempt_webhook_delivery.delay(delivery.id)
    
    return {"status": "retrying"}
    
@router.post("/{webhook_id}/test")
def test_webhook(
    request: Request, webhook_id: str, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id, Webhook.org_id == auth.org_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    trigger_webhook_event(db, auth.org_id, "test.event", {"message": "This is a test webhook"})
    
    return {"status": "test_triggered"}
