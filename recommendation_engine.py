"""
recommendation_engine.py
-------------------------
All scoring / ranking logic for the AI Model Recommendation system.

Score breakdown (100 points total):
    Model type / use-case match  -> 40 points
    Budget match                 -> 25 points
    API requirement match        -> 20 points
    Technical-level match        -> 15 points

app.py should only call `get_recommendations(user_requirements)` and
return the result as JSON. It should never compute scores itself.
"""

from model_data import AI_MODELS, TECHNICAL_LEVEL_ORDER
from recommendation_models import BUDGET_TIER_MAP

MAX_TYPE_SCORE = 40
MAX_BUDGET_SCORE = 25
MAX_API_SCORE = 20
MAX_TECHNICAL_SCORE = 15


def _score_type_match(model, user_model_type):
    """40 points if the model's category matches what the user asked for."""
    if model["model_type"] == user_model_type:
        return MAX_TYPE_SCORE, True
    return 0, False


def _score_budget_match(model, user_budget_key):
    """
    25 points max, based on how the model's price tier compares to the
    user's budget tier.

    - Model fits within (or under) the user's budget tier -> full 25
    - Model is exactly one tier above the user's budget      -> partial 12
    - Model is more than one tier above                      -> 0
    """
    user_tier = BUDGET_TIER_MAP[user_budget_key]
    model_tier = model["price_tier"]

    if model_tier <= user_tier:
        return MAX_BUDGET_SCORE, True
    if model_tier == user_tier + 1:
        return 12, False
    return 0, False


def _score_api_match(model, user_api_requirement):
    """
    20 points max, based on the user's stated API need vs. availability.

    required      -> full points only if API is available
    preferred     -> full points if available, partial if not
    not_required  -> full points regardless (user doesn't care)
    dont_know     -> moderate points regardless (neutral/no penalty)
    """
    has_api = model["api_available"]

    if user_api_requirement == "required":
        return (MAX_API_SCORE, True) if has_api else (0, False)
    if user_api_requirement == "preferred":
        return (MAX_API_SCORE, True) if has_api else (10, False)
    if user_api_requirement == "not_required":
        return MAX_API_SCORE, True
    if user_api_requirement == "dont_know":
        return (15, True) if has_api else (10, False)
    return 0, False


def _score_technical_match(model, user_technical_level):
    """
    15 points max, based on whether the user's experience level is enough
    to comfortably use the model.

    - Model's required level <= user's level        -> full 15
    - Model's required level is one step higher      -> partial 8
    - Model's required level is much higher          -> 0
    """
    user_level = TECHNICAL_LEVEL_ORDER[user_technical_level]
    model_level = TECHNICAL_LEVEL_ORDER[model["technical_level"]]

    if model_level <= user_level:
        return MAX_TECHNICAL_SCORE, True
    if model_level == user_level + 1:
        return 8, False
    return 0, False


def _build_explanation(type_ok, budget_ok, api_ok, technical_ok, user_requirements):
    """
    Build a list of human-readable "why recommended" bullet points based on
    which components actually matched -- never a generic/static explanation.
    """
    reasons = []

    if type_ok:
        reasons.append("Matches your requested model type")
    if budget_ok:
        reasons.append("Fits your budget")
    if api_ok and user_requirements["api_required"] in ("required", "preferred"):
        reasons.append("API access available")
    elif api_ok and user_requirements["api_required"] == "not_required":
        reasons.append("API availability not a concern for your use case")
    if technical_ok:
        reasons.append("Suitable for your technical experience")

    if not reasons:
        reasons.append("Closest available match to your requirements")

    return reasons


def score_model(model, user_requirements):
    """Compute the full score + explanation for a single model."""
    type_score, type_ok = _score_type_match(model, user_requirements["model_type"])
    budget_score, budget_ok = _score_budget_match(model, user_requirements["budget"])
    api_score, api_ok = _score_api_match(model, user_requirements["api_required"])
    technical_score, technical_ok = _score_technical_match(
        model, user_requirements["technical_level"]
    )

    total_score = type_score + budget_score + api_score + technical_score

    return {
        "total_score": total_score,
        "match_percentage": round(total_score),
        "breakdown": {
            "type_match": type_score,
            "budget_match": budget_score,
            "api_match": api_score,
            "technical_match": technical_score,
        },
        "reasons": _build_explanation(type_ok, budget_ok, api_ok, technical_ok, user_requirements),
    }


def get_recommendations(user_requirements, top_n=5):
    """
    Score every model in the catalog against the user's requirements and
    return the top_n highest-scoring models, sorted best-first.
    """
    scored_models = []

    for model in AI_MODELS:
        result = score_model(model, user_requirements)
        scored_models.append({
            "name": model["name"],
            "provider": model["provider"],
            "model_type": model["model_type"],
            "price_note": model["price_note"],
            "api_available": model["api_available"],
            "technical_level": model["technical_level"],
            "description": model["description"],
            "use_cases": model["use_cases"],
            "quality": model["quality"],
            "speed": model["speed"],
            "match_percentage": result["match_percentage"],
            "score_breakdown": result["breakdown"],
            "reasons": result["reasons"],
        })

    scored_models.sort(key=lambda m: m["match_percentage"], reverse=True)

    return scored_models[:top_n]
