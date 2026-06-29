import pytest
from unittest.mock import AsyncMock, patch

from app.services.ai import AIService
from app.schemas.ai import (
    ExecutiveSummaryResult,
    FeedbackAnalysisResult,
    ComplaintAnalysisResult,
    AnalyticsInsightsResult,
    ReportGenerationResult,
    ChatRequest,
    ChatMessage,
    ChatResponse
)

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def mock_provider():
    with patch("app.ai.providers.factory.ProviderFactory.get_provider") as mock_get_provider:
        provider = AsyncMock()
        mock_get_provider.return_value = provider
        yield provider

@pytest.fixture
def mock_cache():
    with patch("app.services.ai.ai_cache") as mock_cache:
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()
        yield mock_cache

@pytest.mark.asyncio
async def test_get_executive_summary(mock_db_session, mock_provider, mock_cache):
    # Mock dashboard stats response
    with patch("app.ai.context_builders.DashboardService") as mock_dash_svc:
        mock_instance = mock_dash_svc.return_value
        mock_stats = AsyncMock()
        mock_stats.total_feedback = 100
        mock_stats.total_complaints = 20
        mock_stats.open_complaints = 5
        mock_instance.get_overview_data = AsyncMock(return_value=mock_stats)

        mock_provider.generate_structured.return_value = ExecutiveSummaryResult(
            summary="All good.",
            key_metrics=["Feedback: 100"],
            urgent_actions=["Fix stuff"]
        )

        result = await AIService.get_executive_summary(mock_db_session)
        
        assert isinstance(result, ExecutiveSummaryResult)
        assert result.summary == "All good."
        
        mock_provider.generate_structured.assert_called_once()
        mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_feedback(mock_provider):
    mock_provider.generate_structured.return_value = FeedbackAnalysisResult(
        sentiment="Positive",
        key_themes=["Great feature"],
        suggested_response="Thank you",
        urgency_level="Low"
    )

    result = await AIService.analyze_feedback("Great app", "General", "I love this app")
    
    assert isinstance(result, FeedbackAnalysisResult)
    assert result.sentiment == "Positive"
    mock_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_complaint(mock_provider):
    mock_provider.generate_structured.return_value = ComplaintAnalysisResult(
        root_cause="Bug",
        action_plan=["Fix bug"],
        risk_assessment="High"
    )

    result = await AIService.analyze_complaint("App crashed", "High", "Open", "Crashed on login")
    
    assert isinstance(result, ComplaintAnalysisResult)
    assert result.root_cause == "Bug"
    mock_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_get_analytics_insights(mock_db_session, mock_provider, mock_cache):
    with patch("app.ai.context_builders.DashboardService") as mock_dash_svc:
        mock_instance = mock_dash_svc.return_value
        mock_stats = AsyncMock()
        mock_stats.total_feedback = 100
        mock_stats.total_complaints = 20
        mock_instance.get_overview_data = AsyncMock(return_value=mock_stats)

        mock_provider.generate_structured.return_value = AnalyticsInsightsResult(
            trends=["Upward trend"],
            anomalies=["None"],
            recommendations=["Keep it up"]
        )

        result = await AIService.get_analytics_insights(mock_db_session)
        
        assert isinstance(result, AnalyticsInsightsResult)
        assert result.trends == ["Upward trend"]
        mock_provider.generate_structured.assert_called_once()
        mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_generate_report(mock_db_session, mock_provider):
    with patch("app.ai.context_builders.DashboardService") as mock_dash_svc:
        mock_instance = mock_dash_svc.return_value
        mock_stats = AsyncMock()
        mock_stats.total_feedback = 100
        mock_stats.total_complaints = 20
        mock_instance.get_overview_data = AsyncMock(return_value=mock_stats)

        mock_provider.generate_structured.return_value = ReportGenerationResult(
            title="Weekly Report",
            content="# Weekly Report\n..."
        )

        result = await AIService.generate_report(mock_db_session, "Weekly", ["UX", "Performance"])
        
        assert isinstance(result, ReportGenerationResult)
        assert result.title == "Weekly Report"
        mock_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_chat(mock_provider):
    mock_provider.chat.return_value = ChatResponse(reply="Hello there")
    
    request = ChatRequest(messages=[ChatMessage(role="user", content="Hi")])
    result = await AIService.chat(request)
    
    assert isinstance(result, ChatResponse)
    assert result.reply == "Hello there"
    mock_provider.chat.assert_called_once()
