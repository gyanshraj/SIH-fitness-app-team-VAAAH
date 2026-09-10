from __future__ import annotations

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "fitness.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                focus TEXT NOT NULL,
                duration INTEGER NOT NULL,
                exercises_json TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS progress_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                minutes INTEGER NOT NULL,
                calories INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                metric TEXT NOT NULL,
                target_value INTEGER NOT NULL,
                current_value INTEGER NOT NULL DEFAULT 0,
                deadline TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )


def row_to_workout(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "day": row["day"],
        "focus": row["focus"],
        "duration": row["duration"],
        "exercises": json.loads(row["exercises_json"]),
    }


def row_to_progress(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "date": row["date"],
        "minutes": row["minutes"],
        "calories": row["calories"],
    }


def row_to_goal(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "metric": row["metric"],
        "targetValue": row["target_value"],
        "currentValue": row["current_value"],
        "deadline": row["deadline"],
        "status": row["status"],
    }
