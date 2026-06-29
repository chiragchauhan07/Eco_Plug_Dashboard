import logging
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured request logging.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        # We can extract request.state.request_id here if needed
        # Skip logging health checks to reduce noise
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)  # type: ignore[no-any-return]

        # Add actual structured logging logic later
        response = await call_next(request)
        return response  # type: ignore[no-any-return]
