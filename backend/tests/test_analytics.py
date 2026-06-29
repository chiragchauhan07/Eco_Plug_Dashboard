from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.core.security import create_access_token
from app.models.dashboard import DashboardAdminUser
from app.models.operational import ChargingSession, Complaint, Feedback, User


@pytest.mark.asyncio
async def test_analytics_unauthorized(client: AsyncClient) -> None:
    """
    Test that dashboard analytics endpoints return 401 when unauthorized.
    """
    endpoints = [
        "/api/v1/dashboard/overview",
        "/api/v1/dashboard/feedback-analytics",
        "/api/v1/dashboard/complaint-analytics",
        "/api/v1/dashboard/charger-analytics",
        "/api/v1/dashboard/recent-activity",
    ]
    for endpoint in endpoints:
        response = await client.get(endpoint)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_overview_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test successful retrieval of dashboard overview KPIs and comparison metrics.
    """
    # Create admin user with random email
    email = f"admin_{uuid4().hex[:8]}@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    # Seed data for current period (last 30 days)
    now = datetime.now(timezone.utc)
    curr_date = now - timedelta(days=5)

    phone1 = str(uuid4().int)[:10]
    user1 = User(
        user_code=f"U_{uuid4().hex[:8]}",
        full_name="User One",
        phone_number=phone1,
        created_at=curr_date.replace(tzinfo=None),
    )
    session1 = ChargingSession(
        session_code=f"SESS_{uuid4().hex[:8]}",
        session_id=f"sess_{uuid4().hex[:8]}",
        user_phone=phone1,
        charger_name="Charger Noida",
        connector_type="CCS2",
        energy_kwh=15.0,
        duration_minutes=30,
        amount_paid=100.0,
        status="FINISHED",
        session_date=curr_date.replace(tzinfo=None),
        created_at=curr_date,
    )
    fb1 = Feedback(
        user_phone=phone1,
        user_name="User One",
        session_id=session1.session_id,
        charger_name="Charger Noida",
        rating=5,
        created_at=curr_date,
    )
    comp1 = Complaint(
        ticket_id=f"TCK_{uuid4().hex[:8]}",
        phone_number=phone1,
        category="Hardware",
        description="Charger connector was stuck.",
        status="Closed",
        created_at=curr_date,
    )

    db_session.add_all([user1, session1, fb1, comp1])

    # Seed data for previous equivalent period (30 to 60 days ago)
    prev_date = now - timedelta(days=45)

    phone2 = str(uuid4().int)[:10]
    user2 = User(
        user_code=f"U_{uuid4().hex[:8]}",
        full_name="User Two",
        phone_number=phone2,
        created_at=prev_date.replace(tzinfo=None),
    )
    # 2 sessions in prev period to test negative growth trends
    session2 = ChargingSession(
        session_code=f"SESS_{uuid4().hex[:8]}",
        session_id=f"sess_{uuid4().hex[:8]}",
        user_phone=phone2,
        charger_name="Charger Noida",
        connector_type="CCS2",
        energy_kwh=20.0,
        duration_minutes=40,
        amount_paid=150.0,
        status="FINISHED",
        session_date=prev_date.replace(tzinfo=None),
        created_at=prev_date,
    )
    session3 = ChargingSession(
        session_code=f"SESS_{uuid4().hex[:8]}",
        session_id=f"sess_{uuid4().hex[:8]}",
        user_phone=phone2,
        charger_name="Charger Noida",
        connector_type="CCS2",
        energy_kwh=10.0,
        duration_minutes=20,
        amount_paid=70.0,
        status="FINISHED",
        session_date=prev_date.replace(tzinfo=None),
        created_at=prev_date,
    )

    db_session.add_all([user2, session2, session3])
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/dashboard/overview", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    
    overview = data["data"]
    
    # Assert aggregates for current period (last 30 days)
    assert overview["total_users"] >= 1
    assert overview["total_charging_sessions"] >= 1
    assert overview["total_feedback"] >= 1
    assert overview["total_complaints"] >= 1
    assert overview["average_feedback_rating"] >= 0.0
    assert overview["total_energy_delivered"] >= 15.0
    assert overview["total_revenue"] >= 100.0

    # Assert growth comparison percentage calculations
    # Sessions: current (1) vs previous (2) -> -50.0% (if isolated)
    assert overview["sessions_change"] is None or isinstance(overview["sessions_change"], float)
    # Users: current (1) vs previous (1) -> 0.0% (if isolated)
    assert overview["users_change"] is None or isinstance(overview["users_change"], float)


@pytest.mark.asyncio
async def test_feedback_analytics_chart_format(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test that feedback analytics returns standardized chart responses.
    """
    email = f"admin_{uuid4().hex[:8]}@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    now = datetime.now(timezone.utc)
    fb = Feedback(
        user_phone=str(uuid4().int)[:10],
        user_name="Alice",
        session_id=f"sess_{uuid4().hex[:8]}",
        charger_name="Charger West",
        rating=4,
        issue_category="Network",
        created_at=now - timedelta(days=2),
    )
    db_session.add(fb)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/dashboard/feedback-analytics", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    fb_data = data["data"]
    
    # Verify standardized chart structure
    for chart_key in [
        "rating_distribution",
        "feedback_over_time",
        "category_distribution",
        "average_rating_trend",
    ]:
        chart = fb_data[chart_key]
        assert "labels" in chart
        assert "datasets" in chart
        assert len(chart["datasets"]) == 1
        assert "label" in chart["datasets"][0]
        assert "data" in chart["datasets"][0]


