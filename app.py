# =============================================================================
# app.py
# Application entry point. Run with:  python app.py
#
# This file:
#   1. Configures Flask + SQLite (via Flask-SQLAlchemy)
#   2. Configures Flask-Login (session-based auth)
#   3. Registers the auth blueprint (all routes live in auth.py)
#   4. Creates the database tables on first run
#   5. Seeds ONE temporary admin account for testing (see seed_admin() below)
# =============================================================================
import os
from flask import Flask
from extensions import db, login_manager
from models import User


def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))

    # CHANGE THIS before any real deployment - fine as-is for a hackathon.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "marketplace.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.role_select"  # where @login_required sends anonymous users

    # Import AFTER db.init_app so the blueprints' models/queries work correctly.
    from auth import auth_bp
    from model_routes import models_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(models_bp)

    # Where creator-uploaded logos get saved (created if missing).
    os.makedirs(os.path.join(basedir, "static", "uploads", "models"), exist_ok=True)

    with app.app_context():
        db.create_all()   # creates marketplace.db + tables if missing (users, models)
        seed_admin()       # ensures exactly one admin account exists

    return app


# -----------------------------------------------------------------------
# Flask-Login needs this to reload a user object from the session on every
# request. Must be registered on the login_manager instance somewhere that
# always runs - here is fine since app.py is the entry point.
# -----------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def seed_admin():
    """
    Creates ONE hardcoded admin account if it doesn't already exist.
    There is intentionally NO admin registration page anywhere in this app -
    this is the only way an admin account gets created.

    TEMPORARY credentials for hackathon/dev testing only.
    Change ADMIN_EMAIL / ADMIN_PASSWORD (or set via environment variables)
    before any real deployment.
    """
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@marketplace.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")

    existing = User.query.filter_by(email=ADMIN_EMAIL).first()
    if existing is None:
        admin = User(
            name="Admin",
            email=ADMIN_EMAIL,
            contact_number="0000000000",
            status="working",
            role="admin",
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"[seed] Created default admin account -> {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
