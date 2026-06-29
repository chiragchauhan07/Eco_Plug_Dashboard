from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.settings import SettingsRepository
from app.schemas.settings import SettingItemResponse, SettingsBulkUpdateRequest


class SettingsService:
    """
    Service layer for Settings operations.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.repo = SettingsRepository(db)

    async def get_all_settings(self) -> List[SettingItemResponse]:
        """
        Retrieve all current dashboard settings.
        """
        settings = await self.repo.get_all()
        return [SettingItemResponse.model_validate(s) for s in settings]

    async def update_settings(
        self, request: SettingsBulkUpdateRequest
    ) -> List[SettingItemResponse]:
        """
        Bulk update dashboard settings.
        """
        updated = await self.repo.upsert_many(request.settings)
        return [SettingItemResponse.model_validate(s) for s in updated]
