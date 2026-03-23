"""
Progressive overload suggestion engine.

Kept as its own module so the logic is easy to explain, test, and tweak
independently of the rest of the application.

How it works
------------
After every logged session the user's reps-per-set are compared against the
target rep range for their training goal.  Three outcomes are possible:

  PROGRESS  — every set hit the TOP of the target range
               → add weight next session (goal-specific increment)

  MAINTAIN  — every set was within range but at least one missed the ceiling
               → keep the same weight and aim for the top of the range

  DELOAD    — at least one set fell BELOW the bottom of the range
               → drop one increment and rebuild

Training goals and their parameters
------------------------------------
  Strength    : 3–5 reps  |  +5 lb jumps  (classic linear progression)
  Hypertrophy : 8–12 reps |  +2.5 lb jumps (double-progression style)
  Fat Loss    : 12–15 reps |  +2.5 lb jumps (metabolic, keep moving)
"""

import json

# (rep_min, rep_max, weight_increment_lbs)
GOAL_PARAMS = {
    "strength":    (3,  5,  5.0),
    "hypertrophy": (8,  12, 2.5),
    "fat loss":    (12, 15, 2.5),
}

# Fallback if goal string is unrecognised
_DEFAULT_PARAMS = (8, 12, 2.5)


def _parse_reps(reps_completed):
    """Accept a JSON string or a plain Python list; always return a list of ints."""
    if isinstance(reps_completed, str):
        return json.loads(reps_completed)
    return list(reps_completed)


def evaluate_performance(reps_per_set, rep_min, rep_max):
    """
    Classify the session outcome.

    Returns one of: 'progress', 'maintain', 'deload'
    """
    if not reps_per_set:
        return "maintain"

    all_hit_ceiling = all(r >= rep_max for r in reps_per_set)
    all_in_range    = all(r >= rep_min for r in reps_per_set)

    if all_hit_ceiling:
        return "progress"
    elif all_in_range:
        return "maintain"
    else:
        return "deload"


def suggest_progression(last_session):
    """
    Return a progression suggestion dict based on the last logged session.

    Keys returned
    -------------
    suggested_weight : float | None
    suggested_reps   : str   | None   e.g. "8–12"
    action           : str            'progress' | 'maintain' | 'deload' | 'first_session'
    message          : str
    """
    if last_session is None:
        return {
            "suggested_weight": None,
            "suggested_reps":   None,
            "action":           "first_session",
            "message":          "No previous data logged. Start with a comfortable weight and record it.",
        }

    goal      = last_session["goal"].lower().strip()
    weight    = float(last_session["weight_lbs"])
    reps_list = _parse_reps(last_session["reps_completed"])

    rep_min, rep_max, increment = GOAL_PARAMS.get(goal, _DEFAULT_PARAMS)
    action = evaluate_performance(reps_list, rep_min, rep_max)

    if action == "progress":
        new_weight = weight + increment
        message = (
            f"You hit {rep_max}+ reps on every set — great work! "
            f"Add {increment} lbs this session."
        )
    elif action == "maintain":
        new_weight = weight
        message = (
            f"Solid session. Keep this weight and push to get {rep_max} reps "
            f"on every set before adding load."
        )
    else:  # deload
        new_weight = max(0.0, weight - increment)
        message = (
            f"You fell below {rep_min} reps on at least one set. "
            f"Drop {increment} lbs and focus on clean form before progressing."
        )

    return {
        "suggested_weight": new_weight,
        "suggested_reps":   f"{rep_min}\u2013{rep_max}",
        "action":           action,
        "message":          message,
    }
