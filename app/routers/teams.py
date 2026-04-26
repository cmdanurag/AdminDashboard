from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import secrets

from app.database import get_db
from app.models.team import Team
from app.models.event import Event
from app.models.registration import Registration, RegistrationStatus
from app.schemas.team import TeamCreate, TeamResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/", response_model=TeamResponse, status_code=201)
def create_team(payload: TeamCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == payload.event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    if not event.is_team_event:
        raise HTTPException(400, "This is not a team event")
        
    join_code = secrets.token_urlsafe(6).upper()
    
    new_team = Team(
        name=payload.name,
        event_id=payload.event_id,
        leader_id=current_user.id,
        join_code=join_code
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    import uuid
    reg = Registration(
        user_id=current_user.id,
        event_id=payload.event_id,
        team_id=new_team.id,
        qr_token=str(uuid.uuid4()),
        status=RegistrationStatus.registered
    )
    db.add(reg)
    db.commit()
    
    return new_team

@router.post("/join/{join_code}")
def join_team(join_code: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    team = db.query(Team).filter(Team.join_code == join_code).first()
    if not team:
        raise HTTPException(404, "Invalid join code")
        
    event = db.query(Event).filter(Event.id == team.event_id).first()
    
    current_members = db.query(Registration).filter(Registration.team_id == team.id).count()
    if event.max_team_size and current_members >= event.max_team_size:
        raise HTTPException(400, "Team is full")
        
    existing_reg = db.query(Registration).filter(
        Registration.user_id == current_user.id, 
        Registration.event_id == team.event_id
    ).first()
    
    if existing_reg:
        if existing_reg.team_id:
            raise HTTPException(400, "You are already in a team for this event")
        existing_reg.team_id = team.id
        db.commit()
    else:
        import uuid
        reg = Registration(
            user_id=current_user.id,
            event_id=team.event_id,
            team_id=team.id,
            qr_token=str(uuid.uuid4()),
            status=RegistrationStatus.registered
        )
        db.add(reg)
        db.commit()
        
    return {"message": f"Successfully joined team {team.name}"}
