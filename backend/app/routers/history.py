from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PredictionHistory
from app.schemas.user import HistoryCreateRequest, HistoryItem

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("", response_model=HistoryItem, status_code=201)
def log_prediction(req: HistoryCreateRequest, db: Session = Depends(get_db)):
    record = PredictionHistory(**req.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[HistoryItem])
def list_history(
    q: Optional[str] = Query(default=None, description="Search by food name"),
    favorites_only: bool = Query(default=False),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(PredictionHistory)
    if q:
        query = query.filter(PredictionHistory.food_name.ilike(f"%{q}%"))
    if favorites_only:
        query = query.filter(PredictionHistory.is_favorite.is_(True))
    return query.order_by(PredictionHistory.created_at.desc()).limit(limit).all()


@router.patch("/{item_id}/favorite", response_model=HistoryItem)
def toggle_favorite(item_id: str, db: Session = Depends(get_db)):
    record = db.query(PredictionHistory).filter(PredictionHistory.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="History item not found.")
    record.is_favorite = not record.is_favorite
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{item_id}", status_code=204)
def delete_history_item(item_id: str, db: Session = Depends(get_db)):
    record = db.query(PredictionHistory).filter(PredictionHistory.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="History item not found.")
    db.delete(record)
    db.commit()
