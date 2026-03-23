import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from workouts import generate_plan
from database import (
    init_db,
    log_session,
    get_exercise_history,
    get_last_session,
    get_all_logged_exercises,
    reset_all_logs,
)
from progression import suggest_progression

app = Flask(__name__)

_origin = os.environ.get('FRONTEND_ORIGIN', 'http://localhost:5173')
CORS(app, origins=[_origin])

init_db()


@app.route('/generate-plan', methods=['POST'])
def generate_workout():
    data = request.get_json()
    goal = data.get('goal')
    days = data.get('days')

    if not goal or not days:
        return jsonify({"error": "Missing goal or days"}), 400

    try:
        result = generate_plan(goal, int(days))
        return jsonify(result)
    except Exception as e:
        print(f"ERROR in generate_plan(): {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/log-session', methods=['POST'])
def log_workout_session():
    """
    Log actual performance for one or more exercises after a workout.

    Request body:
    {
        "goal": "hypertrophy",
        "exercises": [
            {
                "exercise_name": "Barbell Bench Press (Chest)",
                "weight_lbs": 135,
                "sets_completed": 3,
                "reps_completed": [10, 9, 8]
            },
            ...
        ]
    }
    """
    data = request.get_json()
    goal      = data.get('goal')
    exercises = data.get('exercises', [])

    if not goal or not exercises:
        return jsonify({"error": "Missing goal or exercises"}), 400

    try:
        for ex in exercises:
            log_session(
                exercise_name  = ex['exercise_name'],
                goal           = goal,
                weight_lbs     = float(ex.get('weight_lbs', 0)),
                sets_completed = int(ex['sets_completed']),
                reps_completed = ex['reps_completed'],
            )
        return jsonify({"status": "ok", "logged": len(exercises)})
    except Exception as e:
        print(f"ERROR in log_workout_session(): {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/history', methods=['GET'])
def exercise_history():
    """
    GET /history?exercise=<name>
    Returns up to 30 logged sessions for the specified exercise (newest first).
    """
    exercise_name = request.args.get('exercise')
    if not exercise_name:
        return jsonify({"error": "Missing 'exercise' query parameter"}), 400

    try:
        history = get_exercise_history(exercise_name)
        return jsonify({"exercise": exercise_name, "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/exercises-logged', methods=['GET'])
def exercises_logged():
    """Returns all distinct exercise names that have been logged at least once."""
    try:
        names = get_all_logged_exercises()
        return jsonify({"exercises": names})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/suggest/<path:exercise_name>', methods=['GET'])
def suggest(exercise_name):
    """
    GET /suggest/<exercise_name>
    Runs the progression module against the last logged session and returns
    a weight / rep suggestion for the next session.
    """
    try:
        last       = get_last_session(exercise_name)
        suggestion = suggest_progression(last)
        return jsonify({"exercise": exercise_name, **suggestion})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reset-progress', methods=['DELETE'])
def reset_progress():
    """Delete all workout logs — used by the Reset Progress button in the UI."""
    try:
        reset_all_logs()
        return jsonify({"status": "ok", "message": "All progress cleared."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=int(os.environ.get('PORT', 5050)))
