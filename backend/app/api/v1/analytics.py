from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.dependencies.auth import get_current_active_user
from app.models.dashboard import DashboardAdminUser
from app.services.analytics import AnalyticsService
from app.utils.response import StandardResponse
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    TrendResponse,
    CategoryDistributionResponse,
    SentimentDistributionResponse,
    TopIssuesResponse,
    LocationInsightsResponse,
    AIAnalyticsInsightsResponse,
)

router = APIRouter()

@router.get("/overview", response_model=StandardResponse[AnalyticsOverviewResponse])
async def get_overview(
    time_range: str = Query("30days", description="Time filter range (today, 7days, 30days, 90days, year, custom)"),
    start_date: Optional[datetime] = Query(None, description="Start date for custom range"),
    end_date: Optional[datetime] = Query(None, description="End date for custom range"),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[AnalyticsOverviewResponse]:
    try:
        service = AnalyticsService(db)
        start, end = service.resolve_time_filter(time_range, start_date, end_date)
        data = await service.get_overview_data(start, end)
        return StandardResponse(
            success=True,
            message="Analytics overview fetched successfully",
            data=data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overview: {str(e)}")

@router.get("/trends", response_model=StandardResponse[TrendResponse])
async def get_trends(
    time_range: str = Query("30days", description="Time filter range"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[TrendResponse]:
    try:
        service = AnalyticsService(db)
        start, end = service.resolve_time_filter(time_range, start_date, end_date)
        data = await service.get_trends_data(start, end)
        return StandardResponse(
            success=True,
            message="Analytics trends fetched successfully",
            data=data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

@router.get("/categories", response_model=StandardResponse[CategoryDistributionResponse])
async def get_categories(
    time_range: str = Query("30days", description="Time filter range"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[CategoryDistributionResponse]:
    try:
        service = AnalyticsService(db)
        start, end = service.resolve_time_filter(time_range, start_date, end_date)
        data = await service.get_categories_data(start, end)
        return StandardResponse(
            success=True,
            message="Analytics categories fetched successfully",
            data=data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

@router.get("/sentiment", response_model=StandardResponse[SentimentDistributionResponse])
async def get_sentiment(
    time_range: str = Query("30days", description="Time filter range"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[SentimentDistributionResponse]:
    try:
        service = AnalyticsService(db)
        start, end = service.resolve_time_filter(time_range, start_date, end_date)
        data = await service.get_sentiment_data(start, end)
        return StandardResponse(
            success=True,
            message="Analytics sentiment fetched successfully",
            data=data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sentiment: {str(e)}")

@router.get("/top-issues", response_model=StandardResponse[TopIssuesResponse])
async def get_top_issues(
    time_range: str = Query("30days", description="Time filter range"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[TopIssuesResponse]:
    try:
        service = AnalyticsService(db)
        start, end = service.resolve_time_filter(time_range, start_date, end_date)
        data = await service.get_top_issues_data(start, end)
        return StandardResponse(
            success=True,
            message="Analytics top issues fetched successfully",
            data=data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top issues: {str(e)}")

@router.get("/location-insights", response_model=StandardResponse[LocationInsightsResponse])
async def get_location_insights(
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[LocationInsightsResponse]:
    try:
        service = AnalyticsService(db)
        data = await service.get_location_insights_data()
        return StandardResponse(
            success=True,
            message="Location insights fetched successfully",
            data=data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch location insights: {str(e)}")

@router.get("/ai-insights", response_model=StandardResponse[AIAnalyticsInsightsResponse])
async def get_ai_insights(
    time_range: str = Query("30days", description="Time filter range"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[AIAnalyticsInsightsResponse]:
    try:
        service = AnalyticsService(db)
        start, end = service.resolve_time_filter(time_range, start_date, end_date)
        data = await service.get_ai_insights_data(time_range, start, end)
        return StandardResponse(
            success=True,
            message="AI analytics insights fetched successfully",
            data=data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AI insights: {str(e)}")
