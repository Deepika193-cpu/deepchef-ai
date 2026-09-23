import { useState } from 'react';
import Button from '../components/Button';
import { ErrorMessage } from '../components/States';

const MEAL_TYPES = [
  { key: 'breakfast', label: 'Breakfast' },
  { key: 'lunch', label: 'Lunch' },
  { key: 'dinner', label: 'Dinner' },
  { key: 'snack', label: 'Snack' },
];

async function saveMeal(payload) {
  const res = await fetch('/api/meals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

// facts: { calories, protein_g, carbohydrates_g, fat_g, fiber_g } — the
// already-portion-scaled values from NutritionPanel, not re-derived here.
export default function SaveMealButton({ foodName, portion, facts }) {
  const [mealType, setMealType] = useState('lunch');
  const [status, setStatus] = useState('idle'); // idle | saving | saved | error
  const [error, setError] = useState(null);

  async function handleSave() {
    setStatus('saving');
    setError(null);
    try {
      await saveMeal({
        food_name: foodName,
        meal_type: mealType,
        portion,
        ...facts,
      });
      setStatus('saved');
    } catch (e) {
      setError(e.message);
      setStatus('error');
    }
  }

  if (status === 'saved') {
    return <p className="text-sm text-accent font-medium">Meal saved to {mealType}.</p>;
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        {MEAL_TYPES.map((m) => (
          <button
            key={m.key}
            onClick={() => setMealType(m.key)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              mealType === m.key
                ? 'bg-primary text-white border-primary'
                : 'bg-white text-ink-600 border-slate-200 hover:border-primary/40'
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>
      <Button variant="primary" onClick={handleSave} loading={status === 'saving'}>
        Save meal
      </Button>
      {status === 'error' && (
        <ErrorMessage title="Couldn't save meal" description={error} onRetry={handleSave} />
      )}
    </div>
  );
}
