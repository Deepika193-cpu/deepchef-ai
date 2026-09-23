import { useEffect, useState } from 'react';
import Card from '../components/Card';
import ProgressBar from '../components/ProgressBar';
import { LoadingState, ErrorMessage } from '../components/States';

const QUICK_ADD = [
  { label: '+250ml (glass)', ml: 250 },
  { label: '+500ml (bottle)', ml: 500 },
];

async function fetchToday() {
  const res = await fetch('/api/water/today');
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

async function postWater(amount_ml) {
  const res = await fetch('/api/water', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount_ml }),
  });
  if (!res.ok) throw new Error('Request failed');
}

export default function WaterTracker() {
  const [status, setStatus] = useState('loading');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  function load() {
    setStatus('loading');
    fetchToday()
      .then((res) => {
        setData(res);
        setStatus('done');
      })
      .catch((e) => {
        setError(e.message);
        setStatus('error');
      });
  }

  useEffect(load, []);

  async function handleAdd(ml) {
    try {
      await postWater(ml);
      load();
    } catch (e) {
      setError(e.message);
      setStatus('error');
    }
  }

  return (
    <Card padding="lg" className="space-y-4">
      <p className="text-sm font-medium text-ink-900">Water Intake</p>

      {status === 'loading' && <LoadingState message="Loading water intake…" />}
      {status === 'error' && <ErrorMessage title="Couldn't load water intake" description={error} onRetry={load} />}

      {status === 'done' && data && (
        <>
          <ProgressBar
            value={data.total_ml}
            max={data.goal_ml}
            label={`${data.total_ml}ml of ${data.goal_ml}ml`}
            color="accent"
          />
          <div className="flex gap-2">
            {QUICK_ADD.map((q) => (
              <button
                key={q.ml}
                onClick={() => handleAdd(q.ml)}
                className="px-3 py-1.5 rounded-full text-sm font-medium border border-slate-200 text-ink-600 hover:border-primary/40 hover:text-primary"
              >
                {q.label}
              </button>
            ))}
          </div>
        </>
      )}
    </Card>
  );
}
