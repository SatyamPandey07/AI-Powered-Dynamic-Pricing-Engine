from datetime import datetime
from pydantic import BaseModel

class ExperimentCreate(BaseModel):
    sku_id: str
    treatment_price: float
    duration_days: int

class ExperimentResponse(BaseModel):
    experiment_id: str
    control_price: float
    treatment_price: float
    started_at: datetime

class ExperimentResultResponse(BaseModel):
    experiment_id: str
    control_price: float
    treatment_price: float
    control_conversions: int
    treatment_conversions: int
    control_revenue: float
    treatment_revenue: float
    p_value: float | None
    winner: str | None
    confidence: float

class ExperimentConclude(BaseModel):
    winner: str

class PowerAnalysisRequest(BaseModel):
    expected_effect_size: float
    confidence: float = 0.95
    power: float = 0.80

class PowerAnalysisResponse(BaseModel):
    required_sample_size: int
    estimated_duration_days: int
