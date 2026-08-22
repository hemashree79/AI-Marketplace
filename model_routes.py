# =============================================================================
# model_routes.py
#
# Everything related to the creator-upload -> admin-approval -> marketplace
# pipeline. Kept separate from auth.py so the existing authentication file
# stays untouched, per the requirement to preserve existing auth exactly.
# =============================================================================
import os
import uuid
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    current_app, abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db
from models import Model
from decorators import role_required
from marketplace_service import get_marketplace_models, get_model_by_composite_id

models_bp = Blueprint("models_bp", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MODEL_TYPES = {"Text", "Image", "Video", "Audio", "Vision", "Coding", "Embeddings", "Other"}


def _allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def _save_logo(file_storage):
    """
    Saves an uploaded logo under static/uploads/models/ with a random-safe
    filename and returns just the filename (not the full path) - that's
    what gets stored in Model.logo. Returns None if no file was provided.
    Raises ValueError with a friendly message on invalid files.
    """
    if not file_storage or file_storage.filename == "":
        return None

    if not _allowed_file(file_storage.filename):
        raise ValueError("Logo must be a PNG, JPG, JPEG, or WEBP image.")

    safe_name = secure_filename(file_storage.filename)
    ext = safe_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "models")
    os.makedirs(upload_dir, exist_ok=True)

    file_storage.save(os.path.join(upload_dir, unique_name))
    return unique_name


# =============================================================================
# MARKETPLACE (shared - used by both the plain user view and the creator's
# extended view, see auth.py -> user_dashboard / creator_dashboard, which
# both import get_marketplace_models() themselves and render home.html)
# =============================================================================

@models_bp.route("/model/<model_id>")
@login_required
def model_details(model_id):
    """
    Shows one model's full details page. Reachable by any logged-in role.
    A creator model is only visible here if it's APPROVED, UNLESS the
    viewer is the creator who owns it or an admin - so creators/admins can
    still check on pending/rejected submissions.
    """
    model = get_model_by_composite_id(model_id)
    if model is None:
        flash("That model could not be found.", "error")
        return redirect(url_for("auth.role_select"))

    if model["source"] == "db" and model.get("status") != "APPROVED":
        is_owner = (
            current_user.role == "creator"
            and model_id.startswith("db-")
            and _db_model_belongs_to(model_id, current_user.id)
        )
        if not (is_owner or current_user.role == "admin"):
            flash("This model is not currently available.", "error")
            return redirect(url_for("auth.role_select"))

    return render_template("model_details.html", model=model)


def _db_model_belongs_to(composite_id: str, creator_id: int) -> bool:
    numeric_id = int(composite_id.split("-", 1)[1])
    row = Model.query.get(numeric_id)
    return row is not None and row.creator_id == creator_id


# =============================================================================
# CREATOR: UPLOAD A NEW MODEL
# =============================================================================
@models_bp.route("/creator/upload", methods=["GET", "POST"])
@login_required
@role_required("creator")
def creator_upload():
    if request.method == "POST":
        error = _validate_upload_form(request.form)
        if error:
            flash(error, "error")
            return render_template("creator_upload.html", form=request.form, model_types=sorted(MODEL_TYPES))

        try:
            logo_filename = _save_logo(request.files.get("logo"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("creator_upload.html", form=request.form, model_types=sorted(MODEL_TYPES))

        new_model = Model(
            name=request.form["name"].strip(),
            description=request.form["description"].strip(),
            logo=logo_filename,
            model_type=request.form["model_type"],
            category=request.form["category"].strip(),
            use_cases=request.form.get("use_cases", "").strip(),
            features=request.form.get("features", "").strip(),
            technical_requirements=request.form.get("technical_requirements", "").strip(),
            api_available=(request.form.get("api_available") == "yes"),
            version=request.form.get("version", "").strip(),
            accuracy=request.form.get("accuracy", "").strip(),
            performance=request.form.get("performance", "").strip(),
            monthly_price=float(request.form["monthly_price"]),
            yearly_price=float(request.form["yearly_price"]),
            creator_id=current_user.id,
            status="PENDING",
        )

        try:
            db.session.add(new_model)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Something went wrong saving your model. Please try again.", "error")
            return render_template("creator_upload.html", form=request.form, model_types=sorted(MODEL_TYPES))

        flash("Model submitted successfully and is waiting for admin approval.", "success")
        return redirect(url_for("auth.creator_dashboard"))

    return render_template("creator_upload.html", form={}, model_types=sorted(MODEL_TYPES))


def _validate_upload_form(form):
    name = form.get("name", "").strip()
    description = form.get("description", "").strip()
    category = form.get("category", "").strip()
    model_type = form.get("model_type", "")
    monthly_price = form.get("monthly_price", "")
    yearly_price = form.get("yearly_price", "")

    if not name:
        return "Model name is required."
    if not description:
        return "Model description is required."
    if not category:
        return "Category is required."
    if model_type not in MODEL_TYPES:
        return "Please choose a valid model type."
    if form.get("api_available") not in ("yes", "no"):
        return "Please specify whether an API is available."

    try:
        m_price = float(monthly_price)
        y_price = float(yearly_price)
        if m_price < 0 or y_price < 0:
            raise ValueError()
    except ValueError:
        return "Monthly and yearly price must be valid, non-negative numbers."

    return None


# =============================================================================
# ADMIN: PENDING APPROVALS LIST (rendered inside admin_dashboard.html itself -
# see auth.py -> admin_dashboard, which queries pending models and passes
# them in directly, so there's no separate route needed just to list them)
# =============================================================================

@models_bp.route("/admin/model/<int:model_id>/view")
@login_required
@role_required("admin")
def admin_model_view(model_id):
    model = Model.query.get_or_404(model_id)
    return render_template("admin_model_view.html", model=model)


@models_bp.route("/admin/model/<int:model_id>/approve", methods=["POST"])
@login_required
@role_required("admin")
def admin_model_approve(model_id):
    model = Model.query.get_or_404(model_id)
    model.status = "APPROVED"
    db.session.commit()
    flash(f'"{model.name}" has been approved and is now live on the marketplace.', "success")
    return redirect(url_for("auth.admin_dashboard"))


@models_bp.route("/admin/model/<int:model_id>/reject", methods=["POST"])
@login_required
@role_required("admin")
def admin_model_reject(model_id):
    model = Model.query.get_or_404(model_id)
    model.status = "REJECTED"
    db.session.commit()
    flash(f'"{model.name}" has been rejected.', "success")
    return redirect(url_for("auth.admin_dashboard"))
