# ECO PLUG AI Customer Intelligence Dashboard - Backend

This is the FastAPI backend foundation for the ECO PLUG AI Customer Intelligence Dashboard.

## Architecture & Security Boundary

> **CRITICAL ARCHITECTURE REQUIREMENT**
> 
> We employ a strict **Backend-For-Frontend (BFF)** architecture. 
> - The frontend must **NEVER** communicate directly with the database (Supabase).
> - The frontend must **NEVER** receive the Supabase Service Role Key or database credentials.
> - Only this FastAPI backend communicates with Supabase. The frontend communicates exclusively with this API.

## Tech Stack
- Python 3.13+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Supabase PostgreSQL (asyncpg)
- `uv` for dependency management

## Local Setup

1. **Install `uv`**: Follow the [official uv installation guide](https://github.com/astral-sh/uv).
2. **Clone the repository** and navigate to the `backend` folder.
3. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your local or development database URL
   ```
4. **Install Dependencies**:
   ```bash
   uv sync
   ```
5. **Run the Server**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
6. **Access Documentation**:
   - Swagger UI: `http://localhost:8000/docs`

## Docker Setup

To run the application using Docker:

```bash
docker-compose up --build -d
```

## Running Alembic

*Note: Alembic is initialized but no initial migrations have been created yet.*

To create a new migration:
```bash
uv run alembic revision --autogenerate -m "Migration message"
```

To apply migrations:
```bash
uv run alembic upgrade head
```

## Development Workflow
- Code quality is enforced by `ruff`, `black`, `isort`, and `mypy`.
- Pre-commit hooks are configured. To install them: `uv run pre-commit install`
- Tests can be run via: `uv run pytest`
