import { useEffect, useState } from 'react';
import Card from '../components/Card';
import { LoadingState, ErrorMessage, EmptyState } from '../components/States';

async function fetchHistory(q, favoritesOnly) {
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (favoritesOnly) params.set('favorites_only', 'true');
  const res = await fetch(`/api/history?${params}`);
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

async function toggleFavorite(id) {
  const res = await fetch(`/api/history/${id}/favorite`, { method: 'PATCH' });
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

async function deleteItem(id) {
  const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Request failed');
}

export default function History() {
  const [q, setQ] = useState('');
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [status, setStatus] = useState('loading');
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);

  function load() {
    setStatus('loading');
    fetchHistory(q, favoritesOnly)
      .then((res) => {
        setItems(res);
        setStatus('done');
      })
      .catch((e) => {
        setError(e.message);
        setStatus('error');
      });
  }

  useEffect(load, [q, favoritesOnly]);

  async function handleFavorite(id) {
    await toggleFavorite(id);
    load();
  }

  async function handleDelete(id) {
    await deleteItem(id);
    load();
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-12 space-y-6">
      <h1 className="font-display text-2xl font-semibold text-ink-900">Search History</h1>

      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by food name…"
          className="flex-1 min-w-[200px] rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:border-primary"
        />
        <button
          onClick={() => setFavoritesOnly((v) => !v)}
          className={`px-3.5 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            favoritesOnly
              ? 'bg-primary text-white border-primary'
              : 'bg-white text-ink-600 border-slate-200 hover:border-primary/40'
          }`}
        >
          Favorites only
        </button>
      </div>

      {status === 'loading' && <LoadingState message="Loading history…" />}
      {status === 'error' && <ErrorMessage title="Couldn't load history" description={error} onRetry={load} />}

      {status === 'done' && items.length === 0 && (
        <EmptyState
          title="No history yet"
          description="Analyzed foods will show up here so you can revisit them anytime."
        />
      )}

      {status === 'done' && items.length > 0 && (
        <div className="space-y-3">
          {items.map((item) => (
            <Card key={item.id} padding="md" className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-xl bg-secondary shrink-0 overflow-hidden">
                {item.image_url && (
                  <img src={item.image_url} alt={item.food_name} className="w-full h-full object-cover" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-ink-900 truncate">{item.food_name}</p>
                <p className="text-xs text-ink-400">
                  {new Date(item.created_at).toLocaleString()}
                  {item.calories != null ? ` · ${Math.round(item.calories)} kcal` : ''}
                </p>
              </div>
              <button
                onClick={() => handleFavorite(item.id)}
                className={`text-sm font-medium ${item.is_favorite ? 'text-primary' : 'text-ink-400 hover:text-primary'}`}
                aria-label="Toggle favorite"
              >
                {item.is_favorite ? '★' : '☆'}
              </button>
              <button
                onClick={() => handleDelete(item.id)}
                className="text-sm text-ink-400 hover:text-danger"
                aria-label="Delete"
              >
                Delete
              </button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
