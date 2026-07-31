from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
import datetime

from app.database import get_db
from app.models.tenant import WeatherSignal, EventSignal
from app.dependencies import require_role
from app.services.signals import ExternalSignalsService

router = APIRouter(prefix="/api/signals", tags=["signals"])

class EventCreate(BaseModel):
    event_name: str
    event_date: datetime.date
    affected_skus: List[str]
    impact_percent: float

@router.post("/weather")
async def fetch_weather(request: Request, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    service = ExternalSignalsService()
    # Simplified location fetching
    data = await service.fetch_weather("New York")
    if not data:
        raise HTTPException(status_code=500, detail="Failed to fetch weather")
        
    signal = WeatherSignal(
        id=str(uuid.uuid4()),
        org_id=auth.org_id,
        location="New York",
        temperature=data["temperature"],
        humidity=data["humidity"],
        precipitation=data["precipitation"],
        condition=data["condition"],
        forecast_next_7_days=data["forecast_next_7_days"]
    )
    db.add(signal)
    db.commit()
    return {"status": "ok", "temperature": data["temperature"], "condition": data["condition"]}

@router.get("/weather/{sku_id}")
async def get_weather(request: Request, sku_id: str, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    signal = db.query(WeatherSignal).filter(WeatherSignal.org_id == auth.org_id).order_by(WeatherSignal.time.desc()).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Weather not found")
    return signal

@router.post("/events")
async def create_event(request: Request, data: EventCreate, db: Session = Depends(get_db), auth=Depends(require_role("editor"))):
    event = EventSignal(
        id=str(uuid.uuid4()),
        org_id=auth.org_id,
        event_name=data.event_name,
        event_date=data.event_date,
        affected_skus=data.affected_skus,
        impact_percent=data.impact_percent
    )
    db.add(event)
    db.commit()
    return {"status": "ok", "event_id": event.id}

@router.get("/events")
async def list_events(request: Request, db: Session = Depends(get_db), auth=Depends(require_role("viewer"))):
    events = db.query(EventSignal).filter(EventSignal.org_id == auth.org_id).all()
    return events
