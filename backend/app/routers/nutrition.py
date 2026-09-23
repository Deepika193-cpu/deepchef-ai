from fastapi import APIRouter, HTTPException, Query

from app.schemas.nutrition import NutritionLookupResponse
from app.services.nutrition_lookup import lookup_nutrition, NutritionLookupError
from app.services.portion import scale_facts, PORTION_GRAMS, PortionSize
from app.services.health_score import compute_health_score

router = APIRouter(prefix="/api/nutrition", tags=["nutrition"])


@router.get("/lookup", response_model=NutritionLookupResponse)
def get_nutrition(
    food: str = Query(..., min_length=1, description="Detected food name, e.g. 'Pizza'"),
    portion: PortionSize = Query("medium", description="small | medium | large"),
):
    try:
        result = lookup_nutrition(food)
    except NutritionLookupError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not result.found or result.facts is None:
        return result

    scaled = scale_facts(result.facts, portion)
    result.facts = scaled
    result.per = f"{PORTION_GRAMS[portion]}g ({portion} portion)"
    result.portion = portion
    result.portion_grams = PORTION_GRAMS[portion]
    result.health_score = compute_health_score(scaled)
    return result
