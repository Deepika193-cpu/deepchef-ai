import { useEffect, useState } from 'react';
import Card from '../components/Card';
import { LoadingState, ErrorMessage, EmptyState } from '../components/States';

async function fetchNutrition(food, portion) {
  const res = await fetch(
    `/api/nutrition/lookup?food=${encodeURIComponent(food)}&portion=${portion}`
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

const FACT_ROWS = [
  ['calories', 'Calories', 'kcal'],
  ['protein_g', 'Protein', 'g'],
  ['carbohydrates_g', 'Carbohydrates', 'g'],
  ['fat_g', 'Fat', 'g'],
  ['fiber_g', 'Fiber', 'g'],
];

const PORTIONS = [
  { key: 'small', label: 'Small' },
  { key: 'medium', label: 'Medium' },
  { key: 'large', label: 'Large' },
];

function HealthScoreBadge({ healthScore }) {
  if (!healthScore) return null;
  const tone =
    healthScore.score >= 70 ? 'bg-accent-light text-accent' :
    healthScore.score >= 40 ? 'bg-primary-light text-primary' :
    'bg-red-50 text-danger';
  return (
    <div className="flex items-center gap-2">
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${tone}`}>
        {healthScore.label}: {healthScore.score}/100
      </span>
    </div>
  );
}

export default function NutritionPanel({ food, onFactsLoaded }) {
  const [portion, setPortion] = useState('medium');
  const [status, setStatus] = useState('loading'); // loading | error | done
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    fetchNutrition(food, portion)
      .then((res) => {
        if (!cancelled) {
          setData(res);
          setStatus('done');
          if (res.found && onFactsLoaded) {
            onFactsLoaded({ facts: res.facts, portion });
          }
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e.message);
          setStatus('error');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [food, portion]);

  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-medium text-ink-900 mb-2">Portion size</p>
        <div className="flex gap-2">
          {PORTIONS.map((p) => (
            <button
              key={p.key}
              onClick={() => setPortion(p.key)}
              className={`px-3.5 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                portion === p.key
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white text-ink-600 border-slate-200 hover:border-primary/40'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {status === 'loading' && (
        <Card padding="lg">
          <LoadingState message="Looking up nutrition data…" />
        </Card>
      )}

      {status === 'error' && (
        <ErrorMessage title="Nutrition lookup failed" description={error} />
      )}

      {status === 'done' && !data.found && (
        <EmptyState
          title="No nutrition data found"
          description={data.message || `We couldn't find nutrition data for "${food}".`}
        />
      )}

      {status === 'done' && data.found && (
        <Card padding="lg" className="space-y-4">
          <div className="flex items-start justify-between flex-wrap gap-2">
            <div>
              <p className="text-sm text-ink-600">
                Nutrition for <span className="font-medium text-ink-900">{data.matched_food_name}</span>
                {' '}<span className="text-ink-400">({data.per})</span>
              </p>
              {!data.is_exact_match && (
                <p className="text-xs text-warning mt-1">
                  Closest available match — treat these values as an estimate, not exact for this dish.
                </p>
              )}
            </div>
            <HealthScoreBadge healthScore={data.health_score} />
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 text-center">
            {FACT_ROWS.map(([key, label, unit]) => {
              const value = data.facts?.[key];
              return (
                <div key={key}>
                  <p className="font-display font-semibold text-ink-900">
                    {value != null ? Math.round(value) : '—'}
                    {value != null && <span className="text-xs font-normal text-ink-400"> {unit}</span>}
                  </p>
                  <p className="text-xs text-ink-600">{label}</p>
                </div>
              );
            })}
          </div>
          {data.health_score && (
            <p className="text-xs text-ink-400">{data.health_score.disclaimer}</p>
          )}
        </Card>
      )}
    </div>
  );
}
