"""
config.py - Application configuration settings
Loads environment variables and configures Flask app settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask secret key for session management (use env variable in production)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'workforce-hub-secret-key-change-in-production')
    
    # MongoDB connection URI
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/workforce_hub')
    
    # Debug mode (disable in production)
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


# Map config names to config classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
