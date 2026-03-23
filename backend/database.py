import os
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Set DATABASE_URL in your environment (Supabase provides this under
# Project Settings → Database → Connection string → URI).
DATABASE_URL = os.environ.get('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """Create the workout_logs table if it does not exist."""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS workout_logs (
                    id             SERIAL PRIMARY KEY,
                    exercise_name  TEXT    NOT NULL,
                    goal           TEXT    NOT NULL,
                    weight_lbs     REAL    NOT NULL DEFAULT 0,
                    sets_completed INTEGER NOT NULL,
                    reps_completed TEXT    NOT NULL,
                    logged_at      TEXT    NOT NULL
                )
            """)
    conn.close()


def log_session(exercise_name, goal, weight_lbs, sets_completed, reps_completed):
    """Insert one exercise's performance into the log."""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO workout_logs
                    (exercise_name, goal, weight_lbs, sets_completed, reps_completed, logged_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    exercise_name,
                    goal,
                    float(weight_lbs),
                    int(sets_completed),
                    json.dumps(reps_completed),
                    datetime.utcnow().isoformat(),
                ),
            )
    conn.close()


def get_exercise_history(exercise_name, limit=30):
    """Return the most recent sessions for a given exercise, newest first."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, exercise_name, goal, weight_lbs, sets_completed, reps_completed, logged_at
            FROM workout_logs
            WHERE exercise_name = %s
            ORDER BY logged_at DESC
            LIMIT %s
            """,
            (exercise_name, limit),
        )
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_last_session(exercise_name):
    """Return the single most recent session for a given exercise, or None."""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, exercise_name, goal, weight_lbs, sets_completed, reps_completed, logged_at
                FROM workout_logs
                WHERE exercise_name = %s
                ORDER BY logged_at DESC
                LIMIT 1
                """,
                (exercise_name,),
            )
            row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_logged_exercises():
    """Return a sorted list of all distinct exercise names that have been logged."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT exercise_name FROM workout_logs ORDER BY exercise_name"
        )
        rows = cur.fetchall()
    conn.close()
    return [r["exercise_name"] for r in rows]


def reset_all_logs():
    """Delete every row in workout_logs — wipes all progress history."""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM workout_logs")
    conn.close()
