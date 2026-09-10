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
    row_to_student_log,
    row_to_student_profile,
    row_to_vault,
    row_to_workout,
)
from .schemas import (
    GoalPayload,
    LoginPayload,
    LoginResponse,
    ProgressPayload,
    RedeemPenaltyPayload,
    StudentDailyLogPayload,
    StudentDailyLogResponse,
    StudentProfilePayload,
    StudentProfileResponse,
    UserResponse,
    VaultResponse,
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


def _compute_student_targets(age: int, weight_kg: float, height_cm: float, study_hours: float):
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    # Hydration: 35ml/kg + 350ml brain study buffer
    daily_water_target_ml = int(round((weight_kg * 35.0 + 350.0) / 50.0) * 50)

    # Study-friendly workout duration (20 mins prevents fatigue & brain fog)
    daily_workout_target_mins = 20 if study_hours >= 4.0 else 25

    # Mifflin-St Jeor maintenance calories with student sedentary+light activity factor
    bmr = 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age + 5.0
    maintenance_calories = int(bmr * 1.35)

    recommendation = (
        f"For {study_hours}h daily study, keep workouts to {daily_workout_target_mins} mins "
        f"(brisk walking, desk stretching, core mobility) to protect cognitive energy without "
        f"academic fatigue. Drink {daily_water_target_ml}ml water across study breaks to maintain focus and weight."
    )

    return bmi, daily_water_target_ml, daily_workout_target_mins, maintenance_calories, recommendation


def _ensure_vault_exists(connection, user_id: int):
    vault = connection.execute("SELECT * FROM commitment_vault WHERE user_id = ?", (user_id,)).fetchone()
    if not vault:
        connection.execute(
            "INSERT INTO commitment_vault (user_id, wallet_balance, locked_penalty_amount) VALUES (?, 100.0, 0.0)",
            (user_id,),
        )
        vault = connection.execute("SELECT * FROM commitment_vault WHERE user_id = ?", (user_id,)).fetchone()
    return vault



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


@app.get("/api/student/profile", response_model=StudentProfileResponse)
def get_student_profile(user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM student_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    if not row:
        bmi, water_target, workout_target, cal, rec = _compute_student_targets(20, 65.0, 172.0, 6.0)
        return {
            "id": 0,
            "userId": user_id,
            "age": 20,
            "weightKg": 65.0,
            "heightCm": 172.0,
            "studyHoursPerDay": 6.0,
            "dailyWaterTargetMl": water_target,
            "dailyWorkoutTargetMins": workout_target,
            "bmi": bmi,
            "maintenanceCalories": cal,
            "studySafeRecommendation": rec,
        }

    bmi, water_target, workout_target, cal, rec = _compute_student_targets(
        row["age"], row["weight_kg"], row["height_cm"], row["study_hours_per_day"]
    )
    return {
        "id": row["id"],
        "userId": row["user_id"],
        "age": row["age"],
        "weightKg": row["weight_kg"],
        "heightCm": row["height_cm"],
        "studyHoursPerDay": row["study_hours_per_day"],
        "dailyWaterTargetMl": row["daily_water_target_ml"],
        "dailyWorkoutTargetMins": row["daily_workout_target_mins"],
        "bmi": bmi,
        "maintenanceCalories": cal,
        "studySafeRecommendation": rec,
    }


@app.post("/api/student/profile", response_model=StudentProfileResponse)
def set_student_profile(payload: StudentProfilePayload, user_id: int = Depends(_get_current_user_id)):
    bmi, water_target, workout_target, cal, rec = _compute_student_targets(
        payload.age, payload.weightKg, payload.heightCm, payload.studyHoursPerDay
    )

    with get_connection() as connection:
        _ensure_vault_exists(connection, user_id)
        connection.execute(
            """
            INSERT INTO student_profiles (user_id, age, weight_kg, height_cm, study_hours_per_day, daily_water_target_ml, daily_workout_target_mins)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                age = excluded.age,
                weight_kg = excluded.weight_kg,
                height_cm = excluded.height_cm,
                study_hours_per_day = excluded.study_hours_per_day,
                daily_water_target_ml = excluded.daily_water_target_ml,
                daily_workout_target_mins = excluded.daily_workout_target_mins
            """,
            (
                user_id,
                payload.age,
                payload.weightKg,
                payload.heightCm,
                payload.studyHoursPerDay,
                water_target,
                workout_target,
            ),
        )

        row = connection.execute(
            "SELECT * FROM student_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    return {
        "id": row["id"],
        "userId": row["user_id"],
        "age": row["age"],
        "weightKg": row["weight_kg"],
        "heightCm": row["height_cm"],
        "studyHoursPerDay": row["study_hours_per_day"],
        "dailyWaterTargetMl": row["daily_water_target_ml"],
        "dailyWorkoutTargetMins": row["daily_workout_target_mins"],
        "bmi": bmi,
        "maintenanceCalories": cal,
        "studySafeRecommendation": rec,
    }


@app.get("/api/student/vault", response_model=VaultResponse)
def get_vault_status(user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        vault = _ensure_vault_exists(connection, user_id)

    can_redeem = vault["locked_penalty_amount"] >= 20.0
    msg = (
        f"You have ₹{vault['locked_penalty_amount']:.0f} locked in penalty! Complete your study-break workout to refund ₹20 back to your wallet."
        if can_redeem
        else "No penalties locked. Keep up your daily 20-min routine to stay fit without burning out!"
    )

    return {
        "userId": vault["user_id"],
        "walletBalance": vault["wallet_balance"],
        "lockedPenaltyAmount": vault["locked_penalty_amount"],
        "totalPenalized": vault["total_penalized"],
        "totalRefunded": vault["total_refunded"],
        "canRedeem": can_redeem,
        "redemptionMessage": msg,
    }


@app.get("/api/student/logs")
def get_student_logs(user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM student_daily_logs WHERE user_id = ? ORDER BY date DESC LIMIT 30",
            (user_id,),
        ).fetchall()
    return [row_to_student_log(r) for r in rows]


@app.post("/api/student/daily-log", response_model=StudentDailyLogResponse)
def log_student_daily(payload: StudentDailyLogPayload, user_id: int = Depends(_get_current_user_id)):
    with get_connection() as connection:
        _ensure_vault_exists(connection, user_id)
        profile = connection.execute(
            "SELECT daily_workout_target_mins FROM student_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        target_mins = profile["daily_workout_target_mins"] if profile else 20
        status_val = "completed" if payload.workoutMinsCompleted >= target_mins else "pending"

        connection.execute(
            """
            INSERT INTO student_daily_logs (user_id, date, workout_mins_completed, water_ml_completed, status)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                workout_mins_completed = excluded.workout_mins_completed,
                water_ml_completed = excluded.water_ml_completed,
                status = CASE WHEN excluded.workout_mins_completed >= ? THEN 'completed' ELSE student_daily_logs.status END
            """,
            (user_id, payload.date, payload.workoutMinsCompleted, payload.waterMlCompleted, status_val, target_mins),
        )

        row = connection.execute(
            "SELECT * FROM student_daily_logs WHERE user_id = ? AND date = ?",
            (user_id, payload.date),
        ).fetchone()

    return row_to_student_log(row)


@app.post("/api/student/check-daily-penalty")
def check_daily_penalty(date: str, user_id: int = Depends(_get_current_user_id)):
    PENALTY_AMOUNT = 20.0
    with get_connection() as connection:
        vault = _ensure_vault_exists(connection, user_id)
        profile = connection.execute(
            "SELECT daily_workout_target_mins FROM student_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        target_mins = profile["daily_workout_target_mins"] if profile else 20

        log = connection.execute(
            "SELECT * FROM student_daily_logs WHERE user_id = ? AND date = ?",
            (user_id, date),
        ).fetchone()

        workout_done = log["workout_mins_completed"] if log else 0
        already_penalized = (log["penalty_charged"] if log else 0.0) > 0

        if workout_done < target_mins and not already_penalized:
            new_balance = max(0.0, vault["wallet_balance"] - PENALTY_AMOUNT)
            new_locked = vault["locked_penalty_amount"] + PENALTY_AMOUNT
            total_penalized = vault["total_penalized"] + PENALTY_AMOUNT

            connection.execute(
                """
                UPDATE commitment_vault
                SET wallet_balance = ?, locked_penalty_amount = ?, total_penalized = ?
                WHERE user_id = ?
                """,
                (new_balance, new_locked, total_penalized, user_id),
            )

            if log:
                connection.execute(
                    "UPDATE student_daily_logs SET status = 'missed', penalty_charged = ? WHERE id = ?",
                    (PENALTY_AMOUNT, log["id"]),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO student_daily_logs (user_id, date, workout_mins_completed, water_ml_completed, status, penalty_charged)
                    VALUES (?, ?, 0, 0, 'missed', ?)
                    """,
                    (user_id, date, PENALTY_AMOUNT),
                )

            return {
                "penalized": True,
                "amount": PENALTY_AMOUNT,
                "message": f"Daily target of {target_mins} mins missed on {date}. ₹{PENALTY_AMOUNT:.0f} was locked in your Penalty Vault. Complete a makeup workout to get it refunded!",
                "lockedPenalty": new_locked,
                "walletBalance": new_balance,
            }

        return {
            "penalized": False,
            "message": "Workout target completed or penalty already processed.",
            "lockedPenalty": vault["locked_penalty_amount"],
            "walletBalance": vault["wallet_balance"],
        }


@app.post("/api/student/redeem-penalty")
def redeem_penalty(payload: RedeemPenaltyPayload, user_id: int = Depends(_get_current_user_id)):
    REFUND_AMOUNT = 20.0
    with get_connection() as connection:
        vault = _ensure_vault_exists(connection, user_id)

        if vault["locked_penalty_amount"] < REFUND_AMOUNT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No locked penalties available to refund.",
            )

        new_balance = vault["wallet_balance"] + REFUND_AMOUNT
        new_locked = vault["locked_penalty_amount"] - REFUND_AMOUNT
        total_refunded = vault["total_refunded"] + REFUND_AMOUNT

        connection.execute(
            """
            UPDATE commitment_vault
            SET wallet_balance = ?, locked_penalty_amount = ?, total_refunded = ?
            WHERE user_id = ?
            """,
            (new_balance, new_locked, total_refunded, user_id),
        )

        connection.execute(
            """
            INSERT INTO student_daily_logs (user_id, date, workout_mins_completed, water_ml_completed, status, refunded)
            VALUES (?, ?, ?, 0, 'redeemed', ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                workout_mins_completed = student_daily_logs.workout_mins_completed + excluded.workout_mins_completed,
                status = 'redeemed',
                refunded = excluded.refunded
            """,
            (user_id, payload.date, payload.extraWorkoutMins, REFUND_AMOUNT),
        )

    return {
        "refunded": True,
        "refundAmount": REFUND_AMOUNT,
        "message": f"Great job! Makeup workout completed. ₹{REFUND_AMOUNT:.0f} has been refunded back to your wallet.",
        "walletBalance": new_balance,
        "lockedPenaltyAmount": new_locked,
    }

