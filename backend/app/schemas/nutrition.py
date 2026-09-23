from typing import Optional
from pydantic import BaseModel


class NutritionFacts(BaseModel):
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sugar_g: Optional[float] = None
    sodium_mg: Optional[float] = None


class NutritionLookupResponse(BaseModel):
    query: str
    matched_food_name: Optional[str] = None
    fdc_id: Optional[int] = None
    is_exact_match: bool = False
    facts: Optional[NutritionFacts] = None
    per: str = "100g"
    portion: Optional[str] = None
    portion_grams: Optional[int] = None
    health_score: Optional[dict] = None
    found: bool = False
    message: Optional[str] = None
