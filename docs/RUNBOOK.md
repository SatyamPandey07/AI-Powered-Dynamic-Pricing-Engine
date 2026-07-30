# Operational Runbook

This runbook helps on-call engineers troubleshoot deployment and runtime issues.

## Common Issues

### Deploy Fails due to Trivy Scan
**Symptom**: CI pipeline fails at the "docker-scan" step.
**Resolution**: Check the CI logs for CVEs. Update the base image or dependencies in `Dockerfile` to patch the vulnerability.

### High API Latency after Deploy
**Symptom**: Prometheus Alert `HighAPILatency` fires immediately after a production deploy.
**Resolution**: 
1. Check if database migrations caused table locks.
2. Trigger the Rollback pipeline immediately (see `ROLLBACK.md`).

### Staging Smoke Tests Fail
**Symptom**: Deploy to staging succeeds, but smoke tests fail.
**Resolution**: Verify if environment variables (e.g. database credentials) were rotated or missed in the GitHub Secrets configuration.
