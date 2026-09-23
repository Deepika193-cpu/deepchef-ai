from unittest.mock import MagicMock, patch

VALID_LLM_JSON = """{
  "recipe_name": "Classic Pizza",
  "description": "A traditional recipe.",
  "ingredients": ["dough", "sauce", "cheese"],
  "quantities": ["1", "100g", "150g"],
  "prep_time_minutes": 15,
  "cook_time_minutes": 12,
  "difficulty": "medium",
  "instructions": ["Prep", "Bake"],
  "estimated_calories": 600,
  "protein_g": 25,
  "carbohydrates_g": 70,
  "fat_g": 20,
  "fiber_g": 3
}"""


def _mock_completion(content: str):
    return MagicMock(choices=[MagicMock(message=MagicMock(content=content))])


def test_stored_recipe_generates_and_caches_on_first_request(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.recipe_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion(VALID_LLM_JSON)
        response = client.get("/api/recipes/Pizza")
    assert response.status_code == 200
    body = response.json()
    assert body["recipe"]["recipe_name"] == "Classic Pizza"
    assert body["generated_by"] == "groq-llama"


def test_stored_recipe_second_request_uses_cache_not_llm(client, monkeypatch):
    """Second lookup for the same food must NOT call Groq again."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.recipe_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion(VALID_LLM_JSON)
        first = client.get("/api/recipes/Pizza")
        assert first.status_code == 200
        call_count_after_first = MockGroq.return_value.chat.completions.create.call_count

        second = client.get("/api/recipes/Pizza")
        assert second.status_code == 200
        assert second.json()["generated_by"] == "cached"
        # Call count to the LLM must not have increased.
        assert MockGroq.return_value.chat.completions.create.call_count == call_count_after_first


def test_stored_recipe_slug_is_case_insensitive(client, monkeypatch):
    """'Pizza' and 'pizza' should hit the same cached row."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.recipe_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion(VALID_LLM_JSON)
        client.get("/api/recipes/Pizza")
        response = client.get("/api/recipes/pizza")
    assert response.json()["generated_by"] == "cached"


def test_stored_recipe_missing_api_key(client, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.get("/api/recipes/SomeNewFood")
    assert response.status_code == 503
