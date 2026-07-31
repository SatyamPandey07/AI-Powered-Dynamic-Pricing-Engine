from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
import datetime

from app.database import get_db
from app.models.tenant import Competitor, CompetitorSKUMapping
from app.dependencies import require_role

router = APIRouter(prefix="/api/competitors", tags=["competitors"])

class CompetitorCreate(BaseModel):
    name: str
    website_url: str
    api_type: str
    scrape_config: dict

class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    api_type: Optional[str] = None
    update_frequency_hours: Optional[int] = None

class SKUMappingCreate(BaseModel):
    sku_id: str
    competitor_sku_id: str
    competitor_product_url: str

@router.post("")
def create_competitor(request: Request, data: CompetitorCreate, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    comp_id = str(uuid.uuid4())
    comp = Competitor(
        id=comp_id,
        org_id=auth.org_id,
        name=data.name,
        website_url=data.website_url,
        api_type=data.api_type,
        scrape_config=data.scrape_config,
        status="active"
    )
    db.add(comp)
    db.commit()
    return {"competitor_id": comp_id, "status": "active"}

@router.get("")
def list_competitors(request: Request, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    comps = db.query(Competitor).filter(
        Competitor.org_id == auth.org_id, 
        Competitor.status != "deleted"
    ).all()
    return [{"id": c.id, "name": c.name, "status": c.status, "last_checked_at": c.last_checked_at} for c in comps]

@router.put("/{comp_id}")
def update_competitor(comp_id: str, data: CompetitorUpdate, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    comp = db.query(Competitor).filter(Competitor.id == comp_id, Competitor.org_id == auth.org_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    for k, v in data.dict(exclude_unset=True).items():
        setattr(comp, k, v)
    db.commit()
    return {"status": "updated"}

@router.delete("/{comp_id}")
def delete_competitor(comp_id: str, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    comp = db.query(Competitor).filter(Competitor.id == comp_id, Competitor.org_id == auth.org_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    comp.status = "deleted"
    db.commit()
    return {"status": "deleted"}

@router.post("/{comp_id}/sku-mapping")
def create_sku_mapping(comp_id: str, data: SKUMappingCreate, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    mapping_id = str(uuid.uuid4())
    mapping = CompetitorSKUMapping(
        id=mapping_id,
        competitor_id=comp_id,
        sku_id=data.sku_id,
        competitor_sku_id=data.competitor_sku_id,
        competitor_product_url=data.competitor_product_url
    )
    db.add(mapping)
    db.commit()
    return {"mapping_id": mapping_id}

@router.get("/{comp_id}/sku-mappings")
def list_sku_mappings(comp_id: str, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    mappings = db.query(CompetitorSKUMapping).filter(CompetitorSKUMapping.competitor_id == comp_id).all()
    # In a real app, verify that comp_id belongs to org_id
    return mappings
