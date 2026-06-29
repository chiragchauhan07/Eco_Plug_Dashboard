from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import create_access_token
from app.models.dashboard import (
    DashboardAdminUser,
    DashboardAuditLog,
    DashboardComplaintWorkflow,
)
from app.models.operational import Complaint


@pytest.mark.asyncio
async def test_complaints_unauthorized(client: AsyncClient) -> None:
    """
    Test that complaints endpoints require authentication.
    """
    response = await client.get("/api/v1/complaints")
    assert response.status_code == 401

    response = await client.patch(f"/api/v1/complaints/{uuid4()}", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_complaints_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test successful paginated complaints retrieval.
    """
    email = "admin@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    complaint = Complaint(
        ticket_id="TCK-1001",
        phone_number="1111111111",
        category="Payment",
        description="Double payment deduction.",
        status="Open",
    )
    db_session.add(complaint)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/complaints", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) >= 1
    assert data["data"]["items"][0]["ticket_id"] == "TCK-1001"
    assert data["data"]["items"][0]["workflow"]["internal_status"] == "Pending"


@pytest.mark.asyncio
async def test_patch_complaint_workflow_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test successfully patching workflow fields of a complaint, verifying:
    - Only workflow fields are modified.
    - Original operational text remains unchanged.
    - Audit log is created in the database.
    """
    email = "admin@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    orig_desc = "Unable to start session via app."
    complaint = Complaint(
        ticket_id="TCK-1002",
        phone_number="2222222222",
        category="Technical",
        description=orig_desc,
        status="Open",
    )
    db_session.add(complaint)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    # Patch workflow
    patch_data = {
        "internal_status": "InProgress",
        "assigned_admin_id": str(admin.id),
        "internal_notes": "Assigned to Admin User for investigation.",
    }

    response = await client.patch(
        f"/api/v1/complaints/{complaint.id}", json=patch_data, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify response contains the new workflow details
    wf = data["data"]["workflow"]
    assert wf["internal_status"] == "InProgress"
    assert wf["assigned_admin_id"] == str(admin.id)
    assert wf["assigned_admin_name"] == "Admin User"
    assert wf["internal_notes"] == "Assigned to Admin User for investigation."

    # Verify original operational complaint description was NOT modified
    assert data["data"]["description"] == orig_desc

    # Verify workflow is saved in database dashboard workflows table
    result = await db_session.execute(
        select(DashboardComplaintWorkflow).where(
            DashboardComplaintWorkflow.complaint_id == complaint.id
        )
    )
    db_wf = result.scalars().first()
    assert db_wf is not None
    assert db_wf.internal_status == "InProgress"
    assert db_wf.internal_notes == "Assigned to Admin User for investigation."

    # Verify audit log was created
    audit_result = await db_session.execute(
        select(DashboardAuditLog).where(
            DashboardAuditLog.action == "update_complaint_workflow"
        )
    )
    audit = audit_result.scalars().first()
    assert audit is not None
    assert audit.admin_id == admin.id
    assert audit.details["updates"]["internal_status"] == "InProgress"


@pytest.mark.asyncio
async def test_patch_complaint_invalid_admin(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test that assigning a non-existent admin ID returns 400 Bad Request.
    """
    email = "admin@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    complaint = Complaint(
        ticket_id="TCK-1003",
        phone_number="3333333333",
        category="General",
        description="Help request",
        status="Open",
    )
    db_session.add(complaint)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    # Patch with random UUID admin ID
    bad_admin_id = str(uuid4())
    patch_data = {"assigned_admin_id": bad_admin_id}

    response = await client.patch(
        f"/api/v1/complaints/{complaint.id}", json=patch_data, headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Assigned administrator does not exist."


@pytest.mark.asyncio
async def test_get_complaint_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test retrieving non-existent complaint.
    """
    email = "admin@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/complaints/{uuid4()}", headers=headers)
    assert response.status_code == 404
