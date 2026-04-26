import csv
import io
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from app.database import get_db
from app.models.registration import Registration
from app.models.user import User
from app.models.event import Event
from app.core.dependencies import require_admin

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/{event_id}/csv")
def export_csv(event_id: UUID, db: Session = Depends(get_db), _ = Depends(require_admin)):
    regs = db.query(Registration).join(User).filter(Registration.event_id == event_id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Email", "Status", "Registered At"])
    
    for r in regs:
        writer.writerow([str(r.id), r.user.name, r.user.email, r.status.value, str(r.registered_at)])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=registrations.csv"}
    )

@router.get("/{event_id}/sheets")
def export_sheets(event_id: UUID, db: Session = Depends(get_db), _ = Depends(require_admin)):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
    except FileNotFoundError:
        raise HTTPException(500, "Google Sheets credentials.json not found. Place it in the root directory.")
        
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
        
    sheet_name = f"Event_{event.title[:20]}"
    
    try:
        sheet = client.create(sheet_name)
        sheet.share('your_email@gmail.com', perm_type='user', role='writer')
        worksheet = sheet.get_worksheet(0)
    except Exception as e:
        raise HTTPException(500, f"Error interacting with Google Sheets: {e}")
        
    regs = db.query(Registration).join(User).filter(Registration.event_id == event_id).all()
    
    data = [["ID", "Name", "Email", "Status", "Registered At"]]
    for r in regs:
        data.append([str(r.id), r.user.name, r.user.email, r.status.value, str(r.registered_at)])
        
    worksheet.update('A1', data)
    return {"message": "Exported to Google Sheets successfully", "url": sheet.url}
