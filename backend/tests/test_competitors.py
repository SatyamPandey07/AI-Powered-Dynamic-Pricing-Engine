import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_competitor_unauthorized():
    response = client.post("/api/competitors", json={
        "name": "Amazon",
        "website_url": "https://amazon.com",
        "api_type": "website",
        "scrape_config": {"price_selector": ".a-price-whole"}
    })
    assert response.status_code == 401

def test_get_competitor_prices_unauthorized():
    response = client.get("/api/prices/competitor/test-sku")
    assert response.status_code == 401
