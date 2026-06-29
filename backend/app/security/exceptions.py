import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.utils.response import StandardResponse

logger = logging.getLogger("security")


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup centralized exception handlers to prevent stack trace leaks in production.
    """

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(f"Unhandled exception: {exc}")
        request_id = getattr(request.state, "request_id", None)

        content = StandardResponse(
            success=False,
            message="An unexpected server error occurred.",
            request_id=request_id,
        ).model_dump()

        return JSONResponse(
            status_code=500,
            content=content,
        )
