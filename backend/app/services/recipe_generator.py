"""
Recipe generation via Groq (Llama model). Structured JSON output, with
explicit handling for missing key / timeout / malformed response — the
frontend must never receive a silent failure or a fabricated recipe.
"""
import json
import os
from typing import Optional

from groq import Groq, APIConnectionError, APIStatusError, APITimeoutError

from app.schemas.recipe import GeneratedRecipe, RecipeGenerationRequest

PREFERENCE_LABELS = {
    "high_protein": "high protein",
    "weight_loss": "weight loss / calorie-conscious",
    "vegetarian": "vegetarian",
    "vegan": "vegan",
    "indian_style": "Indian style",
    "low_carb": "low carb",
    "classic": "classic / traditional preparation, no specific dietary restriction",
}

SYSTEM_PROMPT = """You are a recipe generation assistant for DeepChef AI. \
Given a detected food and a dietary preference, generate ONE original recipe \
inspired by that food, adapted to the preference. \
Respond with ONLY a single valid JSON object — no markdown, no commentary, no \
code fences — matching exactly this schema:

{
  "recipe_name": string,
  "description": string (1-2 sentences),
  "ingredients": string[],
  "quantities": string[] (same length and order as ingredients),
  "prep_time_minutes": integer,
  "cook_time_minutes": integer,
  "difficulty": "easy" | "medium" | "hard",
  "instructions": string[] (ordered steps),
  "estimated_calories": number (per serving),
  "protein_g": number,
  "carbohydrates_g": number,
  "fat_g": number,
  "fiber_g": number
}

Nutrition numbers are your best estimate for one serving, not clinically verified values."""


class RecipeGenerationError(Exception):
    """Raised for any failure generating a recipe — the caller turns this into a clean HTTP error."""


def _build_user_prompt(req: RecipeGenerationRequest) -> str:
    if req.preference == "custom":
        pref_text = req.custom_preference or "no specific preference, keep it balanced"
    else:
        pref_text = PREFERENCE_LABELS.get(req.preference, req.preference)

    parts = [
        f"Detected food: {req.detected_food}",
        f"Dietary preference: {pref_text}",
        f"Portion size: {req.portion}",
    ]
    if req.nutrition_goal:
        parts.append(f"Nutrition goal: {req.nutrition_goal}")
    return "\n".join(parts)


def generate_recipe(req: RecipeGenerationRequest) -> GeneratedRecipe:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RecipeGenerationError("Recipe generation is unavailable: GROQ_API_KEY is not configured.")

    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = Groq(api_key=api_key)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(req)},
            ],
            temperature=0.7,
            max_tokens=1200,
            response_format={"type": "json_object"},
            timeout=20,
        )
    except APITimeoutError as e:
        raise RecipeGenerationError("Recipe generation timed out. Please try again.") from e
    except APIConnectionError as e:
        raise RecipeGenerationError("Could not reach the recipe generation service.") from e
    except APIStatusError as e:
        raise RecipeGenerationError(f"Recipe generation service returned an error (status {e.status_code}).") from e

    raw_content = completion.choices[0].message.content
    try:
        data = json.loads(raw_content)
        return GeneratedRecipe(**data)
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        raise RecipeGenerationError("Recipe generation returned an unexpected format. Please try again.") from e
