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