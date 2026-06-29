from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.dependencies.auth import get_current_active_user
from app.models.dashboard import DashboardAdminUser
from app.schemas.settings import SettingItemResponse, SettingsBulkUpdateRequest
from app.services.settings import SettingsService
from app.utils.response import StandardResponse

router = APIRouter()


@router.get("", response_model=StandardResponse[List[SettingItemResponse]])
async def get_settings(
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[List[SettingItemResponse]]:
    """
    Get all dashboard settings.
    """
    service = SettingsService(db)
    settings = await service.get_all_settings()
    return StandardResponse(
        success=True,
        message="Settings fetched successfully",
        data=settings,
    )


@router.put("", response_model=StandardResponse[List[SettingItemResponse]])
async def update_settings(
    request: SettingsBulkUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[List[SettingItemResponse]]:
    """
    Bulk update dashboard settings.
    """
    service = SettingsService(db)
    updated = await service.update_settings(request)
    return StandardResponse(
        success=True,
        message="Settings updated successfully",
        data=updated,
    )
