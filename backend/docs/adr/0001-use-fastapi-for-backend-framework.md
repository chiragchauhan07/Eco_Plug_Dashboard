# ADR 0001: Use FastAPI for Backend Framework

## Context
The ECO PLUG AI Customer Intelligence Dashboard requires a high-performance, robust, and scalable backend foundation. We need a framework that natively supports async operations, provides built-in validation, and auto-generates documentation.

## Decision
We will use **FastAPI** as the core backend framework.

## Status
Accepted

## Consequences
- **Pros**: Natively asynchronous, extremely fast, auto-generated OpenAPI documentation, integrates natively with Pydantic for data validation.
- **Cons**: Smaller ecosystem compared to Django; requires manual setup of architecture and security configurations (which we have done).
