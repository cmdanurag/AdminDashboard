from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class RegistrationStatus(str, Enum):
    registered = "registered"
    attended = "attended"
    cancelled = "cancelled"

class RegistrationBase(BaseModel):
    event_id: UUID
    team_id: Optional[UUID] = None

class RegistrationCreate(RegistrationBase):
    pass

class RegistrationUpdate(BaseModel):
    team_id: Optional[UUID] = None

class StatusUpdate(BaseModel):
    status: RegistrationStatus

class RegistrationResponse(RegistrationBase):
    id: UUID
    user_id: UUID
    status: RegistrationStatus
    qr_token: str
    certificate_issued: bool
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
