from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    event_id: UUID

class TeamUpdate(BaseModel):
    name: Optional[str] = None

class TeamResponse(TeamBase):
    id: UUID
    event_id: UUID
    join_code: str
    leader_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
