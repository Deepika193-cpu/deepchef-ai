from datetime import datetime, timedelta

from app.models import MealRecord


def _make_meal(food_name="Pizza", calories=400, days_ago=0):
    return MealRecord(
        food_name=food_name,
        meal_type="lunch",
        portion="medium",
        calories=calories,
        protein_g=15,
        carbohydrates_g=40,
        fat_g=12,
        fiber_g=3,
        logged_at=datetime.utcnow() - timedelta(days=days_ago),
    )


def test_dashboard_no_data(client):
    """No meals logged: real empty state, no fabricated charts."""
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["has_data"] is False
    assert body["today"] is None
    assert body["weekly_trend"] == []


def test_dashboard_one_meal(client, db_session):
    db_session.add(_make_meal(calories=400))
    db_session.commit()

    response = client.get("/api/dashboard")
    body = response.json()
    assert body["has_data"] is True
    assert body["today"]["calories"] == 400
    assert body["meals_logged_total"] == 1


def test_dashboard_multiple_meals_same_day(client, db_session):
    db_session.add(_make_meal(food_name="Pizza", calories=400))
    db_session.add(_make_meal(food_name="Salad", calories=200))
    db_session.commit()

    response = client.get("/api/dashboard")
    body = response.json()
    assert body["today"]["calories"] == 600
    assert body["meals_logged_total"] == 2


def test_dashboard_weekly_trend_spans_seven_days(client, db_session):
    db_session.add(_make_meal(calories=400, days_ago=0))
    db_session.add(_make_meal(calories=300, days_ago=3))
    db_session.add(_make_meal(calories=500, days_ago=6))
    db_session.commit()

    response = client.get("/api/dashboard")
    body = response.json()
    assert len(body["weekly_trend"]) == 7
    total_week_calories = sum(day["calories"] for day in body["weekly_trend"])
    assert total_week_calories == 1200


def test_dashboard_most_consumed_ranks_by_count(client, db_session):
    db_session.add(_make_meal(food_name="Pizza"))
    db_session.add(_make_meal(food_name="Pizza"))
    db_session.add(_make_meal(food_name="Salad"))
    db_session.commit()

    response = client.get("/api/dashboard")
    body = response.json()
    assert body["most_consumed"][0]["food_name"] == "Pizza"
    assert body["most_consumed"][0]["count"] == 2
