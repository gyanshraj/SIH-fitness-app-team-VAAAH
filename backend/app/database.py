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

            CREATE TABLE IF NOT EXISTS student_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                age INTEGER NOT NULL,
                weight_kg REAL NOT NULL,
                height_cm REAL NOT NULL,
                study_hours_per_day REAL NOT NULL,
                daily_water_target_ml INTEGER NOT NULL,
                daily_workout_target_mins INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS commitment_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                wallet_balance REAL NOT NULL DEFAULT 100.0,
                locked_penalty_amount REAL NOT NULL DEFAULT 0.0,
                total_penalized REAL NOT NULL DEFAULT 0.0,
                total_refunded REAL NOT NULL DEFAULT 0.0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS student_daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                workout_mins_completed INTEGER NOT NULL DEFAULT 0,
                water_ml_completed INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                penalty_charged REAL NOT NULL DEFAULT 0.0,
                refunded REAL NOT NULL DEFAULT 0.0,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
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


def row_to_student_profile(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "userId": row["user_id"],
        "age": row["age"],
        "weightKg": row["weight_kg"],
        "heightCm": row["height_cm"],
        "studyHoursPerDay": row["study_hours_per_day"],
        "dailyWaterTargetMl": row["daily_water_target_ml"],
        "dailyWorkoutTargetMins": row["daily_workout_target_mins"],
    }


def row_to_vault(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "userId": row["user_id"],
        "walletBalance": row["wallet_balance"],
        "lockedPenaltyAmount": row["locked_penalty_amount"],
        "totalPenalized": row["total_penalized"],
        "totalRefunded": row["total_refunded"],
    }


def row_to_student_log(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "userId": row["user_id"],
        "date": row["date"],
        "workoutMinsCompleted": row["workout_mins_completed"],
        "waterMlCompleted": row["water_ml_completed"],
        "status": row["status"],
        "penaltyCharged": row["penalty_charged"],
        "refunded": row["refunded"],
    }

