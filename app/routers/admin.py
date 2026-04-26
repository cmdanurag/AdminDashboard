from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.event import Event
from app.models.registration import Registration, RegistrationStatus
from app.models.user import User
from app.schemas.registration import RegistrationResponse, StatusUpdate
from app.core.dependencies import require_admin
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/events/{event_id}/registrations")
def list_registrations(
    event_id: UUID,
    status: Optional[str] = None,
    search: Optional[str] = None,
    team_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _ = Depends(require_admin)
):
    q = db.query(Registration).filter(Registration.event_id == event_id)
    if status:
        q = q.filter(Registration.status == status)
    if search:
        q = q.join(User).filter(
            or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"))
        )
    if team_id:
        q = q.filter(Registration.team_id == team_id)
    return q.offset(skip).limit(limit).all()

@router.patch("/registrations/{reg_id}/status")
def update_status(reg_id: UUID, payload: StatusUpdate, db: Session = Depends(get_db), _ = Depends(require_admin)):
    reg = db.query(Registration).filter(Registration.id == reg_id).first()
    if not reg:
        raise HTTPException(404, "Registration not found")
    reg.status = payload.status
    db.commit()
    return {"message": "Status updated"}

@router.get("/stats")
def stats(db: Session = Depends(get_db), _ = Depends(require_admin)):
    return {
        "total_users": db.query(func.count(User.id)).scalar(),
        "total_events": db.query(func.count(Event.id)).scalar(),
        "total_registrations": db.query(func.count(Registration.id)).scalar(),
        "attended": db.query(func.count(Registration.id))
                      .filter(Registration.status == "attended").scalar(),
    }

class NotifyPayload(BaseModel):
    subject: str
    body: str

@router.post("/events/{event_id}/notify")
async def notify_participants(event_id: UUID, payload: NotifyPayload, status_filter: Optional[str] = None, db: Session = Depends(get_db), _ = Depends(require_admin)):
    from app.utils.email import send_mass_email
    
    q = db.query(User.email).join(Registration).filter(Registration.event_id == event_id)
    if status_filter:
        q = q.filter(Registration.status == status_filter)
    else:
        q = q.filter(Registration.status.in_(["registered", "attended"]))
        
    emails = [row[0] for row in q.all()]
    if not emails:
        return {"message": "No eligible participants found to notify."}
        
    await send_mass_email(emails, payload.subject, payload.body)
    return {"message": f"Successfully notified {len(emails)} participants."}
