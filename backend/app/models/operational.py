import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChargerLocation(Base):
    __tablename__ = "charger_locations"
    __table_args__ = {"info": {"skip_autogenerate": True}}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    charger_code = Column(Text, nullable=False)
    charger_name = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    state = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    charger_type = Column(Text, nullable=True)
    status = Column(Text, nullable=True, default="Available")
    latitude = Column(Numeric, nullable=True)
    longitude = Column(Numeric, nullable=True)
    created_at = Column(DateTime(timezone=False), nullable=True, default=utc_now)


class ChargingSession(Base):
    __tablename__ = "charging_sessions"
    __table_args__ = {"info": {"skip_autogenerate": True}}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_code = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    charger_id = Column(UUID(as_uuid=True), nullable=True)
    energy_kwh = Column(Numeric, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    amount_paid = Column(Numeric, nullable=True)
    payment_status = Column(Text, nullable=True, default="Paid")
    session_date = Column(DateTime(timezone=False), nullable=True, default=utc_now)
    session_id = Column(Text, nullable=False)
    user_phone = Column(Text, nullable=False)
    charger_name = Column(Text, nullable=False)
    connector_type = Column(Text, nullable=False)
    status = Column(Text, nullable=True, default="ACTIVE")
    start_time = Column(DateTime(timezone=True), nullable=True, default=utc_now)
    end_time = Column(DateTime(timezone=True), nullable=True)
    wallet_deduction = Column(Numeric, nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), nullable=True, default=utc_now)
    connector_number = Column(Integer, nullable=True)
    charging_amount = Column(Integer, nullable=True)


class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = {"info": {"skip_autogenerate": True}}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(Text, nullable=False)
    phone_number = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="Open")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    support_agent_contacted = Column(Boolean, nullable=True, default=False)
    support_agent_phone = Column(Text, nullable=True)
    support_agent_name = Column(Text, nullable=True)


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = {"info": {"skip_autogenerate": True}}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_phone = Column(Text, nullable=False)
    user_name = Column(Text, nullable=True)
    session_id = Column(Text, nullable=False)
    charger_name = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    feedback_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, default=utc_now)
    connector_name = Column(Text, nullable=True)
    issue_category = Column(Text, nullable=True)
    support_agent_contacted = Column(Boolean, nullable=True, default=False)
    support_agent_phone = Column(Text, nullable=True)
    support_agent_name = Column(Text, nullable=True)
    charger_issue_type = Column(Text, nullable=True)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = {"info": {"skip_autogenerate": True}}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(Text, nullable=False)
    topic = Column(Text, nullable=False)
    subtopic = Column(Text, nullable=False)
    keywords = Column(JSONB, nullable=True)
    content = Column(Text, nullable=False)
    source = Column(Text, nullable=True)
    version = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, default=utc_now)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"info": {"skip_autogenerate": True}}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_code = Column(Text, nullable=False)
    full_name = Column(Text, nullable=False)
    phone_number = Column(Text, nullable=False)
    vehicle_model = Column(Text, nullable=True)
    membership_plan = Column(Text, nullable=True, default="Basic")
    payment_method = Column(Text, nullable=True, default="UPI")
    created_at = Column(DateTime(timezone=False), nullable=True, default=utc_now)
    phone_verified = Column(Boolean, nullable=True, default=False)
    language = Column(String(50), nullable=True)
    wallet_balance = Column(Integer, nullable=True, default=150)
