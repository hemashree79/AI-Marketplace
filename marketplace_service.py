# =============================================================================
# marketplace_service.py
#
# Single place that knows how to combine:
#   1. Predefined static models (model_data.py)
#   2. Creator-uploaded models from SQLite (models.py -> Model), APPROVED only
#
# into one consistent list of dicts that the marketplace page, the model
# details page, and the model card template can all treat identically -
# they never need to know whether a given model came from a Python file
# or the database.
# =============================================================================
from models import Model
from model_data import PREDEFINED_MODELS, get_predefined_model_by_id


def _serialize_db_model(m: Model) -> dict:
    """Turn a Model row into the same dict shape used by PREDEFINED_MODELS."""
    return {
        "id": f"db-{m.id}",
        "source": "db",
        "name": m.name,
        "description": m.description,
        "logo": m.logo,  # filename inside static/uploads/models/, or None
        "model_type": m.model_type,
        "category": m.category,
        "use_cases": m.use_cases,
        "features": m.features,
        "technical_requirements": m.technical_requirements,
        "api_available": bool(m.api_available),
        "version": m.version,
        "accuracy": m.accuracy,
        "performance": m.performance,
        "monthly_price": m.monthly_price,
        "yearly_price": m.yearly_price,
        "rating": None,  # creator models have no rating yet - no reviews system exists
        "price_tier": None,
        "technical_level": None,
        "quality": None,
        "speed": None,
        "creator_name": m.creator.name if m.creator else "Unknown Creator",
        "creator_bio": "Independent creator on AI Marketplace.",
        "creator_verified": False,  # no verification workflow exists yet
        "status": m.status,
    }


def get_marketplace_models() -> list[dict]:
    """
    Everything a normal user is allowed to see on the marketplace:
    all predefined models + only APPROVED creator models.
    """
    approved_db_models = Model.query.filter_by(status="APPROVED").order_by(Model.created_at.desc()).all()
    combined = list(PREDEFINED_MODELS) + [_serialize_db_model(m) for m in approved_db_models]
    return combined


def get_model_by_composite_id(model_id: str):
    """
    model_id looks like "static-1" or "db-7" (see the "id" field produced above).
    Returns a normalized dict, or None if not found / not visible.
    """
    if model_id.startswith("static-"):
        return get_predefined_model_by_id(model_id)

    if model_id.startswith("db-"):
        try:
            numeric_id = int(model_id.split("-", 1)[1])
        except (IndexError, ValueError):
            return None
        m = Model.query.get(numeric_id)
        return _serialize_db_model(m) if m else None

    return None
