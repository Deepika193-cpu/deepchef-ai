import { useState } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import { LoadingState, ErrorMessage } from '../components/States';

const GOALS = [
  { key: 'weight_loss', label: 'Weight Loss' },
  { key: 'maintenance', label: 'Maintenance' },
  { key: 'high_protein', label: 'High Protein' },
  { key: 'balanced_diet', label: 'Balanced Diet' },
];

const MEAL_SLOTS = ['breakfast', 'lunch', 'dinner', 'snack'];

async function fetchMealPlan(goal) {
  const res = await fetch('/api/meal-plan/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `Request failed (${res.status})`);
  return body;
}

export default function Planner() {
  const [goal, setGoal] = useState('balanced_diet');
  const [status, setStatus] = useState('idle'); // idle | loading | error | done
  const [error, setError] = useState(null);
  const [plan, setPlan] = useState(null);
  const [activeDay, setActiveDay] = useState(0);

  async function handleGenerate() {
    setStatus('loading');
    setError(null);
    try {
      const result = await fetchMealPlan(goal);
      setPlan(result);
      setActiveDay(0);
      setStatus('done');
    } catch (e) {
      setError(e.message);
      setStatus('error');
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-12 space-y-6">
      <h1 className="font-display text-2xl font-semibold text-ink-900">Weekly Meal Planner</h1>

      <div>
        <p className="text-sm font-medium text-ink-900 mb-2">Goal</p>
        <div className="flex flex-wrap gap-2">
          {GOALS.map((g) => (
            <button
              key={g.key}
              onClick={() => setGoal(g.key)}
              className={`px-3.5 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                goal === g.key
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white text-ink-600 border-slate-200 hover:border-primary/40'
              }`}
            >
              {g.label}
            </button>
          ))}
        </div>
      </div>

      <Button variant="primary" onClick={handleGenerate} loading={status === 'loading'}>
        Generate weekly plan
      </Button>

      {status === 'loading' && <LoadingState message="Generating your weekly meal plan… this can take a bit longer than a single recipe." />}

      {status === 'error' && (
        <ErrorMessage title="Couldn't generate meal plan" description={error} onRetry={handleGenerate} />
      )}

      {status === 'done' && plan && (
        <div className="space-y-4">
          <div className="flex gap-2 overflow-x-auto pb-1">
            {plan.days.map((d, i) => (
              <button
                key={d.day}
                onClick={() => setActiveDay(i)}
                className={`px-3.5 py-1.5 rounded-full text-sm font-medium border shrink-0 transition-colors ${
                  activeDay === i
                    ? 'bg-primary text-white border-primary'
                    : 'bg-white text-ink-600 border-slate-200 hover:border-primary/40'
                }`}
              >
                {d.day}
              </button>
            ))}
          </div>

          <Card padding="lg" className="space-y-4">
            <h3 className="font-display font-semibold text-ink-900">{plan.days[activeDay].day}</h3>
            {MEAL_SLOTS.map((slot) => {
              const meal = plan.days[activeDay][slot];
              return (
                <div key={slot} className="border-t border-slate-100 pt-3 first:border-t-0 first:pt-0">
                  <p className="text-xs font-medium text-ink-400 uppercase tracking-wide">{slot}</p>
                  <p className="font-medium text-ink-900">{meal.name}</p>
                  <p className="text-sm text-ink-600">{meal.description}</p>
                  <p className="text-xs text-ink-400 mt-1">{meal.estimated_calories} kcal (estimated)</p>
                </div>
              );
            })}
          </Card>
          <p className="text-xs text-ink-400">{plan.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
