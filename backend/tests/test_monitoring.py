import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "db" in data["services"]

def test_health_ready():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "api_request_count_total" in response.text
