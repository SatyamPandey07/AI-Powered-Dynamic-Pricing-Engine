from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
import uuid
import datetime

from app.database import get_db
from app.models.tenant import ModelVersion, SalesHistory, ForecastHistory
from app.dependencies import require_role
from app.services.forecast import DemandForecaster
from app.worker import retrain_demand_forecasts

router = APIRouter(prefix="/api/forecast", tags=["forecasting"])

class ForecastRequest(BaseModel):
    sku_id: str
    days_back: Optional[int] = 365
    frequency: Optional[str] = 'daily'

class ForecastResponse(BaseModel):
    model_id: str
    accuracy_mape: float
    accuracy_mae: float
    trained_at: datetime.datetime
    data_points: int

@router.post("/train", response_model=ForecastResponse)
async def train_model(request: Request, data: ForecastRequest, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    # Fetch historical data
    cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=data.days_back)
    sales = db.query(SalesHistory).filter(
        SalesHistory.org_id == auth.org_id,
        SalesHistory.sku_id == data.sku_id,
        SalesHistory.date >= cutoff_date
    ).all()
    
    if len(sales) < 30:
        raise HTTPException(status_code=400, detail="Insufficient data: Minimum 30 days required.")
        
    df = pd.DataFrame([{ "ds": s.date, "y": s.units_sold } for s in sales])
    
    # Train
    forecaster = DemandForecaster(auth.org_id, data.sku_id)
    try:
        metrics = forecaster.train(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
        
    # Store version
    model_id = str(uuid.uuid4())
    version = ModelVersion(
        id=model_id,
        org_id=auth.org_id,
        sku_id=data.sku_id,
        model_type="ensemble" if metrics["parameters"]["use_prophet"] else "arima",
        accuracy_mape=metrics["accuracy_mape"],
        accuracy_mae=metrics["accuracy_mae"],
        model_artifact=forecaster.redis_key,
        parameters=metrics["parameters"],
        activated_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(version)
    db.commit()
    
    return {
        "model_id": model_id,
        "accuracy_mape": metrics["accuracy_mape"],
        "accuracy_mae": metrics["accuracy_mae"],
        "trained_at": datetime.datetime.now(datetime.timezone.utc),
        "data_points": len(df)
    }

@router.get("/predict/{sku_id}")
async def predict(request: Request, sku_id: str, horizon: int = 7, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    forecaster = DemandForecaster(auth.org_id, sku_id)
    try:
        predictions = forecaster.predict(horizon=horizon)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
        
    # Optional: save to forecast_history table here
    
    return {
        "sku_id": sku_id,
        "forecasts": predictions
    }

@router.get("/accuracy/{sku_id}")
async def model_accuracy(request: Request, sku_id: str, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    active_model = db.query(ModelVersion).filter(
        ModelVersion.org_id == auth.org_id,
        ModelVersion.sku_id == sku_id,
        ModelVersion.activated_at != None
    ).order_by(ModelVersion.trained_at.desc()).first()
    
    if not active_model:
        raise HTTPException(status_code=404, detail="No active model found for SKU")
        
    return {
        "sku_id": sku_id,
        "mape": active_model.accuracy_mape,
        "mae": active_model.accuracy_mae,
        "model_type": active_model.model_type
    }

@router.post("/retrain")
async def manual_retrain(request: Request, background_tasks: BackgroundTasks, auth=Depends(require_role("admin"))):
    # In a real scenario, this might trigger the celery task instead of background tasks.
    retrain_demand_forecasts.delay()
    return {"message": "Retraining job queued"}
