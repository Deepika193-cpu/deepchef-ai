import Button from '../components/Button';
import Card from '../components/Card';
import { LoadingState, ErrorMessage, EmptyState } from '../components/States';

// VLM recognition self-reports a qualitative label, not a calibrated
// probability — no fake percentage is shown for it.
function ConfidenceLabelBadge({ label }) {
  const tone =
    label === 'high' ? 'bg-accent-light text-accent' :
    label === 'medium' ? 'bg-primary-light text-primary' :
    'bg-slate-100 text-ink-600';
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium capitalize ${tone}`}>
      {label} confidence
    </span>
  );
}

export default function FoodAnalysis({
  imagePreviewUrl,
  status, // 'analyzing' | 'error' | 'low_confidence' | 'done'
  prediction, // { food, category, confidenceLabel, topPredictions: [{label}], source: 'vlm' | 'cnn' }
  errorMessage,
  onRetry,
  onViewRecipe,
  onGenerateRecipe,
  onViewNutrition,
  onAnalyzeAnother,
}) {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="grid md:grid-cols-2 gap-8">
        {/* Left: image */}
        <div>
          <div className="rounded-card overflow-hidden border border-slate-100 shadow-soft aspect-square bg-secondary">
            {imagePreviewUrl && (
              <img src={imagePreviewUrl} alt="Uploaded food" className="w-full h-full object-cover" />
            )}
          </div>
          {prediction?.category && (
            <span className="inline-block mt-3 text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 text-ink-600">
              {prediction.category}
            </span>
          )}
        </div>

        {/* Right: results */}
        <div>
          {status === 'analyzing' && (
            <Card padding="lg">
              <LoadingState message="Running food recognition…" />
            </Card>
          )}

          {status === 'error' && (
            <ErrorMessage
              title="Couldn't analyze this image"
              description={errorMessage || 'Something went wrong while processing the photo. Please try again.'}
              onRetry={onRetry}
            />
          )}

          {status === 'low_confidence' && (
            <EmptyState
              title="Food not confidently recognized"
              description="We couldn't confidently match this to a known food. Try a clearer, well-lit photo of a single dish."
              action={<Button variant="primary" onClick={onAnalyzeAnother}>Try another photo</Button>}
            />
          )}

          {status === 'done' && prediction && (
            <Card padding="lg" className="space-y-6">
              <div>
                <p className="text-sm text-ink-600 mb-1">Detected Food</p>
                <div className="flex items-center gap-3 flex-wrap">
                  <h2 className="font-display text-2xl font-semibold text-ink-900">
                    {prediction.food}
                  </h2>
                  {prediction.confidenceLabel && (
                    <ConfidenceLabelBadge label={prediction.confidenceLabel} />
                  )}
                </div>
                <p className="text-xs text-ink-400 mt-2">
                  Identified by AI vision model — not a fixed-class CNN, so this is a qualitative
                  read rather than a percentage score.
                </p>
              </div>

              {prediction.topPredictions?.length > 1 && (
                <div>
                  <p className="text-sm font-medium text-ink-900 mb-2">Other possibilities</p>
                  <ol className="space-y-2">
                    {prediction.topPredictions.slice(1, 5).map((p, i) => (
                      <li key={p.label} className="flex items-center text-sm text-ink-600">
                        <span className="text-ink-400 mr-2">{i + 2}.</span>
                        {p.label}
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              <div className="flex flex-wrap gap-3 pt-2 border-t border-slate-100">
                <Button variant="primary" onClick={onViewRecipe}>View Recipe</Button>
                <Button variant="secondary" onClick={onGenerateRecipe}>Generate Personalized Recipe</Button>
                <Button variant="outline" onClick={onViewNutrition}>View Nutrition</Button>
                <Button variant="ghost" onClick={onAnalyzeAnother}>Analyze Another Image</Button>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
