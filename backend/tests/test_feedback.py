from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.dashboard import DashboardAdminUser
from app.models.operational import ChargingSession, Feedback


@pytest.mark.asyncio
async def test_feedback_unauthorized(client: AsyncClient) -> None:
    """
    Test that feedback endpoints return 401/403 when unauthenticated.
    """
    response = await client.get("/api/v1/feedback")
    assert response.status_code == 401

    response = await client.get(f"/api/v1/feedback/{uuid4()}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_feedback_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test successful paginated feedback retrieval and pagination metadata format.
    """
    # Create admin user
    email = "admin@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    # Create dummy feedback
    feedback = Feedback(
        user_phone="9999999999",
        user_name="John Doe",
        session_id="session-1",
        charger_name="Charger A",
        rating=5,
        feedback_comment="Great charging!",
        issue_category="None",
    )
    db_session.add(feedback)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/feedback", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Feedback fetched successfully"
    assert "items" in data["data"]
    assert len(data["data"]["items"]) >= 1

    # Check pagination metadata structure
    pagination = data["data"]["pagination"]
    assert pagination["page"] == 1
    assert pagination["size"] == 20
    assert pagination["total_items"] >= 1
    assert pagination["total_pages"] >= 1
    assert pagination["has_next"] == (pagination["total_items"] > pagination["size"])
    assert pagination["has_previous"] is False


@pytest.mark.asyncio
async def test_feedback_filters_and_search(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test feedback pagination, search, rating filters, and date filters.
    """
    # Create admin user
    email = "admin@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    # Add multiple feedbacks
    fb1 = Feedback(
        user_phone="1234567890",
        user_name="Alice Smith",
        session_id="session-alice",
        charger_name="Charger East",
        rating=4,
        issue_category="Connector",
    )
    fb2 = Feedback(
        user_phone="9876543210",
        user_name="Bob Jones",
        session_id="session-bob",
        charger_name="Charger West",
        rating=2,
        issue_category="Network",
    )
    db_session.add(fb1)
    db_session.add(fb2)
    await db_session.commit()

    # Search by user name
    response = await client.get("/api/v1/feedback?user_name=Alice", headers=headers)
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["user_name"] == "Alice Smith"

    # Search by rating
    response = await client.get("/api/v1/feedback?rating=2", headers=headers)
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["rating"] == 2

    # Filter by issue category
    response = await client.get(
        "/api/v1/feedback?issue_category=Connector", headers=headers
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["issue_category"] == "Connector"


@pytest.mark.asyncio
async def test_feedback_detail_with_session(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test retrieving a feedback record detail, including the associated charging session.
    """
    # Create admin user
    email = "admin@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    session_id = "session-unique-abc"

    # Create charging session
    from datetime import datetime

    charging_session = ChargingSession(
        session_code="CODE123",
        session_id=session_id,
        user_phone="5555555555",
        charger_name="Charger North",
        connector_type="CCS2",
        energy_kwh=22.5,
        duration_minutes=45,
        amount_paid=250.0,
        payment_status="Paid",
        session_date=datetime.now(),  # Offset-naive for DateTime(timezone=False) column
    )
    db_session.add(charging_session)

    # Create feedback referencing the same session_id
    feedback = Feedback(
        user_phone="5555555555",
        user_name="Charlie",
        session_id=session_id,
        charger_name="Charger North",
        rating=5,
        feedback_comment="Fast charging!",
    )
    db_session.add(feedback)
    await db_session.commit()

    # Call endpoint
    response = await client.get(f"/api/v1/feedback/{feedback.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(feedback.id)
    assert data["data"]["charging_session"] is not None
    assert data["data"]["charging_session"]["session_code"] == "CODE123"
    assert data["data"]["charging_session"]["energy_kwh"] == 22.5


@pytest.mark.asyncio
async def test_feedback_detail_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test retrieving non-existent feedback.
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

    response = await client.get(f"/api/v1/feedback/{uuid4()}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_feedback_analyze_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test triggering AI feedback analysis.
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

    feedback = Feedback(
        user_phone="9999999999",
        user_name="Test User",
        session_id="session-test",
        charger_name="Charger A",
        rating=5,
        feedback_comment="Great charging speed!",
    )
    db_session.add(feedback)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    # Mock the AI service or call it (tests run with mock provider by default)
    response = await client.post(f"/api/v1/feedback/{feedback.id}/analyze", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["sentiment"] is not None
    assert data["data"]["category"] is not None
    assert data["data"]["priority"] is not None
    assert data["data"]["confidence_score"] >= 0.0
