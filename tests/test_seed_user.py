"""
Unit tests for initial user seed script.
"""

from database.seed_user import seed_user, hash_password
import bcrypt


def test_hash_password():
    """Verify bcrypt hash generation and verification."""
    pwd = "user1234"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert bcrypt.checkpw(pwd.encode('utf-8'), hashed.encode('utf-8'))


def test_seed_user_function(clean_db):
    """Test seed_user inserts and force-updates the user."""
    user_id = seed_user(
        email="user@example.com",
        password="user1234",
        name="Test User",
        force=True
    )
    assert user_id is not None
