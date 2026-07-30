# Rollback Strategy

If a deployment to production fails or introduces critical bugs, follow these steps to roll back.

## 1. Automated Rollback (Application)
The CI/CD pipeline is configured to alert and suggest rollback if the error rate exceeds 5% post-deployment.
To manually trigger a rollback:
1. Go to GitHub Actions -> `Deploy to Production`.
2. Click "Run workflow".
3. Provide the previous known-good version tag (e.g. `v1.0.0`).

## 2. Database Rollback
If the deployment included a database migration (Alembic) that needs reverting:
1. SSH or connect to a production worker pod.
2. Run `alembic downgrade -1` (or specify the target revision).
3. Verify database consistency before rolling back the application code.
