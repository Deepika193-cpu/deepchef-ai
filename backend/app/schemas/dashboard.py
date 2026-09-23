from typing import Optional
from pydantic import BaseModel


class DailyTotals(BaseModel):
    calories: float = 0
    protein_g: float = 0
    carbohydrates_g: float = 0
    fat_g: float = 0
    fiber_g: float = 0
    water_ml: float = 0


class DayPoint(BaseModel):
    date: str
    calories: float = 0
    protein_g: float = 0


class FoodCount(BaseModel):
    food_name: str
    count: int


class DashboardResponse(BaseModel):
    has_data: bool
    today: Optional[DailyTotals] = None
    weekly_trend: list[DayPoint] = []
    most_consumed: list[FoodCount] = []
    meals_logged_total: int = 0
