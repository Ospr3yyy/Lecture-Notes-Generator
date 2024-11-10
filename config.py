import os

class Config:
    # Flask configurations
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    
    # MongoDB configurations
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/database'

    # Additional configurations can go here, such as API keys, upload folder paths, etc.
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for file uploads
    
    # MySQL configurations
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or '120l'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
