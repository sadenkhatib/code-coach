const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5050';

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Server ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

export function getWorkoutPlan(goal, days) {
  return apiFetch('/generate-plan', {
    method: 'POST',
    body: JSON.stringify({ goal, days }),
  });
}

/**
 * Log one workout session.
 * @param {string} goal  - e.g. "hypertrophy"
 * @param {Array}  exercises - [{exercise_name, weight_lbs, sets_completed, reps_completed}]
 */
export function logSession(goal, exercises) {
  return apiFetch('/log-session', {
    method: 'POST',
    body: JSON.stringify({ goal, exercises }),
  });
}

/**
 * Get logged history for a specific exercise name.
 * @param {string} exerciseName
 */
export function getHistory(exerciseName) {
  return apiFetch(`/history?exercise=${encodeURIComponent(exerciseName)}`);
}

/**
 * Get progressive overload suggestion for a specific exercise.
 * @param {string} exerciseName
 */
export function getSuggestion(exerciseName) {
  return apiFetch(`/suggest/${encodeURIComponent(exerciseName)}`);
}

/**
 * Get all exercise names that have been logged at least once.
 */
export function getLoggedExercises() {
  return apiFetch('/exercises-logged');
}

/**
 * Wipe all logged progress from the database.
 */
export function resetProgress() {
  return apiFetch('/reset-progress', { method: 'DELETE' });
}