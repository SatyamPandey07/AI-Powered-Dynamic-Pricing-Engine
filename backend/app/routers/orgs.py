from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tenant import Organization
from app.schemas.schemas import OrgResponse, OrgUpdate
from app.dependencies import require_auth, require_role, audit_log

router = APIRouter(prefix="/api/orgs", tags=["organizations"])

@router.get("", response_model=OrgResponse)
async def get_org(request: Request, db: Session = Depends(get_db), auth=Depends(require_auth)):
    org = db.query(Organization).filter(Organization.id == auth.org_id, Organization.is_active == True).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("", response_model=OrgResponse)
@audit_log(action="update", resource_type="organization")
async def update_org(request: Request, org_data: OrgUpdate, db: Session = Depends(get_db), auth=Depends(require_role("admin"))):
    org = db.query(Organization).filter(Organization.id == auth.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if org_data.name:
        org.name = org_data.name
    if org_data.subscription_tier:
        org.subscription_tier = org_data.subscription_tier
        
    db.commit()
    db.refresh(org)
    return org
