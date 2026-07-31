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