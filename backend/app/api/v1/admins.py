from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.session import get_db_session
from app.dependencies.auth import get_current_active_user
from app.models.dashboard import DashboardAdminUser
from app.utils.response import StandardResponse

router = APIRouter()

@router.get("", response_model=StandardResponse[list[dict[str, Any]]])
async def get_admins(
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[list[dict[str, Any]]]:
    """
    Get a list of all active administrators.
    Returns only id and full_name to prevent exposing unnecessary fields.
    """
    result = await db.execute(
        select(DashboardAdminUser.id, DashboardAdminUser.full_name)
        .where(DashboardAdminUser.is_active)
    )
    admins = result.all()
    
    admin_list = [{"id": str(admin.id), "full_name": admin.full_name} for admin in admins]

    return StandardResponse(
        success=True,
        message="Administrators fetched successfully",
        data=admin_list,
    )
