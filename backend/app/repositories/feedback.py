from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import DashboardAIAnalysis
from app.models.operational import ChargingSession, Feedback


class FeedbackRepository:
    """
    Repository for encapsulating database operations on Feedback.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_multi(
        self,
        *,
        page: int = 1,
        size: int = 20,
        user_name: Optional[str] = None,
        user_phone: Optional[str] = None,
        rating: Optional[int] = None,
        charger_name: Optional[str] = None,
        issue_category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "newest",
    ) -> Tuple[List[Tuple[Feedback, Optional[DashboardAIAnalysis]]], int]:
        """
        Fetch paginated feedback list filtered by various optional criteria.
        """
        query = select(Feedback, DashboardAIAnalysis).outerjoin(
            DashboardAIAnalysis,
            (DashboardAIAnalysis.source_id == Feedback.id) & (DashboardAIAnalysis.source_type == "feedback")
        )

        # Filters
        if user_name:
            query = query.where(Feedback.user_name.ilike(f"%{user_name}%"))
        if user_phone:
            query = query.where(Feedback.user_phone.like(f"%{user_phone}%"))
        if rating is not None:
            query = query.where(Feedback.rating == rating)
        if charger_name:
            query = query.where(Feedback.charger_name.ilike(f"%{charger_name}%"))
        if issue_category:
            if issue_category.lower() == "general":
                query = query.where(Feedback.issue_category.is_(None))
            else:
                query = query.where(Feedback.issue_category.ilike(f"%{issue_category}%"))
        if start_date:
            query = query.where(Feedback.created_at >= start_date)
        if end_date:
            query = query.where(Feedback.created_at <= end_date)

        # Get total count first
        count_query = select(func.count()).select_from(Feedback)
        # Apply same filters to count_query
        if user_name:
            count_query = count_query.where(Feedback.user_name.ilike(f"%{user_name}%"))
        if user_phone:
            count_query = count_query.where(Feedback.user_phone.like(f"%{user_phone}%"))
        if rating is not None:
            count_query = count_query.where(Feedback.rating == rating)
        if charger_name:
            count_query = count_query.where(Feedback.charger_name.ilike(f"%{charger_name}%"))
        if issue_category:
            if issue_category.lower() == "general":
                count_query = count_query.where(Feedback.issue_category.is_(None))
            else:
                count_query = count_query.where(Feedback.issue_category.ilike(f"%{issue_category}%"))
        if start_date:
            count_query = count_query.where(Feedback.created_at >= start_date)
        if end_date:
            count_query = count_query.where(Feedback.created_at <= end_date)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()

        # Sorting
        if sort_by == "newest":
            query = query.order_by(desc(Feedback.created_at))
        elif sort_by == "oldest":
            query = query.order_by(asc(Feedback.created_at))
        elif sort_by == "rating":
            query = query.order_by(desc(Feedback.rating))
        else:
            query = query.order_by(desc(Feedback.created_at))

        # Pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self.db.execute(query)
        items = [(row[0], row[1]) for row in result.all()]

        return items, total

    async def get_by_id(
        self, feedback_id: UUID
    ) -> Optional[Tuple[Feedback, Optional[ChargingSession], Optional[DashboardAIAnalysis]]]:
        """
        Fetch feedback details by ID, including its associated charging session and AI analysis.
        """
        query = select(Feedback).where(Feedback.id == feedback_id)
        result = await self.db.execute(query)
        feedback = result.scalars().first()

        if not feedback:
            return None

        charging_session = None
        if feedback.session_id:
            session_query = select(ChargingSession).where(
                ChargingSession.session_id == feedback.session_id
            )
            session_result = await self.db.execute(session_query)
            charging_session = session_result.scalars().first()

        ai_query = select(DashboardAIAnalysis).where(
            DashboardAIAnalysis.source_id == feedback_id,
            DashboardAIAnalysis.source_type == "feedback"
        )
        ai_result = await self.db.execute(ai_query)
        ai_analysis = ai_result.scalars().first()

        return feedback, charging_session, ai_analysis
