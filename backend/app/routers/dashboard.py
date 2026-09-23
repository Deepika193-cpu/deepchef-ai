from collections import Counter, defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import MealRecord
from app.schemas.dashboard import DashboardResponse, DailyTotals, DayPoint, FoodCount

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    total_meals = db.query(func.count(MealRecord.id)).scalar() or 0

    if total_meals == 0:
        # No fabricated charts — the frontend renders a real empty state for this.
        return DashboardResponse(has_data=False, meals_logged_total=0)

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=6)

    today_rows = db.query(MealRecord).filter(MealRecord.logged_at >= today_start).all()
    today = DailyTotals(
        calories=sum(r.calories or 0 for r in today_rows),
        protein_g=sum(r.protein_g or 0 for r in today_rows),
        carbohydrates_g=sum(r.carbohydrates_g or 0 for r in today_rows),
        fat_g=sum(r.fat_g or 0 for r in today_rows),
        fiber_g=sum(r.fiber_g or 0 for r in today_rows),
    )

    week_rows = db.query(MealRecord).filter(MealRecord.logged_at >= week_start).all()
    by_day = defaultdict(lambda: {"calories": 0.0, "protein_g": 0.0})
    for r in week_rows:
        key = r.logged_at.strftime("%Y-%m-%d")
        by_day[key]["calories"] += r.calories or 0
        by_day[key]["protein_g"] += r.protein_g or 0

    weekly_trend = [
        DayPoint(date=(week_start + timedelta(days=i)).strftime("%Y-%m-%d"),
                  calories=by_day.get((week_start + timedelta(days=i)).strftime("%Y-%m-%d"), {}).get("calories", 0),
                  protein_g=by_day.get((week_start + timedelta(days=i)).strftime("%Y-%m-%d"), {}).get("protein_g", 0))
        for i in range(7)
    ]

    all_rows = db.query(MealRecord.food_name).all()
    counts = Counter(name for (name,) in all_rows)
    most_consumed = [FoodCount(food_name=name, count=c) for name, c in counts.most_common(5)]

    return DashboardResponse(
        has_data=True,
        today=today,
        weekly_trend=weekly_trend,
        most_consumed=most_consumed,
        meals_logged_total=total_meals,
    )
