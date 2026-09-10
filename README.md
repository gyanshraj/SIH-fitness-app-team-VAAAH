# SIH-fitness-app-team-VAAAH

Web-first fitness project with a Python backend and SQL database.

## Current Stack (No Java/Kotlin required)

### Website
- React + Vite
- React Router
- Recharts

### Backend
- FastAPI (Python)
- SQLite (SQL)

## Project Structure

```text
SIH-fitness-app-team-VAAAH/
├── android-app/              # optional future mobile client
├── backend/                  # Python API + SQL storage
│   ├── app/
│   ├── fitness.db
│   ├── README.md
│   └── requirements.txt
├── website/                  # main current app
│   ├── README.md
│   ├── public/
│   └── src/
└── README.md
```

## Quick Start

### 1) Run Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2) Run Website
```bash
cd website
npm install
npm run dev
```

Website calls `http://127.0.0.1:8000/api` by default.
Set `VITE_API_BASE_URL` if needed.
