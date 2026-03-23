"""
progression.py — Progressive Overload Calculation Module

Encapsulates the rules for suggesting weight / rep changes between sessions.
Kept isolated so the logic is easy to explain, test, and tweak independently
of the rest of the application.

Core rule:
  PROGRESS  — user completed every set at or above the top of their target
               rep range → add WEIGHT_INCREMENT_LBS next session.
  MAINTAIN  — user completed every set within the target rep range, but
               at least one set fell below the ceiling → keep weight, aim
               for the top of the range next time.
  DELOAD    — user failed to complete at least one set at the floor of the
               target rep range → drop WEIGHT_INCREMENT_LBS.
"""

import json

WEIGHT_INCREMENT_LBS = 5.0   # standard small-plate jump

# (min_reps, max_reps) per training goal
REP_RANGES = {
    "hypertrophy": (8, 10),
    "strength":    (3, 6),
    "fat loss":    (6, 10),
}


def _parse_reps(reps_completed):
    """Accept a JSON string or a plain Python list; always return a list of ints."""
    if isinstance(reps_completed, str):
        return json.loads(reps_completed)
    return list(reps_completed)


def evaluate_performance(reps_per_set, rep_min, rep_max):
    """
    Classify the session as 'progress', 'maintain', or 'deload'.

    Args:
        reps_per_set (list[int]): actual reps logged for each set.
        rep_min (int): floor of the target rep range.
        rep_max (int): ceiling of the target rep range.

    Returns:
        str: one of 'progress', 'maintain', 'deload'.
    """
    if not reps_per_set:
        return "maintain"

    all_hit_ceiling = all(r >= rep_max for r in reps_per_set)
    all_in_range    = all(r >= rep_min  for r in reps_per_set)

    if all_hit_ceiling:
        return "progress"
    elif all_in_range:
        return "maintain"
    else:
        return "deload"


def suggest_progression(last_session):
    """
    Return a progression suggestion based on the last logged session.

    Args:
        last_session (dict | None): row from the database, or None if no
            history exists yet. Expected keys: exercise_name, goal,
            weight_lbs, sets_completed, reps_completed, logged_at.

    Returns:
        dict with keys:
            suggested_weight (float | None)
            suggested_reps   (str | None)    e.g. "8–10"
            action           (str)           'first_session' | 'progress' | 'maintain' | 'deload'
            message          (str)           human-readable coaching note
    """
    if last_session is None:
        return {
            "suggested_weight": None,
            "suggested_reps":   None,
            "action":           "first_session",
            "message":          "No previous data logged. Start with a comfortable weight and record it.",
        }

    goal       = last_session["goal"].lower().strip()
    weight     = float(last_session["weight_lbs"])
    reps_list  = _parse_reps(last_session["reps_completed"])

    rep_min, rep_max = REP_RANGES.get(goal, (8, 10))
    action = evaluate_performance(reps_list, rep_min, rep_max)

    if action == "progress":
        new_weight = weight + WEIGHT_INCREMENT_LBS
        message = (
            f"Great work — you hit {rep_max}+ reps on every set! "
            f"Add {int(WEIGHT_INCREMENT_LBS)} lbs this session."
        )
    elif action == "maintain":
        new_weight = weight
        message = (
            f"Solid session. Stay at this weight and push to hit "
            f"{rep_max} reps on every set before adding load."
        )
    else:  # deload
        new_weight = max(0.0, weight - WEIGHT_INCREMENT_LBS)
        message = (
            f"You fell below {rep_min} reps on at least one set. "
            f"Drop {int(WEIGHT_INCREMENT_LBS)} lbs and focus on clean form."
        )

    return {
        "suggested_weight": new_weight,
        "suggested_reps":   f"{rep_min}\u2013{rep_max}",
        "action":           action,
        "message":          message,
    }
