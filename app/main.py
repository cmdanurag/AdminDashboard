from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, events, admin, teams, attendance, certificates
from app.utils import export

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(admin.router)
app.include_router(teams.router)
app.include_router(attendance.router)
app.include_router(certificates.router)
app.include_router(export.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Event Management API! Visit /docs for Swagger UI."}
