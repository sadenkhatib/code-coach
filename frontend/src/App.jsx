import { useState } from 'react';
import './App.css';
import { getWorkoutPlan } from './api/workoutApi';
import WorkoutLogger from './components/WorkoutLogger';
import ProgressView from './components/ProgressView';

const GOAL_MAP = {
  'Hypertrophy': 'hypertrophy',
  'Strength':    'strength',
  'Fat Loss':    'fat loss',
};

function App() {
  const [activeTab, setActiveTab] = useState('plan');

  // Plan generator state
  const [goal, setGoal]       = useState('');
  const [days, setDays]       = useState('');
  const [plan, setPlan]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  // Logger state — set when user clicks "Log This Day"
  const [loggerExercises, setLoggerExercises] = useState(null);
  const [loggerGoal, setLoggerGoal]           = useState('');

  async function fetchPlan() {
    setError(null);
    setPlan(null);
    if (!goal || !days) {
      setError('Please choose a goal and number of days.');
      return;
    }
    setLoading(true);
    try {
      const payloadGoal = GOAL_MAP[goal] ?? goal;
      const result = await getWorkoutPlan(payloadGoal, Number(days));
      setPlan(result);
    } catch (e) {
      setError(e.message || 'Failed to fetch workout plan');
    } finally {
      setLoading(false);
    }
  }

  function openLogger(dayExercises) {
    setLoggerExercises(dayExercises);
    setLoggerGoal(plan.goal);
    setActiveTab('log');
  }

  function handleLogComplete() {
    setLoggerExercises(null);
    setLoggerGoal('');
    setActiveTab('progress');
  }

  function handleLogCancel() {
    setLoggerExercises(null);
    setLoggerGoal('');
    setActiveTab('plan');
  }

  return (
    <div className="app">
      <img
        src="https://ih1.redbubble.net/image.5125089331.2719/raf,360x360,075,t,fafafa:ca443f4786.jpg"
        alt="CodeCoach logo"
        style={{ width: 200, height: 'auto' }}
      />
      <h1>CodeCoach Workout Planner</h1>

      {/* Tab Navigation */}
      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'plan' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('plan')}
        >
          Generate Plan
        </button>
        <button
          className={`tab ${activeTab === 'log' ? 'tab-active' : ''}`}
          onClick={() => {
            if (!loggerExercises && plan) {
              // default to first day if no specific day chosen
              openLogger(plan.plan[0].exercises);
            } else {
              setActiveTab('log');
            }
          }}
          disabled={!plan && activeTab !== 'log'}
          title={!plan ? 'Generate a plan first' : undefined}
        >
          Log Session
        </button>
        <button
          className={`tab ${activeTab === 'progress' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('progress')}
        >
          Progress
        </button>
      </nav>

      {/* ── Generate Plan ── */}
      {activeTab === 'plan' && (
        <>
          <div className="card">
            <label>
              Goal:
              <select value={goal} onChange={(e) => setGoal(e.target.value)}>
                <option value="">-- Choose a goal --</option>
                <option value="Hypertrophy">Hypertrophy</option>
                <option value="Strength">Strength</option>
                <option value="Fat Loss">Fat Loss</option>
              </select>
            </label>

            <label>
              Days per Week:
              <select
                value={days}
                onChange={(e) => setDays(e.target.value ? String(e.target.value) : '')}
              >
                <option value="">-- Choose days --</option>
                {[1, 2, 3, 4, 5, 6].map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </label>

            <button
              onClick={fetchPlan}
              disabled={loading || !goal || !days}
              title={!goal || !days ? 'Choose both goal and days' : 'Generate plan'}
            >
              {loading ? 'Loading…' : 'Get Workout Plan'}
            </button>
          </div>

          {error && <p className="error">{error}</p>}

          {plan && (
            <div className="plan-display">
              <h2>Goal: {goal}</h2>
              <p><strong>Note:</strong> {plan.note}</p>
              {plan.plan.map((day) => (
                <div key={day.day} className="day" data-focus={day.focus}>
                  <div className="day-header">
                    <h3>{day.day} — Focus: {day.focus}</h3>
                    <button
                      className="btn-log-day"
                      onClick={() => openLogger(day.exercises)}
                    >
                      Log This Day
                    </button>
                  </div>
                  <ul>
                    {day.exercises.map((ex, idx) => (
                      <li key={idx}>
                        <strong>{ex.exercise}</strong> — {ex.sets} sets × {ex.reps} reps
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Log Session ── */}
      {activeTab === 'log' && (
        <>
          {loggerExercises ? (
            <WorkoutLogger
              exercises={loggerExercises}
              goal={loggerGoal}
              onComplete={handleLogComplete}
              onCancel={handleLogCancel}
            />
          ) : (
            <div className="empty-state">
              <p>Generate a plan first, then click <strong>"Log This Day"</strong> on any workout day to log your session.</p>
              <button onClick={() => setActiveTab('plan')}>Go to Generate Plan</button>
            </div>
          )}
        </>
      )}

      {/* ── Progress ── */}
      {activeTab === 'progress' && <ProgressView />}
    </div>
  );
}

export default App;