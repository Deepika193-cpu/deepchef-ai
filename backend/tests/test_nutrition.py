from unittest.mock import MagicMock, patch

USDA_FOUND_RESPONSE = {
    "foods": [
        {
            "fdcId": 12345,
            "description": "Pizza",
            "foodNutrients": [
                {"nutrientName": "Energy", "value": 266, "unitName": "KCAL"},
                {"nutrientName": "Protein", "value": 11, "unitName": "G"},
                {"nutrientName": "Carbohydrate, by difference", "value": 33, "unitName": "G"},
                {"nutrientName": "Total lipid (fat)", "value": 10, "unitName": "G"},
                {"nutrientName": "Fiber, total dietary", "value": 2.3, "unitName": "G"},
            ],
        }
    ]
}

USDA_EMPTY_RESPONSE = {"foods": []}


def _mock_httpx_response(json_data, status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_lookup_known_food(client, monkeypatch):
    monkeypatch.setenv("USDA_FDC_API_KEY", "test-key")
    with patch("app.services.nutrition_lookup.httpx.get") as mock_get:
        mock_get.return_value = _mock_httpx_response(USDA_FOUND_RESPONSE)
        response = client.get("/api/nutrition/lookup", params={"food": "Pizza", "portion": "medium"})
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["is_exact_match"] is True
    assert body["facts"]["calories"] is not None
    assert body["health_score"] is not None


def test_lookup_unknown_food(client, monkeypatch):
    monkeypatch.setenv("USDA_FDC_API_KEY", "test-key")
    with patch("app.services.nutrition_lookup.httpx.get") as mock_get:
        mock_get.return_value = _mock_httpx_response(USDA_EMPTY_RESPONSE)
        response = client.get("/api/nutrition/lookup", params={"food": "Nonexistent Dish XYZ"})
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is False
    assert "No nutrition data found" in body["message"]


def test_lookup_usda_api_failure(client, monkeypatch):
    monkeypatch.setenv("USDA_FDC_API_KEY", "test-key")
    import httpx as httpx_module

    with patch("app.services.nutrition_lookup.httpx.get") as mock_get:
        mock_get.side_effect = httpx_module.TimeoutException("timed out")
        response = client.get("/api/nutrition/lookup", params={"food": "Pizza"})
    assert response.status_code == 503


def test_lookup_missing_api_key(client, monkeypatch):
    monkeypatch.delenv("USDA_FDC_API_KEY", raising=False)
    response = client.get("/api/nutrition/lookup", params={"food": "Pizza"})
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_portion_scaling_changes_values(client, monkeypatch):
    """Small vs large portion of the same food must return different scaled values."""
    monkeypatch.setenv("USDA_FDC_API_KEY", "test-key")
    with patch("app.services.nutrition_lookup.httpx.get") as mock_get:
        mock_get.return_value = _mock_httpx_response(USDA_FOUND_RESPONSE)
        small = client.get("/api/nutrition/lookup", params={"food": "Pizza", "portion": "small"}).json()
        large = client.get("/api/nutrition/lookup", params={"food": "Pizza", "portion": "large"}).json()

    assert small["facts"]["calories"] < large["facts"]["calories"]
    assert small["portion_grams"] == 150
    assert large["portion_grams"] == 350
