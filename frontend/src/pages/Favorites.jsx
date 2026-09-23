import { useEffect, useState } from 'react';
import Card from '../components/Card';
import { LoadingState, ErrorMessage, EmptyState } from '../components/States';

async function fetchFavoriteRecipes() {
  const res = await fetch('/api/favorites/recipes');
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

async function removeFavorite(id) {
  const res = await fetch(`/api/favorites/recipes/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Request failed');
}

export default function Favorites() {
  const [status, setStatus] = useState('loading');
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);

  function load() {
    setStatus('loading');
    fetchFavoriteRecipes()
      .then((res) => {
        setItems(res);
        setStatus('done');
      })
      .catch((e) => {
        setError(e.message);
        setStatus('error');
      });
  }

  useEffect(load, []);

  async function handleRemove(id) {
    await removeFavorite(id);
    load();
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-12 space-y-6">
      <h1 className="font-display text-2xl font-semibold text-ink-900">Favorites</h1>

      {status === 'loading' && <LoadingState message="Loading favorites…" />}
      {status === 'error' && <ErrorMessage title="Couldn't load favorites" description={error} onRetry={load} />}

      {status === 'done' && items.length === 0 && (
        <EmptyState
          title="No favorite recipes yet"
          description="Save a personalized recipe you like and it'll show up here."
        />
      )}

      {status === 'done' && items.length > 0 && (
        <div className="grid sm:grid-cols-2 gap-4">
          {items.map((item) => {
            const r = item.recipe_json;
            return (
              <Card key={item.id} padding="md" className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-display font-semibold text-ink-900">{item.recipe_name}</p>
                  <button
                    onClick={() => handleRemove(item.id)}
                    className="text-ink-400 hover:text-danger text-sm shrink-0"
                    aria-label="Remove favorite"
                  >
                    ✕
                  </button>
                </div>
                {r?.description && <p className="text-sm text-ink-600">{r.description}</p>}
                {r?.estimated_calories != null && (
                  <p className="text-xs text-ink-400">{Math.round(r.estimated_calories)} kcal per serving</p>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
