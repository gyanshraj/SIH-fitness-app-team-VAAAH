# Website (React + Vite)

This website is now connected to the Python API backend.

## Stack
- React + Vite
- React Router
- Recharts
- Fetch API for backend calls

## Features
- Login with backend auth
- Dashboard from SQL-backed data
- Workout plan list + add + delete
- Progress chart + add + delete entries

## Run Locally
```bash
npm install
npm run dev
```

Default API URL: `http://127.0.0.1:8000/api`

To change API URL, create `.env`:
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```
