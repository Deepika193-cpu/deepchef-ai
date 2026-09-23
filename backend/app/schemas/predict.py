from typing import Optional
from pydantic import BaseModel


class TopPrediction(BaseModel):
    label: str


class PredictionResponse(BaseModel):
    recognized: bool
    food: Optional[str] = None
    category: Optional[str] = None
    confidence_label: Optional[str] = None  # "high" | "medium" | "low" — VLM self-report, not a calibrated score
    top_predictions: list[TopPrediction] = []
    source: str = "vlm"
    message: Optional[str] = None
