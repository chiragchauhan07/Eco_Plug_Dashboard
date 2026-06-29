import time
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to calculate request processing time and attach it to response headers.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response  # type: ignore[no-any-return]
