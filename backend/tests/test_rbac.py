import pytest
from app.dependencies import require_role
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rbac_hierarchy():
    # If a user is a viewer, they should be rejected by require_role("editor")
    # This would normally test the dependency directly or via an endpoint
    pass

def test_unauthenticated_requests():
    response = client.get("/api/orgs")
    # Assuming no auth header is provided
    assert response.status_code == 401
