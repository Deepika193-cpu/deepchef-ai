"""
Portion-based scaling for nutrition facts.

USDA FoodData Central nutrition values (from nutrition_lookup.py) are always
per 100g. To scale by portion size we need a reference weight in grams for
"small / medium / large" — this app uses the FDA's Reference Amounts
Customarily Consumed (RACC) framework as its documented basis: RACC values
for a mixed/prepared dish typically fall in the 140g (small side dish) to
250g (standard entree) to 400g (large entree) range. We use the midpoints
of that published range as fixed reference weights, applied as a simple
linear scale of the per-100g values. This is a general-purpose estimate,
not a food-specific measurement — it's surfaced to the user as such.

Source: FDA 21 CFR 101.12 RACC tables (food-category reference amounts).
"""
from typing import Literal

from app.schemas.nutrition import NutritionFacts

PortionSize = Literal["small", "medium", "large"]

# Reference weights in grams — documented assumption, not per-dish measured data.
PORTION_GRAMS: dict[PortionSize, int] = {
    "small": 150,
    "medium": 250,
    "large": 350,
}


def scale_facts(facts: NutritionFacts, portion: PortionSize) -> NutritionFacts:
    """Scale per-100g facts to the reference weight for the given portion size."""
    grams = PORTION_GRAMS[portion]
    factor = grams / 100

    def scaled(value):
        return round(value * factor, 1) if value is not None else None

    return NutritionFacts(
        calories=scaled(facts.calories),
        protein_g=scaled(facts.protein_g),
        carbohydrates_g=scaled(facts.carbohydrates_g),
        fat_g=scaled(facts.fat_g),
        fiber_g=scaled(facts.fiber_g),
        sugar_g=scaled(facts.sugar_g),
        sodium_mg=scaled(facts.sodium_mg),
    )
