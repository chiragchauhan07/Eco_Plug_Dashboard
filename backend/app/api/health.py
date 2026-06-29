from typing import Any

from fastapi import APIRouter

from app.core.config import settings
from app.utils.response import StandardResponse

router = APIRouter()


@router.get("/health", response_model=StandardResponse[dict[str, Any]])
async def health_check() -> StandardResponse[dict[str, Any]]:
    """
    Basic health check to verify the application is running.
    """
    return StandardResponse(
        success=True,
        message="Application is running",
        data={"version": settings.VERSION, "env": settings.ENV},
    )


@router.get("/ready", response_model=StandardResponse[dict[str, Any]])
async def readiness_check() -> StandardResponse[dict[str, Any]]:
    """
    Readiness check to verify that required services (e.g. database) are ready.
    In a real scenario, this would ping the database.
    """
    # TODO: Add database ping here once models are integrated
    return StandardResponse(
        success=True, message="All services are ready", data={"database": "ok"}
    )
