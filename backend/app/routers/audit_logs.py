from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.tenant import AuditLog
from app.schemas.schemas import AuditLogResponse
from app.dependencies import require_role

router = APIRouter(prefix="/api/audit-logs", tags=["audit_logs"])

@router.get("", response_model=List[AuditLogResponse])
async def get_audit_logs(
    request: Request,
    action_filter: Optional[str] = None,
    user_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    auth=Depends(require_role("admin"))
):
    query = db.query(AuditLog).filter(AuditLog.org_id == auth.org_id)
    
    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
    if user_filter:
        query = query.filter(AuditLog.user_id == user_filter)
        
    logs = query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return logs
