import { useEffect, useState } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import UploadBox from '../components/UploadBox';
import { LoadingState } from '../components/States';

// Illustrative examples only — not tied to a fixed class list, since
// recognition is open-vocabulary (see backend/app/services/vision_recognition.py).
// Emoji placeholders, not photos — no image assets are bundled with this
// project (avoids both broken <img> tags and licensing questions around
// bundling real food photos).
const SAMPLE_FOODS = [
  { id: 'pizza', label: 'Pizza', emoji: '🍕' },
  { id: 'samosa', label: 'Samosa', emoji: '🥟' },
  { id: 'sushi', label: 'Sushi', emoji: '🍣' },
  { id: 'pad_thai', label: 'Pad Thai', emoji: '🍜' },
  { id: 'tacos', label: 'Tacos', emoji: '🌮' },
  { id: 'caesar_salad', label: 'Caesar Salad', emoji: '🥗' },
];

// Wired to real counts from the backend once /api/stats exists — never
// display a number here that wasn't returned by that endpoint.
function StatCard({ value, label }) {
  return (
    <Card padding="md" className="text-center">
      <p className="font-display text-3xl font-semibold text-primary">{value ?? '—'}</p>
      <p className="text-sm text-ink-600 mt-1">{label}</p>
    </Card>
  );
}

export default function Home({ onAnalyze }) {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('/api/stats')
      .then((res) => (res.ok ? res.json() : null))
      .then(setStats)
      .catch(() => setStats(null)); // stays null -> StatCard shows '—', never a fake number
  }, []);

  async function handleAnalyze() {
    if (!file) return;
    setAnalyzing(true);
    try {
      await onAnalyze(file);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-16">
      {/* Hero */}
      <section className="text-center max-w-2xl mx-auto">
        <h1 className="font-display text-4xl md:text-5xl font-semibold text-ink-900 leading-tight">
          Understand Your Food. Eat Smarter.
        </h1>
        <p className="text-ink-600 mt-4 text-lg">
          Identify food, discover recipes, understand nutrition, and make smarter meal
          choices with AI.
        </p>
      </section>

      {/* Upload */}
      <section className="max-w-xl mx-auto">
        <Card padding="lg">
          <UploadBox onFileSelected={setFile} />
          {analyzing ? (
            <div className="mt-6">
              <LoadingState message="Analyzing your food…" />
            </div>
          ) : (
            <Button
              variant="primary"
              size="lg"
              className="w-full mt-6"
              disabled={!file}
              onClick={handleAnalyze}
            >
              Analyze
            </Button>
          )}
        </Card>
      </section>

      {/* Sample foods — illustrative only; see note below on why these
          aren't clickable yet */}
      <section>
        <h2 className="font-display text-xl font-semibold text-ink-900 mb-1">
          Foods DeepChef AI can recognize
        </h2>
        <p className="text-sm text-ink-600 mb-5">
          A few examples — recognition isn't limited to this list, it works on any clear photo of a dish.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
          {SAMPLE_FOODS.map((s) => (
            <div key={s.id} className="text-left">
              <div className="aspect-square rounded-card border border-slate-100 bg-secondary flex items-center justify-center text-4xl">
                {s.emoji}
              </div>
              <p className="text-xs text-ink-600 mt-1.5 truncate">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats — only real numbers from the backend, never invented */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard value={stats?.foods_recognized} label="Foods Recognized" />
        <StatCard value={stats?.recipes_available} label="Recipes Available" />
        <StatCard value={stats?.meals_analyzed} label="Meals Analyzed" />
      </section>
    </div>
  );
}
