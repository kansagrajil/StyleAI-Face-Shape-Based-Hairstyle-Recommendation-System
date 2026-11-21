"""
Authentication Service.
Handles password hashing with bcrypt and JWT token generation/verification.
"""

from datetime import datetime, timedelta, timezone
import bcrypt
import jwt


class AuthService:
    """Password hashing and JWT token operations."""

    def __init__(self, jwt_secret, jwt_expiry_hours=24):
        """
        Args:
            jwt_secret: Secret key for JWT signing.
            jwt_expiry_hours: Token validity duration in hours.
        """
        self.jwt_secret = jwt_secret
        self.jwt_expiry_hours = jwt_expiry_hours

    # ── Password Hashing ──────────────────────────────────

    @staticmethod
    def hash_password(plain_password):
        """
        Hash a plaintext password using bcrypt (12 rounds).
        
        Args:
            plain_password: The plaintext password string.
        
        Returns:
            str: The bcrypt hash string.
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verify a plaintext password against a bcrypt hash.
        
        Args:
            plain_password: The plaintext password to check.
            hashed_password: The stored bcrypt hash.
        
        Returns:
            bool: True if the password matches.
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    # ── JWT Token Operations ──────────────────────────────

    def generate_token(self, user_id, role='user'):
        """
        Generate a JWT access token for a user.
        
        Args:
            user_id: The user's MongoDB ObjectId as a string.
            role: User role ('user' or 'admin').
        
        Returns:
            str: Encoded JWT token.
        """
        payload = {
            'user_id': str(user_id),
            'role': role,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=self.jwt_expiry_hours)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def decode_token(self, token):
        """
        Decode and verify a JWT token.
        
        Args:
            token: The encoded JWT string.
        
        Returns:
            dict: Decoded payload with user_id.
        
        Raises:
            jwt.ExpiredSignatureError: If the token is expired.
            jwt.InvalidTokenError: If the token is invalid.
        """
        return jwt.decode(token, self.jwt_secret, algorithms=['HS256'])

    # ── Password Reset Tokens ──────────────────────────────

    def generate_reset_token(self, user_id):
        """
        Generate a password reset token valid for 1 hour.
        """
        payload = {
            'reset_user_id': str(user_id),
            'type': 'password_reset',
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def decode_reset_token(self, token):
        """
        Decode and verify a password reset token.
        """
        payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
        if payload.get('type') != 'password_reset':
            raise jwt.InvalidTokenError('Invalid reset token type')
        return payload.get('reset_user_id')

