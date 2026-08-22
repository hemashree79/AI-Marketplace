# =============================================================================
# models.py
# Single Users table shared by all three roles: "user", "creator", "admin".
# Distinguishing between them is done purely with the `role` column - there
# is no separate table per role.
# =============================================================================
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    # Email doubles as the login ID - must be unique across ALL roles.
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    contact_number = db.Column(db.String(20), nullable=False)

    # "student" or "working" - collected at registration, not used for logic yet.
    status = db.Column(db.String(20), nullable=False, default="working")

    password_hash = db.Column(db.String(255), nullable=False)

    # "user" | "creator" | "admin" - NEVER set directly from a form field.
    role = db.Column(db.String(20), nullable=False, default="user")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -------------------------------------------------------------------
    # Password helpers - passwords are NEVER stored or compared in plain text.
    # -------------------------------------------------------------------
    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
