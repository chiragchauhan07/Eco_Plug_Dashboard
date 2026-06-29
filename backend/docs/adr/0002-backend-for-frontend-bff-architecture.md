# ADR 0002: Backend-For-Frontend (BFF) Architecture

## Context
A critical decision is how the frontend will communicate with Supabase (which acts as our database). Exposing the Supabase URL and anonymous keys to the frontend directly poses a security risk and couples the frontend to the database schema.

## Decision
We enforce a strict **Backend-For-Frontend (BFF)** architecture. The frontend will NEVER communicate directly with Supabase. Only the FastAPI backend will hold the Supabase credentials and interact with the database.

## Status
Accepted

## Consequences
- **Pros**:
  - **Security**: Supabase credentials (and the Service Role Key if ever needed) remain completely isolated in the backend.
  - **Maintainability**: The frontend is decoupled from the database schema. The backend provides a tailored, stable API contract.
  - **Flexibility**: We can easily swap or augment data sources (e.g., adding a cache layer or interacting with AI LLMs) without changing the frontend logic.
- **Cons**:
  - Requires maintaining a middle tier (FastAPI) rather than leveraging Supabase's client libraries directly in the frontend, adding initial development overhead.
