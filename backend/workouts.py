import random
import json

def generate_plan(goal, days):
    with open('data/exercises.json') as f:
        all_exercises = json.load(f)

    split_patterns = {
        1: ["full"],
        2: ["upper", "lower"],
        3: ["push", "pull", "legs"],
        4: ["upper", "lower", "upper", "lower"],
        5: ["push", "pull", "legs", "upper", "lower"],
        6: ["push", "pull", "legs", "push", "pull", "legs"]
    }

    plan = []
    split_order = split_patterns.get(days, ["push", "pull", "legs"] * (days // 3 + 1))[:days]

    for i in range(days):
        focus = split_order[i]
        daily_exercises = []

        # 1 day special case
        if days == 1:
            for muscle in ["chest", "back", "shoulders", "legs"]:
                muscle_data = all_exercises[muscle]
                compound = muscle_data.get("compound", [])
                selected = random.sample(compound, min(1, len(compound)))
                daily_exercises += build_exercise_entries(selected, muscle.title(), goal)

            biceps = all_exercises["arms"]["biceps"]
            daily_exercises += build_exercise_entries(random.sample(biceps, 1), "Biceps", goal)

            triceps = all_exercises["arms"]["triceps"]
            daily_exercises += build_exercise_entries(random.sample(triceps, 1), "Triceps", goal)

        elif focus == "upper":
            daily_exercises += build_from_comp_iso(all_exercises["chest"], 1, 1, goal, "Chest")
            daily_exercises += build_from_comp_iso(all_exercises["back"], 1, 1, goal, "Back")
            daily_exercises += build_from_comp_iso(all_exercises["shoulders"], 1, 1, goal, "Shoulders")
            biceps = all_exercises["arms"]["biceps"]
            daily_exercises += build_exercise_entries(random.sample(biceps, 1), "Biceps", goal)
            triceps = all_exercises["arms"]["triceps"]
            daily_exercises += build_exercise_entries(random.sample(triceps, 1), "Triceps", goal)

        elif focus == "lower":
            daily_exercises += build_from_comp_iso(all_exercises["legs"], 2, 2, goal, "Legs")

        elif focus == "push":
            daily_exercises += build_from_comp_iso(all_exercises["chest"], 2, 1, goal, "Chest")
            daily_exercises += build_from_comp_iso(all_exercises["shoulders"], 1, 1, goal, "Shoulders")
            triceps = all_exercises["arms"]["triceps"]
            daily_exercises += build_exercise_entries(random.sample(triceps, 2), "Triceps", goal)

        elif focus == "pull":
            daily_exercises += build_from_comp_iso(all_exercises["back"], 3, 1, goal, "Back")
            biceps = all_exercises["arms"]["biceps"]
            daily_exercises += build_exercise_entries(random.sample(biceps, 2), "Biceps", goal)

        elif focus == "legs":
            daily_exercises += build_from_comp_iso(all_exercises["legs"], 2, 2, goal, "Legs")

        core_exercises = all_exercises.get("core", {}).get("general", [])
        if core_exercises:
            daily_exercises.append({
                "exercise": f"{random.choice(core_exercises)} (Core)",
                "muscle": "Core",
                "sets": 3,
                "reps": "10–15"
            })

        plan.append({
            "day": f"Day {i+1}",
            "focus": focus.title(),
            "exercises": daily_exercises
        })

    goal = goal.lower()
    note = "Train to failure within rep range. "
    if goal == "fat loss":
        note += "Do cardio daily. Stretch as needed. Be in a caloric deficit while prioritizing protein and track your weight weekly 6-10 rep range with compounds in the lower half and isolations in the upper half."
    elif goal == "hypertrophy":
        note += "Do light cardio a few times a week. Limit high-intensity cardio to 1–2x/week. Eat in a small surplus if you wannt to bulk, otherwise eat at maintenance and most importantly prioritize protein."
    elif goal == "strength":
        note += "Lift as heavy as possible while maintaining good form. Protein for recovery and carbs for energy"
    
    return {"plan": plan, "goal": goal, "note": note}


def build_exercise_entries(exercises, muscle, goal):
    result = []
    for ex in exercises:
        if goal.lower() == "hypertrophy":
            sets, reps = 3, "8–10"
        elif goal.lower() == "strength":
            sets, reps = 2, "3–6"
        elif goal.lower() == "fat loss":
            # Compounds: slightly lower reps, isolations: higher
                sets, reps = 2, "6–10"
                
        result.append({
            "exercise": f"{ex} ({muscle})",
            "sets": sets,
            "reps": reps
        })
    return result

def build_from_comp_iso(muscle_data, comp_count, iso_count, goal, muscle_name):
    compound = muscle_data.get("compound", [])
    isolation = muscle_data.get("isolation", [])
    selected = random.sample(compound, min(comp_count, len(compound))) + \
               random.sample(isolation, min(iso_count, len(isolation)))
    return build_exercise_entries(selected, muscle_name, goal)
