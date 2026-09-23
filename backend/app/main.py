import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import recipes, nutrition, dashboard, meals, water, history, favorites, profile, predict, meal_plan, stats

app = FastAPI(title="DeepChef AI API", version="0.1.0")

origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipes.router)
app.include_router(nutrition.router)
app.include_router(dashboard.router)
app.include_router(meals.router)
app.include_router(water.router)
app.include_router(history.router)
app.include_router(favorites.router)
app.include_router(profile.router)
app.include_router(predict.router)
app.include_router(meal_plan.router)
app.include_router(stats.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
