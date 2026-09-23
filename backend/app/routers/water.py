from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import WaterRecord
from app.schemas.tracking import WaterAddRequest, WaterTodayResponse

router = APIRouter(prefix="/api/water", tags=["water"])

# General default daily goal (commonly cited ~2L/day guidance). Becomes
# user-configurable once Profile (Phase 20) stores personal targets.
DEFAULT_GOAL_ML = 2000


@router.post("", status_code=201)
def add_water(req: WaterAddRequest, db: Session = Depends(get_db)):
    record = WaterRecord(amount_ml=req.amount_ml)
    db.add(record)
    db.commit()
    return {"status": "ok"}


@router.get("/today", response_model=WaterTodayResponse)
def get_today_water(db: Session = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    rows = db.query(WaterRecord).filter(WaterRecord.logged_at >= today_start).all()
    total = sum(r.amount_ml for r in rows)
    return WaterTodayResponse(
        date=today_start.strftime("%Y-%m-%d"),
        total_ml=total,
        goal_ml=DEFAULT_GOAL_ML,
        progress_pct=round(min(100, total / DEFAULT_GOAL_ML * 100), 1),
    )
