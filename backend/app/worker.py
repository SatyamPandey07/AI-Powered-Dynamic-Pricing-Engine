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
    # Competitor scraping every 4 hours
    sender.add_periodic_task(
        crontab(minute=0, hour='*/4'),
        scrape_competitor_prices.s(),
        name="scrape_competitor_prices_4h"
    )
    # Fetch weather signals daily at 6 AM
    sender.add_periodic_task(
        crontab(minute=0, hour=6),
        fetch_weather_signals.s(),
        name="fetch_weather_signals_daily"
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

@celery_app.task(name="scrape_competitor_prices")
def scrape_competitor_prices():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting competitor price scraping.")
    # In a full implementation, this would:
    # 1. Fetch competitors mapped SKUs
    # 2. Iterate through mapping urls, calling CompetitorScraper
    # 3. Save to DB price_history
    # 4. Fire price alert logic if > 5% diff
    return {"status": "scraping_completed"}

@celery_app.task(name="fetch_weather_signals")
def fetch_weather_signals():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting weather signal fetch.")
    # In a full implementation, this would:
    # 1. Get distinct org locations
    # 2. Call ExternalSignalsService.fetch_weather
    # 3. Store in weather_signals table
    return {"status": "weather_fetched"}
