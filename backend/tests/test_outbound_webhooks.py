"""
Tests for PR #7 — Outbound Webhooks & Real-Time Price Push
"""
import pytest
import json
import httpx
from unittest.mock import patch, MagicMock

from app.services.webhooks import generate_signature
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.tenant import Webhook, WebhookDelivery

client = TestClient(app)

def test_generate_signature():
    secret = "my_secret_key"
    payload = json.dumps({"test": "data"})
    signature = generate_signature(secret, payload)
    
    assert signature.startswith("sha256=")
    assert len(signature) > 10


def test_list_webhooks_unauthorized():
    response = client.get("/api/webhooks")
    assert response.status_code == 401


def test_register_webhook_unauthorized():
    response = client.post("/api/webhooks/register", json={
        "endpoint_type": "price.updated",
        "target_url": "https://example.com/webhook"
    })
    assert response.status_code == 401


# Since testing the actual attempt_webhook_delivery celery task involves 
# DB writes, DB reads, and httpx requests, we can test it directly by
# mocking httpx and Celery's retry mechanism.
@patch("httpx.Client.post")
@patch("app.worker.attempt_webhook_delivery.retry")
def test_attempt_webhook_delivery_success(mock_retry, mock_post):
    from app.worker import attempt_webhook_delivery
    
    # Setup mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "OK"
    mock_resp.is_success = True
    mock_post.return_value = mock_resp
    
    # We create a dummy Webhook and WebhookDelivery directly in DB to test the function
    db = SessionLocal()
    import uuid
    wh_id = str(uuid.uuid4())
    del_id = str(uuid.uuid4())
    
    wh = Webhook(id=wh_id, org_id="org1", endpoint_type="test", target_url="http://test.com", signing_secret="sec")
    wd = WebhookDelivery(id=del_id, webhook_id=wh_id, event_type="test", payload={"a": 1}, status="pending")
    db.add(wh)
    db.add(wd)
    db.commit()
    
    # Call the task function directly
    class DummyTask:
        max_retries = 5
        class request:
            retries = 0
            
    try:
        # Binding the self argument for celery task
        attempt_webhook_delivery.bind(DummyTask())(del_id)
        
        # Verify
        db.refresh(wd)
        assert wd.status == "success"
        assert wd.response_code == 200
        assert mock_retry.called == False
    finally:
        db.delete(wd)
        db.delete(wh)
        db.commit()
        db.close()


@patch("httpx.Client.post")
def test_attempt_webhook_delivery_failure_retries(mock_post):
    from app.worker import attempt_webhook_delivery
    
    # Setup mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"
    mock_resp.is_success = False
    mock_post.return_value = mock_resp
    
    db = SessionLocal()
    import uuid
    wh_id = str(uuid.uuid4())
    del_id = str(uuid.uuid4())
    
    wh = Webhook(id=wh_id, org_id="org1", endpoint_type="test", target_url="http://test.com", signing_secret="sec")
    wd = WebhookDelivery(id=del_id, webhook_id=wh_id, event_type="test", payload={"a": 1}, status="pending")
    db.add(wh)
    db.add(wd)
    db.commit()
    
    class DummyTask:
        max_retries = 5
        class request:
            retries = 0
        def retry(self, countdown):
            return Exception(f"Retry triggered with countdown {countdown}")
            
    try:
        with pytest.raises(Exception, match="Retry triggered"):
            attempt_webhook_delivery.bind(DummyTask())(del_id)
            
        db.refresh(wd)
        assert wd.status == "pending" # Still pending because it's retrying
        assert wd.attempt_number == 1
        assert wd.response_code == 500
    finally:
        db.delete(wd)
        db.delete(wh)
        db.commit()
        db.close()
