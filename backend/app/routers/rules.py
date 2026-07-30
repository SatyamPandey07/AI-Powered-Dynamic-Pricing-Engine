from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

from app.database import get_db
from app.models.tenant import PricingRule
from app.dependencies import require_role

router = APIRouter(prefix="/api/rules", tags=["pricing_rules"])


class RuleCreate(BaseModel):
    name: str
    condition: dict   # e.g. {"type": "min_margin", "value": 0.20}
    action: dict      # e.g. {"type": "clamp_price", "direction": "up"}
    priority: Optional[int] = 0


class RuleUpdate(BaseModel):
    active: Optional[bool] = None
    priority: Optional[int] = None


@router.post("")
def create_rule(
    request: Request, data: RuleCreate, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    rule = PricingRule(
        id=str(uuid.uuid4()),
        org_id=auth.org_id,
        name=data.name,
        condition=data.condition,
        action=data.action,
        priority=data.priority,
        active=True,
    )
    db.add(rule)
    db.commit()
    return {"rule_id": rule.id, "status": "active"}


@router.get("")
def list_rules(request: Request, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    rules = db.query(PricingRule).filter(PricingRule.org_id == auth.org_id).order_by(PricingRule.priority.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "condition": r.condition,
            "action": r.action,
            "active": r.active,
            "priority": r.priority,
            "last_applied_at": r.last_applied_at,
        }
        for r in rules
    ]


@router.put("/{rule_id}")
def update_rule(
    request: Request, rule_id: str, data: RuleUpdate, db: Session = Depends(get_db), auth=Depends(require_role("admin"))
):
    rule = db.query(PricingRule).filter(PricingRule.id == rule_id, PricingRule.org_id == auth.org_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(rule, k, v)
    db.commit()
    return {"status": "updated"}
