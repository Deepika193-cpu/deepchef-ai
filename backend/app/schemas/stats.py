from pydantic import BaseModel


class StatsResponse(BaseModel):
    foods_recognized: int
    recipes_available: int
    meals_analyzed: int