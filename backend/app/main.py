from __future__ import annotations

import json
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .database import (
    get_connection,
    init_db,
    row_to_goal,
    row_to_progress,
    row_to_workout,
)
from .schemas import (
    GoalPayload,
    LoginPayload,
    LoginResponse,
    ProgressPayload,
    UserResponse,
    WorkoutPayload,
)
from .seed import seed_data

app = FastAPI(title="VAAAH Fitness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKENS: dict[str, int] = {}


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_data()


def _get_current_user_id(x_auth_token: Annotated[str | None, Header()] = None) -> int:
    if not x_auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")

    user_id = TOKENS.get(x_auth_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")

    return user_id


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginPayload):
    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, name, email FROM users WHERE email = ? AND password = ?",
            (payload.email, payload.password),
        ).fetchone()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = secrets.token_urlsafe(24)
    TOKENS[token] = user["id"]

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }


@app.get("/api/users/me", response_model=UserResponse)
def get_profile(user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
    }


@app.get("/api/workouts")
def list_workouts(user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, day, focus, duration, exercises_json FROM workouts WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()

    return [row_to_workout(row) for row in rows]


@app.post("/api/workouts", status_code=status.HTTP_201_CREATED)
def create_workout(payload: WorkoutPayload, user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO workouts (user_id, day, focus, duration, exercises_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, payload.day, payload.focus, payload.duration, json.dumps(payload.exercises)),
        )
        workout_id = cursor.lastrowid

        row = connection.execute(
            "SELECT id, day, focus, duration, exercises_json FROM workouts WHERE id = ?",
            (workout_id,),
        ).fetchone()

    return row_to_workout(row)


@app.put("/api/workouts/{workout_id}")
def update_workout(workout_id: int, payload: WorkoutPayload, user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        result = connection.execute(
            """
            UPDATE workouts
            SET day = ?, focus = ?, duration = ?, exercises_json = ?
            WHERE id = ? AND user_id = ?
            """,
            (payload.day, payload.focus, payload.duration, json.dumps(payload.exercises), workout_id, user_id),
        )

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

        row = connection.execute(
            "SELECT id, day, focus, duration, exercises_json FROM workouts WHERE id = ?",
            (workout_id,),
        ).fetchone()

    return row_to_workout(row)


@app.delete("/api/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        result = connection.execute(
            "DELETE FROM workouts WHERE id = ? AND user_id = ?",
            (workout_id, user_id),
        )

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")


@app.get("/api/progress")
def list_progress(user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, date, minutes, calories
            FROM progress_entries
            WHERE user_id = ?
            ORDER BY date
            """,
            (user_id,),
        ).fetchall()

    return [row_to_progress(row) for row in rows]


@app.post("/api/progress", status_code=status.HTTP_201_CREATED)
def create_progress(payload: ProgressPayload, user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO progress_entries (user_id, date, minutes, calories)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, payload.date, payload.minutes, payload.calories),
        )
        entry_id = cursor.lastrowid
        row = connection.execute(
            "SELECT id, date, minutes, calories FROM progress_entries WHERE id = ?",
            (entry_id,),
        ).fetchone()

    return row_to_progress(row)


@app.delete("/api/progress/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_progress(entry_id: int, user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        result = connection.execute(
            "DELETE FROM progress_entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
        )

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress entry not found")


@app.get("/api/goals")
def list_goals(user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, metric, target_value, current_value, deadline, status
            FROM goals
            WHERE user_id = ?
            ORDER BY id
            """,
            (user_id,),
        ).fetchall()

    return [row_to_goal(row) for row in rows]


@app.post("/api/goals", status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalPayload, user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO goals (user_id, title, metric, target_value, current_value, deadline, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                payload.title,
                payload.metric,
                payload.targetValue,
                payload.currentValue,
                payload.deadline,
                payload.status,
            ),
        )
        goal_id = cursor.lastrowid
        row = connection.execute(
            """
            SELECT id, title, metric, target_value, current_value, deadline, status
            FROM goals
            WHERE id = ?
            """,
            (goal_id,),
        ).fetchone()

    return row_to_goal(row)
