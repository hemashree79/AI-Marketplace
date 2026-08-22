# =============================================================================
# storefront.py
# Replaces the old marketplace.py (which referenced an undefined `database`
# module, session['role'] that nothing ever sets, and endpoints that don't
# exist). This is the real "next page after login": the marketplace grid
# and each model's detail page, both driven by the actual catalog in
# model_data.py instead of "Model 01" / "Model 02" placeholders.
# =============================================================================
import re

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from model_data import AI_MODELS

storefront_bp = Blueprint("storefront", __name__)


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _star_string(score_out_of_5: int) -> str:
    """
    No separate "rating" field exists in model_data.py yet, so this reuses
    the real "quality" score (1-5) as the star rating rather than inventing
    a fake number. Swap this for a real ratings table/column later.
    """
    full = "\u2605" * score_out_of_5
    empty = "\u2606" * (5 - score_out_of_5)
    return full + empty


# Built once at import time: slug -> model dict, so /model/<slug> is a
# simple lookup instead of a linear scan.
_MODELS_BY_SLUG = {_slugify(model["name"]): model for model in AI_MODELS}


@storefront_bp.route("/marketplace")
@login_required
def marketplace():
    models = [
        dict(
            model,
            slug=_slugify(model["name"]),
            stars=_star_string(model["quality"]),
        )
        for model in AI_MODELS
    ]
    return render_template("marketplace.html", models=models, account=current_user)


@storefront_bp.route("/model/<slug>")
@login_required
def model_details(slug):
    model = _MODELS_BY_SLUG.get(slug)
    if model is None:
        abort(404)
    model = dict(model, stars=_star_string(model["quality"]))
    return render_template("model_details.html", model=model, slug=slug)
