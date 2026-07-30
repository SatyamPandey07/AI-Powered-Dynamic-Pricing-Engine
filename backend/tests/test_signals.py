import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fetch_weather_unauthorized():
    response = client.post("/api/signals/weather")
    assert response.status_code == 401

def test_create_event_unauthorized():
    response = client.post("/api/signals/events", json={
        "event_name": "Test Event",
        "event_date": "2024-01-01",
        "affected_skus": ["sku-123"],
        "impact_percent": 10.0
    })
    assert response.status_code == 401
