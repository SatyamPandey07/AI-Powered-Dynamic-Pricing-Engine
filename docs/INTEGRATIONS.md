# E-Commerce Integrations

The DynamicPricingEngine connects to e-commerce platforms to sync inventory, pull historical sales, and push optimized prices. The integration framework is extensible — any REST API can be supported via the Custom adapter.

## Supported Platforms

| Platform | Auth | Products | Orders | Push Prices |
|----------|------|----------|--------|-------------|
| Shopify | OAuth2 | ✅ | ✅ | ✅ (via variant ID) |
| WooCommerce | API Key + Secret | ✅ | ✅ | ✅ (via product ID) |
| Custom API | API Key / Bearer / Basic | ✅ configurable | ✅ configurable | ✅ configurable |

## Shopify Setup

1. Create a Shopify Private App or Public App in the Partner Dashboard.
2. Request OAuth scopes: `read_products`, `write_products`, `read_orders`.
3. Register the integration:

```bash
POST /api/integrations
{
  "platform": "shopify",
  "name": "My Shopify Store",
  "credentials": {
    "shop_url": "https://my-store.myshopify.com",
    "api_key": "<client_id>",
    "api_secret": "<client_secret>",
    "webhook_secret": "<webhook_signing_secret>"
  }
}
```

4. Visit the `auth_url` returned to complete the OAuth flow.
5. Test the connection: `POST /api/integrations/{id}/test`

## WooCommerce Setup

1. In WooCommerce → Settings → Advanced → REST API, generate a new key with Read/Write permissions.
2. Register the integration:

```bash
POST /api/integrations
{
  "platform": "woocommerce",
  "name": "My WooCommerce Store",
  "credentials": {
    "site_url": "https://mysite.com",
    "api_key": "ck_xxx",
    "api_secret": "cs_xxx"
  }
}
```

## Custom API Setup

Define your API shape via `config.field_mappings`:

```json
{
  "platform": "custom",
  "credentials": {
    "base_url": "https://api.my-platform.com",
    "auth_type": "api_key",
    "api_key_header": "X-API-Key",
    "api_key": "my_key"
  },
  "config": {
    "products_endpoint": "/catalog/products",
    "orders_endpoint": "/sales/orders",
    "update_price_endpoint": "/catalog/products/{product_id}",
    "price_field": "sale_price",
    "field_mappings": {
      "products": {
        "sku": "product_code",
        "price": "unit_price",
        "inventory_quantity": "stock_on_hand"
      }
    }
  }
}
```

## Sync Frequencies

| Sync Type | Frequency | Trigger |
|-----------|-----------|---------|
| Inventory | Every 2 hours | Celery crontab |
| Sales history | Every 4 hours | Celery crontab |
| Price push | Daily 8 AM UTC | Celery crontab |
| Manual | On-demand | `GET /api/integrations/{id}/sync-inventory` |

## Credential Security

- Credentials are **never stored in plaintext**. They are encrypted using **Fernet (AES-128-CBC + HMAC-SHA256)** before persisting.
- The encryption key is loaded from the `ENCRYPTION_KEY` environment variable.
- Credential changes are audit-logged in `integration_credentials_history` (by key-set hash, never the actual secrets).
- Credentials are **never logged** at any log level.
