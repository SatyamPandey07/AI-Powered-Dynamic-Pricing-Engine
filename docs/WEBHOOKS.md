# Webhook Integration

External platforms can push real-time events (new orders, inventory changes, price updates) to the DynamicPricingEngine via webhooks.

## Endpoint

```
POST /api/webhooks/integrations/{integration_id}
```

## Shopify Webhooks

Configure in Shopify Admin → Settings → Notifications → Webhooks.

**Supported topics**: `orders/create`, `orders/updated`, `inventory_levels/update`

**Signature verification**: Shopify signs every webhook with HMAC-SHA256 using the Webhook Signing Secret. The engine verifies the `X-Shopify-Hmac-Sha256` header before processing.

```python
import hmac, hashlib, base64
computed = base64.b64encode(
    hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).digest()
).decode()
assert computed == request.headers["X-Shopify-Hmac-Sha256"]
```

## Generic Webhooks (WooCommerce, Custom)

For generic webhooks, the `X-Hub-Signature-256` header is used:

```
X-Hub-Signature-256: sha256=<hmac_hex>
```

## Payload Example (Shopify Order)

```json
{
  "id": 12345678,
  "email": "customer@example.com",
  "created_at": "2024-01-15T10:00:00-05:00",
  "line_items": [
    {
      "id": 987,
      "sku": "WIDGET-001",
      "quantity": 2,
      "price": "49.99"
    }
  ]
}
```

## Security Notes

- All payloads are signature-verified before any processing.
- If verification fails, a `403 Forbidden` is returned immediately.
- If no signature header is present, the request is allowed but flagged in logs.
- Each processed webhook is logged to `sync_logs` with `sync_type=webhook`.

---

# Outbound Webhooks

The system can push real-time events to external systems (e.g., e-commerce platforms, ERPs, analytics).

## Registration

Register an outbound webhook via `POST /api/webhooks/register`:
```json
{
  "endpoint_type": "price.updated",
  "target_url": "https://example.com/webhook",
  "events_subscribed": ["price.updated", "forecast.generated"]
}
```

The response contains a `signing_secret`.

## Signature Verification (External Systems)

Every outbound webhook includes an `X-Webhook-Signature` header:
```
X-Webhook-Signature: sha256=<hmac_hex>
```

You can verify the payload on your server:
```python
import hmac, hashlib
computed = "sha256=" + hmac.new(SIGNING_SECRET.encode(), request_body, hashlib.sha256).hexdigest()
assert computed == request.headers["X-Webhook-Signature"]
```

## Retry and Idempotency

- Failed deliveries are automatically retried using **exponential backoff** (e.g., 1m, 5m, 30m, 2h).
- Max retries: 5 attempts.
- Payload includes a `webhook_id` and `timestamp`. Use these to ensure idempotent processing on your end.

## Delivery History

Check delivery logs via `GET /api/webhooks/{webhook_id}/deliveries`. You can manually trigger a retry via `POST /api/webhooks/{webhook_id}/retry`.

