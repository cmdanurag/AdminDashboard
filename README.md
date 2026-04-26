# Event Management API

A secure, database-driven FastAPI backend for an event management system.

## Features
- **JWT Authentication** (Signup/Login)
- **Event CRUD** with dynamic filtering
- **Team Event Registration** (with join codes)
- **Admin Dashboard** (stats, status management)
- **Bulk Email Notifications** (SMTP)
- **QR Code Attendance** Generation & Scanning
- **Automatic Certificate** Generation (PDF)
- **Export** to CSV & Google Sheets

## Setup & Run Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables in `.env`
3. Run the server: `uvicorn app.main:app --reload`
4. View interactive docs: `http://localhost:8000/docs`

## Docker
Run `docker-compose up --build` to start the API and PostgreSQL instances automatically.

## Tests
Run the test suite using: `pytest`

## AI Usage Log
*AI code generation was heavily utilized via Antigravity to quickly prototype and scaffold features including team registration logic, QR codes, PDF certificate generation, CSV/Sheets exports, Docker setup, and this README.*