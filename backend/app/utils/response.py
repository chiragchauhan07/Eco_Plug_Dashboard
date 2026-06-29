from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """
    Standard API Response architecture.
    All future endpoints should return this structure.
    """

    success: bool
    message: str
    data: Optional[T] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    request_id: Optional[str] = None
