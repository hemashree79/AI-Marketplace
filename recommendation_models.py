"""
models.py
---------
Lightweight data-shape helpers for the Recommendation Module.

This module intentionally does NOT touch any database. It only defines:
  - the set of valid questionnaire values (used for input validation)
  - a small helper to build a clean "UserRequirements" dict from request JSON

Keeping this separate from app.py and recommendation_engine.py keeps the
validation rules in one obvious place.
"""

VALID_BUDGETS = {"free", "0-500", "500-2000", "2000-5000", "5000+"}
VALID_MODEL_TYPES = {"text", "image", "audio", "video", "vision", "coding", "embeddings"}
VALID_API_REQUIREMENTS = {"required", "preferred", "not_required", "dont_know"}
VALID_TECHNICAL_LEVELS = {"beginner", "intermediate", "advanced"}

# Maps questionnaire budget strings to the same numeric tiers used in model_data.py
BUDGET_TIER_MAP = {
    "free": 0,
    "0-500": 1,
    "500-2000": 2,
    "2000-5000": 3,
    "5000+": 4,
}


class ValidationError(Exception):
    """Raised when incoming questionnaire data is missing or invalid."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def build_user_requirements(payload):
    """
    Validate and normalize the JSON body sent to POST /api/recommend.

    Expected payload:
    {
        "budget": "0-500",
        "model_type": "image",
        "api_required": "required",
        "technical_level": "beginner"
    }

    Returns a clean dict on success, raises ValidationError on bad input.
    """
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")

    budget = payload.get("budget")
    model_type = payload.get("model_type")
    api_required = payload.get("api_required")
    technical_level = payload.get("technical_level")

    missing = [
        field_name
        for field_name, value in [
            ("budget", budget),
            ("model_type", model_type),
            ("api_required", api_required),
            ("technical_level", technical_level),
        ]
        if not value
    ]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")

    if budget not in VALID_BUDGETS:
        raise ValidationError(f"Invalid budget value: '{budget}'")
    if model_type not in VALID_MODEL_TYPES:
        raise ValidationError(f"Invalid model_type value: '{model_type}'")
    if api_required not in VALID_API_REQUIREMENTS:
        raise ValidationError(f"Invalid api_required value: '{api_required}'")
    if technical_level not in VALID_TECHNICAL_LEVELS:
        raise ValidationError(f"Invalid technical_level value: '{technical_level}'")

    return {
        "budget": budget,
        "model_type": model_type,
        "api_required": api_required,
        "technical_level": technical_level,
    }
