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
