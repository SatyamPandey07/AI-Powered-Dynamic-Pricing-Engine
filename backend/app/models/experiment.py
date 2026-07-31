import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class ExperimentModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sku_id: str
    control_price: float
    treatment_price: float
    duration_days: int
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    status: str = "running" # running, concluded
    winner: str | None = None # control, treatment, manual

class ExperimentResultModel(BaseModel):
    experiment_id: str
    control_conversions: int = 0
    treatment_conversions: int = 0
    control_revenue: float = 0.0
    treatment_revenue: float = 0.0
    control_visitors: int = 0
    treatment_visitors: int = 0
