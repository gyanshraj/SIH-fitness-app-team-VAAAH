from __future__ import annotations

import json
from pathlib import Path

from .database import get_connection

ROOT_DIR = Path(__file__).resolve().parents[2]
WEBSITE_DATA_DIR = ROOT_DIR / "website" / "src" / "data"
DEFAULT_SEED_DATA = {
    "user.json": {
        "name": "Demo Student",
        "email": "demo@vaaah.com",
        "password": "demo123",
    },
    "workouts.json": [
        {"day": "Monday", "focus": "Full Body", "duration": 30, "exercises": ["Squats", "Push-ups"]},
        {"day": "Wednesday", "focus": "Cardio", "duration": 25, "exercises": ["Brisk walk", "Jumping jacks"]},
        {"day": "Friday", "focus": "Mobility", "duration": 20, "exercises": ["Hip stretches", "Plank"]},
    ],
    "progressSeed.json": [
        {"date": "2026-09-08", "minutes": 30, "calories": 220},
        {"date": "2026-09-09", "minutes": 25, "calories": 180},
    ],
}


def _read_json(file_name: str):
    data_file = WEBSITE_DATA_DIR / file_name
    if not data_file.exists():
        return DEFAULT_SEED_DATA[file_name]

    with data_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def seed_data() -> None:
    user_seed = _read_json("user.json")
    workouts_seed = _read_json("workouts.json")
    progress_seed = _read_json("progressSeed.json")

    with get_connection() as connection:
        existing_user = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (user_seed["email"],),
        ).fetchone()

        if existing_user:
            user_id = existing_user["id"]
        else:
            cursor = connection.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (user_seed["name"], user_seed["email"], user_seed["password"]),
            )
            user_id = cursor.lastrowid

        existing_workouts = connection.execute(
            "SELECT COUNT(*) AS count FROM workouts WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if existing_workouts and existing_workouts["count"] == 0:
            for workout in workouts_seed:
                connection.execute(
                    """
                    INSERT INTO workouts (user_id, day, focus, duration, exercises_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        workout["day"],
                        workout["focus"],
                        workout["duration"],
                        json.dumps(workout["exercises"]),
                    ),
                )

        existing_progress = connection.execute(
            "SELECT COUNT(*) AS count FROM progress_entries WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if existing_progress and existing_progress["count"] == 0:
            for entry in progress_seed:
                connection.execute(
                    """
                    INSERT INTO progress_entries (user_id, date, minutes, calories)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, entry["date"], entry["minutes"], entry["calories"]),
                )

        existing_goals = connection.execute(
            "SELECT COUNT(*) AS count FROM goals WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if existing_goals and existing_goals["count"] == 0:
            connection.execute(
                """
                INSERT INTO goals (user_id, title, metric, target_value, current_value, deadline, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, "Weekly Active Minutes", "minutes", 180, 0, None, "active"),
            )
