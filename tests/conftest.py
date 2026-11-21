"""
Test configuration and shared fixtures for pytest.
Sets up the Flask test client with a test database.
"""

import pytest
import os
import sys
from unittest.mock import MagicMock

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock cv2 and mediapipe if not installed on the system
try:
    import cv2
except ImportError:
    sys.modules['cv2'] = MagicMock()

try:
    import mediapipe
except ImportError:
    sys.modules['mediapipe'] = MagicMock()

from server.app import create_app
from server.config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Create a Flask application configured for testing."""
    test_app = create_app(config_class=TestingConfig)
    yield test_app


@pytest.fixture(scope='function')
def client(app):
    """Create a Flask test client for each test function."""
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client


@pytest.fixture(scope='function')
def clean_db(app):
    """
    Clean test database before each test.
    Drops all collections to ensure test isolation.
    """
    with app.app_context():
        db = app.db
        db.db.users.delete_many({})
        db.db.analyses.delete_many({})
        db.db.hairstyles.delete_many({})
        db.db.tryons.delete_many({})
    yield
    # Cleanup after test
    with app.app_context():
        db = app.db
        db.db.users.delete_many({})
        db.db.analyses.delete_many({})
        db.db.hairstyles.delete_many({})
        db.db.tryons.delete_many({})


@pytest.fixture
def auth_headers(client, clean_db):
    """
    Register a test user and return auth headers with JWT token.
    
    Returns:
        dict: {'Authorization': 'Bearer <token>'}
    """
    response = client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'TestPass123',
        'gender': 'female'
    })
    data = response.get_json()
    return {
        'Authorization': f"Bearer {data['token']}",
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_hairstyles(app, clean_db):
    """Insert sample hairstyles into the test database."""
    from datetime import datetime, timezone

    hairstyles = [
        {
            'name': 'Long Layered Waves',
            'slug': 'long-layered-waves',
            'face_shapes': ['oval', 'heart'],
            'gender': 'female',
            'hair_types': ['wavy', 'straight'],
            'description': 'Soft cascading layers',
            'image_url': '/test/image.jpg',
            'tags': ['layered', 'long'],
            'avg_rating': 4.5,
            'view_count': 100,
            'created_at': datetime.now(timezone.utc)
        },
        {
            'name': 'Classic Bob',
            'slug': 'classic-bob',
            'face_shapes': ['oval', 'diamond'],
            'gender': 'female',
            'hair_types': ['straight'],
            'description': 'A timeless chin-length bob',
            'image_url': '/test/bob.jpg',
            'tags': ['bob', 'short'],
            'avg_rating': 4.2,
            'view_count': 200,
            'created_at': datetime.now(timezone.utc)
        },
        {
            'name': 'Textured Quiff',
            'slug': 'textured-quiff',
            'face_shapes': ['round', 'square'],
            'gender': 'male',
            'hair_types': ['straight', 'wavy'],
            'description': 'A modern quiff with texture',
            'image_url': '/test/quiff.jpg',
            'tags': ['quiff', 'modern'],
            'avg_rating': 4.0,
            'view_count': 150,
            'created_at': datetime.now(timezone.utc)
        },
    ]

    with app.app_context():
        app.db.db.hairstyles.insert_many(hairstyles)

    return hairstyles
