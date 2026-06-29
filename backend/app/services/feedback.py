from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import (
    ChargingSessionResponse,
    FeedbackDetailResponse,
    FeedbackListItemResponse,
    FeedbackAIAnalysisResponse,
)
from app.models.dashboard import DashboardAIAnalysis
from app.services.ai import AIService
from app.schemas.pagination import PaginatedResponseData, PaginationInfo


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FeedbackService:
    """
    Service layer for Feedback operations.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = FeedbackRepository(db)

    async def get_feedback_page(
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
    ) -> PaginatedResponseData[FeedbackListItemResponse]:
        """
        Orchestrate paginated feedback list query and calculate pagination metadata.
        """
        items, total = await self.repo.get_multi(
            page=page,
            size=size,
            user_name=user_name,
            user_phone=user_phone,
            rating=rating,
            charger_name=charger_name,
            issue_category=issue_category,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
        )

        total_pages = (total + size - 1) // size if total > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1

        pagination = PaginationInfo(
            page=page,
            size=size,
            total_items=total,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )

        mapped_items = []
        for item, ai_analysis in items:
            analysis_response = None
            if ai_analysis:
                analysis_response = FeedbackAIAnalysisResponse(
                    sentiment=str(ai_analysis.sentiment) if ai_analysis.sentiment else "Neutral",
                    summary=str(ai_analysis.ai_summary) if ai_analysis.ai_summary else "Unknown",
                    category=str(ai_analysis.category) if ai_analysis.category else "General",
                    priority=str(ai_analysis.severity) if ai_analysis.severity else "Medium",
                    suggested_action=str(ai_analysis.recommendation) if ai_analysis.recommendation else "No action needed",
                    confidence_score=float(ai_analysis.confidence_score) if ai_analysis.confidence_score else 0.0,
                    model_name=str(ai_analysis.model_name) if ai_analysis.model_name else None,
                    model_version=str(ai_analysis.model_version) if ai_analysis.model_version else None,
                    analyzed_at=ai_analysis.analyzed_at,  # type: ignore[arg-type]
                )

            item_dict = {
                "id": item.id,
                "user_phone": item.user_phone,
                "user_name": item.user_name,
                "charger_name": item.charger_name,
                "rating": item.rating,
                "issue_category": item.issue_category,
                "feedback_comment": item.feedback_comment,
                "created_at": item.created_at,
                "ai_analysis": analysis_response,
            }
            mapped_items.append(FeedbackListItemResponse.model_validate(item_dict))

        return PaginatedResponseData(items=mapped_items, pagination=pagination)

    async def get_feedback_detail(
        self, feedback_id: UUID
    ) -> Optional[FeedbackDetailResponse]:
        """
        Retrieve a single feedback record detailed with its charging session information and AI analysis.
        """
        result = await self.repo.get_by_id(feedback_id)
        if not result:
            return None

        feedback, session, ai_analysis = result

        session_data = None
        if session:
            session_data = ChargingSessionResponse.model_validate(session)

        analysis_response = None
        if ai_analysis:
            analysis_response = FeedbackAIAnalysisResponse(
                sentiment=str(ai_analysis.sentiment) if ai_analysis.sentiment else "Neutral",
                summary=str(ai_analysis.ai_summary) if ai_analysis.ai_summary else "Unknown",
                category=str(ai_analysis.category) if ai_analysis.category else "General",
                priority=str(ai_analysis.severity) if ai_analysis.severity else "Medium",
                suggested_action=str(ai_analysis.recommendation) if ai_analysis.recommendation else "No action needed",
                confidence_score=float(ai_analysis.confidence_score) if ai_analysis.confidence_score else 0.0,
                model_name=str(ai_analysis.model_name) if ai_analysis.model_name else None,
                model_version=str(ai_analysis.model_version) if ai_analysis.model_version else None,
                analyzed_at=ai_analysis.analyzed_at,  # type: ignore[arg-type]
            )

        feedback_dict = {
            "id": feedback.id,
            "user_phone": feedback.user_phone,
            "user_name": feedback.user_name,
            "session_id": feedback.session_id,
            "charger_name": feedback.charger_name,
            "rating": feedback.rating,
            "feedback_comment": feedback.feedback_comment,
            "created_at": feedback.created_at,
            "connector_name": feedback.connector_name,
            "issue_category": feedback.issue_category,
            "support_agent_contacted": feedback.support_agent_contacted,
            "support_agent_phone": feedback.support_agent_phone,
            "support_agent_name": feedback.support_agent_name,
            "charger_issue_type": feedback.charger_issue_type,
            "charging_session": session_data,
            "ai_analysis": analysis_response,
        }

        return FeedbackDetailResponse.model_validate(feedback_dict)

    async def analyze_feedback_item(
        self, feedback_id: UUID, force: bool = False
    ) -> Optional[FeedbackAIAnalysisResponse]:
        """
        Perform or refresh AI analysis on a feedback item, saving it to database and returning schema.
        """
        feedback_res = await self.repo.get_by_id(feedback_id)
        if not feedback_res:
            return None

        feedback, _, current_analysis = feedback_res

        if not force and current_analysis:
            # Return existing stored analysis
            return FeedbackAIAnalysisResponse(
                sentiment=str(current_analysis.sentiment) if current_analysis.sentiment else "Neutral",
                summary=str(current_analysis.ai_summary) if current_analysis.ai_summary else "Unknown",
                category=str(current_analysis.category) if current_analysis.category else "General",
                priority=str(current_analysis.severity) if current_analysis.severity else "Medium",
                suggested_action=str(current_analysis.recommendation) if current_analysis.recommendation else "No action needed",
                confidence_score=float(current_analysis.confidence_score) if current_analysis.confidence_score else 0.0,
                model_name=str(current_analysis.model_name) if current_analysis.model_name else None,
                model_version=str(current_analysis.model_version) if current_analysis.model_version else None,
                analyzed_at=current_analysis.analyzed_at,  # type: ignore[arg-type]
            )

        # Trigger Gemini
        gemini_result = await AIService.analyze_feedback(
            rating=int(feedback.rating),
            charger_name=str(feedback.charger_name),
            comment=str(feedback.feedback_comment or ""),
        )

        now = utc_now()
        if current_analysis:
            # Update existing
            current_analysis.sentiment = gemini_result.sentiment  # type: ignore[assignment]
            current_analysis.category = gemini_result.category  # type: ignore[assignment]
            current_analysis.severity = gemini_result.priority  # type: ignore[assignment]
            current_analysis.confidence_score = gemini_result.confidence_score  # type: ignore[assignment]
            current_analysis.ai_summary = gemini_result.summary  # type: ignore[assignment]
            current_analysis.recommendation = gemini_result.suggested_action  # type: ignore[assignment]
            current_analysis.model_name = "Gemini"  # type: ignore[assignment]
            current_analysis.model_version = "1.5-Pro"  # type: ignore[assignment]
            current_analysis.analyzed_at = now  # type: ignore[assignment]
            current_analysis.updated_at = now  # type: ignore[assignment]
            self.db.add(current_analysis)
        else:
            # Insert new
            new_analysis = DashboardAIAnalysis(
                source_type="feedback",
                source_id=feedback_id,
                sentiment=gemini_result.sentiment,
                category=gemini_result.category,
                severity=gemini_result.priority,
                confidence_score=gemini_result.confidence_score,
                ai_summary=gemini_result.summary,
                recommendation=gemini_result.suggested_action,
                model_name="Gemini",
                model_version="1.5-Pro",
                analyzed_at=now,
                created_at=now,
                updated_at=now,
            )
            self.db.add(new_analysis)

        await self.db.commit()

        # Re-fetch or return directly
        return FeedbackAIAnalysisResponse(
            sentiment=gemini_result.sentiment,
            summary=gemini_result.summary,
            category=gemini_result.category,
            priority=gemini_result.priority,
            suggested_action=gemini_result.suggested_action,
            confidence_score=gemini_result.confidence_score,
            model_name="Gemini",
            model_version="1.5-Pro",
            analyzed_at=now,
        )
