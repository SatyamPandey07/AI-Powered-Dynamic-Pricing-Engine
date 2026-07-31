"""
Outbound Webhooks Service
==========================
Handles generating signatures and triggering webhooks.
"""
import hmac
import hashlib
import json
import logging
import uuid
import datetime
from sqlalchemy.orm import Session
from app.models.tenant import Webhook, WebhookDelivery
# The actual delivery happens via Celery task `attempt_webhook_delivery` in worker.py

logger = logging.getLogger(__name__)

def generate_signature(secret: str, payload: str) -> str:
    """Generates an HMAC-SHA256 signature for the given payload (X-Webhook-Signature format)."""
    digest = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"sha256={digest}"

def trigger_webhook_event(db: Session, org_id: str, event_type: str, data: dict):
    """
    Finds all active webhooks for the org subscribed to this event_type,
    creates delivery records, and enqueues Celery tasks to deliver them.
    """
    from app.worker import attempt_webhook_delivery

    # Fetch active webhooks for this org
    webhooks = db.query(Webhook).filter(
        Webhook.org_id == org_id,
        Webhook.active == True
    ).all()

    deliveries_to_enqueue = []
    
    for wh in webhooks:
        # Check if subscribed (empty list means subscribe to all, or specifically subscribed)
        subscribed = wh.events_subscribed or []
        if subscribed and event_type not in subscribed:
            continue
            
        delivery_id = str(uuid.uuid4())
        payload_dict = {
            "webhook_id": wh.id,
            "event_type": event_type,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "org_id": org_id,
            "data": data
        }
        
        delivery = WebhookDelivery(
            id=delivery_id,
            webhook_id=wh.id,
            event_type=event_type,
            payload=payload_dict,
            status="pending",
            attempt_number=0
        )
        db.add(delivery)
        deliveries_to_enqueue.append(delivery_id)
        
    db.commit()
    
    # Enqueue tasks after commit
    for d_id in deliveries_to_enqueue:
        attempt_webhook_delivery.delay(d_id)
