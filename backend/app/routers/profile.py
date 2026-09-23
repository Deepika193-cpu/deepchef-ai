from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import UserProfile
from app.schemas.user import ProfileUpdateRequest, ProfileResponse

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _get_or_create(db: Session) -> UserProfile:
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile(favorite_foods=[], preferred_portion="medium")
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    return _get_or_create(db)


@router.put("", response_model=ProfileResponse)
def update_profile(req: ProfileUpdateRequest, db: Session = Depends(get_db)):
    profile = _get_or_create(db)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
