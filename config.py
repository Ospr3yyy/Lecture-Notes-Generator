import os

class Config:
    # Flask configurations
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    
    # MongoDB configurations
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/database'

    # Additional configurations can go here, such as API keys, upload folder paths, etc.
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for file uploads

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
