from typing import List, Optional
from pydantic import BaseModel, Field

class AnalyticsOverviewResponse(BaseModel):
    total_feedback: int
    total_complaints: int
    average_rating: float
    complaint_rate: float
    resolved_complaints: int
    pending_complaints: int
    resolution_percentage: float
    average_response_time: Optional[float] = None
    active_users: int
    total_sessions: int
    energy_delivered: float
    energy_saved: float

class TrendDataset(BaseModel):
    label: str
    data: List[float]

class TrendResponse(BaseModel):
    labels: List[str]
    datasets: List[TrendDataset]

class CategoryDistributionItem(BaseModel):
    category: str
    count: int
    percentage: float

class CategoryDistributionResponse(BaseModel):
    categories: List[CategoryDistributionItem]

class SentimentDistributionItem(BaseModel):
    sentiment: str
    count: int
    percentage: float

class SentimentDistributionResponse(BaseModel):
    distribution: List[SentimentDistributionItem]

class TopIssueItem(BaseModel):
    issue: str
    count: int

class TopIssuesResponse(BaseModel):
    issues: List[TopIssueItem]

class LocationInsightItem(BaseModel):
    location_name: str
    complaint_count: int
    average_rating: float
    session_count: int

class LocationInsightsResponse(BaseModel):
    most_complaints_by_location: List[LocationInsightItem]
    highest_rated_locations: List[LocationInsightItem]
    lowest_rated_locations: List[LocationInsightItem]
    most_active_chargers: List[LocationInsightItem]

class AIAnalyticsInsightsResponse(BaseModel):
    trends: List[str] = Field(..., description="Positive trends in the analytics data")
    anomalies: List[str] = Field(..., description="Risk indicators or anomalies in the analytics data")
    recommendations: List[str] = Field(..., description="Actionable opportunities based on interpretation")
