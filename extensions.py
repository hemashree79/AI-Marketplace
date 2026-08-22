# =============================================================================
# extensions.py
# Shared extension instances (db, login_manager) so both app.py and auth.py
# can import them without circular-import problems.
# =============================================================================
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
