import sqlite3

DB_NAME = "marketplace.db"

def init_db():
    """Initializes the database and creates necessary tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Create Users Table (Handles Admin, Developer, User roles)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL  -- 'admin', 'developer', or 'user'
        )
    ''')
    
    # 2. Create Products Table (AI Models uploaded by Developers)
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            developer_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            logo_url TEXT,
            specs TEXT,
            price REAL NOT NULL,
            status TEXT DEFAULT 'pending',  -- 'pending', 'approved', or 'rejected'
            FOREIGN KEY(developer_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database tables created successfully!")

# Helpful Database Functions for later:
def get_db_connection():
    """Returns a database connection that behaves like a dictionary"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    # If you run this file directly, it will just create the tables.
    init_db()