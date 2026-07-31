# Deployment Guide

This document outlines the deployment strategy for the AI-Powered Dynamic Pricing Engine.

## Environments
1. **Development**: Local environment using `docker-compose`.
2. **Staging**: Automatically deployed from `develop` branch.
3. **Production**: Manually deployed from `main` branch.

## Staging Deployment
Pushes to the `develop` branch automatically trigger `.github/workflows/deploy-staging.yml`.
- Docker images are built and pushed to GHCR with the `staging` tag.
- The staging environment pulls the latest image.

## Production Deployment
Production deployments are manually triggered via GitHub Actions -> **Deploy to Production** (`workflow_dispatch`).
- Ensure all CI tests pass.
- Images are tagged with the Git SHA and `latest`.
- Database migrations are run automatically.
- After deployment, a smoke test runs against the production health endpoint.

## Secrets
All secrets (database credentials, API keys) must be injected via environment variables and configured in your hosting provider (e.g. Render/AWS) and GitHub Actions Secrets (`SLACK_WEBHOOK_URL`, `RENDER_PROD_DEPLOY_HOOK`).
