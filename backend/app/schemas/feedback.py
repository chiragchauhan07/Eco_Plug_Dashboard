from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChargingSessionResponse(BaseModel):
    id: UUID
    session_code: str
    energy_kwh: Optional[float] = None
    duration_minutes: Optional[int] = None
    amount_paid: Optional[float] = None
    payment_status: Optional[str] = None
    session_date: Optional[datetime] = None
    connector_type: str
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackAIAnalysisResponse(BaseModel):
    sentiment: str
    summary: str
    category: str
    priority: str
    suggested_action: str
    confidence_score: float
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    analyzed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackListItemResponse(BaseModel):
    id: UUID
    user_phone: str
    user_name: Optional[str] = None
    charger_name: str
    rating: int
    issue_category: Optional[str] = None
    feedback_comment: Optional[str] = None
    created_at: Optional[datetime] = None
    ai_analysis: Optional[FeedbackAIAnalysisResponse] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackDetailResponse(BaseModel):
    id: UUID
    user_phone: str
    user_name: Optional[str] = None
    session_id: str
    charger_name: str
    rating: int
    feedback_comment: Optional[str] = None
    created_at: Optional[datetime] = None
    connector_name: Optional[str] = None
    issue_category: Optional[str] = None
    support_agent_contacted: Optional[bool] = False
    support_agent_phone: Optional[str] = None
    support_agent_name: Optional[str] = None
    charger_issue_type: Optional[str] = None
    charging_session: Optional[ChargingSessionResponse] = None
    ai_analysis: Optional[FeedbackAIAnalysisResponse] = None

    model_config = ConfigDict(from_attributes=True)
