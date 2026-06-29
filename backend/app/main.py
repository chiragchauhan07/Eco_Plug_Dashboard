import sys

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

    # --- Startup Diagnostics ---
    print(f"[STARTUP] ENV={settings.ENV}", file=sys.stderr)
    print(f"[STARTUP] DEBUG={settings.DEBUG}", file=sys.stderr)
    print(f"[STARTUP] ALLOWED_HOSTS={settings.ALLOWED_HOSTS}", file=sys.stderr)
    print(f"[STARTUP] CORS_ORIGINS={settings.CORS_ORIGINS}", file=sys.stderr)

    # Setup Middleware (Order is important)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Setup Security
    setup_compression(app)
    setup_cors(app)

    # TrustedHostMiddleware: Only enable when explicit hosts are configured
    # (not the wildcard default). On Render / cloud platforms the reverse
    # proxy already validates the Host header, so application-level
    # validation is redundant and causes "Invalid host header" errors
    # when the proxy forwards an unexpected Host value.
    if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS != ["*"]:
        print(f"[STARTUP] TrustedHostMiddleware ENABLED with: {settings.ALLOWED_HOSTS}", file=sys.stderr)
        setup_trusted_host(app, allowed_hosts=settings.ALLOWED_HOSTS)
    else:
        print("[STARTUP] TrustedHostMiddleware DISABLED (ALLOWED_HOSTS=['*'] or empty)", file=sys.stderr)

    setup_exception_handlers(app)

    # Setup Routers
    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
