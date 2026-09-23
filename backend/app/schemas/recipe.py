from typing import Optional, Literal
from pydantic import BaseModel, Field

DietaryPreference = Literal[
    "high_protein", "weight_loss", "vegetarian", "vegan", "indian_style", "low_carb", "custom", "classic"
]


class RecipeGenerationRequest(BaseModel):
    detected_food: str
    preference: DietaryPreference
    custom_preference: Optional[str] = Field(
        default=None, description="Required text when preference == 'custom'"
    )
    portion: Literal["small", "medium", "large"] = "medium"
    nutrition_goal: Optional[str] = None


class GeneratedRecipe(BaseModel):
    recipe_name: str
    description: str
    ingredients: list[str]
    quantities: list[str]
    prep_time_minutes: int
    cook_time_minutes: int
    difficulty: Literal["easy", "medium", "hard"]
    instructions: list[str]
    estimated_calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    fiber_g: float


class RecipeGenerationResponse(BaseModel):
    recipe: GeneratedRecipe
    generated_by: str = "groq-llama"
    disclaimer: str = "AI-generated suggestion. Nutrition values are estimates, not medical or clinically verified figures."
