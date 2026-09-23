"""
Food recognition endpoint — backed by Groq's vision model (see
app/services/vision_recognition.py) rather than a fine-tuned CNN.

Honesty note (still applies): the Phase 1.5 plan was a fine-tuned
EfficientNetB0 on Food-101 as the primary recognizer, with a vision-LLM
as a fallback for anything outside its trained classes. That CNN was
never trained. What's below is genuinely working, open-vocabulary
recognition via the VLM alone — real, not a stub — but it is NOT the
calibrated, fixed-class CNN originally planned. If you train that CNN
later, this becomes the fallback tier it was always meant to be, and
`source` can switch to "cnn" with a real numeric confidence for the
cases it covers.
"""
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.predict import PredictionResponse, TopPrediction
from app.services.vision_recognition import recognize_food, RecognitionError

router = APIRouter(prefix="/api/predict", tags=["predict"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("", response_model=PredictionResponse)
async def predict_food(image: UploadFile = File(...)):
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{image.content_type}'. Upload a JPEG, PNG, or WEBP image.",
        )

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")

    try:
        result = recognize_food(image_bytes, image.content_type)
    except RecognitionError as e:
        raise HTTPException(status_code=503, detail=str(e))

    is_food = bool(result.get("is_food"))
    confidence_label = result.get("confidence", "low")
    # Treat the model's own "low" self-rating the same as "not recognized" —
    # matches the spec's requirement to show "not confidently recognized"
    # rather than force a shaky guess onto the screen.
    if not is_food or not result.get("food_name") or confidence_label == "low":
        return PredictionResponse(
            recognized=False,
            confidence_label=confidence_label,
            message="Food not confidently recognized.",
        )

    alternatives = result.get("alternative_guesses") or []
    return PredictionResponse(
        recognized=True,
        food=result["food_name"],
        category=result.get("category") or None,
        confidence_label=result.get("confidence", "medium"),
        top_predictions=[TopPrediction(label=result["food_name"])]
        + [TopPrediction(label=a) for a in alternatives[:4]],
        source="vlm",
    )
