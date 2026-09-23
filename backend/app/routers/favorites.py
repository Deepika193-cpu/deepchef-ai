from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FavoriteRecipe
from app.schemas.user import FavoriteRecipeCreateRequest, FavoriteRecipeItem

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("/recipes", response_model=FavoriteRecipeItem, status_code=201)
def add_favorite_recipe(req: FavoriteRecipeCreateRequest, db: Session = Depends(get_db)):
    record = FavoriteRecipe(recipe_name=req.recipe_name, recipe_json=req.recipe_json)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/recipes", response_model=list[FavoriteRecipeItem])
def list_favorite_recipes(db: Session = Depends(get_db)):
    return db.query(FavoriteRecipe).order_by(FavoriteRecipe.created_at.desc()).all()


@router.delete("/recipes/{item_id}", status_code=204)
def remove_favorite_recipe(item_id: str, db: Session = Depends(get_db)):
    record = db.query(FavoriteRecipe).filter(FavoriteRecipe.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Favorite not found.")
    db.delete(record)
    db.commit()
