import { useState, useEffect } from 'react';
import { logSession, getSuggestion } from '../api/workoutApi';

/**
 * WorkoutLogger
 *
 * Renders a logging form for each exercise in a workout day.
 * For each exercise it:
 *   - Fetches and shows the progressive overload suggestion from the last session
 *   - Accepts weight (lbs), sets completed, and reps per set
 *
 * Props:
 *   exercises  {Array}    [{exercise, sets, reps}, ...]
 *   goal       {string}   e.g. "hypertrophy"
 *   onComplete {Function} called after a successful save
 *   onCancel   {Function} called when the user hits "Back"
 */
export default function WorkoutLogger({ exercises, goal, onComplete, onCancel }) {
  const [logs, setLogs] = useState(() =>
    exercises.map((ex) => ({
      exerciseName: ex.exercise,
      targetSets: ex.sets,
      targetReps: ex.reps,
      weight_lbs: '',
      sets_completed: ex.sets,
      reps_completed: Array(ex.sets).fill(''),
    }))
  );
  const [suggestions, setSuggestions] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);

  // Fetch progression suggestions for every exercise on mount
  useEffect(() => {
    exercises.forEach(async (ex) => {
      try {
        const sugg = await getSuggestion(ex.exercise);
        setSuggestions((prev) => ({ ...prev, [ex.exercise]: sugg }));
      } catch {
        // non-critical — ignore network errors for suggestions
      }
    });
  }, [exercises]);

  function updateField(index, field, value) {
    setLogs((prev) => {
      const next = [...prev];
      if (field === 'sets_completed') {
        const n = Math.max(0, parseInt(value) || 0);
        next[index] = {
          ...next[index],
          sets_completed: n,
          reps_completed: Array(n)
            .fill('')
            .map((_, i) => next[index].reps_completed[i] ?? ''),
        };
      } else {
        next[index] = { ...next[index], [field]: value };
      }
      return next;
    });
  }

  function updateRep(logIndex, setIndex, value) {
    setLogs((prev) => {
      const next = [...prev];
      const reps = [...next[logIndex].reps_completed];
      reps[setIndex] = value;
      next[logIndex] = { ...next[logIndex], reps_completed: reps };
      return next;
    });
  }

  async function handleSubmit() {
    setError(null);
    const toLog = logs
      .filter((l) => l.weight_lbs !== '' && l.sets_completed > 0)
      .map((l) => ({
        exercise_name: l.exerciseName,
        weight_lbs: parseFloat(l.weight_lbs) || 0,
        sets_completed: l.sets_completed,
        reps_completed: l.reps_completed.map((r) => parseInt(r) || 0),
      }));

    if (toLog.length === 0) {
      setError('Enter weight and reps for at least one exercise.');
      return;
    }

    setLoading(true);
    try {
      await logSession(goal, toLog);
      setSaved(true);
      setTimeout(onComplete, 1200);
    } catch (e) {
      setError(e.message || 'Failed to save session.');
    } finally {
      setLoading(false);
    }
  }

  if (saved) {
    return <p className="logger-success">Session saved! Redirecting to Progress…</p>;
  }

  return (
    <div className="logger">
      <div className="logger-header">
        <button className="btn-ghost" onClick={onCancel}>← Back</button>
        <h2>Log Workout Session</h2>
        <p className="logger-goal-label">Goal: <strong>{goal}</strong></p>
      </div>

      {logs.map((log, i) => {
        const sugg = suggestions[log.exerciseName];
        const hasHistory = sugg && sugg.action !== 'first_session';

        return (
          <div key={i} className="log-entry">
            <div className="log-entry-header">
              <span className="log-exercise-name">{log.exerciseName}</span>
              <span className="log-target">
                Target: {log.targetSets} × {log.targetReps}
              </span>
            </div>

            {hasHistory && (
              <div className={`suggestion-chip suggestion-${sugg.action}`}>
                <span className="suggestion-weight">
                  {sugg.suggested_weight} lbs
                </span>
                <span className="suggestion-msg">{sugg.message}</span>
              </div>
            )}

            {sugg && sugg.action === 'first_session' && (
              <div className="suggestion-chip suggestion-first">
                {sugg.message}
              </div>
            )}

            <div className="log-inputs">
              <label className="log-label">
                Weight (lbs)
                <input
                  type="number"
                  min="0"
                  step="2.5"
                  value={log.weight_lbs}
                  onChange={(e) => updateField(i, 'weight_lbs', e.target.value)}
                  placeholder={hasHistory ? String(sugg.suggested_weight) : '0'}
                  className="log-input"
                />
              </label>
              <label className="log-label">
                Sets Completed
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={log.sets_completed}
                  onChange={(e) => updateField(i, 'sets_completed', e.target.value)}
                  className="log-input"
                />
              </label>
            </div>

            {log.sets_completed > 0 && (
              <div className="reps-inputs">
                {Array.from({ length: log.sets_completed }).map((_, si) => (
                  <label key={si} className="rep-label">
                    Set {si + 1}
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={log.reps_completed[si] ?? ''}
                      onChange={(e) => updateRep(i, si, e.target.value)}
                      placeholder={log.targetReps.split('–')[0]}
                      className="rep-input"
                    />
                  </label>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {error && <p className="error">{error}</p>}

      <button
        className="btn-primary btn-full"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? 'Saving…' : 'Save Session'}
      </button>
    </div>
  );
}