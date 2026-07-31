from fastapi import APIRouter, HTTPException
from typing import Dict
import uuid
from datetime import datetime

from app.schemas.experiment import (
    ExperimentCreate, ExperimentResponse, ExperimentResultResponse,
    ExperimentConclude, PowerAnalysisRequest, PowerAnalysisResponse
)
from app.services.experimentation import ExperimentationService
from app.models.experiment import ExperimentModel, ExperimentResultModel

router = APIRouter(prefix="/api/experiments", tags=["A/B Testing"])
exp_service = ExperimentationService()

# In-memory storage for demonstration
EXPERIMENTS_DB: Dict[str, ExperimentModel] = {}
RESULTS_DB: Dict[str, ExperimentResultModel] = {}

@router.post("/create", response_model=ExperimentResponse)
async def create_experiment(req: ExperimentCreate):
    exp = ExperimentModel(
        sku_id=req.sku_id,
        control_price=100.0, # Mocked baseline
        treatment_price=req.treatment_price,
        duration_days=req.duration_days
    )
    EXPERIMENTS_DB[exp.id] = exp
    RESULTS_DB[exp.id] = ExperimentResultModel(experiment_id=exp.id)
    
    return ExperimentResponse(
        experiment_id=exp.id,
        control_price=exp.control_price,
        treatment_price=exp.treatment_price,
        started_at=exp.started_at
    )

@router.get("/{id}", response_model=ExperimentResultResponse)
async def get_experiment(id: str):
    if id not in EXPERIMENTS_DB:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    exp = EXPERIMENTS_DB[id]
    res = RESULTS_DB[id]
    
    stats = exp_service.calculate_results(
        res.control_conversions, res.control_visitors,
        res.treatment_conversions, res.treatment_visitors
    )
    
    return ExperimentResultResponse(
        experiment_id=exp.id,
        control_price=exp.control_price,
        treatment_price=exp.treatment_price,
        control_conversions=res.control_conversions,
        treatment_conversions=res.treatment_conversions,
        control_revenue=res.control_revenue,
        treatment_revenue=res.treatment_revenue,
        p_value=stats.get("p_value"),
        winner=exp.winner,
        confidence=stats.get("confidence", 0.0)
    )

@router.post("/{id}/conclude")
async def conclude_experiment(id: str, req: ExperimentConclude):
    if id not in EXPERIMENTS_DB:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    exp = EXPERIMENTS_DB[id]
    exp.status = "concluded"
    exp.winner = req.winner
    exp.ended_at = datetime.utcnow()
    
    return {"status": "success", "winner": req.winner}

@router.post("/power-analysis", response_model=PowerAnalysisResponse)
async def power_analysis(req: PowerAnalysisRequest):
    result = exp_service.power_analysis(
        req.expected_effect_size, req.confidence, req.power
    )
    return PowerAnalysisResponse(**result)
