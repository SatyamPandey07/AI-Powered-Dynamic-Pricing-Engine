# Rollback Strategy

## Automated Rollback
Currently, the pipeline monitors the 5-minute error rate post-deployment. If it exceeds 5%, an alert is fired to Slack. In a fully managed environment like Render or Kubernetes, you can configure automatic traffic shifting or rollback based on these health checks failing.

## Manual Rollback
If a production deployment introduces a critical bug:
1. Go to your hosting provider's dashboard (e.g., Render).
2. Select the previous successful deployment and click **"Rollback to this deploy"**.
3. (Alternatively) If using manual Docker commands, update the orchestration to use the previous Git SHA tag instead of `latest`.

## Database Rollback
If a database migration caused the issue:
1. SSH into a running backend container (or use a standalone migration task).
2. Run `alembic downgrade -1` (or to the specific safe revision).
3. Ensure the rolled-back code version matches the downgraded schema.
