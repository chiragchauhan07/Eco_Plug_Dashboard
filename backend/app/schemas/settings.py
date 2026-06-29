from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SettingItemResponse(BaseModel):
    """
    Response schema for a single dashboard setting.
    """

    id: UUID
    setting_key: str
    setting_value: Any
    description: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SettingUpdateRequest(BaseModel):
    """
    Request schema for updating a single setting.
    """

    setting_key: str
    setting_value: Any
    description: Optional[str] = None


class SettingsBulkUpdateRequest(BaseModel):
    """
    Request schema for bulk updating multiple settings.
    """

    settings: List[SettingUpdateRequest]
