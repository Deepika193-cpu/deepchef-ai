"""
Weekly meal plan generation via Groq, structured JSON output. Mirrors the
error-handling pattern from recipe_generator.py — same failure modes,
same "never fabricate a fallback plan" rule.
"""
import json
import os

from groq import Groq, APIConnectionError, APIStatusError, APITimeoutError

from app.schemas.meal_plan import MealPlanRequest, PlannedDay

GOAL_LABELS = {
    "weight_loss": "weight loss (calorie-conscious, high satiety)",
    "maintenance": "weight maintenance (balanced calories)",
    "high_protein": "high protein (muscle building/maintenance focus)",
    "balanced_diet": "balanced diet (general healthy eating, no specific goal)",
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

SYSTEM_PROMPT = """You are a meal-planning assistant for DeepChef AI. Given a \
weekly nutrition goal, generate a 7-day meal plan (Monday through Sunday). \
Respond with ONLY a single valid JSON object — no markdown, no commentary, no \
code fences — matching exactly this schema:

{
  "days": [
    {
      "day": "Monday",
      "breakfast": {"name": string, "description": string, "estimated_calories": integer},
      "lunch": {"name": string, "description": string, "estimated_calories": integer},
      "dinner": {"name": string, "description": string, "estimated_calories": integer},
      "snack": {"name": string, "description": string, "estimated_calories": integer}
    },
    ... (7 entries total, Monday through Sunday, in order)
  ]
}

Vary the meals across the week rather than repeating the same dish every day. \
Calories are your best estimate per serving, not clinically verified values."""


class MealPlanError(Exception):
    """Raised for any failure generating a meal plan — caller turns this into a clean HTTP error."""


def generate_meal_plan(req: MealPlanRequest) -> list[PlannedDay]:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise MealPlanError("Meal plan generation is unavailable: GROQ_API_KEY is not configured.")

    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = Groq(api_key=api_key)

    goal_text = GOAL_LABELS.get(req.goal, req.goal)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Weekly nutrition goal: {goal_text}"},
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"},
            timeout=30,
        )
    except APITimeoutError as e:
        raise MealPlanError("Meal plan generation timed out. Please try again.") from e
    except APIConnectionError as e:
        raise MealPlanError("Could not reach the meal plan generation service.") from e
    except APIStatusError as e:
        raise MealPlanError(f"Meal plan generation service returned an error (status {e.status_code}).") from e

    raw_content = completion.choices[0].message.content
    try:
        data = json.loads(raw_content)
        days = [PlannedDay(**d) for d in data["days"]]
    except (json.JSONDecodeError, TypeError, KeyError, ValueError) as e:
        raise MealPlanError("Meal plan generation returned an unexpected format. Please try again.") from e

    if len(days) != 7:
        raise MealPlanError("Meal plan generation returned an incomplete week. Please try again.")

    return days
