from prometheus_client import Counter, Histogram, Gauge

# API Metrics
REQUEST_COUNT = Counter('api_request_count', 'Total API requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'API request latency', ['method', 'endpoint'])

# Database Metrics
DB_QUERY_LATENCY = Histogram('db_query_latency_seconds', 'Database query latency', ['operation'])

# Cache Metrics
CACHE_HITS = Counter('cache_hits_total', 'Total cache hits', ['cache_type'])
CACHE_MISSES = Counter('cache_misses_total', 'Total cache misses', ['cache_type'])

# Celery Task Metrics
CELERY_TASK_DURATION = Histogram('celery_task_duration_seconds', 'Celery task duration', ['task_name', 'status'])
CELERY_TASK_FAILURES = Counter('celery_task_failures_total', 'Celery task failures', ['task_name'])

# Business Metrics
FORECAST_MAPE = Gauge('forecast_mape', 'Forecast Mean Absolute Percentage Error', ['sku_id'])
PRICE_RECOMMENDATION_ACCEPTED = Counter('price_recommendation_accepted_total', 'Price recommendation accepted')
PRICE_RECOMMENDATION_REJECTED = Counter('price_recommendation_rejected_total', 'Price recommendation rejected')

# Integration Metrics
INTEGRATION_SYNC_SUCCESS = Counter('integration_sync_success_total', 'Integration sync success', ['platform'])
INTEGRATION_SYNC_FAILURE = Counter('integration_sync_failure_total', 'Integration sync failure', ['platform'])

# Webhook Metrics
WEBHOOK_DELIVERY_SUCCESS = Counter('webhook_delivery_success_total', 'Webhook delivery success')
WEBHOOK_DELIVERY_FAILURE = Counter('webhook_delivery_failure_total', 'Webhook delivery failure')
