from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import DashboardAdminUser, DashboardComplaintWorkflow
from app.models.operational import Complaint


class ComplaintRepository:
    """
    Repository for encapsulating database operations on Complaints and Workflows.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_multi(
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
    ) -> Tuple[
        List[Tuple[Complaint, Optional[DashboardComplaintWorkflow], Optional[str]]], int
    ]:
        """
        Fetch paginated list of complaints joined with their dashboard workflow status and assigned admin name.
        """
        # Outer join to include complaints without a workflow row
        query = (
            select(Complaint, DashboardComplaintWorkflow, DashboardAdminUser.full_name)
            .outerjoin(
                DashboardComplaintWorkflow,
                Complaint.id == DashboardComplaintWorkflow.complaint_id,
            )
            .outerjoin(
                DashboardAdminUser,
                DashboardComplaintWorkflow.assigned_admin_id == DashboardAdminUser.id,
            )
        )

        # Filters
        if status:
            query = query.where(Complaint.status.ilike(f"%{status}%"))
        if category:
            query = query.where(Complaint.category.ilike(f"%{category}%"))
        if start_date:
            query = query.where(Complaint.created_at >= start_date)
        if end_date:
            query = query.where(Complaint.created_at <= end_date)
        if ticket_id:
            query = query.where(Complaint.ticket_id.ilike(f"%{ticket_id}%"))
        if phone_number:
            query = query.where(Complaint.phone_number.like(f"%{phone_number}%"))
        if internal_status:
            if internal_status == "Pending":
                query = query.where(
                    (DashboardComplaintWorkflow.internal_status == "Pending")
                    | (DashboardComplaintWorkflow.internal_status.is_(None))
                )
            else:
                query = query.where(
                    DashboardComplaintWorkflow.internal_status == internal_status
                )

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()

        # Sorting
        if sort_by == "newest":
            query = query.order_by(desc(Complaint.created_at))
        elif sort_by == "oldest":
            query = query.order_by(asc(Complaint.created_at))
        elif sort_by == "status":
            query = query.order_by(asc(Complaint.status))
        elif sort_by == "category":
            query = query.order_by(asc(Complaint.category))
        else:
            query = query.order_by(desc(Complaint.created_at))

        # Pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self.db.execute(query)
        items = [(row[0], row[1], row[2]) for row in result.all()]

        return items, total

    async def get_by_id(
        self, complaint_id: UUID
    ) -> Optional[
        Tuple[Complaint, Optional[DashboardComplaintWorkflow], Optional[str]]
    ]:
        """
        Fetch a single complaint by ID with its workflow and assigned administrator name.
        """
        query = (
            select(Complaint, DashboardComplaintWorkflow, DashboardAdminUser.full_name)
            .outerjoin(
                DashboardComplaintWorkflow,
                Complaint.id == DashboardComplaintWorkflow.complaint_id,
            )
            .outerjoin(
                DashboardAdminUser,
                DashboardComplaintWorkflow.assigned_admin_id == DashboardAdminUser.id,
            )
            .where(Complaint.id == complaint_id)
        )
        result = await self.db.execute(query)
        row = result.first()
        if not row:
            return None
        return row[0], row[1], row[2]

    async def upsert_workflow(
        self, complaint_id: UUID, update_dict: Dict[str, Any]
    ) -> DashboardComplaintWorkflow:
        """
        Upsert a complaint's workflow record.
        """
        query = select(DashboardComplaintWorkflow).where(
            DashboardComplaintWorkflow.complaint_id == complaint_id
        )
        result = await self.db.execute(query)
        workflow = result.scalars().first()

        if not workflow:
            workflow = DashboardComplaintWorkflow(
                complaint_id=complaint_id,
                internal_status=update_dict.get("internal_status", "Pending"),
                assigned_admin_id=update_dict.get("assigned_admin_id"),
                internal_notes=update_dict.get("internal_notes"),
            )
            self.db.add(workflow)
        else:
            if "internal_status" in update_dict:
                workflow.internal_status = update_dict["internal_status"]
            if "assigned_admin_id" in update_dict:
                workflow.assigned_admin_id = update_dict["assigned_admin_id"]
            if "internal_notes" in update_dict:
                workflow.internal_notes = update_dict["internal_notes"]

        await self.db.flush()
        return workflow
