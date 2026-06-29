from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.session import get_db_session as get_db
from app.services.ai import AIService
from app.schemas.ai import (
    ExecutiveSummaryResult,
    FeedbackAnalysisResult,
    ComplaintAnalysisResult,
    AnalyticsInsightsResult,
    ReportGenerationRequest,
    ReportGenerationResult,
    ChatRequest,
    ChatResponse
)

router = APIRouter()

class AnalyzeFeedbackRequest(BaseModel):
    title: str
    category: str
    description: str

class AnalyzeComplaintRequest(BaseModel):
    title: str
    priority: str
    status: str
    description: str

@router.get("/executive-summary", response_model=ExecutiveSummaryResult)
async def get_executive_summary(db: AsyncSession = Depends(get_db)) -> Any:
    """
    Get an AI-generated executive summary of the dashboard.
    """
    return await AIService.get_executive_summary(db)

@router.post("/analyze-feedback", response_model=FeedbackAnalysisResult)
async def analyze_feedback(request: AnalyzeFeedbackRequest) -> Any:
    """
    Analyze customer feedback.
    """
    return await AIService.analyze_feedback(
        title=request.title,
        category=request.category,
        description=request.description
    )

@router.post("/analyze-complaint", response_model=ComplaintAnalysisResult)
async def analyze_complaint(request: AnalyzeComplaintRequest) -> Any:
    """
    Analyze a customer complaint.
    """
    return await AIService.analyze_complaint(
        title=request.title,
        priority=request.priority,
        status=request.status,
        description=request.description
    )

@router.get("/analytics-insights", response_model=AnalyticsInsightsResult)
async def get_analytics_insights(db: AsyncSession = Depends(get_db)) -> Any:
    """
    Get AI-generated insights based on system analytics.
    """
    return await AIService.get_analytics_insights(db)

@router.post("/generate-report", response_model=ReportGenerationResult)
async def generate_report(request: ReportGenerationRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Generate a comprehensive business report.
    """
    return await AIService.generate_report(db, request.report_type, request.focus_areas)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> Any:
    """
    Interact with the AI assistant.
    """
    return await AIService.chat(request)
