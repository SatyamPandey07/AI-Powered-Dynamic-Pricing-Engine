from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

from app.database import get_db
from app.models.tenant import PriceRecommendation, ElasticityMeasurement, CompetitorSKUMapping, Competitor
from app.dependencies import require_role
from app.services.optimizer import (
    optimize_price,
    demand_at_price,
    markdown_schedule,
    inventory_signal,
)

router = APIRouter(prefix="/api/optimize", tags=["optimization"])


class OptimizeRequest(BaseModel):
    sku_id: str
    objective: str = "revenue"   # revenue | margin | clearance
    current_price: float
    cost: Optional[float] = 0.0
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    max_change_pct: Optional[float] = 0.10
    inventory_units: Optional[float] = None
    daily_demand: Optional[float] = None


class ScenarioRequest(BaseModel):
    sku_id: str
    test_price: float
    current_price: float
    current_quantity: float


@router.post("/price")
def optimize_price_endpoint(
    request: Request,
    data: OptimizeRequest,
    db: Session = Depends(get_db),
    auth=Depends(require_role("editor")),
):
    # Gather elasticity
    em = (
        db.query(ElasticityMeasurement)
        .filter(ElasticityMeasurement.org_id == auth.org_id, ElasticityMeasurement.sku_id == data.sku_id)
        .order_by(ElasticityMeasurement.calculated_at.desc())
        .first()
    )
    elasticity = em.elasticity_value if em else 1.2  # default assumption

    # Gather competitor prices
    mappings = (
        db.query(CompetitorSKUMapping)
        .join(Competitor)
        .filter(CompetitorSKUMapping.sku_id == data.sku_id, Competitor.org_id == auth.org_id)
        .all()
    )
    competitor_prices = [m.last_price for m in mappings if m.last_price]
    competitor_avg = sum(competitor_prices) / len(competitor_prices) if competitor_prices else None

    constraints = {
        "min_price": data.min_price or data.cost * 1.2 or data.current_price * 0.5,
        "max_price": data.max_price or data.current_price * 2.0,
        "current_price": data.current_price,
        "max_change_pct": data.max_change_pct or 0.10,
    }

    # Reference quantity (use daily_demand or default)
    ref_quantity = data.daily_demand or 100.0

    # Inventory-based signal adjustment
    inv_sig = None
    if data.inventory_units is not None and data.daily_demand:
        inv_sig = inventory_signal(data.inventory_units, data.daily_demand)
        # Nudge min/max based on signal
        if inv_sig["signal"] in ("aggressive_discount", "slight_discount", "excess_inventory"):
            constraints["max_price"] = data.current_price * (1 + inv_sig["price_adjustment"])

    result = optimize_price(
        current_price=data.current_price,
        ref_quantity=ref_quantity,
        elasticity=abs(elasticity),
        objective=data.objective,
        constraints=constraints,
        cost=data.cost or 0.0,
        competitor_avg_price=competitor_avg,
    )

    # Build factors dict
    factors = {
        "elasticity": elasticity,
        "demand_forecast": f"~{ref_quantity:.0f} units/day",
        "competitor_signal": f"avg ${competitor_avg:.2f}" if competitor_avg else "no data",
        "inventory_signal": inv_sig["signal"] if inv_sig else "not provided",
    }
    result["factors"] = factors

    # Persist recommendation
    rec = PriceRecommendation(
        id=str(uuid.uuid4()),
        org_id=auth.org_id,
        sku_id=data.sku_id,
        recommended_price=result["recommended_price"],
        current_price=data.current_price,
        objective=data.objective,
        expected_revenue_impact=result["expected_revenue_delta"],
        expected_margin_impact=result["expected_margin_delta"],
        confidence_score=result["confidence"],
        reasoning=result["reasoning"],
        factors=factors,
    )
    db.add(rec)
    db.commit()

    return result


@router.get("/{sku_id}/recommendation")
def get_latest_recommendation(
    request: Request, sku_id: str, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))
):
    rec = (
        db.query(PriceRecommendation)
        .filter(PriceRecommendation.org_id == auth.org_id, PriceRecommendation.sku_id == sku_id)
        .order_by(PriceRecommendation.created_at.desc())
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="No recommendation found for this SKU")

    accepted_count = (
        db.query(PriceRecommendation)
        .filter(
            PriceRecommendation.org_id == auth.org_id,
            PriceRecommendation.sku_id == sku_id,
            PriceRecommendation.accepted_at != None,
        )
        .count()
    )
    total_count = (
        db.query(PriceRecommendation)
        .filter(PriceRecommendation.org_id == auth.org_id, PriceRecommendation.sku_id == sku_id)
        .count()
    )
    acceptance_rate = accepted_count / max(total_count, 1)

    return {
        "sku_id": sku_id,
        "recommended_price": rec.recommended_price,
        "current_price": rec.current_price,
        "confidence": rec.confidence_score,
        "reasoning": rec.reasoning,
        "factors": rec.factors,
        "objective": rec.objective,
        "created_at": rec.created_at,
        "acceptance_rate": round(acceptance_rate, 2),
    }


@router.post("/scenario")
def simulate_scenario(
    request: Request, data: ScenarioRequest, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))
):
    # Get elasticity
    em = (
        db.query(ElasticityMeasurement)
        .filter(ElasticityMeasurement.org_id == auth.org_id, ElasticityMeasurement.sku_id == data.sku_id)
        .order_by(ElasticityMeasurement.calculated_at.desc())
        .first()
    )
    elasticity = abs(em.elasticity_value) if em else 1.2

    simulated_q = demand_at_price(data.test_price, data.current_price, data.current_quantity, elasticity)
    current_revenue = data.current_price * data.current_quantity
    simulated_revenue = data.test_price * simulated_q
    delta = simulated_revenue - current_revenue

    return {
        "current_price": data.current_price,
        "current_quantity": data.current_quantity,
        "current_revenue": round(current_revenue, 2),
        "test_price": data.test_price,
        "simulated_quantity": round(simulated_q, 1),
        "simulated_revenue": round(simulated_revenue, 2),
        "revenue_delta": round(delta, 2),
        "delta_pct": round((delta / max(current_revenue, 1)) * 100, 2),
    }


@router.post("/markdown/{sku_id}")
def markdown_recommendation(
    request: Request,
    sku_id: str,
    current_price: float,
    days_in_stock: int,
    auth=Depends(require_role("editor")),
):
    schedule = markdown_schedule(current_price, days_in_stock)
    return {"sku_id": sku_id, "current_price": current_price, "markdown_schedule": schedule}
