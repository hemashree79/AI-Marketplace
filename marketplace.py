from flask import Blueprint, request, redirect, url_for, session
import Database

# Create another Blueprint for marketplace actions
market_bp = Blueprint('market', __name__)

@market_bp.route('/upload_model', methods=['POST'])
def upload_model():
    """Allows a Developer to upload a new AI model to the marketplace."""
    # Security check: Make sure they are logged in as a developer!
    if session.get('role') != 'developer':
        return "Access Denied: Only developers can upload models.", 403
        
    dev_id = session.get('user_id')
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    specs = request.form.get('specs')
    
    conn = database.get_db_connection()
    c = conn.cursor()
    
    # Note: Status defaults to 'pending' in the database!
    c.execute('''
        INSERT INTO products (developer_id, name, description, price, specs) 
        VALUES (?, ?, ?, ?, ?)
    ''', (dev_id, name, description, price, specs))
    
    conn.commit()
    conn.close()
    
    print(f"Model '{name}' uploaded successfully. Waiting for Admin approval.")
    return redirect(url_for('dev_dashboard'))

@market_bp.route('/approve_model/<int:product_id>')
def approve_model(product_id):
    """Allows an Admin to verify and approve a pending AI model."""
    # Security check: Make sure they are logged in as an admin!
    if session.get('role') != 'admin':
        return "Access Denied: Only admins can approve models.", 403
        
    conn = database.get_db_connection()
    c = conn.cursor()
    
    # Change the status from 'pending' to 'approved'
    c.execute("UPDATE products SET status = 'approved' WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    print(f"Model #{product_id} has been verified and approved!")
    return redirect(url_for('admin_dashboard'))