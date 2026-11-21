from datetime import datetime, timezone
from flask_login import UserMixin


class User(UserMixin):
    """User object wrapper for Flask-Login session management."""

    def __init__(self, user_doc):
        self.user_doc = user_doc
        self.id = str(user_doc['_id'])
        self.name = user_doc.get('name', '')
        self.email = user_doc.get('email', '')
        self.gender = user_doc.get('gender', 'other')
        self.role = user_doc.get('role', 'user')
        self.preferences = user_doc.get('preferences', {})
        self.password_hash = user_doc.get('password_hash', '')
        self._is_active = user_doc.get('is_active', True)

    @property
    def is_active(self):
        return self._is_active

    @property
    def is_admin(self):
        return self.role == 'admin'

    def get_id(self):
        return self.id


class UserModel:
    """Schema and helpers for the users collection."""

    COLLECTION = 'users'

    @staticmethod
    def create_document(name, email, password_hash, gender='other', role='user'):
        """
        Build a new user document ready for MongoDB insertion.
        """
        return {
            'name': name,
            'email': email.lower().strip(),
            'password_hash': password_hash,
            'gender': gender,
            'role': role,
            'preferences': {
                'hair_type': '',
                'hair_length': '',
                'style_preference': ''
            },
            'is_active': True,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }

    @staticmethod
    def to_response(user_doc):
        """
        Serialize a user document for API response (strips sensitive fields).
        """
        return {
            'user_id': str(user_doc['_id']),
            'name': user_doc.get('name', ''),
            'email': user_doc.get('email', ''),
            'gender': user_doc.get('gender', 'other'),
            'role': user_doc.get('role', 'user'),
            'is_active': user_doc.get('is_active', True),
            'preferences': user_doc.get('preferences', {}),
            'created_at': user_doc.get('created_at', datetime.now(timezone.utc)).isoformat()
            if isinstance(user_doc.get('created_at'), datetime) else str(user_doc.get('created_at', ''))
        }
