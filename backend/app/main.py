import time
import logging
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram
from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from pythonjsonlogger import jsonlogger

from app.config import settings
from app.middleware.tenant import TenantMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import (
    auth, orgs, users, api_keys, audit_logs, forecast, competitors, 
    signals, prices, elasticity, optimize, rules, integrations, 
    webhooks, outbound_webhooks
)

# Logging Setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

app = FastAPI(title="Dynamic Pricing Engine API")

# Middlewares
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantMiddleware)

from app.routers import experiments, analytics
app.include_router(experiments.router)
app.include_router(analytics.router)

# Prometheus Metrics
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
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

# Routers
app.include_router(auth.router)
app.include_router(orgs.router)
app.include_router(users.router)
app.include_router(api_keys.router)
app.include_router(audit_logs.router)
app.include_router(forecast.router)
app.include_router(competitors.router)
app.include_router(signals.router)
app.include_router(prices.router)
app.include_router(elasticity.router)
app.include_router(optimize.router)
app.include_router(rules.router)
app.include_router(integrations.router)
app.include_router(webhooks.router)
app.include_router(outbound_webhooks.router)

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy", "timestamp": time.time(), "services": {"db": "ok", "redis": "ok"}})

@app.get("/health/ready")
async def health_ready():
    return JSONResponse(content={"status": "ready", "timestamp": time.time(), "services": {"db": "ok", "redis": "ok"}})

@app.get("/")
async def root():
    return {"message": "Dynamic Pricing Engine Backend Running"}
