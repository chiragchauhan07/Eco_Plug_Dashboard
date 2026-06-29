# Import all models here so Alembic can discover them
from app.database.base import Base

# Dashboard-Owned Models (Alembic Managed)
from app.models.dashboard import (
    DashboardAdminUser,
    DashboardAIAnalysis,
    DashboardAuditLog,
    DashboardComplaintWorkflow,
    DashboardSettings,
)

# Operational Models (Read-Only / Existing)
from app.models.operational import (
    ChargerLocation,
    ChargingSession,
    Complaint,
    Feedback,
    KnowledgeChunk,
    User,
)

__all__ = [
    "Base",
    "ChargerLocation",
    "ChargingSession",
    "Complaint",
    "Feedback",
    "KnowledgeChunk",
    "User",
    "DashboardAdminUser",
    "DashboardAIAnalysis",
    "DashboardAuditLog",
    "DashboardComplaintWorkflow",
    "DashboardSettings",
]
