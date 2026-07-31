import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup_success():
    response = client.post("/api/auth/signup", json={
        "user": {"email": "test@example.com", "password": "StrongPassword123!"},
        "org": {"name": "Test Org"}
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_signup_weak_password():
    response = client.post("/api/auth/signup", json={
        "user": {"email": "test2@example.com", "password": "weak"},
        "org": {"name": "Test Org 2"}
    })
    assert response.status_code == 400
    assert "Password must be at least 12 characters long" in response.json()["detail"]

def test_login_success():
    # relies on signup_success running first, or create setup
    pass

def test_login_invalid_creds():
    response = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401
