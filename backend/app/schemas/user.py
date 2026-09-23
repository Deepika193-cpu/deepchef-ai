from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class HistoryCreateRequest(BaseModel):
    food_name: str
    image_url: Optional[str] = None
    confidence: Optional[float] = None
    source: str = "cnn"
    category: Optional[str] = None
    calories: Optional[float] = None


class HistoryItem(BaseModel):
    id: UUID
    food_name: str
    image_url: Optional[str]
    confidence: Optional[float]
    source: str
    category: Optional[str]
    calories: Optional[float]
    is_favorite: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteRecipeCreateRequest(BaseModel):
    recipe_name: str
    recipe_json: dict


class FavoriteRecipeItem(BaseModel):
    id: UUID
    recipe_name: str
    recipe_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    dietary_preference: Optional[str] = None
    nutrition_goal: Optional[str] = None
    favorite_foods: Optional[list[str]] = None
    preferred_portion: Optional[str] = None


class ProfileResponse(BaseModel):
    name: Optional[str]
    dietary_preference: Optional[str]
    nutrition_goal: Optional[str]
    favorite_foods: list[str]
    preferred_portion: str
    updated_at: datetime

    class Config:
        from_attributes = True
