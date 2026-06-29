from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ChartDataset(BaseModel):
    label: str
    data: List[float]

    model_config = ConfigDict(from_attributes=True)


class ChartResponse(BaseModel):
    labels: List[str]
    datasets: List[ChartDataset]

    model_config = ConfigDict(from_attributes=True)


class DashboardOverviewResponse(BaseModel):
    total_users: int
    total_charging_sessions: int
    total_feedback: int
    total_complaints: int
    average_feedback_rating: float
    open_complaints: int
    closed_complaints: int
    total_energy_delivered: float
    total_revenue: float
    average_session_duration: float

    # Comparison metrics (percentage changes against previous equivalent period)
    users_change: Optional[float] = None
    sessions_change: Optional[float] = None
    feedback_change: Optional[float] = None
    complaints_change: Optional[float] = None
    revenue_change: Optional[float] = None
    energy_change: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackAnalyticsResponse(BaseModel):
    rating_distribution: ChartResponse
    feedback_over_time: ChartResponse
    category_distribution: ChartResponse
    average_rating_trend: ChartResponse

    model_config = ConfigDict(from_attributes=True)


class ComplaintAnalyticsResponse(BaseModel):
    status_distribution: ChartResponse
    category_distribution: ChartResponse
    complaints_over_time: ChartResponse
    workflow_status_distribution: ChartResponse

    model_config = ConfigDict(from_attributes=True)


class ChargerAnalyticsResponse(BaseModel):
    sessions: ChartResponse
    ratings: ChartResponse
    complaints: ChartResponse
    energy: ChartResponse
    revenue: ChartResponse

    model_config = ConfigDict(from_attributes=True)


class RecentActivityItem(BaseModel):
    type: str  # "feedback", "complaint", "session"
    id: UUID
    title: str
    description: Optional[str] = None
    timestamp: datetime
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RecentActivityResponse(BaseModel):
    activities: List[RecentActivityItem]

    model_config = ConfigDict(from_attributes=True)
