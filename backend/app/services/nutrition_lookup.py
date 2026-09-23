"""
Nutrition lookup via USDA FoodData Central. The frontend never sees the API
key — all requests go through this backend service. When no exact match
exists for a detected food (e.g. "Biryani"), we return the closest ranked
result but mark it clearly as an approximation rather than presenting it as
authoritative.
"""
import os
from typing import Optional

import httpx

from app.schemas.nutrition import NutritionFacts, NutritionLookupResponse

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

NUTRIENT_MAP = {
    "Energy": "calories",
    "Protein": "protein_g",
    "Carbohydrate, by difference": "carbohydrates_g",
    "Total lipid (fat)": "fat_g",
    "Fiber, total dietary": "fiber_g",
    "Sugars, total including NLEA": "sugar_g",
    "Sodium, Na": "sodium_mg",
}


class NutritionLookupError(Exception):
    """Raised for a failure calling USDA — caller turns this into a clean HTTP error, never fake data."""


def _extract_facts(food_nutrients: list[dict]) -> NutritionFacts:
    values = {}
    for n in food_nutrients:
        name = n.get("nutrientName")
        field = NUTRIENT_MAP.get(name)
        if field and field not in values:
            values[field] = n.get("value")
    return NutritionFacts(**values)


def lookup_nutrition(food_name: str) -> NutritionLookupResponse:
    api_key = os.environ.get("USDA_FDC_API_KEY")
    if not api_key:
        raise NutritionLookupError("Nutrition lookup is unavailable: USDA_FDC_API_KEY is not configured.")

    try:
        resp = httpx.get(
            USDA_SEARCH_URL,
            params={
                "query": food_name,
                "api_key": api_key,
                "pageSize": 5,
                "dataType": ["Foundation", "SR Legacy"],
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.TimeoutException as e:
        raise NutritionLookupError("Nutrition lookup timed out. Please try again.") from e
    except httpx.HTTPStatusError as e:
        raise NutritionLookupError(f"USDA API returned an error (status {e.response.status_code}).") from e
    except httpx.HTTPError as e:
        raise NutritionLookupError("Could not reach the nutrition lookup service.") from e

    foods = data.get("foods", [])
    if not foods:
        return NutritionLookupResponse(
            query=food_name,
            found=False,
            message=f"No nutrition data found for '{food_name}'.",
        )

    best = foods[0]
    matched_name = best.get("description", "")
    is_exact = matched_name.strip().lower() == food_name.strip().lower()

    facts = _extract_facts(best.get("foodNutrients", []))

    return NutritionLookupResponse(
        query=food_name,
        matched_food_name=matched_name,
        fdc_id=best.get("fdcId"),
        is_exact_match=is_exact,
        facts=facts,
        per="100g",
        found=True,
        message=None if is_exact else f"Closest match for '{food_name}' — treat as an estimate.",
    )
