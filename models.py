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


# =============================================================================
# Model
# Creator-uploaded AI models. Predefined/demo models stay in model_data.py -
# ONLY dynamically uploaded creator models live in this table.
# =============================================================================
class Model(db.Model):
    __tablename__ = "models"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    logo = db.Column(db.String(255), nullable=True)  # filename only, e.g. "3f9a1c.png"

    model_type = db.Column(db.String(50), nullable=False)   # Text/Image/Video/Audio/Vision/Coding/Embeddings/Other
    category = db.Column(db.String(100), nullable=False)

    use_cases = db.Column(db.Text, nullable=True)
    features = db.Column(db.Text, nullable=True)
    technical_requirements = db.Column(db.Text, nullable=True)

    api_available = db.Column(db.Boolean, nullable=False, default=False)
    version = db.Column(db.String(30), nullable=True)

    accuracy = db.Column(db.String(30), nullable=True)     # free text, e.g. "94%"
    performance = db.Column(db.String(30), nullable=True)  # free text, e.g. "Fast"

    monthly_price = db.Column(db.Float, nullable=False, default=0.0)
    yearly_price = db.Column(db.Float, nullable=False, default=0.0)

    # Who uploaded it - links back to the Users table (a "creator" role account).
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    creator = db.relationship("User", backref="uploaded_models")

    # PENDING -> APPROVED / REJECTED. Never deleted, even if rejected.
    status = db.Column(db.String(20), nullable=False, default="PENDING")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Model id={self.id} name={self.name} status={self.status}>"
