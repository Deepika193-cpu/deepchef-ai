"""
NOTE: no auth/user system exists yet (that's Phase 20 — User Profile).
MealRecord has a nullable user_id placeholder so the dashboard works
single-user today and can be scoped per-user later without a schema
rewrite — not pretending multi-user support exists before it does.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, JSON
from app.db import Base, GUID



class MealRecord(Base):
    __tablename__ = "meal_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True)  # populated once auth exists

    food_name = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)  # breakfast | lunch | dinner | snack
    portion = Column(String, nullable=False)  # small | medium | large

    calories = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbohydrates_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)

    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WaterRecord(Base):
    __tablename__ = "water_tracking"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True)

    amount_ml = Column(Integer, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PredictionHistory(Base):
    __tablename__ = "search_history"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True)

    food_name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    source = Column(String, nullable=False, default="cnn")  # cnn | vlm
    category = Column(String, nullable=True)
    calories = Column(Float, nullable=True)
    is_favorite = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FavoriteRecipe(Base):
    __tablename__ = "favorites"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True)

    recipe_name = Column(String, nullable=False)
    recipe_json = Column(JSON, nullable=False)  # full GeneratedRecipe payload
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserProfile(Base):
    """Single-row profile until real auth exists (Phase 20 scope note applies here too)."""
    __tablename__ = "user_preferences"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    dietary_preference = Column(String, nullable=True)
    nutrition_goal = Column(String, nullable=True)
    favorite_foods = Column(JSON, default=list)
    preferred_portion = Column(String, default="medium")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class StoredRecipe(Base):
    """
    'Stored recipe retrieval' — generate-once-then-cache. The first request
    for a given food generates a default (no dietary preference) recipe via
    Groq and saves it here; every request after that is a real DB read, no
    LLM call. This is genuinely retrieval from a growing recipe database —
    it's just seeded by generation instead of a scraped corpus, since the
    original project's chefkoch.de recipe text was never actually included
    in the uploaded repo (see Phase 1 inspection).
    """
    __tablename__ = "recipes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    food_slug = Column(String, unique=True, nullable=False, index=True)
    recipe_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
