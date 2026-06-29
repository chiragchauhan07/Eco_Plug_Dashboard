from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import case, desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import DashboardComplaintWorkflow, DashboardAIAnalysis
from app.models.operational import ChargingSession, Complaint, Feedback, User


class DashboardRepository:
    """
    Repository for aggregating database metrics for the Dashboard.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_period_stats(
        self, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics for a specific date range, or all-time if not provided.
        """
        # 1. Users count in period
        user_q = select(func.count(User.id))
        if start_date and end_date:
            user_q = user_q.where(
                User.created_at >= start_date.replace(tzinfo=None),
                User.created_at <= end_date.replace(tzinfo=None),
            )
        user_res = await self.db.execute(user_q)
        users_count = user_res.scalar_one()

        # 2. Charging sessions stats in period
        session_q = select(
            func.count(ChargingSession.id),
            func.sum(ChargingSession.energy_kwh),
            func.sum(ChargingSession.amount_paid),
            func.avg(ChargingSession.duration_minutes),
        )
        if start_date and end_date:
            session_q = session_q.where(
                ChargingSession.created_at >= start_date,
                ChargingSession.created_at <= end_date,
            )
        session_res = await self.db.execute(session_q)
        sessions_row = session_res.first()
        if sessions_row:
            sessions_count, energy_sum, revenue_sum, duration_avg = sessions_row
        else:
            sessions_count, energy_sum, revenue_sum, duration_avg = 0, 0, 0, 0

        # 3. Feedback stats in period
        fb_q = select(
            func.count(Feedback.id),
            func.avg(Feedback.rating),
        )
        if start_date and end_date:
            fb_q = fb_q.where(Feedback.created_at >= start_date, Feedback.created_at <= end_date)
        fb_res = await self.db.execute(fb_q)
        fb_row = fb_res.first()
        if fb_row:
            feedback_count, rating_avg = fb_row
        else:
            feedback_count, rating_avg = 0, 0

        # 4. Complaints stats in period
        comp_q = select(
            func.count(Complaint.id),
            func.sum(case((Complaint.status == "Open", 1), else_=0)),
            func.sum(case((Complaint.status == "Closed", 1), else_=0)),
        )
        if start_date and end_date:
            comp_q = comp_q.where(
                Complaint.created_at >= start_date, Complaint.created_at <= end_date
            )
        comp_res = await self.db.execute(comp_q)
        comp_row = comp_res.first()
        if comp_row:
            complaints_count, open_count, closed_count = comp_row
        else:
            complaints_count, open_count, closed_count = 0, 0, 0

        return {
            "users": users_count or 0,
            "sessions": sessions_count or 0,
            "feedback": feedback_count or 0,
            "average_rating": float(rating_avg or 0.0),
            "complaints": complaints_count or 0,
            "open_complaints": int(open_count or 0),
            "closed_complaints": int(closed_count or 0),
            "energy": float(energy_sum or 0.0),
            "revenue": float(revenue_sum or 0.0),
            "average_duration": float(duration_avg or 0.0),
        }

    async def get_feedback_rating_dist(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[int, int]]:
        """
        Get rating count distribution.
        """
        q = (
            select(Feedback.rating, func.count(Feedback.id))
            .where(Feedback.created_at >= start_date, Feedback.created_at <= end_date)
            .group_by(Feedback.rating)
            .order_by(Feedback.rating.asc())
        )
        res = await self.db.execute(q)
        return [(row[0], row[1]) for row in res.all()]

    async def get_feedback_count_over_time(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[str, int]]:
        """
        Get feedback count daily trend.
        """
        date_trunc = func.date_trunc("day", Feedback.created_at)
        q = (
            select(date_trunc, func.count(Feedback.id))
            .where(Feedback.created_at >= start_date, Feedback.created_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc.asc())
        )
        res = await self.db.execute(q)
        return [(str(row[0].date()), row[1]) for row in res.all()]

    async def get_feedback_category_dist(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[str, int]]:
        """
        Get feedback issue category distribution.
        """
        q = (
            select(Feedback.issue_category, func.count(Feedback.id))
            .where(Feedback.created_at >= start_date, Feedback.created_at <= end_date)
            .group_by(Feedback.issue_category)
        )
        res = await self.db.execute(q)
        return [(row[0] or "None", row[1]) for row in res.all()]

    async def get_feedback_rating_trend(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[str, float]]:
        """
        Get average feedback rating daily trend.
        """
        date_trunc = func.date_trunc("day", Feedback.created_at)
        q = (
            select(date_trunc, func.avg(Feedback.rating))
            .where(Feedback.created_at >= start_date, Feedback.created_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc.asc())
        )
        res = await self.db.execute(q)
        return [(str(row[0].date()), float(row[1] or 0.0)) for row in res.all()]

    async def get_complaint_status_dist(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[str, int]]:
        """
        Get complaint operational status distribution.
        """
        q = (
            select(Complaint.status, func.count(Complaint.id))
            .where(Complaint.created_at >= start_date, Complaint.created_at <= end_date)
            .group_by(Complaint.status)
        )
        res = await self.db.execute(q)
        return [(row[0], row[1]) for row in res.all()]

    async def get_complaint_category_dist(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[str, int]]:
        """
        Get complaint category distribution.
        """
        q = (
            select(Complaint.category, func.count(Complaint.id))
            .where(Complaint.created_at >= start_date, Complaint.created_at <= end_date)
            .group_by(Complaint.category)
        )
        res = await self.db.execute(q)
        return [(row[0], row[1]) for row in res.all()]

    async def get_complaints_count_over_time(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[str, int]]:
        """
        Get daily complaints count trend.
        """
        date_trunc = func.date_trunc("day", Complaint.created_at)
        q = (
            select(date_trunc, func.count(Complaint.id))
            .where(Complaint.created_at >= start_date, Complaint.created_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc.asc())
        )
        res = await self.db.execute(q)
        return [(str(row[0].date()), row[1]) for row in res.all()]

    async def get_complaint_workflow_status_dist(
        self, start_date: datetime, end_date: datetime
    ) -> List[Tuple[str, int]]:
        """
        Get internal workflow status distribution, joining dashboard complaint workflows.
        """
        status_col = func.coalesce(
            DashboardComplaintWorkflow.internal_status, "Pending"
        )
        q = (
            select(status_col, func.count(Complaint.id))
            .outerjoin(
                DashboardComplaintWorkflow,
                Complaint.id == DashboardComplaintWorkflow.complaint_id,
            )
            .where(Complaint.created_at >= start_date, Complaint.created_at <= end_date)
            .group_by(status_col)
        )
        res = await self.db.execute(q)
        return [(row[0], row[1]) for row in res.all()]

    async def get_charger_analytics(self) -> List[Dict[str, Any]]:
        """
        Compile aggregated stats per charger. Uses CTEs to safely group and join metrics.
        """
        sql = """
        WITH session_stats AS (
            SELECT 
                charger_name, 
                COUNT(*) as session_count,
                COALESCE(SUM(energy_kwh), 0) as energy_delivered,
                COALESCE(SUM(amount_paid), 0) as revenue
            FROM charging_sessions
            GROUP BY charger_name
        ),
        feedback_stats AS (
            SELECT 
                charger_name,
                AVG(rating) as average_rating
            FROM feedback
            GROUP BY charger_name
        ),
        complaint_stats AS (
            SELECT charger_name, COUNT(*) as complaint_count FROM (
                SELECT (
                    SELECT s.charger_name 
                    FROM charging_sessions s 
                    WHERE s.user_phone = c.phone_number AND s.created_at <= c.created_at 
                    ORDER BY s.created_at DESC 
                    LIMIT 1
                ) as charger_name
                FROM complaints c
            ) sub
            WHERE charger_name IS NOT NULL
            GROUP BY charger_name
        )
        SELECT 
            l.charger_name,
            COALESCE(s.session_count, 0) as session_count,
            COALESCE(f.average_rating, 0.0) as average_rating,
            COALESCE(c.complaint_count, 0) as complaint_count,
            COALESCE(s.energy_delivered, 0.0) as energy_delivered,
            COALESCE(s.revenue, 0.0) as revenue
        FROM (
            SELECT DISTINCT charger_name FROM charging_sessions
            UNION
            SELECT DISTINCT charger_name FROM feedback
            UNION
            SELECT DISTINCT charger_name FROM charger_locations
        ) l
        LEFT JOIN session_stats s ON l.charger_name = s.charger_name
        LEFT JOIN feedback_stats f ON l.charger_name = f.charger_name
        LEFT JOIN complaint_stats c ON l.charger_name = c.charger_name;
        """
        res = await self.db.execute(text(sql))
        return [
            {
                "charger_name": row[0],
                "session_count": int(row[1]),
                "average_rating": float(row[2]),
                "complaint_count": int(row[3]),
                "energy_delivered": float(row[4]),
                "revenue": float(row[5]),
            }
            for row in res.all()
        ]

    async def get_recent_feedback(self, limit: int) -> List[Feedback]:
        q = select(Feedback).order_by(desc(Feedback.created_at)).limit(limit)
        res = await self.db.execute(q)
        return list(res.scalars().all())

    async def get_recent_complaints(self, limit: int) -> List[Complaint]:
        q = select(Complaint).order_by(desc(Complaint.created_at)).limit(limit)
        res = await self.db.execute(q)
        return list(res.scalars().all())

    async def get_recent_sessions(self, limit: int) -> List[ChargingSession]:
        q = select(ChargingSession).order_by(desc(ChargingSession.created_at)).limit(limit)
        res = await self.db.execute(q)
        return list(res.scalars().all())

    async def get_sentiment_distribution(self, start_date: datetime, end_date: datetime) -> List[Tuple[str, int]]:
        q = (
            select(DashboardAIAnalysis.sentiment, func.count(DashboardAIAnalysis.id))
            .where(
                DashboardAIAnalysis.source_type == "feedback",
                DashboardAIAnalysis.created_at >= start_date,
                DashboardAIAnalysis.created_at <= end_date
            )
            .group_by(DashboardAIAnalysis.sentiment)
        )
        res = await self.db.execute(q)
        return [(str(row[0]), int(row[1])) for row in res.all() if row[0] is not None]

    async def get_top_complaint_categories(self, start_date: datetime, end_date: datetime, limit: int = 5) -> List[Tuple[str, int]]:
        q = (
            select(Complaint.category, func.count(Complaint.id))
            .where(Complaint.created_at >= start_date, Complaint.created_at <= end_date)
            .group_by(Complaint.category)
            .order_by(desc(func.count(Complaint.id)))
            .limit(limit)
        )
        res = await self.db.execute(q)
        return [(str(row[0]), int(row[1])) for row in res.all() if row[0] is not None]

    async def get_feedback_trend_analytics(self, start_date: datetime, end_date: datetime, interval: str = "day") -> List[Tuple[str, int]]:
        date_trunc = func.date_trunc(interval, Feedback.created_at)
        q = (
            select(date_trunc, func.count(Feedback.id))
            .where(Feedback.created_at >= start_date, Feedback.created_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc.asc())
        )
        res = await self.db.execute(q)
        return [(str(row[0].date() if interval != "month" else row[0].strftime("%Y-%m")), int(row[1])) for row in res.all()]

    async def get_complaints_trend_analytics(self, start_date: datetime, end_date: datetime, interval: str = "day") -> List[Tuple[str, int]]:
        date_trunc = func.date_trunc(interval, Complaint.created_at)
        q = (
            select(date_trunc, func.count(Complaint.id))
            .where(Complaint.created_at >= start_date, Complaint.created_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc.asc())
        )
        res = await self.db.execute(q)
        return [(str(row[0].date() if interval != "month" else row[0].strftime("%Y-%m")), int(row[1])) for row in res.all()]

    async def get_rating_trend_analytics(self, start_date: datetime, end_date: datetime, interval: str = "day") -> List[Tuple[str, float]]:
        date_trunc = func.date_trunc(interval, Feedback.created_at)
        q = (
            select(date_trunc, func.avg(Feedback.rating))
            .where(Feedback.created_at >= start_date, Feedback.created_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc.asc())
        )
        res = await self.db.execute(q)
        return [(str(row[0].date() if interval != "month" else row[0].strftime("%Y-%m")), float(row[1] or 0.0)) for row in res.all()]

    async def get_complaint_resolution_trend_analytics(self, start_date: datetime, end_date: datetime, interval: str = "day") -> List[Tuple[str, float]]:
        date_trunc = func.date_trunc(interval, Complaint.created_at)
        q = (
            select(
                date_trunc,
                func.sum(case((Complaint.status == "Closed", 1), else_=0)),
                func.count(Complaint.id)
            )
            .where(Complaint.created_at >= start_date, Complaint.created_at <= end_date)
            .group_by(date_trunc)
            .order_by(date_trunc.asc())
        )
        res = await self.db.execute(q)
        trend = []
        for row in res.all():
            dt_str = str(row[0].date() if interval != "month" else row[0].strftime("%Y-%m"))
            closed = row[1] or 0
            total = row[2] or 0
            pct = (closed / total * 100.0) if total > 0 else 0.0
            trend.append((dt_str, round(pct, 2)))
        return trend
