# Event Management API — Design Document

> **Stack:** FastAPI · PostgreSQL · SQLAlchemy · JWT · Python 3.11+
> **Deliverables:** GitHub repo + live Swagger UI at `/docs`
> **Submission note:** Parts marked 🤖 are AI-generated. Parts marked ✍️ are written by me.
> This distinction is declared honestly in the AI Usage Log below.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Database Schema](#2-database-schema)
3. [API Endpoints — Full List](#3-api-endpoints--full-list)
4. [Feature Breakdown — Who Codes What](#4-feature-breakdown--who-codes-what)
5. [Creative Features Deep Dive](#5-creative-features-deep-dive)
6. [AI Usage Log Template](#6-ai-usage-log-template)
7. [Running the Project](#7-running-the-project)
8. [Implementation Order for Today](#8-implementation-order-for-today)

---

## 1. Project Structure

```
event-api/
├── app/
│   ├── main.py                  ✍️  YOU — wire routers, app metadata, CORS
│   ├── database.py              🤖  AI — SQLAlchemy engine + session + Base
│   ├── models/
│   │   ├── user.py              ✍️  YOU — User model (know your own schema)
│   │   ├── event.py             ✍️  YOU — Event model
│   │   ├── registration.py      🤖  AI — Registration join table
│   │   └── team.py              🤖  AI — Team + membership model
│   ├── schemas/
│   │   ├── user.py              🤖  AI — Pydantic request/response schemas
│   │   ├── event.py             🤖  AI — Event schemas
│   │   └── auth.py              🤖  AI — Token schemas
│   ├── routers/
│   │   ├── auth.py              ✍️  YOU — signup + login (core, 40 pts)
│   │   ├── events.py            ✍️  YOU — event CRUD (core, 40 pts)
│   │   ├── admin.py             ✍️  YOU — admin dashboard (core, 40 pts)
│   │   ├── registrations.py     🤖  AI — register/cancel endpoints
│   │   ├── teams.py             🤖  AI — team create/join with code
│   │   ├── attendance.py        🤖  AI — QR generation + scan verify
│   │   └── certificates.py      🤖  AI — PDF certificate generation
│   ├── core/
│   │   ├── security.py          ✍️  YOU — bcrypt + JWT encode/decode
│   │   ├── dependencies.py      ✍️  YOU — get_current_user, require_admin
│   │   └── config.py            🤖  AI — pydantic settings from .env
│   └── utils/
│       ├── qr.py                🤖  AI — QR code PNG generator
│       ├── certificate.py       🤖  AI — Pillow/ReportLab PDF cert
│       ├── email.py             🤖  AI — SMTP mass email sender
│       └── export.py            🤖  AI — CSV + Google Sheets export
├── tests/
│   ├── conftest.py              🤖  AI — pytest fixtures, in-memory test DB
│   ├── test_auth.py             ✍️  YOU — write at least 3 tests yourself
│   └── test_events.py           🤖  AI — CRUD test scaffolding
├── alembic/                     🤖  AI — migration setup
├── .env.example                 ✍️  YOU — know every variable in here
├── Dockerfile                   🤖  AI
├── docker-compose.yml           🤖  AI
└── README.md                    ✍️  YOU — write this entirely yourself
```

---

## 2. Database Schema

Design these yourself. Understand every column before asking AI to generate the SQLAlchemy model.

### users
| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | `default=uuid4` |
| name | String | |
| email | String (unique) | |
| hashed_password | String | bcrypt — never plaintext |
| is_admin | Boolean | default False |
| created_at | DateTime | server default now() |

### events
| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| title | String | |
| description | Text | |
| location | String | |
| start_time | DateTime | |
| end_time | DateTime | |
| max_participants | Integer | nullable = no limit |
| is_team_event | Boolean | default False |
| max_team_size | Integer | nullable |
| created_by | UUID (FK → users.id) | admin who created it |
| created_at | DateTime | |

### registrations
| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | |
| event_id | UUID (FK → events.id) | |
| team_id | UUID (FK → teams.id) | nullable |
| status | Enum | `registered`, `attended`, `cancelled` |
| qr_token | String (unique) | UUID-based, for QR scan |
| certificate_issued | Boolean | default False |
| registered_at | DateTime | |

### teams
| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| name | String | |
| event_id | UUID (FK → events.id) | |
| join_code | String (unique) | 6-char alphanumeric e.g. `XK92TL` |
| leader_id | UUID (FK → users.id) | |
| created_at | DateTime | |

---

## 3. API Endpoints — Full List

### Auth  ✍️ you write these
```
POST   /auth/signup                     Register new user
POST   /auth/login                      Returns JWT access token
GET    /auth/me                         Current user profile
```

### Events  ✍️ you write these
```
GET    /events                          List events (filter: date, location, is_team_event)
POST   /events                          Create event [admin only]
GET    /events/{id}                     Single event detail
PUT    /events/{id}                     Update event [admin only]
DELETE /events/{id}                     Delete event [admin only]
POST   /events/{id}/register            Register current user
DELETE /events/{id}/register            Cancel registration
```

### Admin Dashboard  ✍️ you write these — this is the 40 pt core
```
GET    /admin/events/{id}/registrations List registrants
                                        ?status=attended|registered|cancelled
                                        &search=name_or_email
                                        &team_id=...
PATCH  /admin/registrations/{id}/status Mark attended / cancelled / registered
POST   /admin/events/{id}/notify        Send mass email to all registrants
GET    /admin/events/{id}/export/csv    Download registrations as CSV
GET    /admin/events/{id}/export/sheets Push to Google Sheet (returns sheet URL)
GET    /admin/stats                     Platform-wide summary stats
POST   /admin/events/{id}/certificates  Bulk-generate certificates for attendees
```

### Teams  🤖 AI generates
```
POST   /teams/create                    Create team → returns join_code
POST   /teams/join                      Join with join_code
GET    /teams/{id}                      Team members + event info
DELETE /teams/{id}/leave                Leave team
```

### Attendance / QR  🤖 AI generates
```
GET    /attendance/qr/{registration_id} Returns QR code PNG image
POST   /attendance/verify               Body: {qr_token} → marks attended
```

### Certificates  🤖 AI generates
```
GET    /certificates/{registration_id}  Download personal PDF certificate
```

---

## 4. Feature Breakdown — Who Codes What

### ✍️ YOU must write these — examined most closely

#### A. `app/core/security.py`
The most important file. Write it yourself, line by line.

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
```

#### B. `app/core/dependencies.py`
Write this yourself. It protects every secured route.

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token
from app.database import get_db
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    payload = decode_token(token)           # raises 401 if bad
    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

#### C. `app/routers/auth.py`
Write both routes. The examiner will open this file first.

```python
@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(payload: UserCreate, db = Depends(get_db)):
    # 1. check email uniqueness → 400 if exists
    # 2. hash_password(payload.password)
    # 3. create User object, db.add, db.commit, db.refresh
    # 4. return user

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    # 1. find user by email → 401 if not found
    # 2. verify_password → 401 if wrong
    # 3. create_access_token({"sub": str(user.id)})
    # 4. return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def me(current_user = Depends(get_current_user)):
    return current_user
```

#### D. `app/routers/admin.py`
This is the heart of the submission. Write every route yourself.

```python
# Filtering registrations — learn SQLAlchemy dynamic filtering
@router.get("/events/{event_id}/registrations")
def list_registrations(
    event_id: UUID,
    status: Optional[str] = None,
    search: Optional[str] = None,
    team_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 50,
    db = Depends(get_db),
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

# Mark status — understand this pattern
@router.patch("/registrations/{reg_id}/status")
def update_status(reg_id: UUID, status: StatusUpdate, db = Depends(get_db), _ = Depends(require_admin)):
    reg = db.query(Registration).filter(Registration.id == reg_id).first()
    if not reg:
        raise HTTPException(404, "Registration not found")
    reg.status = status.status
    db.commit()
    return {"message": "Status updated"}

# Stats — learn func.count
@router.get("/stats")
def stats(db = Depends(get_db), _ = Depends(require_admin)):
    return {
        "total_users": db.query(func.count(User.id)).scalar(),
        "total_events": db.query(func.count(Event.id)).scalar(),
        "total_registrations": db.query(func.count(Registration.id)).scalar(),
        "attended": db.query(func.count(Registration.id))
                      .filter(Registration.status == "attended").scalar(),
    }
```

#### E. `app/routers/events.py` — write CRUD yourself
Focus on the list endpoint — add query param filters:
- `?date=2025-04-26` — filter by event date
- `?location=Mumbai` — ilike filter
- `?is_team_event=true`

This demonstrates you understand how real APIs serve filtered data.

#### F. `tests/test_auth.py` — write these 3 tests yourself

```python
def test_signup_success(client):
    r = client.post("/auth/signup", json={"name": "Test", "email": "t@t.com", "password": "pass123"})
    assert r.status_code == 201
    assert "id" in r.json()

def test_signup_duplicate_email(client):
    # register same email twice → second should be 400
    ...

def test_login_wrong_password(client):
    # signup then login with wrong password → 401
    ...
```

---

### 🤖 AI generates these — but READ every file before submitting

For each one, paste the exact prompt into Claude/ChatGPT, read the output, and test it.

#### `app/database.py`
> Prompt: *"Write a SQLAlchemy database.py for FastAPI with PostgreSQL. Include engine, SessionLocal, Base, and a get_db dependency generator."*

#### `app/schemas/*.py`
> Prompt: *"Write Pydantic v2 schemas for User, Event, Registration, and Team. Each needs a Create schema, an Update schema, and a Response schema. Use model_config with from_attributes=True."*

#### `app/utils/qr.py`
> Prompt: *"Write a Python function that takes a string token and returns a PNG QR code as bytes using the qrcode library."*

#### `app/utils/certificate.py`
> Prompt: *"Write a Python function using Pillow that generates a certificate image. It takes participant_name, event_name, and date as inputs and returns PDF bytes. Use a white background with a border, title Certificate of Participation, and the participant name in large centered text."*

#### `app/utils/email.py`
> Prompt: *"Write an async Python function that sends an HTML email to a list of recipients using smtplib and Gmail SMTP. Read credentials from environment variables."*

#### `app/utils/export.py` (CSV)
> Prompt: *"Write a FastAPI route that queries all registrations for an event_id and returns a StreamingResponse CSV file with columns: name, email, status, registered_at, team_name."*

#### `app/utils/export.py` (Google Sheets)
> Prompt: *"Write a Python function using the gspread library and a Google service account to create a new Google Sheet, write registration data to it, and return the sheet URL."*

#### `app/routers/teams.py`
> Prompt: *"Write FastAPI routes to: (1) create a team for an event and generate a random 6-character alphanumeric join_code, (2) join a team using a join_code, (3) get team details with member list."*

#### `app/routers/attendance.py`
> Prompt: *"Write FastAPI routes to: (1) return a QR code PNG image for a registration_id where the QR encodes the registration qr_token field, (2) accept a POST with a qr_token and mark that registration status as attended."*

#### `app/routers/certificates.py`
> Prompt: *"Write a FastAPI route that bulk-generates certificates for all attended registrations in an event (admin only), and allows a user to download their own certificate PDF by registration_id."*

#### `alembic/`
> Prompt: *"Show me how to set up Alembic with FastAPI and SQLAlchemy. Include alembic.ini config, the env.py modification to import my models, and the commands to create and run the first migration."*

#### `Dockerfile` + `docker-compose.yml`
> Prompt: *"Write a Dockerfile for a FastAPI app using uvicorn and a docker-compose.yml that starts both FastAPI and PostgreSQL 15. Include a healthcheck on the DB."*

---

## 5. Creative Features Deep Dive

These are the "think outside the box" features that target the 30 creativity points.

### 🎫 QR Code Attendance
- When a user registers, a unique `qr_token` (UUID) is generated and stored on the registration row
- `GET /attendance/qr/{registration_id}` generates a QR image encoding that token, returned as `image/png`
- `POST /attendance/verify` with `{qr_token}` → admin scans it at the door → status set to `attended`
- **Why it impresses:** Shows real-world event logistics thinking, not just CRUD

### 📜 Automatic Certificate Generator
- Admin hits `POST /admin/events/{id}/certificates` after the event ends
- For every registration with `status = attended`, a PDF is generated with name + event + date
- `certificate_issued = True` is set on the row; user downloads at `GET /certificates/{registration_id}`
- **Why it impresses:** Demonstrates Python PDF/image generation, a tangible real-world output

### 👥 Team Code System
- Events can be marked `is_team_event = True` with a `max_team_size`
- Any participant hits `POST /teams/create` → gets a code like `XK92TL`
- Teammates hit `POST /teams/join {join_code: "XK92TL"}` → added to the team
- Admin can filter the registrations dashboard by team
- **Why it impresses:** Many-to-many relationships, real group coordination logic

### 📧 Mass Email with HTML Template
- Admin hits `POST /admin/events/{id}/notify` with `{subject, body}`
- Sends to all participants with `registered` or `attended` status via Gmail SMTP
- Email body auto-fills `{{participant_name}}` and `{{event_title}}` placeholders
- Optional filter: `?status=registered` to only email a subset
- **Why it impresses:** A real admin power tool — event organisers genuinely need this

### 📊 CSV Export + Google Sheets Push
- `GET /admin/events/{id}/export/csv` → instant download of registrations as CSV
- `GET /admin/events/{id}/export/sheets` → pushes same data to a new Google Sheet, returns the URL
- Columns: name, email, status, team, registered_at
- **Why it impresses:** The brief literally namedrops Google Sheets — this is a direct brownie point

### 📈 Admin Stats Endpoint
`GET /admin/stats` returns:
```json
{
  "total_users": 120,
  "total_events": 8,
  "total_registrations": 340,
  "attendance_rate": "73%",
  "top_events": [
    {"title": "Hackathon 2025", "registrations": 89}
  ]
}
```
**Why it impresses:** Shows your dashboard surfaces real insights, not just raw data.

---

## 6. AI Usage Log Template

Put this in your README. The examiner will read it and may ask you to explain any line.

```markdown
## AI Assistance Log

| File / Feature | Tool | Prompt Summary | What I Verified / Changed |
|---|---|---|---|
| app/database.py | Claude | SQLAlchemy setup for FastAPI + PostgreSQL | Verified get_db generator pattern |
| app/schemas/*.py | Claude | Pydantic v2 schemas for all models | Added missing fields, fixed response models |
| app/utils/qr.py | Claude | QR code PNG bytes with qrcode lib | Tested output, confirmed PNG format |
| app/utils/certificate.py | Claude | Pillow certificate with name + event | Adjusted font, layout, border |
| app/utils/email.py | Claude | Async Gmail SMTP HTML email sender | Added error handling, env var creds |
| app/utils/export.py | Claude | StreamingResponse CSV + gspread Sheets | Verified CSV headers and sheet URL return |
| app/routers/teams.py | Claude | Team create/join with 6-char code | Added uniqueness check, size limit |
| app/routers/attendance.py | Claude | QR verify + mark attended | Added 404 + already-attended guard |
| app/routers/certificates.py | Claude | Bulk PDF cert generation | Tested PDF output, fixed encoding |
| tests/test_events.py | Claude | Pytest CRUD test scaffolding | Added edge case for full-capacity event |
| Dockerfile | Claude | FastAPI + uvicorn container | Changed port, added .env mounting |
| docker-compose.yml | Claude | FastAPI + PostgreSQL compose | Added DB healthcheck |

### Written entirely by me (no AI):
- app/core/security.py — password hashing and JWT logic
- app/core/dependencies.py — get_current_user and require_admin
- app/routers/auth.py — signup, login, /me
- app/routers/events.py — full event CRUD with query filters
- app/routers/admin.py — filtering, mark status, stats, mass notify, export triggers
- app/models/user.py — User SQLAlchemy model
- app/models/event.py — Event SQLAlchemy model
- tests/test_auth.py — signup, duplicate email, wrong password tests
- README.md — this file
```

---

## 7. Running the Project

```bash
# Clone and install
git clone https://github.com/your-username/event-api
cd event-api
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in all values in .env

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000

# Swagger UI (your demo link) → http://localhost:8000/docs
# ReDoc                       → http://localhost:8000/redoc

# Or run with Docker
docker-compose up --build
```

### `.env` variables
```
DATABASE_URL=postgresql://user:password@localhost:5432/eventdb
SECRET_KEY=replace-with-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=youremail@gmail.com
SMTP_PASSWORD=your-gmail-app-password
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service-account.json
```

### Key dependencies (`requirements.txt`)
```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
alembic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
pydantic-settings
qrcode[pil]
Pillow
reportlab
gspread
google-auth
pytest
httpx
```

---

## 8. Implementation Order for Today

Do these strictly in order. Stop when time runs out — steps 1–7 alone guarantee 70+ pts.

| # | Task | Who | Est. Time |
|---|---|---|---|
| 1 | `models/user.py` + `models/event.py` | ✍️ you | 20 min |
| 2 | `database.py` + all `schemas/` | 🤖 AI | 15 min |
| 3 | `core/security.py` + `core/dependencies.py` | ✍️ you | 30 min |
| 4 | `routers/auth.py` — signup + login + /me | ✍️ you | 30 min |
| 5 | `routers/events.py` — CRUD with filters | ✍️ you | 35 min |
| 6 | `routers/admin.py` — filter, mark, stats, notify | ✍️ you | 45 min |
| 7 | `tests/test_auth.py` — 3 tests | ✍️ you | 20 min |
| 8 | `utils/qr.py` + `routers/attendance.py` | 🤖 AI | 20 min |
| 9 | `utils/certificate.py` + `routers/certificates.py` | 🤖 AI | 20 min |
| 10 | `utils/email.py` wired into admin notify | 🤖 AI | 15 min |
| 11 | `utils/export.py` — CSV + Google Sheets | 🤖 AI | 20 min |
| 12 | `routers/teams.py` | 🤖 AI | 15 min |
| 13 | `Dockerfile` + `docker-compose.yml` | 🤖 AI | 10 min |
| 14 | Deploy to Railway (connect GitHub repo) | — | 15 min |
| 15 | `README.md` with full AI usage log | ✍️ you | 20 min |

**Total: ~5.5 hours moving fast.**

> ⚡ Steps 1–7 = auth + CRUD + admin dashboard + tests + Swagger = strong 70+ pt submission.
> Steps 8–12 = the creativity bonus. Do as many as time allows, in order.
> Each feature you ship beyond step 7 is a visible differentiator.
