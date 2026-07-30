from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.middleware.tenant import TenantMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import auth, orgs, users, api_keys, audit_logs, forecast, competitors, signals, prices, elasticity, optimize, rules, integrations, webhooks
import logging

logging.basicConfig(level=settings.LOG_LEVEL)

app = FastAPI(title="Dynamic Pricing Engine API")

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

@app.get("/health")
def health_check(request: Request):
    return {"status": "ok"}