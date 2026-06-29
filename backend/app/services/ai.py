import logging
import typing
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import (
    ExecutiveSummaryResult,
    ComplaintAnalysisResult,
    AnalyticsInsightsResult,
    ReportGenerationResult,
    ChatRequest,
    ChatResponse
)
from app.schemas.feedback import FeedbackAIAnalysisResponse
from app.ai.providers.factory import ProviderFactory
from app.ai.prompts import templates
from app.ai.context_builders import build_executive_summary_context, build_analytics_context
from app.ai.cache import ai_cache

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    async def get_executive_summary(db: AsyncSession) -> ExecutiveSummaryResult:
        cache_key = "executive_summary"
        cached = await ai_cache.get(cache_key)
        if cached:
            return typing.cast(ExecutiveSummaryResult, cached)

        provider = ProviderFactory.get_provider()
        context = await build_executive_summary_context(db)
        
        prompt = templates.EXECUTIVE_SUMMARY_PROMPT.format(**context)
        
        result = await provider.generate_structured(
            prompt=prompt,
            schema=ExecutiveSummaryResult
        )
        result_typed = typing.cast(ExecutiveSummaryResult, result)
        
        # Cache for 15 minutes
        await ai_cache.set(cache_key, result_typed, ttl=900)
        return result_typed

    @staticmethod
    async def analyze_feedback(rating: int, charger_name: str, comment: str) -> FeedbackAIAnalysisResponse:
        provider = ProviderFactory.get_provider()
        prompt = templates.FEEDBACK_ANALYSIS_PROMPT.format(
            rating=rating,
            charger_name=charger_name,
            comment=comment
        )
        
        result = await provider.generate_structured(
            prompt=prompt,
            schema=FeedbackAIAnalysisResponse
        )
        return typing.cast(FeedbackAIAnalysisResponse, result)

    @staticmethod
    async def analyze_complaint(title: str, priority: str, status: str, description: str) -> ComplaintAnalysisResult:
        provider = ProviderFactory.get_provider()
        prompt = templates.COMPLAINT_ANALYSIS_PROMPT.format(
            title=title,
            priority=priority,
            status=status,
            description=description
        )
        
        result = await provider.generate_structured(
            prompt=prompt,
            schema=ComplaintAnalysisResult
        )
        return typing.cast(ComplaintAnalysisResult, result)

    @staticmethod
    async def get_analytics_insights(db: AsyncSession) -> AnalyticsInsightsResult:
        cache_key = "analytics_insights"
        cached = await ai_cache.get(cache_key)
        if cached:
            return typing.cast(AnalyticsInsightsResult, cached)

        provider = ProviderFactory.get_provider()
        context = await build_analytics_context(db)
        
        prompt = templates.ANALYTICS_INSIGHTS_PROMPT.format(**context)
        
        result = await provider.generate_structured(
            prompt=prompt,
            schema=AnalyticsInsightsResult
        )
        result_typed = typing.cast(AnalyticsInsightsResult, result)
        
        # Cache for 60 minutes
        await ai_cache.set(cache_key, result_typed, ttl=3600)
        return result_typed

    @staticmethod
    async def generate_report(db: AsyncSession, report_type: str, focus_areas: list[str]) -> ReportGenerationResult:
        provider = ProviderFactory.get_provider()
        context = await build_analytics_context(db)
        
        prompt = templates.REPORT_GENERATION_PROMPT.format(
            report_type=report_type,
            focus_areas=", ".join(focus_areas) if focus_areas else "General Overview",
            **context
        )
        
        result = await provider.generate_structured(
            prompt=prompt,
            schema=ReportGenerationResult
        )
        return typing.cast(ReportGenerationResult, result)

    @staticmethod
    async def chat(request: ChatRequest) -> ChatResponse:
        provider = ProviderFactory.get_provider()
        result = await provider.chat(request.messages)
        return result