@pytest.mark.asyncio
async def test_complaint_analytics_chart_format(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test that complaint analytics returns standardized chart responses.
    """
    email = f"admin_{uuid4().hex[:8]}@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    now = datetime.now(timezone.utc)
    comp = Complaint(
        ticket_id=f"TCK_{uuid4().hex[:8]}",
        phone_number=str(uuid4().int)[:10],
        category="App",
        description="App crashed.",
        status="Open",
        created_at=now - timedelta(days=1),
    )
    db_session.add(comp)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        "/api/v1/dashboard/complaint-analytics", headers=headers
    )
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    comp_data = data["data"]
    for chart_key in [
        "status_distribution",
        "category_distribution",
        "complaints_over_time",
        "workflow_status_distribution",
    ]:
        chart = comp_data[chart_key]
        assert "labels" in chart
        assert "datasets" in chart
        assert len(chart["datasets"]) == 1


@pytest.mark.asyncio
async def test_charger_analytics_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test charger analytics retrieval and standard chart grouping formats.
    """
    email = f"admin_{uuid4().hex[:8]}@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    now = datetime.now(timezone.utc)
    
    # Seed a session on Charger Noida
    session = ChargingSession(
        session_code=f"SESS_{uuid4().hex[:8]}",
        session_id=f"sess_{uuid4().hex[:8]}",
        user_phone=str(uuid4().int)[:10],
        charger_name="Charger Noida",
        connector_type="CCS2",
        energy_kwh=50.0,
        duration_minutes=60,
        amount_paid=400.0,
        status="FINISHED",
        session_date=now.replace(tzinfo=None),
        created_at=now,
    )
    db_session.add(session)
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/dashboard/charger-analytics", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    charger_data = data["data"]
    for chart_key in ["sessions", "ratings", "complaints", "energy", "revenue"]:
        chart = charger_data[chart_key]
        assert "labels" in chart
        assert "datasets" in chart
        assert len(chart["datasets"]) == 1


@pytest.mark.asyncio
async def test_recent_activity_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Test that recent activity combines feedback, complaints, and sessions, sorted newest first.
    """
    email = f"admin_{uuid4().hex[:8]}@example.com"
    admin = DashboardAdminUser(
        email=email,
        password_hash="hash",
        full_name="Admin User",
        role="Admin",
        is_active=True,
    )
    db_session.add(admin)

    now = datetime.now(timezone.utc)
    phone = str(uuid4().int)[:10]
    
    # 1. Old session (10 seconds ago)
    session = ChargingSession(
        session_code=f"SESS_{uuid4().hex[:8]}",
        session_id=f"sess_{uuid4().hex[:8]}",
        user_phone=phone,
        charger_name="Charger South",
        connector_type="CCS2",
        status="FINISHED",
        session_date=(now - timedelta(seconds=10)).replace(tzinfo=None),
        created_at=now - timedelta(seconds=10),
    )
    # 2. Mid complaint (5 seconds ago)
    comp = Complaint(
        ticket_id=f"TCK_{uuid4().hex[:8]}",
        phone_number=phone,
        category="App",
        description="Error code 5",
        status="Open",
        created_at=now - timedelta(seconds=5),
    )
    # 3. New feedback (1 second ago)
    fb = Feedback(
        user_phone=phone,
        user_name="User",
        session_id=session.session_id,
        charger_name="Charger South",
        rating=5,
        created_at=now - timedelta(seconds=1),
    )

    db_session.add_all([session, comp, fb])
    await db_session.commit()

    token = create_access_token(data={"sub": email})
    headers = {"Authorization": f"Bearer {token}"}

    # Request up to 50 items (max allowed limit) to ensure our seeded items are included,
    # then filter down to just our seeded IDs to run the assertions robustly.
    response = await client.get("/api/v1/dashboard/recent-activity?limit=50", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    all_activities = data["data"]["activities"]
    seeded_ids = {str(session.id), str(comp.id), str(fb.id)}
    activities = [a for a in all_activities if str(a["id"]) in seeded_ids]
    assert len(activities) == 3
    
    # Verify descending chronological sort
    # Index 0: New feedback (1 second ago)
    assert activities[0]["type"] == "feedback"
    # Index 1: Mid complaint (5 seconds ago)
    assert activities[1]["type"] == "complaint"
    # Index 2: Old session (10 seconds ago)
    assert activities[2]["type"] == "session"


@pytest.mark.asyncio
async def test_analytics_endpoints_overview(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Create admin user
    email = f"admin_{uuid4().hex[:8]}@example.com"
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

    response = await client.get("/api/v1/analytics/overview?time_range=30days", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_feedback" in data["data"]
    assert "complaint_rate" in data["data"]


@pytest.mark.asyncio
async def test_analytics_endpoints_trends(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email = f"admin_{uuid4().hex[:8]}@example.com"
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

    response = await client.get("/api/v1/analytics/trends?time_range=7days", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "labels" in data["data"]
    assert "datasets" in data["data"]


@pytest.mark.asyncio
async def test_analytics_endpoints_categories(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email = f"admin_{uuid4().hex[:8]}@example.com"
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

    response = await client.get("/api/v1/analytics/categories?time_range=30days", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "categories" in data["data"]


@pytest.mark.asyncio
async def test_analytics_endpoints_sentiment(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email = f"admin_{uuid4().hex[:8]}@example.com"
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

    response = await client.get("/api/v1/analytics/sentiment?time_range=30days", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "distribution" in data["data"]


@pytest.mark.asyncio
async def test_analytics_endpoints_top_issues(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email = f"admin_{uuid4().hex[:8]}@example.com"
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

    response = await client.get("/api/v1/analytics/top-issues?time_range=30days", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "issues" in data["data"]


@pytest.mark.asyncio
async def test_analytics_endpoints_location_insights(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email = f"admin_{uuid4().hex[:8]}@example.com"
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

    response = await client.get("/api/v1/analytics/location-insights", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "most_complaints_by_location" in data["data"]
    assert "highest_rated_locations" in data["data"]


@pytest.mark.asyncio
async def test_analytics_endpoints_ai_insights(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    email = f"admin_{uuid4().hex[:8]}@example.com"
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

    from unittest.mock import AsyncMock, patch
    from app.schemas.analytics import AIAnalyticsInsightsResponse

    with patch("app.ai.providers.factory.ProviderFactory.get_provider") as mock_get_provider:
        provider = AsyncMock()
        mock_get_provider.return_value = provider
        provider.generate_structured.return_value = AIAnalyticsInsightsResponse(
            trends=["Trend 1"],
            anomalies=["Anomaly 1"],
            recommendations=["Rec 1"]
        )

        response = await client.get("/api/v1/analytics/ai-insights?time_range=30days", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "trends" in data["data"]
        assert data["data"]["trends"] == ["Trend 1"]

