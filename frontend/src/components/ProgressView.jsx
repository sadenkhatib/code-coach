import { useState, useEffect } from 'react';
import { getLoggedExercises, getHistory, getSuggestion } from '../api/workoutApi';

/**
 * ProgressView
 *
 * Lets the user pick a logged exercise and see:
 *   - Their full session history (newest first) in a table
 *   - The progression suggestion for their next session
 */
export default function ProgressView() {
  const [exercises, setExercises]   = useState([]);
  const [selected, setSelected]     = useState('');
  const [history, setHistory]       = useState([]);
  const [suggestion, setSuggestion] = useState(null);
  const [loading, setLoading]       = useState(false);
  const [listLoading, setListLoading] = useState(true);

  // Load distinct exercise names on mount
  useEffect(() => {
    getLoggedExercises()
      .then((data) => setExercises(data.exercises || []))
      .catch(() => {})
      .finally(() => setListLoading(false));
  }, []);

  // Load history + suggestion whenever the selected exercise changes
  useEffect(() => {
    if (!selected) return;
    setLoading(true);
    Promise.all([getHistory(selected), getSuggestion(selected)])
      .then(([histData, suggData]) => {
        setHistory(histData.history || []);
        setSuggestion(suggData);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [selected]);

  function formatDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  function parseReps(repsJson) {
    try {
      const arr = typeof repsJson === 'string' ? JSON.parse(repsJson) : repsJson;
      return arr.join(', ');
    } catch {
      return repsJson;
    }
  }

  function avgReps(repsJson) {
    try {
      const arr = typeof repsJson === 'string' ? JSON.parse(repsJson) : repsJson;
      if (!arr.length) return '—';
      return (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1);
    } catch {
      return '—';
    }
  }

  return (
    <div className="progress-view">
      <h2>Exercise Progress</h2>

      {listLoading && <p className="muted">Loading logged exercises…</p>}

      {!listLoading && exercises.length === 0 && (
        <p className="muted">
          No sessions logged yet. Generate a plan, then use "Log This Day" to record your lifts.
        </p>
      )}

      {exercises.length > 0 && (
        <div className="progress-select-row">
          <label className="progress-label">
            Exercise
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className="progress-select"
            >
              <option value="">— choose an exercise —</option>
              {exercises.map((name) => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          </label>
        </div>
      )}

      {loading && <p className="muted">Loading…</p>}

      {suggestion && !loading && (
        <div className={`suggestion-chip suggestion-${suggestion.action} suggestion-lg`}>
          <div className="suggestion-header">
            Next Session Suggestion
          </div>
          {suggestion.action !== 'first_session' ? (
            <>
              <div className="suggestion-weight-lg">{suggestion.suggested_weight} lbs</div>
              <div className="suggestion-reps-lg">{suggestion.suggested_reps} reps</div>
            </>
          ) : null}
          <div className="suggestion-msg">{suggestion.message}</div>
        </div>
      )}

      {history.length > 0 && !loading && (
        <div className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Goal</th>
                <th>Weight (lbs)</th>
                <th>Sets</th>
                <th>Reps per Set</th>
                <th>Avg Reps</th>
              </tr>
            </thead>
            <tbody>
              {history.map((row) => (
                <tr key={row.id}>
                  <td>{formatDate(row.logged_at)}</td>
                  <td className="goal-tag">{row.goal}</td>
                  <td>{row.weight_lbs}</td>
                  <td>{row.sets_completed}</td>
                  <td>{parseReps(row.reps_completed)}</td>
                  <td>{avgReps(row.reps_completed)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}