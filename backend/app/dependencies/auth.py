from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import decode_token
from app.database.session import get_db_session
from app.models.dashboard import DashboardAdminUser

reusable_oauth2 = HTTPBearer()


async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token_credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> DashboardAdminUser:
    """
    Resolve the JWT from the Authorization: Bearer <token> header,
    decode and validate it, and fetch the corresponding admin user.
    """
    token = token_credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch admin user from DB
    result = await db.execute(
        select(DashboardAdminUser).where(DashboardAdminUser.email == email)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: DashboardAdminUser = Depends(get_current_user),
) -> DashboardAdminUser:
    """
    Ensure the resolved user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


class RequireRole:
    """
    Enforce role-based access control (RBAC).
    """

    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: DashboardAdminUser = Depends(get_current_active_user),
    ) -> DashboardAdminUser:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user
