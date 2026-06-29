from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ComplaintWorkflowResponse(BaseModel):
    internal_status: str
    assigned_admin_id: Optional[UUID] = None
    assigned_admin_name: Optional[str] = None
    internal_notes: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplaintResponse(BaseModel):
    id: UUID
    ticket_id: str
    phone_number: str
    category: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    support_agent_contacted: Optional[bool] = False
    support_agent_phone: Optional[str] = None
    support_agent_name: Optional[str] = None
    workflow: Optional[ComplaintWorkflowResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ComplaintUpdateRequest(BaseModel):
    internal_status: Optional[str] = None
    assigned_admin_id: Optional[UUID] = None
    internal_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
