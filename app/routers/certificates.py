from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.registration import Registration, RegistrationStatus
from app.models.event import Event
from app.models.user import User
from app.core.dependencies import get_current_user, require_admin
from app.utils.certificate import generate_certificate

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("/{event_id}/download")
def download_certificate(event_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    reg = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.user_id == current_user.id
    ).first()
    
    if not reg or reg.status != RegistrationStatus.attended:
        raise HTTPException(400, "You must attend the event to get a certificate")
        
    event = db.query(Event).filter(Event.id == event_id).first()
    
    cert_bytes = generate_certificate(
        name=current_user.name, 
        event_title=event.title, 
        date=str(event.start_time.date())
    )
    
    reg.certificate_issued = True
    db.commit()
    
    return Response(
        content=cert_bytes, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f'attachment; filename="certificate_{event.title}.pdf"'}
    )

@router.post("/admin/{event_id}/bulk")
def bulk_generate_certificates(event_id: UUID, db: Session = Depends(get_db), _ = Depends(require_admin)):
    regs = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.status == RegistrationStatus.attended,
        Registration.certificate_issued == False
    ).all()
    
    count = 0
    for reg in regs:
        reg.certificate_issued = True
        count += 1
        
    db.commit()
    return {"message": f"Bulk generated {count} certificates for attendees."}
