# Monitoring Guide

This document outlines the monitoring infrastructure for the Dynamic Pricing Engine.

## Stack Overview
- **Prometheus**: Time-series database scraping `/metrics`.
- **Grafana**: Visualization dashboards.
- **Loki**: Log aggregation.
- **Promtail**: Ships Docker container logs to Loki.

## Accessing Dashboards
- **Grafana**: http://localhost:3001
  - User: `admin`
  - Password: `admin` (or defined in `GF_SECURITY_ADMIN_PASSWORD`)

## Key Metrics Scraped
1. **API Metrics**: `api_request_count`, `api_request_latency_seconds`.
2. **Business Metrics**: `forecast_mape`, `webhook_success_rate`.

## Health Checks
- `/health`: Fast status check for dependencies.
- `/health/ready`: Strict check to ensure the application can take traffic.
