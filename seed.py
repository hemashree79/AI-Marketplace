import sqlite3
import Database

def seed_data():
    conn = Database.get_db_connection()
    c = conn.cursor()

    # Create a fake Admin, Developer, and User
    c.execute("INSERT INTO users (username, password_hash, role) VALUES ('admin_bob', 'hashed_pw_1', 'admin')")
    c.execute("INSERT INTO users (username, password_hash, role) VALUES ('dev_alice', 'hashed_pw_2', 'developer')")
    c.execute("INSERT INTO users (username, password_hash, role) VALUES ('user_charlie', 'hashed_pw_3', 'user')")
    
    # Get the developer's ID (which is 2) to assign products to them
    dev_id = 2

    # Add some fake AI models for the marketplace
    c.execute("INSERT INTO products (developer_id, name, description, specs, price, status) VALUES (?, ?, ?, ?, ?, ?)", 
              (dev_id, 'Smart Receipt OCR', 'Extracts text from receipts.', 'Python, OpenCV', 15.99, 'approved'))
    
    c.execute("INSERT INTO products (developer_id, name, description, specs, price, status) VALUES (?, ?, ?, ?, ?, ?)", 
              (dev_id, 'Voice Sentiment AI', 'Analyzes tone of voice.', 'TensorFlow', 29.50, 'approved'))

    conn.commit()
    conn.close()
    print("Dummy data injected successfully!")

if __name__ == '__main__':
    seed_data()