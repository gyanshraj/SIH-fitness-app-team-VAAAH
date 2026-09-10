from __future__ import annotations

import json
from pathlib import Path

from .database import get_connection

ROOT_DIR = Path(__file__).resolve().parents[2]
WEBSITE_DATA_DIR = ROOT_DIR / "website" / "src" / "data"


def _read_json(file_name: str):
    with (WEBSITE_DATA_DIR / file_name).open("r", encoding="utf-8") as file:
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
