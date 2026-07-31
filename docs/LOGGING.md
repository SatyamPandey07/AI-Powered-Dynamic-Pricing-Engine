# Logging Guide

This document outlines the structured logging architecture.

## Format
All applications output **JSON structured logs** to stdout. This ensures they can be easily parsed by Promtail and indexed by Loki.

### Example Log
```json
{
  "timestamp": "2026-07-30T12:00:00Z",
  "level": "INFO",
  "name": "fastapi",
  "message": "Request processed",
  "request_id": "req-12345",
  "method": "POST",
  "path": "/api/v1/optimize",
  "status_code": 200,
  "duration_ms": 150.5
}
```

## Correlation IDs
A `request_id` is generated for every incoming request via `CorrelationIdMiddleware`. This ID is injected into every log emitted during the lifecycle of the request, allowing for distributed tracing across services.

## Querying Loki in Grafana
Use LogQL in Grafana's Explore tab:
1. View all API logs: `{job="containerlogs"}`
2. Find errors: `{job="containerlogs"} |= "ERROR"`
3. Trace a specific request: `{job="containerlogs"} |= "req-12345"`
