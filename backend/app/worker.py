from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "dynamic_pricing",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Scheduled: 0 0 * * 1 (Monday midnight UTC)
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_week=1),
        retrain_demand_forecasts.s(),
        name="weekly_retrain_demand_forecasts"
    )

@celery_app.task(name="retrain_demand_forecasts")
def retrain_demand_forecasts():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting weekly demand forecast retraining.")
    
    # In a full implementation, this would:
    # 1. Fetch all active organizations and their SKUs from DB
    # 2. Iterate through each SKU
    # 3. Call DemandForecaster(org_id, sku_id).train()
    # 4. Compare MAPE with the active ModelVersion in DB
    # 5. Update DB and activate new model if MAPE improved
    # 6. Log results
    
    results = {
        "skus_retrained": 0,
        "successful": 0,
        "failed": 0,
        "avg_accuracy_improvement": 0.0
    }
    
    logger.info(f"Retraining completed: {results}")
    return results
