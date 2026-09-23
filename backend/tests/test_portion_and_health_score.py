from app.schemas.nutrition import NutritionFacts
from app.services.portion import scale_facts, PORTION_GRAMS
from app.services.health_score import compute_health_score


def test_scale_facts_medium_is_2_5x_the_100g_base():
    facts = NutritionFacts(calories=100, protein_g=10, carbohydrates_g=20, fat_g=5, fiber_g=2)
    scaled = scale_facts(facts, "medium")
    assert scaled.calories == 250  # 250g portion, per-100g base of 100
    assert scaled.protein_g == 25


def test_scale_facts_handles_missing_values():
    facts = NutritionFacts(calories=100, protein_g=None, carbohydrates_g=20, fat_g=None, fiber_g=None)
    scaled = scale_facts(facts, "small")
    assert scaled.protein_g is None
    assert scaled.calories == 150  # 150g small portion


def test_portion_grams_ordering():
    assert PORTION_GRAMS["small"] < PORTION_GRAMS["medium"] < PORTION_GRAMS["large"]


def test_health_score_only_uses_available_attributes():
    # No sugar/sodium data at all — those factors should be skipped, not assumed.
    facts = NutritionFacts(calories=400, protein_g=20, carbohydrates_g=40, fat_g=10, fiber_g=5)
    result = compute_health_score(facts)
    assert "sugar" not in result["factors_used"]
    assert "sodium" not in result["factors_used"]
    assert "protein" in result["factors_used"]
    assert 0 <= result["score"] <= 100


def test_health_score_high_sugar_lowers_score():
    low_sugar = NutritionFacts(calories=300, sugar_g=2)
    high_sugar = NutritionFacts(calories=300, sugar_g=50)
    assert compute_health_score(high_sugar)["score"] < compute_health_score(low_sugar)["score"]


def test_health_score_is_never_presented_as_medical():
    facts = NutritionFacts(calories=300)
    result = compute_health_score(facts)
    assert "not a medical" in result["disclaimer"].lower()
