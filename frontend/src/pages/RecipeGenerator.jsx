import { useState } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import { LoadingState, ErrorMessage } from '../components/States';

const PREFERENCES = [
  { key: 'high_protein', label: 'High Protein' },
  { key: 'weight_loss', label: 'Weight Loss' },
  { key: 'vegetarian', label: 'Vegetarian' },
  { key: 'vegan', label: 'Vegan' },
  { key: 'indian_style', label: 'Indian Style' },
  { key: 'low_carb', label: 'Low Carb' },
  { key: 'custom', label: 'Custom' },
];

async function fetchGeneratedRecipe(payload) {
  const res = await fetch('/api/recipes/generate', {
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

export default function RecipeGenerator({ detectedFood, portion = 'medium' }) {
  const [preference, setPreference] = useState('high_protein');
  const [customText, setCustomText] = useState('');
  const [status, setStatus] = useState('idle'); // idle | loading | error | done
  const [error, setError] = useState(null);
  const [recipe, setRecipe] = useState(null);

  async function handleGenerate() {
    setStatus('loading');
    setError(null);
    try {
      const data = await fetchGeneratedRecipe({
        detected_food: detectedFood,
        preference,
        custom_preference: preference === 'custom' ? customText : undefined,
        portion,
      });
      setRecipe(data.recipe);
      setStatus('done');
    } catch (e) {
      setError(e.message);
      setStatus('error');
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-medium text-ink-900 mb-2">Dietary preference</p>
        <div className="flex flex-wrap gap-2">
          {PREFERENCES.map((p) => (
            <button
              key={p.key}
              onClick={() => setPreference(p.key)}
              className={`px-3.5 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                preference === p.key
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white text-ink-600 border-slate-200 hover:border-primary/40'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
        {preference === 'custom' && (
          <input
            type="text"
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            placeholder="e.g. low sodium, Mediterranean style, kid-friendly…"
            className="mt-3 w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:border-primary"
          />
        )}
      </div>

      <Button
        variant="primary"
        onClick={handleGenerate}
        loading={status === 'loading'}
        disabled={preference === 'custom' && !customText.trim()}
      >
        Generate Recipe
      </Button>

      {status === 'loading' && <LoadingState message="Generating your personalized recipe…" />}

      {status === 'error' && (
        <ErrorMessage
          title="Couldn't generate a recipe"
          description={error}
          onRetry={handleGenerate}
        />
      )}

      {status === 'done' && recipe && <RecipeCard recipe={recipe} />}
    </div>
  );
}

export function RecipeCard({ recipe }) {
  const [saved, setSaved] = useState(false);

  async function handleSaveFavorite() {
    const res = await fetch('/api/favorites/recipes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipe_name: recipe.recipe_name, recipe_json: recipe }),
    });
    if (res.ok) setSaved(true);
  }

  return (
    <Card padding="lg" className="space-y-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-xl font-semibold text-ink-900">{recipe.recipe_name}</h3>
          <p className="text-sm text-ink-600 mt-1">{recipe.description}</p>
        </div>
        <button
          onClick={handleSaveFavorite}
          disabled={saved}
          className={`text-sm font-medium shrink-0 ${saved ? 'text-primary' : 'text-ink-400 hover:text-primary'}`}
        >
          {saved ? '★ Saved' : '☆ Save'}
        </button>
      </div>

      <div className="flex flex-wrap gap-4 text-sm text-ink-600">
        <span>Prep {recipe.prep_time_minutes} min</span>
        <span>Cook {recipe.cook_time_minutes} min</span>
        <span className="capitalize">{recipe.difficulty}</span>
      </div>

      <div className="grid sm:grid-cols-2 gap-6">
        <div>
          <p className="text-sm font-medium text-ink-900 mb-2">Ingredients</p>
          <ul className="space-y-1 text-sm text-ink-600">
            {recipe.ingredients.map((ing, i) => (
              <li key={ing}>
                {recipe.quantities?.[i] ? `${recipe.quantities[i]} ` : ''}
                {ing}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-sm font-medium text-ink-900 mb-2">Instructions</p>
          <ol className="space-y-1.5 text-sm text-ink-600 list-decimal list-inside">
            {recipe.instructions.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 pt-4 border-t border-slate-100 text-center">
        {[
          ['Calories', `${Math.round(recipe.estimated_calories)}`],
          ['Protein', `${Math.round(recipe.protein_g)}g`],
          ['Carbs', `${Math.round(recipe.carbohydrates_g)}g`],
          ['Fat', `${Math.round(recipe.fat_g)}g`],
          ['Fiber', `${Math.round(recipe.fiber_g)}g`],
        ].map(([label, value]) => (
          <div key={label}>
            <p className="font-display font-semibold text-ink-900">{value}</p>
            <p className="text-xs text-ink-600">{label}</p>
          </div>
        ))}
      </div>
      <p className="text-xs text-ink-400">
        AI-generated suggestion. Nutrition values are estimates, not medical advice.
      </p>
    </Card>
  );
}
