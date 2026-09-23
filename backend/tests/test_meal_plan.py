import json
from unittest.mock import MagicMock, patch

def _make_day(name):
    meal = {"name": f"{name} meal", "description": "desc", "estimated_calories": 400}
    return {"day": name, "breakfast": meal, "lunch": meal, "dinner": meal, "snack": meal}


VALID_WEEK_JSON = json.dumps({
    "days": [_make_day(d) for d in
              ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
})

INCOMPLETE_WEEK_JSON = json.dumps({"days": [_make_day("Monday")]})


def _mock_completion(content: str):
    return MagicMock(choices=[MagicMock(message=MagicMock(content=content))])


def test_generate_meal_plan_success(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.meal_plan_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion(VALID_WEEK_JSON)
        response = client.post("/api/meal-plan/generate", json={"goal": "balanced_diet"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["days"]) == 7
    assert body["days"][0]["day"] == "Monday"


def test_generate_meal_plan_incomplete_week_is_rejected(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.meal_plan_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion(INCOMPLETE_WEEK_JSON)
        response = client.post("/api/meal-plan/generate", json={"goal": "high_protein"})
    assert response.status_code == 503


def test_generate_meal_plan_missing_api_key(client, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post("/api/meal-plan/generate", json={"goal": "weight_loss"})
    assert response.status_code == 503


def test_generate_meal_plan_invalid_goal_returns_422(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    response = client.post("/api/meal-plan/generate", json={"goal": "not_a_real_goal"})
    assert response.status_code == 422
