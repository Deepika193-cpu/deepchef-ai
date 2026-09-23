import { useEffect, useState } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import { LoadingState, ErrorMessage } from '../components/States';

const DIETARY_PREFS = ['high_protein', 'weight_loss', 'vegetarian', 'vegan', 'indian_style', 'low_carb', 'none'];
const PORTIONS = ['small', 'medium', 'large'];

async function fetchProfile() {
  const res = await fetch('/api/profile');
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

async function saveProfile(payload) {
  const res = await fetch('/api/profile', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

export default function Profile() {
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState(null);
  const [form, setForm] = useState(null);
  const [saveStatus, setSaveStatus] = useState('idle'); // idle | saving | saved

  useEffect(() => {
    fetchProfile()
      .then((res) => {
        setForm({
          name: res.name || '',
          dietary_preference: res.dietary_preference || 'none',
          nutrition_goal: res.nutrition_goal || '',
          favorite_foods: res.favorite_foods?.join(', ') || '',
          preferred_portion: res.preferred_portion || 'medium',
        });
        setStatus('done');
      })
      .catch((e) => {
        setError(e.message);
        setStatus('error');
      });
  }, []);

  async function handleSave() {
    setSaveStatus('saving');
    try {
      await saveProfile({
        ...form,
        favorite_foods: form.favorite_foods
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
      });
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (e) {
      setError(e.message);
      setSaveStatus('idle');
    }
  }

  if (status === 'loading') {
    return (
      <div className="max-w-2xl mx-auto px-6 py-12">
        <LoadingState message="Loading profile…" />
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="max-w-2xl mx-auto px-6 py-12">
        <ErrorMessage title="Couldn't load profile" description={error} />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-12 space-y-6">
      <h1 className="font-display text-2xl font-semibold text-ink-900">Profile</h1>

      <Card padding="lg" className="space-y-5">
        <Field label="Name">
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:border-primary"
          />
        </Field>

        <Field label="Dietary preference">
          <select
            value={form.dietary_preference}
            onChange={(e) => setForm({ ...form, dietary_preference: e.target.value })}
            className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:border-primary"
          >
            {DIETARY_PREFS.map((p) => (
              <option key={p} value={p}>{p.replace('_', ' ')}</option>
            ))}
          </select>
        </Field>

        <Field label="Nutrition goal">
          <input
            type="text"
            value={form.nutrition_goal}
            onChange={(e) => setForm({ ...form, nutrition_goal: e.target.value })}
            placeholder="e.g. maintain weight, build muscle"
            className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:border-primary"
          />
        </Field>

        <Field label="Favorite foods (comma separated)">
          <input
            type="text"
            value={form.favorite_foods}
            onChange={(e) => setForm({ ...form, favorite_foods: e.target.value })}
            className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:border-primary"
          />
        </Field>

        <Field label="Preferred portion size">
          <div className="flex gap-2">
            {PORTIONS.map((p) => (
              <button
                key={p}
                onClick={() => setForm({ ...form, preferred_portion: p })}
                className={`px-3.5 py-1.5 rounded-full text-sm font-medium border capitalize transition-colors ${
                  form.preferred_portion === p
                    ? 'bg-primary text-white border-primary'
                    : 'bg-white text-ink-600 border-slate-200 hover:border-primary/40'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </Field>

        <Button variant="primary" onClick={handleSave} loading={saveStatus === 'saving'}>
          {saveStatus === 'saved' ? 'Saved ✓' : 'Save changes'}
        </Button>
      </Card>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <label className="block text-sm font-medium text-ink-900 mb-1.5">{label}</label>
      {children}
    </div>
  );
}
