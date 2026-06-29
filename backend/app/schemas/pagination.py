from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationInfo(BaseModel):
    page: int
    size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponseData(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationInfo
