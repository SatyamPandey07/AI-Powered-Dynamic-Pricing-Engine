from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

from app.database import get_db
from app.models.tenant import ElasticityMeasurement, PricingTest, SalesHistory
from app.dependencies import require_role
from app.services.elasticity import measure_elasticity_regression, evaluate_ab_test

router = APIRouter(prefix="/api/elasticity", tags=["elasticity"])


class ABTestCreate(BaseModel):
    control_price: float
    treatment_price: float
    duration_days: int = 7
    traffic_split: float = 0.5


@router.get("/{sku_id}")
def get_elasticity(request: Request, sku_id: str, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    # Try to find cached measurement
    measurement = (
        db.query(ElasticityMeasurement)
        .filter(
            ElasticityMeasurement.org_id == auth.org_id,
            ElasticityMeasurement.sku_id == sku_id,
        )
        .order_by(ElasticityMeasurement.calculated_at.desc())
        .first()
    )
    if measurement:
        return {
            "sku_id": sku_id,
            "elasticity": measurement.elasticity_value,
            "confidence_lower": measurement.confidence_lower,
            "confidence_upper": measurement.confidence_upper,
            "model": measurement.model_type,
            "data_points": measurement.data_points,
            "r_squared": measurement.r_squared,
        }

    # Compute from sales history
    sales = (
        db.query(SalesHistory)
        .filter(SalesHistory.org_id == auth.org_id, SalesHistory.sku_id == sku_id)
        .all()
    )
    if len(sales) < 30:
        raise HTTPException(status_code=400, detail="Need at least 30 days of sales data to compute elasticity.")

    prices = [s.price for s in sales if s.price]
    quantities = [s.units_sold for s in sales if s.units_sold]

    try:
        result = measure_elasticity_regression(prices, quantities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Persist result
    em = ElasticityMeasurement(
        id=str(uuid.uuid4()),
        org_id=auth.org_id,
        sku_id=sku_id,
        **result,
    )
    db.add(em)
    db.commit()

    return {"sku_id": sku_id, **result}


@router.post("/test/{sku_id}")
def create_ab_test(
    request: Request, sku_id: str, data: ABTestCreate, db: Session = Depends(get_db), auth=Depends(require_role("editor"))
):
    test_id = str(uuid.uuid4())
    end_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=data.duration_days)
    test = PricingTest(
        id=test_id,
        org_id=auth.org_id,
        sku_id=sku_id,
        control_price=data.control_price,
        treatment_price=data.treatment_price,
        traffic_split=data.traffic_split,
        ended_at=end_date,
        status="running",
    )
    db.add(test)
    db.commit()
    return {
        "test_id": test_id,
        "sku_id": sku_id,
        "control_price": data.control_price,
        "treatment_price": data.treatment_price,
        "started_at": datetime.datetime.now(datetime.timezone.utc),
        "expected_end_date": end_date,
    }


@router.get("/test/{test_id}")
def get_ab_test_results(
    request: Request, test_id: str, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))
):
    test = db.query(PricingTest).filter(
        PricingTest.id == test_id, PricingTest.org_id == auth.org_id
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    stats = evaluate_ab_test(
        control_conversions=test.control_conversions or 0,
        control_impressions=max(test.control_conversions or 1, 1),
        treatment_conversions=test.treatment_conversions or 0,
        treatment_impressions=max(test.treatment_conversions or 1, 1),
    )

    control_rate = (test.control_conversions or 0) / max(test.control_conversions or 1, 1)
    treatment_rate = (test.treatment_conversions or 0) / max(test.treatment_conversions or 1, 1)

    return {
        "test_id": test_id,
        "control": {
            "units_sold": test.control_conversions or 0,
            "revenue": test.control_revenue or 0.0,
            "conversion_rate": round(control_rate, 4),
        },
        "treatment": {
            "units_sold": test.treatment_conversions or 0,
            "revenue": test.treatment_revenue or 0.0,
            "conversion_rate": round(treatment_rate, 4),
        },
        "p_value": stats["p_value"],
        "winner": stats["winner"],
        "confidence": test.confidence,
    }
