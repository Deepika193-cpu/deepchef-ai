from typing import Literal
from pydantic import BaseModel

MealPlanGoal = Literal["weight_loss", "maintenance", "high_protein", "balanced_diet"]


class MealPlanRequest(BaseModel):
    goal: MealPlanGoal


class PlannedMeal(BaseModel):
    name: str
    description: str
    estimated_calories: int


class PlannedDay(BaseModel):
    day: str  # "Monday", "Tuesday", ...
    breakfast: PlannedMeal
    lunch: PlannedMeal
    dinner: PlannedMeal
    snack: PlannedMeal


class MealPlanResponse(BaseModel):
    goal: MealPlanGoal
    days: list[PlannedDay]
    disclaimer: str = "AI-generated meal suggestions. Not medical or dietetic advice — adjust to your own needs."
