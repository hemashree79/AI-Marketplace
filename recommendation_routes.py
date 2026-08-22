"""
recommendation_routes.py
-------------------------
Blueprint version of the AI Model Recommendation module, meant to be
registered on your EXISTING Flask app (the one in your old app.py).

This file replaces recommendation_module/app.py from the standalone
version. It does not create its own Flask() instance, does not touch
your auth, your existing routes, or your database config — it only
defines a blueprint with a page route and an API route.

Copy this file into your project alongside:
    recommendation_engine.py
    model_data.py
    models.py
    templates/recommendation.html
    static/recommendation.css
    static/recommendation.js

Then, in your OLD app.py, add just two lines (shown at the bottom of
this file's docstring and in the chat message).
"""

from flask import Blueprint, render_template, request, jsonify, current_app

from recommendation_models import build_user_requirements, ValidationError
from recommendation_engine import get_recommendations

# url_prefix keeps every route under /recommend/... so it can't collide
# with any of your existing routes. Change it if you'd prefer a different
# path (e.g. "/ai-recommend").
recommendation_bp = Blueprint(
    "recommendation",
    __name__,
    url_prefix="/recommend",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)


@recommendation_bp.route("/")
def recommendation_page():
    """Serve the recommendation questionnaire / results page."""
    return render_template("recommendation.html")


@recommendation_bp.route("/api/recommend", methods=["POST"])
def recommend():
    """
    Accepts questionnaire answers as JSON and returns the top 5 matching
    AI models with match percentages and explanations.

    Full path once registered: POST /recommend/api/recommend

    Expected JSON body:
    {
        "budget": "0-500",
        "model_type": "image",
        "api_required": "required",
        "technical_level": "beginner"
    }
    """
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify({
                "success": False,
                "error": "Request body must be valid JSON with a "
                         "'Content-Type: application/json' header."
            }), 400

        user_requirements = build_user_requirements(payload)
        recommendations = get_recommendations(user_requirements, top_n=5)

        if not recommendations:
            return jsonify({
                "success": True,
                "count": 0,
                "recommendations": [],
                "message": "No matching models were found for your requirements."
            }), 200

        return jsonify({
            "success": True,
            "count": len(recommendations),
            "recommendations": recommendations,
        }), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": e.message}), 400

    except Exception:
        current_app.logger.exception("Unexpected error in /recommend/api/recommend")
        return jsonify({
            "success": False,
            "error": "Something went wrong on the server while generating "
                     "recommendations. Please try again."
        }), 500
