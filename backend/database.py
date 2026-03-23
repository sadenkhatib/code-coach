import sqlite3
import os
import json
from datetime import datetime

# Allow the DB path to be overridden via environment variable.
# On cloud platforms set DB_PATH to a writable persistent-disk location.
DB_PATH = os.environ.get(
    'DB_PATH',
    os.path.join(os.path.dirname(__file__), 'data', 'workouts.db')
)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the workout_logs table if it does not exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT    NOT NULL,
            goal          TEXT    NOT NULL,
            weight_lbs    REAL    NOT NULL DEFAULT 0,
            sets_completed INTEGER NOT NULL,
            reps_completed TEXT   NOT NULL,
            logged_at     TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_session(exercise_name, goal, weight_lbs, sets_completed, reps_completed):
    """Insert one exercise's performance into the log."""
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO workout_logs
            (exercise_name, goal, weight_lbs, sets_completed, reps_completed, logged_at)
        VALUES (?, ?, ?, ?, ?, ?)
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
    conn.commit()
    conn.close()


def get_exercise_history(exercise_name, limit=30):
    """Return the most recent sessions for a given exercise, newest first."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, exercise_name, goal, weight_lbs, sets_completed, reps_completed, logged_at
        FROM workout_logs
        WHERE exercise_name = ?
        ORDER BY logged_at DESC
        LIMIT ?
        """,
        (exercise_name, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_last_session(exercise_name):
    """Return the single most recent session for a given exercise, or None."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, exercise_name, goal, weight_lbs, sets_completed, reps_completed, logged_at
        FROM workout_logs
        WHERE exercise_name = ?
        ORDER BY logged_at DESC
        LIMIT 1
        """,
        (exercise_name,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_logged_exercises():
    """Return a sorted list of all distinct exercise names that have been logged."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT exercise_name FROM workout_logs ORDER BY exercise_name"
    ).fetchall()
    conn.close()
    return [r["exercise_name"] for r in rows]