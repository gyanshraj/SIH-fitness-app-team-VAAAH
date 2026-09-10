# Backend API (Python + FastAPI + SQLite)

This backend replaces the website's offline-only data flow with API + SQL storage.

## Stack
- FastAPI
- SQLite

## Run Locally
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000/api`

## Demo Login Seed
- Email: `demo@vaaah.com`
- Password: `demo123`

The database (`backend/fitness.db`) is auto-created and seeded on first startup with demo data. If `website/src/data/*.json` exists, those files are used instead.
