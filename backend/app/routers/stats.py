from fastapi import APIRouter, Depends
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PredictionHistory, StoredRecipe, MealRecord
from app.schemas.stats import StatsResponse

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    # Distinct food names actually recognized (search_history), not total
    # requests — repeatedly analyzing the same dish shouldn't inflate this.
    foods_recognized = (
        db.query(func.count(distinct(PredictionHistory.food_name))).scalar() or 0
    )
    recipes_available = db.query(func.count(StoredRecipe.id)).scalar() or 0
    meals_analyzed = db.query(func.count(MealRecord.id)).scalar() or 0

    return StatsResponse(
        foods_recognized=foods_recognized,
        recipes_available=recipes_available,
        meals_analyzed=meals_analyzed,
    )