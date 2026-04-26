from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.database import get_db
from app.models.event import Event
from app.models.registration import Registration, RegistrationStatus
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.schemas.registration import RegistrationResponse
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from sqlalchemy import cast,Date

router = APIRouter(prefix="/events", tags=["events"])

@router.post('/',response_model=EventResponse)
def create_event(payload:EventCreate,current_user=Depends(require_admin),db=Depends(get_db)):
     # 1. Unpack the payload and add the admin's ID
    new_event = Event(**payload.model_dump(), created_by=current_user.id)
    
    # 2. Save it to the database
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    # 3. Return it
    return new_event

@router.get('/', response_model=List[EventResponse])
def read_events(
    date_filter:Optional[date]=None,
    location:Optional[str]=None,
    is_team_event:Optional[bool]=None,
    db:Session=Depends(get_db)
):
    query = db.query(Event)
    if date_filter:
        query=query.filter(cast(Event.start_time,Date) == date_filter)

    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))
    if is_team_event is not None:
        query = query.filter(Event.is_team_event == is_team_event)
    events=query.all()

    return events    

@router.get('/{event_id}',response_model=EventResponse)
def get_event(event_id:UUID,db=Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put('/{event_id}',response_model=EventResponse)
def update_event(event_id:UUID,payload:EventUpdate,current_user=Depends(require_admin),db=Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this event")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event

@router.delete('/{event_id}')
def delete_event(event_id:UUID,current_user=Depends(require_admin),db=Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")
    db.delete(event)
    db.commit()
    return {"detail":"Event deleted successfully"}

@router.post('/{event_id}/register',response_model=RegistrationResponse,status_code=201)
def register_for_event(event_id:UUID,current_user=Depends(get_current_user),db=Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.is_team_event:
        raise HTTPException(status_code=400, detail="This is a team event. Please use the team registration endpoint.")
    existing_registration = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.user_id == current_user.id
    ).first()
    if existing_registration:
        raise HTTPException(status_code=400, detail="You have already registered for this event.")
    # 4. Check Capacity
    count = db.query(Registration).filter(Registration.event_id == event_id).count()
    if event.max_participants is not None and count >= event.max_participants:
        raise HTTPException(status_code=400, detail="Event is full.")
    # 5. Check if event already started
    if event.start_time < datetime.now():
        raise HTTPException(status_code=400, detail="Cannot register for an event that has already started.")
    new_registration = Registration(
        user_id=current_user.id,
        event_id=event_id,
        qr_token=str(uuid.uuid4()),
        status=RegistrationStatus.registered
    )
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    return new_registration

@router.delete('/{event_id}/register')
def cancel_registration(event_id:UUID,current_user=Depends(get_current_user),db=Depends(get_db)):
    registration = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.user_id == current_user.id
    ).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    db.delete(registration)
    db.commit()
    return {"detail":"Registration cancelled successfully"}   
    
    

    

    



    