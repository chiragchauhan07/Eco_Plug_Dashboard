# Security Guidelines

## Security Philosophy
Security is a core pillar of the ECO PLUG AI platform. We follow the principle of least privilege, strict input validation, and defense in depth.

## Backend/Frontend Trust Boundary
> **CRITICAL**: The frontend must **NEVER** communicate directly with the Supabase database. All communications go through the FastAPI backend API. The backend is the single source of truth and the only component authorized to interact with the database.

## Secret Management
- Secrets must **NEVER** be hardcoded.
- All secrets are loaded via environment variables using `pydantic-settings`.
- In production, a secrets manager should inject these environment variables.

## API Security
- Strict CORS configuration is enforced.
- Trusted Host middleware prevents Host header injection.
- Centralized exception handlers prevent stack trace leakage.

## Future Strategy
- **Authentication**: To be implemented via JWT or secure session cookies.
- **Audit Logging**: The `app/audit` package will track logins, sensitive actions, and administrative operations.
