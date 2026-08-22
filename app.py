from flask import Flask, redirect, url_for
from extensions import db
from flask_login import LoginManager
from models import User

import config
import auth
import marketplace as market

app = Flask(__name__)
app.secret_key = "super_secret_codefury_key"

# Configure the advanced SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Initialize Flask-Login for secure sessions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.role_select" # Sends them to the login page if they try to sneak in

# This tells Flask-Login how to find a user in the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Automatically create the database tables if they don't exist
with app.app_context():
    db.create_all()

# Register your Blueprints
app.register_blueprint(auth.auth_bp)
app.register_blueprint(market.market_bp)

# ==========================================
# MARKETPLACE ROUTES
# Note: The new auth.py handles the dashboards and logins now!
# ==========================================

@app.route('/store')
def store():
    # We changed this from '/' to '/store' because auth.py uses '/' for the login selector!
    return "Homepage working! Grid coming soon..."

@app.route('/buy/<int:model_id>')
def buy_model(model_id):
    # todo: figure out how the cart works
    return f"Buying model number {model_id}"

if __name__ == '__main__':
    app.run(debug=True)