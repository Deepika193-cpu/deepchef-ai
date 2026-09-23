import { useState } from 'react';
import FoodAnalysis from './FoodAnalysis';
import NutritionPanel from './NutritionPanel';
import RecipeGenerator, { RecipeCard } from './RecipeGenerator';
import SaveMealButton from './SaveMealButton';
import { LoadingState, ErrorMessage } from '../components/States';

export default function AnalysisScreen({ imagePreviewUrl, status, prediction, predictError, onRetry, onAnalyzeAnother }) {
  const [panel, setPanel] = useState(null); // null | 'nutrition' | 'recipe' | 'stored_recipe'
  const [storedRecipeStatus, setStoredRecipeStatus] = useState('idle'); // idle | loading | done | error
  const [storedRecipe, setStoredRecipe] = useState(null);
  const [storedRecipeError, setStoredRecipeError] = useState(null);
  const [nutritionState, setNutritionState] = useState({ facts: null, portion: 'medium' });

  async function handleViewRecipe() {
    setPanel('stored_recipe');
    setStoredRecipeStatus('loading');
    setStoredRecipeError(null);
    try {
      const res = await fetch(`/api/recipes/${encodeURIComponent(prediction.food)}`);
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(body.detail || 'Stored recipe not available.');
      }
      setStoredRecipe(body.recipe);
      setStoredRecipeStatus('done');
    } catch (e) {
      setStoredRecipeError(e.message);
      setStoredRecipeStatus('error');
    }
  }

  return (
    <div>
      <FoodAnalysis
        imagePreviewUrl={imagePreviewUrl}
        status={status === 'error' ? 'error' : status}
        prediction={prediction}
        errorMessage={predictError}
        onRetry={onRetry}
        onViewRecipe={handleViewRecipe}
        onGenerateRecipe={() => setPanel('recipe')}
        onViewNutrition={() => setPanel('nutrition')}
        onAnalyzeAnother={onAnalyzeAnother}
      />

      {status === 'done' && prediction && panel && (
        <div className="max-w-5xl mx-auto px-6 pb-16">
          <div className="max-w-xl mx-auto md:ml-auto md:mr-0">
            {panel === 'nutrition' && (
              <div className="space-y-4">
                <NutritionPanel food={prediction.food} onFactsLoaded={setNutritionState} />
                {nutritionState.facts && (
                  <SaveMealButton
                    foodName={prediction.food}
                    portion={nutritionState.portion}
                    facts={nutritionState.facts}
                  />
                )}
              </div>
            )}
            {panel === 'recipe' && <RecipeGenerator detectedFood={prediction.food} />}
            {panel === 'stored_recipe' && storedRecipeStatus === 'loading' && (
              <LoadingState message="Fetching recipe…" />
            )}
            {panel === 'stored_recipe' && storedRecipeStatus === 'error' && (
              <ErrorMessage
                title="Recipe unavailable"
                description={storedRecipeError}
                onRetry={handleViewRecipe}
              />
            )}
            {panel === 'stored_recipe' && storedRecipeStatus === 'done' && storedRecipe && (
              <RecipeCard recipe={storedRecipe} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}