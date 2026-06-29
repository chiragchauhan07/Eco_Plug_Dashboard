from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.dependencies.auth import get_current_active_user
from app.models.dashboard import DashboardAdminUser
from app.schemas.complaint import ComplaintResponse, ComplaintUpdateRequest
from app.schemas.pagination import PaginatedResponseData
from app.services.complaint import ComplaintService
from app.utils.response import StandardResponse

router = APIRouter()


@router.get(
    "",
    response_model=StandardResponse[PaginatedResponseData[ComplaintResponse]],
)
async def get_complaints(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by operational status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    ticket_id: Optional[str] = Query(None, description="Search by ticket ID"),
    phone_number: Optional[str] = Query(None, description="Search by phone number"),
    internal_status: Optional[str] = Query(
        None, description="Filter by internal status"
    ),
    sort_by: str = Query(
        "newest",
        description="Sort by option: newest, oldest, status, category",
    ),
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[PaginatedResponseData[ComplaintResponse]]:
    """
    Get complaints with optional filters, pagination, and sorting.
    """
    service = ComplaintService(db)
    paginated_data = await service.get_complaints_page(
        page=page,
        size=size,
        status=status,
        category=category,
        start_date=start_date,
        end_date=end_date,
        ticket_id=ticket_id,
        phone_number=phone_number,
        internal_status=internal_status,
        sort_by=sort_by,
    )
    return StandardResponse(
        success=True,
        message="Complaints fetched successfully",
        data=paginated_data,
    )


@router.get("/{id}", response_model=StandardResponse[ComplaintResponse])
async def get_complaint_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[ComplaintResponse]:
    """
    Get detailed complaint by ID.
    """
    service = ComplaintService(db)
    complaint = await service.get_complaint_detail(id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {id} not found",
        )
    return StandardResponse(
        success=True,
        message="Complaint details fetched successfully",
        data=complaint,
    )


@router.patch("/{id}", response_model=StandardResponse[ComplaintResponse])
async def update_complaint_workflow(
    id: UUID,
    request: Request,
    update_data: ComplaintUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: DashboardAdminUser = Depends(get_current_active_user),
) -> StandardResponse[ComplaintResponse]:
    """
    Update only dashboard-managed workflow fields for a complaint.
    Does not allow modifying operational data.
    """
    service = ComplaintService(db)
    ip_address = request.client.host if request.client else None

    try:
        updated_complaint = await service.update_complaint_workflow(
            complaint_id=id,
            update_data=update_data,
            current_admin=current_user,
            ip_address=ip_address,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not updated_complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {id} not found",
        )

    return StandardResponse(
        success=True,
        message="Complaint workflow updated successfully",
        data=updated_complaint,
    )
