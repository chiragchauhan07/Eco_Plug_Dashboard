from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.dependencies.auth import get_current_active_user
from app.models.dashboard import DashboardAdminUser
from app.schemas.feedback import FeedbackDetailResponse, FeedbackListItemResponse, FeedbackAIAnalysisResponse
from app.schemas.pagination import PaginatedResponseData
from app.services.feedback import FeedbackService
from app.utils.response import StandardResponse

router = APIRouter()


@router.get(
    "",
    response_model=StandardResponse[PaginatedResponseData[FeedbackListItemResponse]],
)
async def get_feedback(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    user_name: Optional[str] = Query(None, description="Search by user name"),
    user_phone: Optional[str] = Query(None, description="Search by phone number"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    charger_name: Optional[str] = Query(None, description="Filter by charger"),
    issue_category: Optional[str] = Query(None, description="Filter by issue category"),
    start_date: Optional[datetime] = Query(
        None, description="Filter by start date range"
    ),
    end_date: Optional[datetime] = Query(None, description="Filter by end date range"),
    sort_by: str = Query(
        "newest",
        description="Sort by option: newest, oldest, rating",
    ),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[PaginatedResponseData[FeedbackListItemResponse]]:
    """
    Get all feedback records with optional filtering, sorting, and pagination.
    """
    service = FeedbackService(db)
    paginated_data = await service.get_feedback_page(
        page=page,
        size=size,
        user_name=user_name,
        user_phone=user_phone,
        rating=rating,
        charger_name=charger_name,
        issue_category=issue_category,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
    )
    return StandardResponse(
        success=True,
        message="Feedback fetched successfully",
        data=paginated_data,
    )


@router.get("/{id}", response_model=StandardResponse[FeedbackDetailResponse])
async def get_feedback_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[FeedbackDetailResponse]:
    """
    Get detailed feedback record by its ID, with associated charging session data nested.
    """
    service = FeedbackService(db)
    feedback_detail = await service.get_feedback_detail(id)
    if not feedback_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {id} not found",
        )
    return StandardResponse(
        success=True,
        message="Feedback details fetched successfully",
        data=feedback_detail,
    )


@router.post("/{id}/analyze", response_model=StandardResponse[FeedbackAIAnalysisResponse])
async def analyze_feedback_item(
    id: UUID,
    force: bool = Query(False, description="Force re-run AI analysis"),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[FeedbackAIAnalysisResponse]:
    """
    Run or force re-run AI analysis for a specific customer feedback item.
    """
    service = FeedbackService(db)
    analysis = await service.analyze_feedback_item(id, force=force)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {id} not found",
        )
    return StandardResponse(
        success=True,
        message="Feedback analyzed successfully",
        data=analysis,
    )
