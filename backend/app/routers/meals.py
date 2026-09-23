from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import MealRecord
from app.schemas.tracking import MealCreateRequest, MealResponse, DayMealsResponse

router = APIRouter(prefix="/api/meals", tags=["meals"])

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]


@router.post("", response_model=MealResponse, status_code=201)
def save_meal(req: MealCreateRequest, db: Session = Depends(get_db)):
    record = MealRecord(**req.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=DayMealsResponse)
def get_meals_for_day(
    date: str = Query(default=None, description="YYYY-MM-DD, defaults to today (UTC)"),
    db: Session = Depends(get_db),
):
    day = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    next_day = day + timedelta(days=1)

    rows = (
        db.query(MealRecord)
        .filter(MealRecord.logged_at >= day, MealRecord.logged_at < next_day)
        .order_by(MealRecord.logged_at)
        .all()
    )

    meals_by_type = defaultdict(list)
    totals = {"calories": 0.0, "protein_g": 0.0, "carbohydrates_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
    for r in rows:
        meals_by_type[r.meal_type].append(r)
        for field in totals:
            totals[field] += getattr(r, field) or 0

    return DayMealsResponse(
        date=day.strftime("%Y-%m-%d"),
        meals_by_type={mt: meals_by_type.get(mt, []) for mt in MEAL_TYPES},
        totals=totals,
    )
