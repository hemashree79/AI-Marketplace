from flask import Blueprint, request, redirect, url_for
from extensions import db
from models import Product
from flask_login import current_user

market_bp = Blueprint('market', __name__)

@market_bp.route('/upload_model', methods=['POST'])
def upload_model():
    if current_user.is_authenticated and current_user.role == 'creator':
        new_model = Product(
            developer_id=current_user.id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=request.form.get('price'),
            specs=request.form.get('specs'),
            status='pending'
        )
        db.session.add(new_model)
        db.session.commit()
    return redirect(url_for('auth.creator_dashboard'))

@market_bp.route('/approve_model/<int:product_id>')
def approve_model(product_id):
    if current_user.is_authenticated and current_user.role == 'admin':
        model = Product.query.get(product_id)
        if model:
            model.status = 'approved'
            db.session.commit()
    return redirect(url_for('auth.admin_dashboard'))