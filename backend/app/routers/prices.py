from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import datetime
import numpy as np

from app.database import get_db
from app.models.tenant import PriceHistory, CompetitorSKUMapping, Competitor
from app.dependencies import require_role

router = APIRouter(prefix="/api/prices", tags=["prices"])

@router.get("/competitor/{sku_id}")
def current_competitor_prices(request: Request, sku_id: str, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    mappings = db.query(CompetitorSKUMapping).join(Competitor).filter(
        CompetitorSKUMapping.sku_id == sku_id,
        Competitor.org_id == auth.org_id
    ).all()
    
    results = []
    for m in mappings:
        if m.last_price is not None:
            comp = db.query(Competitor).filter(Competitor.id == m.competitor_id).first()
            results.append({
                "name": comp.name,
                "price": m.last_price,
                "source": comp.api_type,
                "last_updated": m.last_updated_at
            })
            
    # Sort by price (lowest first)
    results = sorted(results, key=lambda x: x["price"])
    return {"sku_id": sku_id, "competitors": results}

@router.get("/competitor/{sku_id}/history")
def competitor_price_history(
    request: Request, 
    sku_id: str, 
    date_from: Optional[datetime.date] = None, 
    date_to: Optional[datetime.date] = None,
    competitor_filter: Optional[str] = None,
    db: Session = Depends(get_db), 
    auth=Depends(require_role("viewer"))
):
    query = db.query(PriceHistory).filter(
        PriceHistory.org_id == auth.org_id,
        PriceHistory.sku_id == sku_id,
        PriceHistory.source != None
    )
    
    if date_from:
        query = query.filter(PriceHistory.date >= date_from)
    if date_to:
        query = query.filter(PriceHistory.date <= date_to)
    if competitor_filter:
        query = query.filter(PriceHistory.source == competitor_filter)
        
    history = query.all()
    return {"sku_id": sku_id, "history": history}

@router.get("/competitor/{sku_id}/analysis")
def competitor_price_analysis(request: Request, sku_id: str, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    mappings = db.query(CompetitorSKUMapping).join(Competitor).filter(
        CompetitorSKUMapping.sku_id == sku_id,
        Competitor.org_id == auth.org_id
    ).all()
    
    prices = [m.last_price for m in mappings if m.last_price is not None]
    if not prices:
        raise HTTPException(status_code=404, detail="No competitor prices found")
        
    avg_price = np.mean(prices)
    min_price = np.min(prices)
    max_price = np.max(prices)
    std_dev = np.std(prices)
    
    return {
        "sku_id": sku_id,
        "avg_price": float(avg_price),
        "min_price": float(min_price),
        "max_price": float(max_price),
        "price_std_dev": float(std_dev),
        "competitor_leading_price": float(min_price),
        "price_spread": float(max_price - min_price),
        "trend": "stable" # Mocked trend
    }
