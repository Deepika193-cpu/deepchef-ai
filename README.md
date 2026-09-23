# DeepChef AI

Food Recognition, Recipe Generation & Calorie Intelligence System — a full-stack app.

Upload a food photo → see what it is → check its nutrition → get a personalized AI recipe → track it as a meal → see trends on a dashboard.


Uploading DeepChef.mp4…


## Tech stack
- **Frontend:** React + Tailwind CSS (Vite)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **AI:** Groq (Llama 4 Scout, vision) for food recognition; Groq (Llama 3.3) for recipe & meal plan generation
- **Nutrition data:** USDA FoodData Central

## What works right now
✅ Food recognition (via Groq's vision model — see note below), AI recipe generation, stored recipe retrieval (generate-once, cached), nutrition lookup, portion scaling, nutrition score, meal & water tracking, dashboard, weekly meal planner, history, favorites, profile

**Important note on food recognition:** this uses a vision-capable LLM (Groq/Llama 4 Scout), not a fine-tuned CNN classifier. That means:
- It's genuinely open-vocabulary (not limited to a fixed training-class list)
- Confidence is a qualitative self-report ("high"/"medium"/"low"), not a calibrated probability score


## Quick start

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your API keys
python scripts/init_db.py
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Open it
- App: http://localhost:5173
- API docs: http://localhost:8000/docs

## Environment variables (`backend/.env`)
```
GROQ_API_KEY=              # from console.groq.com
GROQ_MODEL=openai/gpt-oss-120b
GROQ_VISION_MODEL=qwen/qwen3.8-27b
USDA_FDC_API_KEY=          # from fdc.nal.usda.gov/api-key-signup.html
DATABASE_URL=postgresql://user:password@localhost:5432/deepchef
```

## Docker (alternative)
```bash
docker compose up --build
```

## Testing
```bash
cd backend
pip install -r requirements-dev.txt
pytest
```
Covers recognition, recipe generation, stored-recipe caching, meal planning, nutrition, and dashboard 


