import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_train_model_unauthorized():
    response = client.post("/api/forecast/train", json={"sku_id": "test-sku"})
    assert response.status_code == 401

def test_predict_unauthorized():
    response = client.get("/api/forecast/predict/test-sku")
    assert response.status_code == 401

def test_accuracy_unauthorized():
    response = client.get("/api/forecast/accuracy/test-sku")
    assert response.status_code == 401
