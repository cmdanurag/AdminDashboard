from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class EventBase(BaseModel):
    title: str
    description: str
    location: str
    start_time: datetime
    end_time: datetime
    max_participants: Optional[int] = None
    is_team_event: bool = False
    max_team_size: Optional[int] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_participants: Optional[int] = None
    is_team_event: Optional[bool] = None
    max_team_size: Optional[int] = None

class EventResponse(EventBase):
    id: UUID
    created_by: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
