# MARINA INTELLIGENCE — Production Deployment & Infrastructure Guide

**Document Version:** 4.0.0  
**Infrastructure Stack:** Docker • Docker Compose • Nginx • PostgreSQL 16  

---

## 1. Local Development Setup

### Prerequisites
- Python 3.12+
- Node.js 20+ and pnpm
- SQLite (built-in) or PostgreSQL 16

### Backend Setup:
```powershell
# In project root
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
$env:PYTHONPATH="backend\src"
python -m uvicorn marina.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup:
```powershell
cd frontend
pnpm install
pnpm dev
# Frontend is served at http://localhost:3000
```

---

## 2. Docker & Containerized Production Deployment

The platform provides a complete `docker-compose.yml` orchestrating the database, API server, and frontend web client:

### Launch Containers:
```bash
docker compose up -d --build
```

### Environment Configuration (`.env`):
```env
# Application Environment
NODE_ENV=production
PYTHONUNBUFFERED=1

# Backend Database
DATABASE_URL=postgresql+asyncpg://marina_admin:secret_password@postgres:5432/marina_intelligence

# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Healthcheck Endpoints:
- Backend: `GET http://localhost:8000/health`
- Frontend: `GET http://localhost:3000`
