# Architecture

## Monorepo
- `/backend`: FastAPI Python backend
- `/frontend`: Next.js React frontend
- `/infra`: Docker compose and DB migrations

## Database
- PostgreSQL + TimescaleDB for time-series data
- Redis for caching

## Multi-Tenancy
- Row-level security / logical separation via `org_id`