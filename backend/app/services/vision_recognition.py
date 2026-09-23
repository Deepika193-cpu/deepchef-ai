"""
Food recognition via Groq's vision-capable model (multimodal Llama), used
in place of a fine-tuned CNN. This is a real, working implementation —
not a stub — but it's architecturally different from the CNN originally
planned (Phase 1.5), and that difference matters:

- A fine-tuned CNN gives a calibrated confidence score (softmax probability)
  over a fixed, known set of classes.
- This VLM gives an open-vocabulary judgment with a self-reported
  qualitative confidence ("high"/"medium"/"low") — genuinely useful, but
  not a calibrated number, and there's no fixed class list to validate
  against. We surface this honestly: `source: "vlm"` and no numeric
  confidence in the API response, which the frontend already renders
  differently (an "AI-identified" badge instead of a percentage bar).

Model: meta-llama/llama-4-scout-17b-16e-instruct (Groq's current
vision-capable model as of this writing — check
https://console.groq.com/docs/vision for the current model ID, since
these change). Base64-encoded images are supported directly, capped at
4MB per Groq's documented limit for base64 payloads.
"""
import base64
import json
import os

from groq import Groq, APIConnectionError, APIStatusError, APITimeoutError

MAX_BASE64_BYTES = 4 * 1024 * 1024  # Groq's documented limit for base64 image payloads
VISION_MODEL = os.environ.get("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

SYSTEM_PROMPT = """You are a food recognition assistant for DeepChef AI. \
Look at the image and identify the food shown, if any. \
Respond with ONLY a single valid JSON object — no markdown, no commentary, no \
code fences — matching exactly this schema:

{
  "is_food": boolean,
  "food_name": string,      // e.g. "Margherita Pizza" — empty string if is_food is false
  "category": string,       // general cuisine/category, e.g. "Italian", "Dessert" — empty string if not applicable
  "confidence": "high" | "medium" | "low",
  "alternative_guesses": string[]  // 0-4 other plausible names, most to least likely, excluding food_name
}

If the image does not clearly show a single food item (e.g. it's blurry, not food, \
or shows an ambiguous mix), set is_food to false and confidence to "low" rather \
than guessing."""


class RecognitionError(Exception):
    """Raised for a failure calling the vision model — caller turns this into a clean HTTP error."""


def recognize_food(image_bytes: bytes, mime_type: str) -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RecognitionError("Food recognition is unavailable: GROQ_API_KEY is not configured.")

    if len(image_bytes) > MAX_BASE64_BYTES:
        raise RecognitionError(
            f"Image is too large for recognition (max {MAX_BASE64_BYTES // (1024*1024)}MB). "
            "Please upload a smaller photo."
        )

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{encoded}"

    client = Groq(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": SYSTEM_PROMPT},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"},
            timeout=45,
        )
    except APITimeoutError as e:
        raise RecognitionError("Food recognition timed out. Please try again.") from e
    except APIConnectionError as e:
        raise RecognitionError("Could not reach the food recognition service.") from e
    except APIStatusError as e:
        raise RecognitionError(f"Food recognition service returned an error (status {e.status_code}).") from e

    raw_content = completion.choices[0].message.content
    try:
        data = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as e:
        raise RecognitionError("Food recognition returned an unexpected format. Please try again.") from e

    return data
