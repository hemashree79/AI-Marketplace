from flask import Blueprint, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import Database

# Create a 'Blueprint' to keep our login code separate from the main app
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Securely registers a new user, admin, or developer."""
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role') # 'user', 'admin', or 'developer'
    
    # Hash the password for security!
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    
    conn = Database.get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                  (username, hashed_pw, role))
        conn.commit()
        print(f"Successfully registered {role}: {username}")
    except:
        print("Username already exists!")
        
    conn.close()
    return redirect(url_for('home'))

@auth_bp.route('/login_submit', methods=['POST'])
def login_submit():
    """Securely logs the user in and starts a session."""
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = Database.get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    # Check if user exists AND if the password matches the secure hash
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['role'] = user['role']
        print(f"Logged in as {user['role']}")
        
        # Redirect them to their specific dashboard based on their role!
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user['role'] == 'developer':
            return redirect(url_for('dev_dashboard'))
    
    # If login fails, send them back to the homepage
    return redirect(url_for('home'))

@auth_bp.route('/logout')
def logout():
    """Clears the secure session."""
    session.clear()
    return redirect(url_for('home'))