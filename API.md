# API Documentation

## Authentication Endpoints
- `POST /api/auth/signup`: Create a new organization and admin user.
- `POST /api/auth/login`: Authenticate and receive JWT tokens.
- `POST /api/auth/refresh`: Refresh access token.

## Organization Endpoints
- `GET /api/orgs`: Retrieve current organization details.
- `PUT /api/orgs`: Update organization settings (Admin only).

## User Endpoints
- `GET /api/users`: List users in the organization.
- `POST /api/users`: Invite a new user.
- `PUT /api/users/{id}`: Update a user's role.
- `DELETE /api/users/{id}`: Deactivate a user.

## API Keys
- `GET /api/api-keys`: List API keys for the organization.
- `POST /api/api-keys`: Generate a new API key.
- `DELETE /api/api-keys/{id}`: Revoke an API key.

## Audit Logs
- `GET /api/audit-logs`: View organization audit logs with optional filtering.

## Demand Forecasting
- `POST /api/forecast/train`: Train Prophet/ARIMA ensemble models for a specific SKU.
- `GET /api/forecast/predict/{sku_id}`: Generate a forecast for the next N days.
- `GET /api/forecast/accuracy/{sku_id}`: Retrieve model accuracy metrics (MAPE/MAE).
- `POST /api/forecast/retrain`: Manually trigger the Celery retraining pipeline.

## Competitor Tracking
- `POST /api/competitors`: Register a new competitor to track.
- `GET /api/competitors`: List configured competitors.
- `PUT /api/competitors/{id}`: Update competitor scraping config.
- `DELETE /api/competitors/{id}`: Deactivate a competitor.
- `POST /api/competitors/{id}/sku-mapping`: Map an internal SKU to a competitor product.
- `GET /api/prices/competitor/{sku_id}`: View the current lowest competitor prices for a SKU.
- `GET /api/prices/competitor/{sku_id}/history`: View historical price trends.

## External Signals
- `POST /api/signals/weather`: Fetch weather for the organization's location.
- `POST /api/signals/events`: Add a custom event affecting SKU demand.

## Price Elasticity
- `GET /api/elasticity/{sku_id}`: Calculate or retrieve elasticity estimate with confidence interval.
- `POST /api/elasticity/test/{sku_id}`: Start an A/B pricing test.
- `GET /api/elasticity/test/{test_id}`: View A/B test results and statistical winner.

## Price Optimization
- `POST /api/optimize/price`: Get an AI-driven price recommendation for a SKU.
- `GET /api/optimize/{sku_id}/recommendation`: Fetch latest recommendation for a SKU.
- `POST /api/optimize/scenario`: Simulate the revenue/demand impact of a hypothetical price.
- `POST /api/optimize/markdown/{sku_id}`: Get a proactive markdown schedule for aging inventory.

## Pricing Rules
- `POST /api/rules`: Create a pricing guardrail rule.
- `GET /api/rules`: List all pricing rules.
- `PUT /api/rules/{id}`: Activate or deactivate a rule.

## Platform Integrations
- `POST /api/integrations`: Register a new Shopify, WooCommerce, or Custom integration.
- `GET /api/integrations`: List all integrations.
- `PUT /api/integrations/{id}`: Update sync config or rotate credentials.
- `DELETE /api/integrations/{id}`: Disconnect an integration.
- `POST /api/integrations/{id}/test`: Test connection and verify credentials.
- `GET /api/integrations/{id}/sync-inventory`: Trigger manual inventory sync.
- `GET /api/integrations/{id}/sync-sales-history`: Trigger manual sales sync.
- `POST /api/integrations/{id}/push-prices`: Push price recommendations to platform.

## Webhooks (Inbound)
- `POST /api/webhooks/integrations/{integration_id}`: Receive and process platform webhooks (HMAC-SHA256 verified).

## Webhooks (Outbound)
- `POST /api/webhooks/register`: Register a new outbound webhook.
- `GET /api/webhooks`: List all outbound webhooks for the org.
- `PUT /api/webhooks/{id}`: Update webhook target or subscriptions.
- `DELETE /api/webhooks/{id}`: Deactivate a webhook.
- `GET /api/webhooks/{id}/deliveries`: List delivery history and retry status.
- `POST /api/webhooks/{id}/retry`: Manually retry a failed delivery.
- `POST /api/webhooks/{id}/test`: Trigger a test webhook payload.