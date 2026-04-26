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

This project was developed through a structured, collaborative approach:
- **Foundational Code:** I manually coded the core architecture, database schemas, user authentication (JWT), and the primary Event CRUD operations to ensure a deep, foundational understanding of FastAPI and SQLAlchemy.
- **Planning Assistance:** AI (Antigravity) was used as an architectural partner to plan the system design and structure the creative feature roadmap.
- **Advanced Feature Scaffolding:** Due to time constraints, I utilized AI to accelerate the implementation of the advanced "creative" features (QR Code generation, PDF Certificates, Google Sheets export, and Docker containerization). However, these features were implemented with full comprehension of the underlying logic to ensure they seamlessly and securely integrated with the core system I built.