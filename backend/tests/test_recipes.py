"""
Recipe generation tests. Groq is mocked throughout — this sandbox has no
network access, so these have been reviewed for correctness but never
actually executed. Run `pytest` locally to confirm.
"""
import os
from unittest.mock import MagicMock, patch

import pytest

VALID_LLM_JSON = """{
  "recipe_name": "Test Recipe",
  "description": "A test recipe.",
  "ingredients": ["flour", "water"],
  "quantities": ["200g", "100ml"],
  "prep_time_minutes": 10,
  "cook_time_minutes": 20,
  "difficulty": "easy",
  "instructions": ["Mix", "Cook"],
  "estimated_calories": 400,
  "protein_g": 10,
  "carbohydrates_g": 50,
  "fat_g": 12,
  "fiber_g": 4
}"""


def _mock_groq_completion(content: str):
    mock_message = MagicMock(content=content)
    mock_choice = MagicMock(message=mock_message)
    return MagicMock(choices=[mock_choice])


@pytest.mark.parametrize(
    "preference",
    ["high_protein", "weight_loss", "vegetarian", "vegan", "indian_style", "low_carb"],
)
def test_generate_recipe_for_each_preference(client, preference, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.recipe_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_groq_completion(VALID_LLM_JSON)
        response = client.post(
            "/api/recipes/generate",
            json={"detected_food": "Pizza", "preference": preference, "portion": "medium"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["recipe"]["recipe_name"] == "Test Recipe"
    assert "disclaimer" in body


def test_generate_recipe_custom_preference_requires_text(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    response = client.post(
        "/api/recipes/generate",
        json={"detected_food": "Pizza", "preference": "custom", "portion": "medium"},
    )
    assert response.status_code == 422


def test_generate_recipe_missing_api_key(client, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post(
        "/api/recipes/generate",
        json={"detected_food": "Pizza", "preference": "high_protein", "portion": "medium"},
    )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_generate_recipe_timeout(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    from groq import APITimeoutError

    # NOTE: constructed via __new__ to sidestep the real constructor's
    # signature (which needs an httpx.Request) — untested against the
    # actual groq package locally since it isn't installed in this
    # sandbox. Verify this instantiation works once you run pytest for real;
    # adjust to `APITimeoutError(request=<mock>)` if __new__ turns out
    # insufficient for your installed groq version.
    fake_timeout_error = object.__new__(APITimeoutError)

    with patch("app.services.recipe_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.side_effect = fake_timeout_error
        response = client.post(
            "/api/recipes/generate",
            json={"detected_food": "Pizza", "preference": "high_protein", "portion": "medium"},
        )
    assert response.status_code == 503
    assert "timed out" in response.json()["detail"].lower()


def test_generate_recipe_invalid_llm_response(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.recipe_generator.Groq") as MockGroq:
        # Malformed: not valid JSON at all
        MockGroq.return_value.chat.completions.create.return_value = _mock_groq_completion("not json")
        response = client.post(
            "/api/recipes/generate",
            json={"detected_food": "Pizza", "preference": "high_protein", "portion": "medium"},
        )
    assert response.status_code == 503
    assert "unexpected format" in response.json()["detail"].lower()
