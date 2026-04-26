from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.registration import Registration, RegistrationStatus
from app.core.dependencies import require_admin, get_current_user
from app.utils.qr import generate_qr_code

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/qr/{event_id}")
def get_my_qr(event_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    reg = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.user_id == current_user.id
    ).first()
    
    if not reg:
        raise HTTPException(404, "Registration not found")
        
    qr_bytes = generate_qr_code(reg.qr_token)
    return Response(content=qr_bytes, media_type="image/png")

@router.post("/scan/{qr_token}")
def scan_qr(qr_token: str, db: Session = Depends(get_db), _ = Depends(require_admin)):
    reg = db.query(Registration).filter(Registration.qr_token == qr_token).first()
    if not reg:
        raise HTTPException(404, "Invalid QR Token")
        
    if reg.status == RegistrationStatus.attended:
        return {"message": "User already marked as attended", "user_id": reg.user_id}
        
    reg.status = RegistrationStatus.attended
    db.commit()
    return {"message": "Attendance marked successfully", "user_id": reg.user_id}
