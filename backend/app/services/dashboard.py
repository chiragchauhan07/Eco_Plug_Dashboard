from datetime import datetime, timezone
from typing import Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    ChartDataset,
    ChartResponse,
    ChargerAnalyticsResponse,
    ComplaintAnalyticsResponse,
    DashboardOverviewResponse,
    FeedbackAnalyticsResponse,
    RecentActivityItem,
    RecentActivityResponse,
)


class DashboardService:
    """
    Service layer for dashboard analytics computations.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.repo = DashboardRepository(db)

    def _calc_pct_change(self, curr: float, prev: float) -> Optional[float]:
        """
        Calculate percentage change between current and previous values.
        Returns None (null) if previous equivalent period had zero value
        to indicate unavailable trend base.
        """
        if prev == 0:
            return 100.0 if curr > 0 else 0.0
        return round(((curr - prev) / prev) * 100.0, 2)

    def _make_chart(self, label: str, kv_pairs: List[Tuple[Any, Any]]) -> ChartResponse:
        """
        Standardize raw database aggregates into a frontend-friendly ChartResponse object.
        """
        labels = [str(k) for k, _ in kv_pairs]
        data = [float(v) for _, v in kv_pairs]
        return ChartResponse(
            labels=labels,
            datasets=[ChartDataset(label=label, data=data)],
        )

    async def get_overview_data(
        self, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> DashboardOverviewResponse:
        """
        Retrieve overview metrics and calculate comparisons against the previous equivalent period.
        """
        if start_date is None or end_date is None:
            # Query all-time stats
            curr = await self.repo.get_period_stats(None, None)
            return DashboardOverviewResponse(
                total_users=curr["users"],
                total_charging_sessions=curr["sessions"],
                total_feedback=curr["feedback"],
                total_complaints=curr["complaints"],
                average_feedback_rating=curr["average_rating"],
                open_complaints=curr["open_complaints"],
                closed_complaints=curr["closed_complaints"],
                total_energy_delivered=curr["energy"],
                total_revenue=curr["revenue"],
                average_session_duration=curr["average_duration"],
                users_change=None,
                sessions_change=None,
                feedback_change=None,
                complaints_change=None,
                revenue_change=None,
                energy_change=None,
            )

        duration = end_date - start_date
        prev_start = start_date - duration
        prev_end = start_date

        curr = await self.repo.get_period_stats(start_date, end_date)
        prev = await self.repo.get_period_stats(prev_start, prev_end)

        return DashboardOverviewResponse(
            total_users=curr["users"],
            total_charging_sessions=curr["sessions"],
            total_feedback=curr["feedback"],
            total_complaints=curr["complaints"],
            average_feedback_rating=curr["average_rating"],
            open_complaints=curr["open_complaints"],
            closed_complaints=curr["closed_complaints"],
            total_energy_delivered=curr["energy"],
            total_revenue=curr["revenue"],
            average_session_duration=curr["average_duration"],
            users_change=self._calc_pct_change(curr["users"], prev["users"]),
            sessions_change=self._calc_pct_change(curr["sessions"], prev["sessions"]),
            feedback_change=self._calc_pct_change(curr["feedback"], prev["feedback"]),
            complaints_change=self._calc_pct_change(
                curr["complaints"], prev["complaints"]
            ),
            revenue_change=self._calc_pct_change(curr["revenue"], prev["revenue"]),
            energy_change=self._calc_pct_change(curr["energy"], prev["energy"]),
        )

    async def get_feedback_analytics_data(
        self, start_date: datetime, end_date: datetime
    ) -> FeedbackAnalyticsResponse:
        """
        Compile feedback metrics into standardized chart structures.
        """
        rating_dist = await self.repo.get_feedback_rating_dist(start_date, end_date)
        count_trend = await self.repo.get_feedback_count_over_time(start_date, end_date)
        category_dist = await self.repo.get_feedback_category_dist(start_date, end_date)
        rating_trend = await self.repo.get_feedback_rating_trend(start_date, end_date)

        return FeedbackAnalyticsResponse(
            rating_distribution=self._make_chart("Ratings Distribution", rating_dist),
            feedback_over_time=self._make_chart("Feedback Submissions", count_trend),
            category_distribution=self._make_chart("Issues by Category", category_dist),
            average_rating_trend=self._make_chart("Average Rating Trend", rating_trend),
        )

    async def get_complaint_analytics_data(
        self, start_date: datetime, end_date: datetime
    ) -> ComplaintAnalyticsResponse:
        """
        Compile complaints metrics into standardized chart structures.
        """
        status_dist = await self.repo.get_complaint_status_dist(start_date, end_date)
        category_dist = await self.repo.get_complaint_category_dist(start_date, end_date)
        count_trend = await self.repo.get_complaints_count_over_time(start_date, end_date)
        workflow_dist = await self.repo.get_complaint_workflow_status_dist(
            start_date, end_date
        )

        return ComplaintAnalyticsResponse(
            status_distribution=self._make_chart("Complaints Status", status_dist),
            category_distribution=self._make_chart("Complaints Category", category_dist),
            complaints_over_time=self._make_chart("Complaints Submissions", count_trend),
            workflow_status_distribution=self._make_chart(
                "Internal Review Status", workflow_dist
            ),
        )

    async def get_charger_analytics_data(self) -> ChargerAnalyticsResponse:
        """
        Compile charger analytics metrics into standardized chart responses per charger.
        """
        rows = await self.repo.get_charger_analytics()

        labels = [r["charger_name"] for r in rows]
        session_data = [float(r["session_count"]) for r in rows]
        rating_data = [float(r["average_rating"]) for r in rows]
        complaint_data = [float(r["complaint_count"]) for r in rows]
        energy_data = [float(r["energy_delivered"]) for r in rows]
        revenue_data = [float(r["revenue"]) for r in rows]

        return ChargerAnalyticsResponse(
            sessions=ChartResponse(
                labels=labels,
                datasets=[ChartDataset(label="Sessions Count", data=session_data)],
            ),
            ratings=ChartResponse(
                labels=labels,
                datasets=[ChartDataset(label="Average Rating", data=rating_data)],
            ),
            complaints=ChartResponse(
                labels=labels,
                datasets=[ChartDataset(label="Complaints Count", data=complaint_data)],
            ),
            energy=ChartResponse(
                labels=labels,
                datasets=[ChartDataset(label="Energy Delivered (kWh)", data=energy_data)],
            ),
            revenue=ChartResponse(
                labels=labels,
                datasets=[ChartDataset(label="Revenue (INR)", data=revenue_data)],
            ),
        )

    async def get_recent_activity_data(self, limit: int = 5) -> RecentActivityResponse:
        """
        Fetch latest feedback, complaints, and sessions, and assemble them
        into a unified, timestamp-sorted feed.
        """
        # Fetch raw lists
        feedbacks = await self.repo.get_recent_feedback(limit)
        complaints = await self.repo.get_recent_complaints(limit)
        sessions = await self.repo.get_recent_sessions(limit)

        activities: List[RecentActivityItem] = []

        # Wrap feedback
        for f in feedbacks:
            activities.append(
                RecentActivityItem(
                    type="feedback",
                    id=f.id,  # type: ignore[arg-type]
                    title=f"Feedback from {f.user_name or f.user_phone}",
                    description=f"Rating: {f.rating} - {f.feedback_comment or ''}",
                    timestamp=f.created_at or datetime.now(timezone.utc),  # type: ignore[arg-type]
                    status=None,
                )
            )

        # Wrap complaints
        for c in complaints:
            activities.append(
                RecentActivityItem(
                    type="complaint",
                    id=c.id,  # type: ignore[arg-type]
                    title=f"Complaint ticket {c.ticket_id}",
                    description=f"Category: {c.category} - {c.description[:60]}...",
                    timestamp=c.created_at,  # type: ignore[arg-type]
                    status=c.status,  # type: ignore[arg-type]
                )
            )

        # Wrap sessions
        for s in sessions:
            activities.append(
                RecentActivityItem(
                    type="session",
                    id=s.id,  # type: ignore[arg-type]
                    title=f"Session {s.session_code}",
                    description=f"Charger: {s.charger_name} - {s.duration_minutes or 0} mins, {s.energy_kwh or 0} kWh",
                    timestamp=s.created_at or datetime.now(timezone.utc),  # type: ignore[arg-type]
                    status=s.status,  # type: ignore[arg-type]
                )
            )

        # Sort combined feed newest first
        activities.sort(key=lambda x: x.timestamp, reverse=True)

        # Truncate to the overall requested limit
        truncated_activities = activities[:limit]

        return RecentActivityResponse(activities=truncated_activities)
