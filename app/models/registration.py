import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import enum

class RegistrationStatus(str, enum.Enum):
    registered = "registered"
    attended = "attended"
    cancelled = "cancelled"

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    status = Column(Enum(RegistrationStatus), default=RegistrationStatus.registered, nullable=False)
    qr_token = Column(String, unique=True, index=True, nullable=False)
    certificate_issued = Column(Boolean, default=False)
    registered_at = Column(DateTime, server_default=func.now())
