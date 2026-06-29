from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Tuple

from app.database.session import get_db_session
from app.dependencies.auth import get_current_active_user
from app.models.dashboard import DashboardAdminUser
from app.schemas.dashboard import (
    ChargerAnalyticsResponse,
    ComplaintAnalyticsResponse,
    DashboardOverviewResponse,
    FeedbackAnalyticsResponse,
    RecentActivityResponse,
)
from app.services.dashboard import DashboardService
from app.utils.response import StandardResponse

router = APIRouter()


def resolve_dates(
    start_date: Optional[datetime], end_date: Optional[datetime]
) -> Tuple[datetime, datetime]:
    """
    Resolve start and end dates. Default to the last 30 days if not provided.
    """
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=30)
    return start_date, end_date


@router.get("/overview", response_model=StandardResponse[DashboardOverviewResponse])
async def get_overview(
    start_date: Optional[datetime] = Query(None, description="Start date of filter range"),
    end_date: Optional[datetime] = Query(None, description="End date of filter range"),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[DashboardOverviewResponse]:
    """
    Get overview KPIs for the dashboard homepage, including comparison trends against the previous period.
    """
    s_date, e_date = None, None
    if start_date is not None or end_date is not None:
        s_date, e_date = resolve_dates(start_date, end_date)
    service = DashboardService(db)
    overview_data = await service.get_overview_data(s_date, e_date)
    return StandardResponse(
        success=True,
        message="Overview analytics fetched successfully",
        data=overview_data,
    )


@router.get(
    "/feedback-analytics",
    response_model=StandardResponse[FeedbackAnalyticsResponse],
)
async def get_feedback_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date of filter range"),
    end_date: Optional[datetime] = Query(None, description="End date of filter range"),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[FeedbackAnalyticsResponse]:
    """
    Get rating distributions, submissions over time, category breakdowns, and rating trends.
    """
    s_date, e_date = resolve_dates(start_date, end_date)
    service = DashboardService(db)
    feedback_data = await service.get_feedback_analytics_data(s_date, e_date)
    return StandardResponse(
        success=True,
        message="Feedback analytics fetched successfully",
        data=feedback_data,
    )


@router.get(
    "/complaint-analytics",
    response_model=StandardResponse[ComplaintAnalyticsResponse],
)
async def get_complaint_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date of filter range"),
    end_date: Optional[datetime] = Query(None, description="End date of filter range"),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[ComplaintAnalyticsResponse]:
    """
    Get operational status, categories, submission volume trends, and internal review workflow statuses.
    """
    s_date, e_date = resolve_dates(start_date, end_date)
    service = DashboardService(db)
    complaint_data = await service.get_complaint_analytics_data(s_date, e_date)
    return StandardResponse(
        success=True,
        message="Complaint analytics fetched successfully",
        data=complaint_data,
    )


@router.get(
    "/charger-analytics",
    response_model=StandardResponse[ChargerAnalyticsResponse],
)
async def get_charger_analytics(
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[ChargerAnalyticsResponse]:
    """
    Get session count, average ratings, complaint counts, energy, and revenue per charger in standard chart format.
    """
    service = DashboardService(db)
    charger_data = await service.get_charger_analytics_data()
    return StandardResponse(
        success=True,
        message="Charger analytics fetched successfully",
        data=charger_data,
    )


@router.get(
    "/recent-activity", response_model=StandardResponse[RecentActivityResponse]
)
async def get_recent_activity(
    limit: int = Query(5, ge=1, le=50, description="Max activities to return"),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[RecentActivityResponse]:
    """
    Get a unified chronologically sorted feed of recent feedbacks, complaints, and charging sessions.
    """
    service = DashboardService(db)
    activity_data = await service.get_recent_activity_data(limit=limit)
    return StandardResponse(
        success=True,
        message="Recent activity feed fetched successfully",
        data=activity_data,
    )
