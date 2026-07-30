from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import uuid
import secrets
import hashlib
from app.database import get_db
from app.models.tenant import ApiKey
from app.schemas.schemas import ApiKeyCreate, ApiKeyResponse
from app.dependencies import require_role, audit_log

router = APIRouter(prefix="/api/api-keys", tags=["api_keys"])

@router.get("", response_model=List[ApiKeyResponse])
async def get_api_keys(request: Request, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    keys = db.query(ApiKey).filter(ApiKey.org_id == auth.org_id).all()
    # Masking keys for response
    results = []
    for k in keys:
        results.append({
            "id": k.id,
            "name": k.name,
            "key_prefix": "****",
            "created_at": k.created_at
        })
    return results

@router.post("")
@audit_log(action="create", resource_type="api_key")
async def create_api_key(request: Request, key_data: ApiKeyCreate, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    raw_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    new_key = ApiKey(
        id=str(uuid.uuid4()),
        org_id=auth.org_id,
        key_hash=key_hash,
        name=key_data.name
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    return {
        "id": new_key.id,
        "name": new_key.name,
        "api_key": raw_key,
        "created_at": new_key.created_at
    }

@router.delete("/{key_id}")
@audit_log(action="delete", resource_type="api_key")
async def delete_api_key(request: Request, key_id: str, db: Session = Depends(get_db), auth=Depends(require_role("admin"))):
    key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.org_id == auth.org_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
        
    db.delete(key)
    db.commit()
    return {"message": "API Key revoked successfully"}
