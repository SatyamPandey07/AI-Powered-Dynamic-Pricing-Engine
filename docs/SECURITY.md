# Security

- **Auth model**: JWT with `org_id` scoped access. Supports Refresh tokens.
- **Data protection**: passwords hashed via bcrypt.
- **Multi-tenancy**: Strict isolation; no cross-org data leakage.
- **RBAC**: Three roles implemented (ADMIN, EDITOR, VIEWER).
- **Audit Logging**: Comprehensive action logging for compliance (GDPR/SOX). Logs IP, user_agent, action, and resource.
- **Rate Limiting**: Redis-backed limits of 100 req/min/user.
- **Security Headers**: Strict transport security, X-Frame-Options, CSP, and no-sniff enabled.
- **Password Policy**: Requires minimum 12 chars, uppercase, lowercase, numbers, and special characters.