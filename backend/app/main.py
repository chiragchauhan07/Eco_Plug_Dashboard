from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.api import api_router
from app.core.config import settings
from app.middleware.compression import setup_compression
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware
from app.security.cors import setup_cors
from app.security.exceptions import setup_exception_handlers
from app.security.headers import setup_trusted_host


def create_app() -> FastAPI:
    """
    Factory to create the FastAPI application with custom OpenAPI metadata.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-ready backend for ECO PLUG AI Customer Intelligence Dashboard.",
        version=settings.VERSION,
        contact={
            "name": "ECO PLUG AI Support",
            "email": "support@ecoplug.ai",
        },
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Setup Middleware (Order is important)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Setup Security
    setup_compression(app)
    setup_cors(app)
    setup_trusted_host(app, allowed_hosts=settings.ALLOWED_HOSTS)
    setup_exception_handlers(app)

    # Setup Routers
    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
