import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DashboardAIAnalysis(Base):
    """
    Generalized table to store AI-generated analysis for any operational record.
    """

    __tablename__ = "dashboard_ai_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(50), nullable=False)  # e.g., 'feedback', 'complaints'
    source_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # references the ID of the source record

    sentiment = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    severity = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)

    extracted_keywords = Column(JSONB, nullable=True)
    ai_summary = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)

    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)

    analyzed_at = Column(DateTime(timezone=True), nullable=True, default=utc_now)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    __table_args__ = (
        Index("idx_dashboard_ai_analysis_source", "source_type", "source_id"),
    )


class DashboardAuditLog(Base):
    """
    Tracks actions performed by dashboard administrators.
    """

    __tablename__ = "dashboard_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class DashboardSettings(Base):
    """
    Key-value store for dashboard configuration.
    """

    __tablename__ = "dashboard_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String(100), nullable=False, unique=True)
    setting_value = Column(JSONB, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class DashboardAdminUser(Base):
    """
    Dashboard administrator users.
    """

    __tablename__ = "dashboard_admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(Text, nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(50), nullable=False, default="Support")
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class DashboardComplaintWorkflow(Base):
    """
    Dashboard-specific workflow fields for complaints.
    Keeps read-only operational complaints table untouched.
    """

    __tablename__ = "dashboard_complaint_workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    internal_status = Column(String(50), nullable=False, default="Pending")
    assigned_admin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dashboard_admin_users.id", ondelete="SET NULL"),
        nullable=True,
    )
    internal_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )
