import { useState } from 'react';
import './App.css';
import { getWorkoutPlan } from './api/workoutApi';


function App() {
  const [goal, setGoal] = useState('');      
  const [days, setDays] = useState('');      
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const goalMap = {
    'Hypertrophy': 'hypertrophy',
    'Strength': 'strength',
    'Fat Loss': 'fat loss'
  };

  const fetchPlan = async () => {
    setError(null);
    setPlan(null);

    if (!goal || !days) {
      setError('Please choose a goal and number of days.');
      return;
    }

    setLoading(true);

    try {
      const payloadGoal = goalMap[goal] ?? goal;
      const payloadDays = Number(days);

      console.debug('Sending request', { goal: payloadGoal, days: payloadDays });
      const result = await getWorkoutPlan(payloadGoal, payloadDays);
      console.debug('Server returned', result);
      setPlan(result);
    } catch (e) {
      console.error(e);
      setError(e.message || 'Failed to fetch workout plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <img 
        src="https://ih1.redbubble.net/image.5125089331.2719/raf,360x360,075,t,fafafa:ca443f4786.jpg" 
        style={{ width: 200, height: 'auto'}} 
      />
      <h1>CodeCoach Workout Planner</h1>

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
            {[1, 2, 3, 4, 5, 6].map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </label>

        <button
          onClick={fetchPlan}
          disabled={loading || !goal || !days}
          title={!goal || !days ? 'Choose both goal and days' : 'Generate plan'}
        >
          {loading ? 'Loading...' : 'Get Workout Plan'}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {plan && (
        <div className="plan-display">
          <h2>Goal: {goal}</h2>
          <p><strong>Note:</strong> {plan.note}</p>
          {plan.plan.map((day) => (
            <div key={day.day} className="day" data-focus={day.focus}>
              <h3>{day.day} — Focus: {day.focus}</h3>
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

    </div>
  );
}

export default App;
