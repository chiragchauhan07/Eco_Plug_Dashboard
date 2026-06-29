from datetime import datetime, timezone
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.database.session import get_db_session
from app.dependencies.auth import get_current_active_user
from app.models.dashboard import DashboardAdminUser, DashboardAuditLog
from app.schemas.auth import AdminUserResponse, LoginRequest, RefreshRequest, Token
from app.utils.response import StandardResponse

router = APIRouter()


@router.post("/login", response_model=StandardResponse[Token])
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> StandardResponse[Token]:
    # Query user by email
    result = await db.execute(
        select(DashboardAdminUser).where(DashboardAdminUser.email == login_data.email)
    )
    user = result.scalars().first()

    ip_address = request.client.host if request.client else None

    if not user or not verify_password(
        login_data.password, cast(str, user.password_hash)
    ):
        # Audit log login failure
        audit_log = DashboardAuditLog(
            admin_id=user.id if user else None,
            action="login_failure",
            resource_type="auth",
            resource_id=user.id if user else None,
            ip_address=ip_address,
            details={"email": login_data.email, "reason": "invalid_credentials"},
        )
        db.add(audit_log)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        audit_log = DashboardAuditLog(
            admin_id=user.id,
            action="login_failure",
            resource_type="auth",
            resource_id=user.id,
            ip_address=ip_address,
            details={"email": login_data.email, "reason": "user_inactive"},
        )
        db.add(audit_log)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Generate tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    # Update last login time
    user.last_login_at = datetime.now(timezone.utc)  # type: ignore[assignment]
    db.add(user)

    # Audit log login success
    audit_log = DashboardAuditLog(
        admin_id=user.id,
        action="login_success",
        resource_type="auth",
        resource_id=user.id,
        ip_address=ip_address,
        details={"email": user.email},
    )
    db.add(audit_log)
    await db.commit()

    return StandardResponse(
        success=True,
        message="Login successful",
        data=Token(access_token=access_token, refresh_token=refresh_token),
    )


@router.post("/refresh", response_model=StandardResponse[Token])
async def refresh(
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db_session),
) -> StandardResponse[Token]:
    payload = decode_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    result = await db.execute(
        select(DashboardAdminUser).where(DashboardAdminUser.email == email)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    # Generate new access and refresh tokens
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})

    return StandardResponse(
        success=True,
        message="Token refreshed successfully",
        data=Token(access_token=new_access_token, refresh_token=new_refresh_token),
    )


@router.post("/logout", response_model=StandardResponse[None])
async def logout(
    request: Request,
    current_user: DashboardAdminUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
) -> StandardResponse[None]:
    ip_address = request.client.host if request.client else None

    # Audit log logout
    audit_log = DashboardAuditLog(
        admin_id=current_user.id,
        action="logout",
        resource_type="auth",
        resource_id=current_user.id,
        ip_address=ip_address,
        details={"email": current_user.email},
    )
    db.add(audit_log)
    await db.commit()

    return StandardResponse(
        success=True,
        message="Logout successful",
        data=None,
    )


@router.get("/me", response_model=StandardResponse[AdminUserResponse])
async def get_me(
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[AdminUserResponse]:
    return StandardResponse(
        success=True,
        message="Current user fetched successfully",
        data=AdminUserResponse.model_validate(current_user),
    )
