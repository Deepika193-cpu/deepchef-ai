import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import StoredRecipe
from app.schemas.recipe import RecipeGenerationRequest, RecipeGenerationResponse
from app.services.recipe_generator import generate_recipe, RecipeGenerationError

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _slugify(food_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", food_name.strip().lower()).strip("-")


@router.post("/generate", response_model=RecipeGenerationResponse)
def generate_personalized_recipe(req: RecipeGenerationRequest):
    if req.preference == "custom" and not req.custom_preference:
        raise HTTPException(status_code=422, detail="custom_preference is required when preference is 'custom'.")

    try:
        recipe = generate_recipe(req)
    except RecipeGenerationError as e:
        # 503: the failure is the LLM service, not the client's request
        raise HTTPException(status_code=503, detail=str(e))

    return RecipeGenerationResponse(recipe=recipe)


@router.get("/{food_name}", response_model=RecipeGenerationResponse)
def get_stored_recipe(food_name: str, db: Session = Depends(get_db)):
    """
    'Stored' recipe retrieval — generate-once, cache-forever per food.
    First request for a given food generates a default (no dietary
    preference) recipe and saves it; every request after that is a plain
    DB read, no LLM call. See StoredRecipe in models.py for why this
    counts as genuine retrieval and not just a relabeled generation call.
    """
    slug = _slugify(food_name)
    existing = db.query(StoredRecipe).filter(StoredRecipe.food_slug == slug).first()
    if existing:
        return RecipeGenerationResponse(recipe=existing.recipe_json, generated_by="cached")

    try:
        recipe = generate_recipe(
            RecipeGenerationRequest(detected_food=food_name, preference="classic", portion="medium")
        )
    except RecipeGenerationError as e:
        raise HTTPException(status_code=503, detail=str(e))

    record = StoredRecipe(food_slug=slug, recipe_json=recipe.model_dump())
    db.add(record)
    db.commit()

    return RecipeGenerationResponse(recipe=recipe)
