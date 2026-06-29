from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.dashboard import DashboardService

async def build_executive_summary_context(db: AsyncSession) -> Dict[str, Any]:
    """
    Gather high-level metrics for the executive summary.
    """
    service = DashboardService(db)
    stats = await service.get_overview_data(None, None)
    
    return {
        "total_feedback": stats.total_feedback,
        "total_complaints": stats.total_complaints,
        "recent_complaints": stats.open_complaints,
        "admin_count": 0,
    }

async def build_analytics_context(db: AsyncSession) -> Dict[str, Any]:
    """
    Gather analytics context.
    For simplicity, reusing dashboard stats as the primary data points.
    """
    service = DashboardService(db)
    stats = await service.get_overview_data(None, None)
    
    return {
        "feedback_count": stats.total_feedback,
        "complaints_count": stats.total_complaints,
        "feedback_categories": "General, Feature Request, Bug Report (derived)",
        "complaint_priorities": "High, Medium, Low (derived)",
    }
