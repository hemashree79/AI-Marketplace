# =============================================================================
# auth.py
# All authentication routes: user + creator registration/login, admin login
# (no admin registration route exists on purpose), logout, and the three
# temporary role-protected dashboards.
# =============================================================================
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User
from decorators import role_required

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")


# =============================================================================
# ROLE SELECTION / LANDING PAGE
# This is what /logout redirects back to, and where a fresh visitor picks
# whether they're a user, creator, or admin.
# =============================================================================
@auth_bp.route("/")
def role_select():
    return render_template("role_select.html")


# =============================================================================
# USER REGISTRATION
# =============================================================================
@auth_bp.route("/register/user", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        error = _validate_registration_form(request.form)
        if error:
            flash(error, "error")
            return render_template("user_register.html", form=request.form)

        user = User(
            name=request.form["name"].strip(),
            email=request.form["email"].strip().lower(),
            contact_number=request.form["contact_number"].strip(),
            status=request.form["status"],
            role="user",  # <-- role is hardcoded here, never read from the form
        )
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Your email is your Login ID.", "success")
        return redirect(url_for("auth.user_login"))

    return render_template("user_register.html", form={})


# =============================================================================
# USER LOGIN
# =============================================================================
@auth_bp.route("/login/user", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Filtering by role="user" here means a creator/admin account with
        # the same email+password combo (impossible anyway, emails are
        # globally unique) still couldn't log in through this form.
        account = User.query.filter_by(email=email, role="user").first()

        if account is None or not account.check_password(password):
            # Deliberately generic - never reveals whether the email exists.
            flash("Invalid email or password.", "error")
            return render_template("user_login.html")

        login_user(account)
        return redirect(url_for("auth.user_dashboard"))

    return render_template("user_login.html")


# =============================================================================
# CREATOR REGISTRATION
# =============================================================================
@auth_bp.route("/register/creator", methods=["GET", "POST"])
def creator_register():
    if request.method == "POST":
        error = _validate_registration_form(request.form)
        if error:
            flash(error, "error")
            return render_template("creator_register.html", form=request.form)

        creator = User(
            name=request.form["name"].strip(),
            email=request.form["email"].strip().lower(),
            contact_number=request.form["contact_number"].strip(),
            status=request.form["status"],
            role="creator",
        )
        creator.set_password(request.form["password"])
        db.session.add(creator)
        db.session.commit()

        flash("Creator account created successfully. Your email is your Login ID.", "success")
        return redirect(url_for("auth.creator_login"))

    return render_template("creator_register.html", form={})


# =============================================================================
# CREATOR LOGIN
# =============================================================================
@auth_bp.route("/login/creator", methods=["GET", "POST"])
def creator_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        account = User.query.filter_by(email=email, role="creator").first()

        if account is None or not account.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("creator_login.html")

        login_user(account)
        return redirect(url_for("auth.creator_dashboard"))

    return render_template("creator_login.html")


# =============================================================================
# ADMIN LOGIN
# No admin registration route exists anywhere in this file, on purpose -
# the only admin account is the one seeded in app.py.
# =============================================================================
@auth_bp.route("/login/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        account = User.query.filter_by(email=email, role="admin").first()

        if account is None or not account.check_password(password):
            flash("Invalid admin credentials.", "error")
            return render_template("admin_login.html")

        login_user(account)
        return redirect(url_for("auth.admin_dashboard"))

    return render_template("admin_login.html")


# =============================================================================
# LOGOUT (shared by all roles)
# =============================================================================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.role_select"))


# =============================================================================
# TEMPORARY ROLE-PROTECTED DASHBOARDS
# Just enough to prove the auth + role system works end-to-end. Real
# dashboards are a later phase.
# =============================================================================
@auth_bp.route("/user/dashboard")
@login_required
@role_required("user")
def user_dashboard():
    return render_template("user_dashboard.html", account=current_user)


@auth_bp.route("/creator/dashboard")
@login_required
@role_required("creator")
def creator_dashboard():
    return render_template("creator_dashboard.html", account=current_user)


@auth_bp.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    return render_template("admin_dashboard.html", account=current_user)


# =============================================================================
# SHARED REGISTRATION VALIDATION
# Used by both /register/user and /register/creator since the form shape
# is identical - only the resulting `role` differs.
# =============================================================================
def _validate_registration_form(form) -> str | None:
    """Returns an error message string if the form is invalid, else None."""
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    contact_number = form.get("contact_number", "").strip()
    status = form.get("status", "")
    password = form.get("password", "")
    confirm_password = form.get("confirm_password", "")

    if not all([name, email, contact_number, status, password, confirm_password]):
        return "All fields are required."

    if status not in ("student", "working"):
        return "Please select Student or Working."

    if not EMAIL_REGEX.match(email):
        return "Please enter a valid email address."

    if not PHONE_REGEX.match(contact_number):
        return "Please enter a valid contact number (7-15 digits)."

    if password != confirm_password:
        return "Password and Confirm Password do not match."

    if len(password) < 6:
        return "Password must be at least 6 characters long."

    if User.query.filter_by(email=email).first() is not None:
        return "An account with this email already exists."

    return None
