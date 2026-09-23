import { useEffect, useState } from 'react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell,
} from 'recharts';
import Card from '../components/Card';
import { LoadingState, ErrorMessage, EmptyState } from '../components/States';
import WaterTracker from './WaterTracker';

const MACRO_COLORS = ['#FF6B35', '#2E7D32', '#FFC078'];

async function fetchDashboard() {
  const res = await fetch('/api/dashboard');
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

function StatBlock({ label, value, unit }) {
  return (
    <div className="text-center">
      <p className="font-display text-2xl font-semibold text-ink-900">
        {Math.round(value)} <span className="text-sm font-normal text-ink-400">{unit}</span>
      </p>
      <p className="text-xs text-ink-600 mt-1">{label}</p>
    </div>
  );
}

export default function Dashboard() {
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchDashboard()
      .then((res) => {
        setData(res);
        setStatus('done');
      })
      .catch((e) => {
        setError(e.message);
        setStatus('error');
      });
  }, []);

  if (status === 'loading') {
    return (
      <div className="max-w-5xl mx-auto px-6 py-12">
        <LoadingState message="Loading your nutrition dashboard…" />
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="max-w-5xl mx-auto px-6 py-12">
        <ErrorMessage title="Couldn't load dashboard" description={error} />
      </div>
    );
  }

  if (!data.has_data) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-12 space-y-8">
        <WaterTracker />
        <EmptyState
          title="No meals logged yet"
          description="Analyze a food photo and save it as a meal to start seeing your nutrition trends here."
        />
      </div>
    );
  }

  const macroData = [
    { name: 'Protein', value: data.today.protein_g },
    { name: 'Carbs', value: data.today.carbohydrates_g },
    { name: 'Fat', value: data.today.fat_g },
  ].filter((d) => d.value > 0);

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-8">
      <h1 className="font-display text-2xl font-semibold text-ink-900">Nutrition Dashboard</h1>

      <WaterTracker />

      {/* Today */}
      <Card padding="lg">
        <p className="text-sm font-medium text-ink-900 mb-4">Today</p>
        <div className="grid grid-cols-3 sm:grid-cols-5 gap-4">
          <StatBlock label="Calories" value={data.today.calories} unit="kcal" />
          <StatBlock label="Protein" value={data.today.protein_g} unit="g" />
          <StatBlock label="Carbs" value={data.today.carbohydrates_g} unit="g" />
          <StatBlock label="Fat" value={data.today.fat_g} unit="g" />
          <StatBlock label="Fiber" value={data.today.fiber_g} unit="g" />
        </div>
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Calorie trend */}
        <Card padding="lg">
          <p className="text-sm font-medium text-ink-900 mb-4">Weekly Calorie Trend</p>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data.weekly_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94A3B8' }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fontSize: 11, fill: '#94A3B8' }} />
              <Tooltip />
              <Line type="monotone" dataKey="calories" stroke="#FF6B35" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Macro distribution */}
        <Card padding="lg">
          <p className="text-sm font-medium text-ink-900 mb-4">Today's Macro Distribution</p>
          {macroData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={macroData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
                  {macroData.map((_, i) => (
                    <Cell key={i} fill={MACRO_COLORS[i % MACRO_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-ink-400 py-16 text-center">No macros logged today yet.</p>
          )}
        </Card>
      </div>

      {/* Most consumed */}
      <Card padding="lg">
        <p className="text-sm font-medium text-ink-900 mb-4">Most Consumed Foods</p>
        {data.most_consumed.length > 0 ? (
          <ul className="space-y-2">
            {data.most_consumed.map((f) => (
              <li key={f.food_name} className="flex items-center justify-between text-sm">
                <span className="text-ink-900">{f.food_name}</span>
                <span className="text-ink-400">{f.count}x</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-ink-400">Not enough data yet.</p>
        )}
      </Card>
    </div>
  );
}
