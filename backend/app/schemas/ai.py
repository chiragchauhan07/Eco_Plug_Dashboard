from typing import List
from pydantic import BaseModel, Field

class ExecutiveSummaryResult(BaseModel):
    summary: str = Field(..., description="High level summary of the current dashboard state")
    key_metrics: List[str] = Field(..., description="List of key metric highlights")
    urgent_actions: List[str] = Field(..., description="List of urgent actions that require attention")

class FeedbackAnalysisResult(BaseModel):
    sentiment: str = Field(..., description="The overall sentiment of the feedback (Positive, Neutral, Negative)")
    key_themes: List[str] = Field(..., description="Key themes extracted from the feedback")
    suggested_response: str = Field(..., description="A suggested response to the user")
    urgency_level: str = Field(..., description="Urgency level (Low, Medium, High, Critical)")

class ComplaintAnalysisResult(BaseModel):
    root_cause: str = Field(..., description="The likely root cause of the complaint")
    action_plan: List[str] = Field(..., description="Recommended steps to resolve the complaint")
    risk_assessment: str = Field(..., description="Assessment of the risk associated with this complaint")

class AnalyticsInsightsResult(BaseModel):
    trends: List[str] = Field(..., description="Key trends identified in the data")
    anomalies: List[str] = Field(..., description="Anomalies detected in the data")
    recommendations: List[str] = Field(..., description="Actionable recommendations based on analytics")

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="List of chat messages representing the conversation history")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="The AI's reply")

class ReportGenerationRequest(BaseModel):
    report_type: str = Field(..., description="The type of report to generate (e.g., Weekly, Monthly)")
    focus_areas: List[str] = Field(default_factory=list, description="Specific areas to focus the report on")

class ReportGenerationResult(BaseModel):
    title: str = Field(..., description="Title of the report")
    content: str = Field(..., description="Markdown content of the generated report")
