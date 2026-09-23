"""
Food recognition tests. Groq's vision model is mocked — never actually
called in this sandbox (no network). Run pytest locally to confirm.
"""
from unittest.mock import MagicMock, patch

RECOGNIZED_JSON = """{
  "is_food": true,
  "food_name": "Margherita Pizza",
  "category": "Italian",
  "confidence": "high",
  "alternative_guesses": ["Flatbread", "Focaccia"]
}"""

NOT_FOOD_JSON = """{
  "is_food": false,
  "food_name": "",
  "category": "",
  "confidence": "low",
  "alternative_guesses": []
}"""

LOW_CONFIDENCE_FOOD_JSON = """{
  "is_food": true,
  "food_name": "Some Soup",
  "category": "",
  "confidence": "low",
  "alternative_guesses": []
}"""


def _mock_completion(content: str):
    return MagicMock(choices=[MagicMock(message=MagicMock(content=content))])


def test_predict_valid_image_returns_recognized_food(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.vision_recognition.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion(RECOGNIZED_JSON)
        response = client.post(
            "/api/predict",
            files={"image": ("food.jpg", b"fake-jpeg-bytes", "image/jpeg")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["recognized"] is True
    assert body["food"] == "Margherita Pizza"
    assert body["source"] == "vlm"
    assert len(body["top_predictions"]) == 3  # main guess + 2 alternatives


def test_predict_not_food_returns_not_recognized(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.vision_recognition.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion(NOT_FOOD_JSON)
        response = client.post(
            "/api/predict",
            files={"image": ("not_food.jpg", b"fake-bytes", "image/jpeg")},
        )
    assert response.status_code == 200
    assert response.json()["recognized"] is False


def test_predict_low_confidence_food_treated_as_not_recognized(client, monkeypatch):
    """Even when is_food is true, a self-reported 'low' confidence must not
    be shown as a confident result — matches the spec's requirement."""
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.vision_recognition.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion(LOW_CONFIDENCE_FOOD_JSON)
        response = client.post(
            "/api/predict",
            files={"image": ("blurry.jpg", b"fake-bytes", "image/jpeg")},
        )
    assert response.status_code == 200
    assert response.json()["recognized"] is False


def test_predict_unsupported_file_type_returns_422(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    response = client.post(
        "/api/predict",
        files={"image": ("notes.txt", b"just text", "text/plain")},
    )
    assert response.status_code == 422


def test_predict_missing_image_field_returns_422(client):
    response = client.post("/api/predict")
    assert response.status_code == 422


def test_predict_missing_api_key(client, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post(
        "/api/predict",
        files={"image": ("food.jpg", b"fake-bytes", "image/jpeg")},
    )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_predict_malformed_vlm_response(client, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch("app.services.vision_recognition.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = _mock_completion("not json")
        response = client.post(
            "/api/predict",
            files={"image": ("food.jpg", b"fake-bytes", "image/jpeg")},
        )
    assert response.status_code == 503
