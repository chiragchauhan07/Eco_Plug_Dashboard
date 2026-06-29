from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import DashboardAdminUser, DashboardAuditLog
from app.repositories.complaint import ComplaintRepository
from app.schemas.complaint import (
    ComplaintResponse,
    ComplaintUpdateRequest,
    ComplaintWorkflowResponse,
)
from app.schemas.pagination import PaginatedResponseData, PaginationInfo


class ComplaintService:
    """
    Service layer for Complaint operations.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ComplaintRepository(db)

    async def get_complaints_page(
        self,
        *,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ticket_id: Optional[str] = None,
        phone_number: Optional[str] = None,
        internal_status: Optional[str] = None,
        sort_by: str = "newest",
    ) -> PaginatedResponseData[ComplaintResponse]:
        """
        Fetch paginated complaints with pagination metadata and mapped workflow schemas.
        """
        rows, total = await self.repo.get_multi(
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

        total_pages = (total + size - 1) // size if total > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1

        pagination = PaginationInfo(
            page=page,
            size=size,
            total_items=total,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )

        mapped_items = []
        for complaint, workflow, admin_name in rows:
            workflow_dict = {
                "internal_status": workflow.internal_status if workflow else "Pending",
                "assigned_admin_id": workflow.assigned_admin_id if workflow else None,
                "assigned_admin_name": admin_name,
                "internal_notes": workflow.internal_notes if workflow else None,
                "updated_at": workflow.updated_at if workflow else complaint.created_at,
            }
            workflow_data = ComplaintWorkflowResponse.model_validate(workflow_dict)

            complaint_dict = {
                "id": complaint.id,
                "ticket_id": complaint.ticket_id,
                "phone_number": complaint.phone_number,
                "category": complaint.category,
                "description": complaint.description,
                "status": complaint.status,
                "created_at": complaint.created_at,
                "updated_at": complaint.updated_at,
                "support_agent_contacted": complaint.support_agent_contacted,
                "support_agent_phone": complaint.support_agent_phone,
                "support_agent_name": complaint.support_agent_name,
                "workflow": workflow_data,
            }
            mapped_items.append(ComplaintResponse.model_validate(complaint_dict))

        return PaginatedResponseData(items=mapped_items, pagination=pagination)

    async def get_complaint_detail(
        self, complaint_id: UUID
    ) -> Optional[ComplaintResponse]:
        """
        Get details of a single complaint with its workflow status.
        """
        row = await self.repo.get_by_id(complaint_id)
        if not row:
            return None

        complaint, workflow, admin_name = row
        workflow_dict = {
            "internal_status": workflow.internal_status if workflow else "Pending",
            "assigned_admin_id": workflow.assigned_admin_id if workflow else None,
            "assigned_admin_name": admin_name,
            "internal_notes": workflow.internal_notes if workflow else None,
            "updated_at": workflow.updated_at if workflow else complaint.created_at,
        }
        workflow_data = ComplaintWorkflowResponse.model_validate(workflow_dict)

        complaint_dict = {
            "id": complaint.id,
            "ticket_id": complaint.ticket_id,
            "phone_number": complaint.phone_number,
            "category": complaint.category,
            "description": complaint.description,
            "status": complaint.status,
            "created_at": complaint.created_at,
            "updated_at": complaint.updated_at,
            "support_agent_contacted": complaint.support_agent_contacted,
            "support_agent_phone": complaint.support_agent_phone,
            "support_agent_name": complaint.support_agent_name,
            "workflow": workflow_data,
        }
        return ComplaintResponse.model_validate(complaint_dict)

    async def update_complaint_workflow(
        self,
        complaint_id: UUID,
        update_data: ComplaintUpdateRequest,
        current_admin: DashboardAdminUser,
        ip_address: Optional[str] = None,
    ) -> Optional[ComplaintResponse]:
        """
        Update the workflow status for a complaint, log the action, and return details.
        """
        # 1. Verify complaint exists
        row = await self.repo.get_by_id(complaint_id)
        if not row:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        # 2. Input validation: Verify assigned admin exists if specified
        if (
            "assigned_admin_id" in update_dict
            and update_dict["assigned_admin_id"] is not None
        ):
            admin_id = update_dict["assigned_admin_id"]
            admin_result = await self.db.execute(
                select(DashboardAdminUser).where(DashboardAdminUser.id == admin_id)
            )
            admin = admin_result.scalars().first()
            if not admin:
                raise ValueError("Assigned administrator does not exist.")

        # 3. Perform update/upsert
        await self.repo.upsert_workflow(complaint_id, update_dict)

        # 4. Create audit log
        audit_details: Dict[str, Any] = {
            "complaint_id": str(complaint_id),
            "updates": {
                k: str(v) if isinstance(v, UUID) else v for k, v in update_dict.items()
            },
        }

        audit_log = DashboardAuditLog(
            admin_id=current_admin.id,
            action="update_complaint_workflow",
            resource_type="complaints",
            resource_id=complaint_id,
            ip_address=ip_address,
            details=audit_details,
        )
        self.db.add(audit_log)
        await self.db.commit()

        # 5. Fetch and return fresh combined complaint detail
        return await self.get_complaint_detail(complaint_id)
