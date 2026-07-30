# Deployment Guide

The application is deployed using GitHub Actions pipelines.

## Environments
- **Staging**: `develop` branch automatically deploys to staging.
- **Production**: Manual trigger targeting `main` or specific tags.

## Infrastructure Options
1. **Render (Default)**: We use Render Web Services for both backend and frontend. The `render.yaml` (if added) configures IaC.
2. **AWS ECS**: Scalable, load-balanced deployment.

## Deployment Checklist
- [ ] CI pipeline (tests, linting, Trivy scan) passes.
- [ ] No CRITICAL vulnerabilities in the Docker image.
- [ ] Staging environment has been stable for >1 hour.
- [ ] Runbook has been reviewed and team lead has given approval.
