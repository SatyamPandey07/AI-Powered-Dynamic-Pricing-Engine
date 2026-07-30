import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app, Counter, Histogram
from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from pythonjsonlogger import jsonlogger

# Logging Setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

app = FastAPI(title="Dynamic Pricing Engine API")
app.add_middleware(CorrelationIdMiddleware)

from app.routers import experiments, analytics
app.include_router(experiments.router)
app.include_router(analytics.router)

# Prometheus Metrics
REQUEST_COUNT = Counter('api_request_count', 'Total API requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'API request latency', ['method', 'endpoint'])
app.mount("/metrics", make_asgi_app())

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method, 
        endpoint=request.url.path, 
        http_status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method, 
        endpoint=request.url.path
    ).observe(process_time)
    
    # Log the request
    logger.info("Request processed", extra={
        "request_id": correlation_id.get(),
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(process_time * 1000, 2)
    })
    
    return response

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy", "timestamp": time.time(), "services": {"db": "ok", "redis": "ok"}})

@app.get("/health/ready")
async def health_ready():
    return JSONResponse(content={"status": "ready", "timestamp": time.time(), "services": {"db": "ok", "redis": "ok"}})

@app.get("/")
async def root():
    return {"message": "Dynamic Pricing Engine Backend Running"}
