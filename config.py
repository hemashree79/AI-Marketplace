import os

class Config:
    # This is a secret key for securing your logins
    SECRET_KEY = os.environ.get('SECRET_KEY') or "super-secret-codefury-key"
    
    # The name of your database file
    DB_NAME = "marketplace.db"