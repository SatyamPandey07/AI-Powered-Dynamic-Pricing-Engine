# Alerting Runbooks

This document outlines the alerts defined in Prometheus and their respective runbooks.

## Infrastructure Alerts

### `DatabaseDown`
**Severity:** Critical
**Trigger:** PostgreSQL has not responded to scrapes for 1 minute.
**Action:**
1. Check if the database instance is running.
2. Review database logs for OOM (Out of Memory) kills or deadlocks.
3. Verify network connectivity between the app and the database.

## API Alerts

### `HighAPILatency`
**Severity:** Warning
**Trigger:** p99 latency > 5 seconds for 5 minutes.
**Action:**
1. Check database query performance in Grafana.
2. Review API logs for specific endpoints causing the spike.

### `HighErrorRate`
**Severity:** Critical
**Trigger:** 5xx error rate > 5% for 5 minutes.
**Action:**
1. Check the Loki logs for exceptions and tracebacks.
2. Identify the failing endpoint and rollback the latest deployment if necessary.

## Business Alerts

### `ForecastAccuracyDropped`
**Severity:** Warning
**Trigger:** MAPE > 30% for 7 days.
**Action:**
1. Review the Prophet model training logs.
2. Consider retraining the model with recent historical data.

### `WebhookDeliveryFailed`
**Severity:** Warning
**Trigger:** Webhook success rate < 95%.
**Action:**
1. Check integration logs.
2. Verify external API status (e.g. Shopify/WooCommerce).
