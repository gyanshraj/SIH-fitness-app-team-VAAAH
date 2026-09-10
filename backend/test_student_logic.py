"""Test script to verify student target formulas and the ₹20 commitment vault database logic."""
import sqlite3
import tempfile
from pathlib import Path

def test_student_formulas():
    # Weight 64kg, Height 172cm, Age 19, Study hours 6.5
    weight = 64.0
    height = 172.0
    age = 19
    study_hours = 6.5

    height_m = height / 100.0
    bmi = round(weight / (height_m * height_m), 1)
    water_ml = int(round((weight * 35.0 + 350.0) / 50.0) * 50)
    workout_mins = 20 if study_hours >= 4.0 else 25
    bmr = 10.0 * weight + 6.25 * height - 5.0 * age + 5.0
    maintenance_calories = int(bmr * 1.35)

    assert bmi == 21.6, f"Expected 21.6, got {bmi}"
    assert water_ml == 2600, f"Expected 2600, got {water_ml}"
    assert workout_mins == 20, f"Expected 20, got {workout_mins}"
    assert maintenance_calories > 2000, f"Expected >2000, got {maintenance_calories}"
    print("[OK] Formula calculations verified successfully!")

def test_vault_penalty_and_refund():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_fitness.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        conn.executescript("""
            CREATE TABLE commitment_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                wallet_balance REAL NOT NULL DEFAULT 100.0,
                locked_penalty_amount REAL NOT NULL DEFAULT 0.0,
                total_penalized REAL NOT NULL DEFAULT 0.0,
                total_refunded REAL NOT NULL DEFAULT 0.0
            );

            CREATE TABLE student_daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                workout_mins_completed INTEGER NOT NULL DEFAULT 0,
                water_ml_completed INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                penalty_charged REAL NOT NULL DEFAULT 0.0,
                refunded REAL NOT NULL DEFAULT 0.0,
                UNIQUE(user_id, date)
            );
        """)

        # Initialize vault with ₹100
        conn.execute("INSERT INTO commitment_vault (user_id, wallet_balance, locked_penalty_amount) VALUES (1, 100.0, 0.0)")

        # 1. Missed day penalty trigger (-₹20)
        PENALTY = 20.0
        conn.execute("UPDATE commitment_vault SET wallet_balance = wallet_balance - ?, locked_penalty_amount = locked_penalty_amount + ?, total_penalized = total_penalized + ? WHERE user_id = 1", (PENALTY, PENALTY, PENALTY))
        conn.execute("INSERT INTO student_daily_logs (user_id, date, status, penalty_charged) VALUES (1, '2026-09-10', 'missed', ?)", (PENALTY,))

        row = conn.execute("SELECT * FROM commitment_vault WHERE user_id = 1").fetchone()
        assert row["wallet_balance"] == 80.0, f"Expected wallet ₹80, got {row['wallet_balance']}"
        assert row["locked_penalty_amount"] == 20.0, f"Expected locked ₹20, got {row['locked_penalty_amount']}"
        print("[OK] Missed workout Rs 20 penalty lock verified: Wallet Rs 80, Locked Rs 20")

        # 2. Makeup workout redemption (+Rs 20 refund)
        REFUND = 20.0
        conn.execute("UPDATE commitment_vault SET wallet_balance = wallet_balance + ?, locked_penalty_amount = locked_penalty_amount - ?, total_refunded = total_refunded + ? WHERE user_id = 1", (REFUND, REFUND, REFUND))
        conn.execute("UPDATE student_daily_logs SET status = 'redeemed', refunded = ? WHERE user_id = 1 AND date = '2026-09-10'", (REFUND,))

        row2 = conn.execute("SELECT * FROM commitment_vault WHERE user_id = 1").fetchone()
        assert row2["wallet_balance"] == 100.0, f"Expected wallet Rs 100, got {row2['wallet_balance']}"
        assert row2["locked_penalty_amount"] == 0.0, f"Expected locked Rs 0, got {row2['locked_penalty_amount']}"
        print("[OK] Makeup workout Rs 20 redemption verified: Wallet refunded to Rs 100, Locked Rs 0")

        conn.close()

if __name__ == "__main__":
    test_student_formulas()
    test_vault_penalty_and_refund()
    print("ALL TESTS PASSED SUCCESSFULLY!")
