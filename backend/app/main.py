from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.middleware.tenant import TenantMiddleware
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
app.add_middleware(TenantMiddleware)

@app.get("/health")
def health_check():
    return {"status": "ok"}