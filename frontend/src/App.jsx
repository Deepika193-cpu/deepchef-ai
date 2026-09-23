import { useState } from 'react';
import { Navbar, MobileTabBar } from './components/Layout';
import Home from './pages/Home';
import AnalysisScreen from './pages/AnalysisScreen';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Favorites from './pages/Favorites';
import Planner from './pages/Planner';
import Profile from './pages/Profile';

async function runPrediction(fileOrUrl) {
  const formData = new FormData();
  if (fileOrUrl instanceof File) {
    formData.append('image', fileOrUrl);
  } else {
    // Retry path: `analysis.imagePreviewUrl` is a blob: URL (from
    // URL.createObjectURL on the original file), not a File object —
    // fetching it back gives the same bytes, so Retry works without
    // needing to keep the original File in state.
    const res = await fetch(fileOrUrl);
    const blob = await res.blob();
    formData.append('image', blob, 'photo.jpg');
  }
  const res = await fetch('/api/predict', { method: 'POST', body: formData });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body.detail || `Prediction failed (${res.status})`);
  }
  return body;
}

export default function App() {
  const [view, setView] = useState('home');
  const [analysis, setAnalysis] = useState({
    imagePreviewUrl: null,
    status: 'idle',
    prediction: null,
    error: null,
  });

  async function handleAnalyze(fileOrUrl) {
    const isFile = fileOrUrl instanceof File;
    const previewUrl = isFile ? URL.createObjectURL(fileOrUrl) : fileOrUrl;

    setAnalysis({ imagePreviewUrl: previewUrl, status: 'analyzing', prediction: null, error: null });
    setView('analysis');

    try {
      const result = await runPrediction(fileOrUrl);
      setAnalysis({
        imagePreviewUrl: previewUrl,
        status: result.recognized ? 'done' : 'low_confidence',
        prediction: result.recognized
          ? {
              food: result.food,
              category: result.category,
              source: result.source,
              confidenceLabel: result.confidence_label,
              topPredictions: (result.top_predictions || []).map((p) => ({ label: p.label })),
            }
          : null,
        error: null,
      });

      // Log every recognized prediction to history — best-effort, doesn't
      // block or affect the analysis screen if it fails.
      if (result.recognized) {
        fetch('/api/history', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            food_name: result.food,
            category: result.category || null,
            source: result.source,
          }),
        }).catch((err) => console.error('Failed to log history entry:', err));
      }
    } catch (e) {
      console.error('Prediction failed:', e);
      setAnalysis({ imagePreviewUrl: previewUrl, status: 'error', prediction: null, error: e.message });
    }
  }

  function handleAnalyzeAnother() {
    setAnalysis({ imagePreviewUrl: null, status: 'idle', prediction: null, error: null });
    setView('home');
  }

  return (
    <div className="min-h-screen pb-16 md:pb-0">
      <Navbar active={view} onNavigate={setView} />

      {view === 'home' && <Home onAnalyze={handleAnalyze} />}

      {view === 'analysis' && (
        <AnalysisScreen
          imagePreviewUrl={analysis.imagePreviewUrl}
          status={analysis.status}
          prediction={analysis.prediction}
          predictError={analysis.error}
          onRetry={() => handleAnalyze(analysis.imagePreviewUrl)}
          onAnalyzeAnother={handleAnalyzeAnother}
        />
      )}

      {view === 'dashboard' && <Dashboard />}
      {view === 'history' && <History />}
      {view === 'favorites' && <Favorites />}
      {view === 'planner' && <Planner />}
      {view === 'profile' && <Profile />}

      <MobileTabBar active={view} onNavigate={setView} />
    </div>
  );
}