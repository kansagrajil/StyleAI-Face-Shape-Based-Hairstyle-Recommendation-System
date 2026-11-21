"""
Environment-based configuration for the Flask application.
Loads settings from .env file and provides config classes for
development, testing, and production environments.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration shared across all environments."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/faceshape')
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-change-me')
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', 24))
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'server/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200/hour')

    # ML Model paths
    MODEL_PATH = os.getenv('MODEL_PATH', 'ml/models/face_shape_model.h5')

    # Virtual Try-On Provider Configuration
    TRYON_PROVIDER = os.getenv('TRYON_PROVIDER', 'replicate')
    REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')
    REPLICATE_MODEL = os.getenv('REPLICATE_MODEL', 'openai/gpt-image-2.5-flare')
    REPLICATE_QUALITY = os.getenv('REPLICATE_QUALITY', 'low')

    # ComfyUI API Configuration (Alternative Provider)
    COMFYUI_API_URL = os.getenv('COMFYUI_API_URL', 'http://127.0.0.1:8188')
    COMFYUI_API_KEY = os.getenv('COMFYUI_API_KEY', '')
    COMFYUI_WORKFLOW_PATH = os.getenv('COMFYUI_WORKFLOW_PATH', 'workflow/sd1.5.json')
    COMFYUI_TIMEOUT = float(os.getenv('COMFYUI_TIMEOUT', 180.0))
    COMFYUI_POLL_INTERVAL = float(os.getenv('COMFYUI_POLL_INTERVAL', 1.0))

    # Face shape categories (7 target classes)
    FACE_SHAPES = ['oval', 'round', 'square', 'heart', 'diamond', 'oblong', 'triangle']


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    DEBUG = False
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/faceshape_test'


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PREFERRED_URL_SCHEME = 'https'


# Config selector
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


def get_config():
    """Return the config class based on FLASK_ENV environment variable."""
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)
