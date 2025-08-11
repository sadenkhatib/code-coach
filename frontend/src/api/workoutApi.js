export async function getWorkoutPlan(goal, days) {
  const url = 'http://localhost:5050/generate-plan';

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ goal, days })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Server ${res.status}: ${text || res.statusText}`);
  }

  return res.json();
}
