from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import DashboardSettings
from app.schemas.settings import SettingUpdateRequest


class SettingsRepository:
    """
    Repository for encapsulating database operations on DashboardSettings.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self) -> List[DashboardSettings]:
        """
        Fetch all dashboard settings.
        """
        query = select(DashboardSettings).order_by(DashboardSettings.setting_key)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def upsert_many(
        self, updates: List[SettingUpdateRequest]
    ) -> List[DashboardSettings]:
        """
        Bulk update or insert settings.
        """
        updated_settings = []
        for update in updates:
            # Check if setting already exists
            query = select(DashboardSettings).where(
                DashboardSettings.setting_key == update.setting_key
            )
            result = await self.db.execute(query)
            setting = result.scalars().first()

            if setting:
                setting.setting_value = update.setting_value
                if update.description is not None:
                    setting.description = update.description  # type: ignore[assignment]
            else:
                setting = DashboardSettings(
                    setting_key=update.setting_key,
                    setting_value=update.setting_value,
                    description=update.description,
                )
                self.db.add(setting)

            updated_settings.append(setting)

        await self.db.commit()

        for setting in updated_settings:
            await self.db.refresh(setting)

        return updated_settings
