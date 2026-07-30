from app.models.tenant import Organization, User, ApiKey, Sku, Supplier, Competitor, CompetitorSkuMapping, PriceHistory, SalesHistory, ForecastHistory, AuditLog
from app.models.base import Base
from app.security import verify_password, get_password_hash, create_access_token
from app.middleware.tenant import TenantMiddleware
from fastapi import Request
import pytest
from unittest.mock import AsyncMock

def test_imports():
    assert Organization.__tablename__ == 'organizations'
    assert User.__tablename__ == 'users'
    assert ApiKey.__tablename__ == 'api_keys'
    assert Sku.__tablename__ == 'skus'
    assert Supplier.__tablename__ == 'suppliers'
    assert Competitor.__tablename__ == 'competitors'
    assert CompetitorSkuMapping.__tablename__ == 'competitor_sku_mappings'
    assert PriceHistory.__tablename__ == 'price_history'
    assert SalesHistory.__tablename__ == 'sales_history'
    assert ForecastHistory.__tablename__ == 'forecast_history'
    assert AuditLog.__tablename__ == 'audit_logs'

def test_security():
    hashed = get_password_hash("test")
    assert verify_password("test", hashed)
    
    token = create_access_token({"sub": "test"})
    assert token is not None

@pytest.mark.asyncio
async def test_middleware():
    app = AsyncMock()
    middleware = TenantMiddleware(app)
    
    request = Request(scope={'type': 'http', 'headers': [(b'authorization', b'Bearer invalid')]})
    await middleware.dispatch(request, app)
