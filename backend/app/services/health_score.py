"""
DeepChef Nutrition Score: an application-generated 0-100 heuristic, not a
clinical or medical measurement. It only scores attributes that are actually
present in the nutrition data for that food — if e.g. sugar or sodium wasn't
returned by USDA, that factor is simply skipped rather than assumed.

Method (per-serving values, after portion scaling):
- Protein and fiber contribute positively (satiety / nutrient density).
- Fat, sugar, and sodium contribute negatively past moderate thresholds.
- Calories are scored against a rough "moderate meal" reference (600 kcal)
  rather than a strict cap, since a filling healthy meal isn't penalized
  just for being substantial.
This is a simple, transparent, documented rule set — not a trained model
and not a substitute for professional dietary advice.
"""
from app.schemas.nutrition import NutritionFacts

CALORIE_REFERENCE = 600  # kcal — rough "typical moderate meal" reference point


def compute_health_score(facts: NutritionFacts) -> dict:
    score = 100.0
    factors_used = []

    if facts.calories is not None:
        over = max(0, facts.calories - CALORIE_REFERENCE)
        score -= min(20, over / 40)  # up to -20 for very high-calorie portions
        factors_used.append("calories")

    if facts.fat_g is not None:
        score -= min(15, max(0, facts.fat_g - 15) * 0.8)
        factors_used.append("fat")

    if facts.sugar_g is not None:
        score -= min(15, max(0, facts.sugar_g - 10) * 1.0)
        factors_used.append("sugar")

    if facts.sodium_mg is not None:
        score -= min(15, max(0, facts.sodium_mg - 600) / 40)
        factors_used.append("sodium")

    if facts.protein_g is not None:
        score += min(10, facts.protein_g * 0.4)
        factors_used.append("protein")

    if facts.fiber_g is not None:
        score += min(10, facts.fiber_g * 1.2)
        factors_used.append("fiber")

    score = round(max(0, min(100, score)))

    return {
        "score": score,
        "label": "DeepChef Nutrition Score",
        "factors_used": factors_used,
        "disclaimer": "Application-generated score based on available nutrition data. Not a medical or clinical measurement.",
    }
