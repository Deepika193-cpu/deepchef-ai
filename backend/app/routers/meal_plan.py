from fastapi import APIRouter, HTTPException

from app.schemas.meal_plan import MealPlanRequest, MealPlanResponse
from app.services.meal_plan_generator import generate_meal_plan, MealPlanError

router = APIRouter(prefix="/api/meal-plan", tags=["meal-plan"])


@router.post("/generate", response_model=MealPlanResponse)
def generate_weekly_meal_plan(req: MealPlanRequest):
    try:
        days = generate_meal_plan(req)
    except MealPlanError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return MealPlanResponse(goal=req.goal, days=days)
