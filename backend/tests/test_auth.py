from typing import cast
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.dashboard import DashboardAdminUser, DashboardAuditLog
from scripts.bootstrap_admin import bootstrap_super_admin


def test_password_hashing() -> None:
    """
    Test password hashing and verification.
    """
    password = "SuperSecurePassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


@pytest.mark.asyncio
async def test_bootstrap_super_admin(db_session: AsyncSession) -> None:
    """
    Test the bootstrap script logic.
    """
    email = "bootstrap@example.com"
    password = "BootstrapPassword123!"
    name = "Bootstrap Admin"

    # Mock async_session_maker to yield our transactional db_session
    class MockSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    with patch("scripts.bootstrap_admin.async_session_maker", new=MockSessionMaker()):
        # 1. First run should succeed
        success = await bootstrap_super_admin(email, password, name)
        assert success is True

        # Verify the user was created
        result = await db_session.execute(
            select(DashboardAdminUser).where(DashboardAdminUser.email == email)
        )
        user = result.scalars().first()
        assert user is not None
        assert user.full_name == name
        assert user.role == "SuperAdmin"
        assert verify_password(password, cast(str, user.password_hash)) is True

        # 2. Second run should fail/refuse since an admin now exists
        success_second = await bootstrap_super_admin(
            "another@example.com", "pass", "Another Admin"
        )
        assert success_second is False


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Test successful login endpoint.
    """
    # Create test user
    email = "testadmin@example.com"
    password = "MyPassword123"
    hashed = hash_password(password)

    admin = DashboardAdminUser(
        email=email,
        password_hash=hashed,
        full_name="Test Admin",
        role="Support",
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    # Call endpoint
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"

    # Check audit logs
    result = await db_session.execute(
        select(DashboardAuditLog).where(DashboardAuditLog.admin_id == admin.id)
    )
    audit = result.scalars().first()
    assert audit is not None
    assert audit.action == "login_success"


@pytest.mark.asyncio
async def test_login_invalid_password(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test login failure with invalid password.
    """
    email = "testadmin2@example.com"
    password = "MyPassword123"
    hashed = hash_password(password)

    admin = DashboardAdminUser(
        email=email,
        password_hash=hashed,
        full_name="Test Admin 2",
        role="Support",
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "WrongPassword"}
    )
    assert response.status_code == 401

    # Audit log should exist for failure
    result = await db_session.execute(
        select(DashboardAuditLog).where(DashboardAuditLog.action == "login_failure")
    )
    audit = result.scalars().first()
    assert audit is not None
    assert audit.details["reason"] == "invalid_credentials"


@pytest.mark.asyncio
async def test_login_inactive_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test login with inactive user.
    """
    email = "testadmin3@example.com"
    password = "MyPassword123"
    hashed = hash_password(password)

    admin = DashboardAdminUser(
        email=email,
        password_hash=hashed,
        full_name="Test Admin 3",
        role="Support",
        is_active=False,
    )
    db_session.add(admin)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 403

    # Audit log should exist for inactive user login failure
    result = await db_session.execute(
        select(DashboardAuditLog).where(DashboardAuditLog.action == "login_failure")
    )
    audit = result.scalars().first()
    assert audit is not None
    assert audit.details["reason"] == "user_inactive"


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Test refreshing token with valid refresh token.
    """
    email = "refreshuser@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash=hash_password("password"),
        full_name="Refresh User",
        role="Support",
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    # Generate a refresh token manually
    refresh_token = create_refresh_token(data={"sub": email})

    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


@pytest.mark.asyncio
async def test_token_refresh_invalid(client: AsyncClient) -> None:
    """
    Test refreshing token with invalid refresh token.
    """
    # 1. Invalid token format
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "not-a-valid-token"}
    )
    assert response.status_code == 401

    # 2. Access token used as refresh token
    access_token = create_access_token(data={"sub": "user@example.com"})
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": access_token}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Test GET /me with valid authentication.
    """
    email = "meuser@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash=hash_password("password"),
        full_name="Me User",
        role="Support",
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    # Generate access token
    access_token = create_access_token(data={"sub": email})

    # Call /me without auth
    response = await client.get("/api/v1/auth/me")
    assert (
        response.status_code == 401
    )  # HTTPBearer raises 401 Unauthorized when missing header

    # Call /me with auth
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == email
    assert data["data"]["full_name"] == "Me User"


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Test POST /logout endpoint.
    """
    email = "logoutuser@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash=hash_password("password"),
        full_name="Logout User",
        role="Support",
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    access_token = create_access_token(data={"sub": email})

    response = await client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify audit logs
    result = await db_session.execute(
        select(DashboardAuditLog).where(DashboardAuditLog.action == "logout")
    )
    audit = result.scalars().first()
    assert audit is not None
    assert audit.admin_id == admin.id
