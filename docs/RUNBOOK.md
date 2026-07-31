# Runbook

## Troubleshooting Deployment Issues

### 1. Database Migration Failures
**Symptom**: Application fails to start, health check returns 500. logs show `psycopg2.errors` or `alembic` errors.
**Action**:
- Check the deployment logs to identify the failing migration.
- If the migration is flawed, trigger a manual rollback to the previous deployment.
- Revert the problematic migration commit locally, fix it, and create a new PR.

### 2. High Error Rate Post-Deployment
**Symptom**: Slack alerts for "Error rate > 5%". Grafana shows spikes in 5xx errors.
**Action**:
- Check Loki logs for stack traces.
- If it's a critical bug introduced in the new version, perform an immediate manual rollback.

### 3. Integration Sync Failures
**Symptom**: Webhook delivery fails or inventory sync jobs fail repeatedly.
**Action**:
- Ensure external APIs (Shopify, WooCommerce) have not changed their endpoints or rate limits.
- Validate the encrypted credentials in the database are correct.
