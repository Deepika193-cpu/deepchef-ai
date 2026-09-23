from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel

MealType = Literal["breakfast", "lunch", "dinner", "snack"]
PortionSize = Literal["small", "medium", "large"]


class MealCreateRequest(BaseModel):
    food_name: str
    meal_type: MealType
    portion: PortionSize
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None


class MealResponse(BaseModel):
    id: UUID
    food_name: str
    meal_type: MealType
    portion: PortionSize
    calories: Optional[float]
    protein_g: Optional[float]
    carbohydrates_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    logged_at: datetime

    class Config:
        from_attributes = True


class DayMealsResponse(BaseModel):
    date: str
    meals_by_type: dict[str, list[MealResponse]]
    totals: dict[str, float]


class WaterAddRequest(BaseModel):
    amount_ml: int


class WaterTodayResponse(BaseModel):
    date: str
    total_ml: int
    goal_ml: int
    progress_pct: float
