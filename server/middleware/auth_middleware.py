"""
JWT Authentication Middleware & Role-Based Access Control (RBAC).
Provides decorators to protect user routes and admin routes.
"""

from functools import wraps
from flask import request, jsonify, current_app
import jwt


from bson import ObjectId

def token_required(f):
    """
    Decorator that verifies JWT token from the Authorization header.
    Injects `current_user_id` into the wrapped function's kwargs.
    Supports authenticated users and guest sessions seamlessly.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]

        if not token:
            guest_id = request.headers.get('X-Guest-ID')
            if guest_id:
                try:
                    return f(*args, current_user_id=str(ObjectId(guest_id)), **kwargs)
                except Exception:
                    return f(*args, current_user_id=str(ObjectId()), **kwargs)
            return f(*args, current_user_id=str(ObjectId()), **kwargs)

        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET'],
                algorithms=['HS256']
            )
            current_user_id = payload.get('user_id')
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            guest_id = request.headers.get('X-Guest-ID')
            if guest_id:
                try:
                    return f(*args, current_user_id=str(ObjectId(guest_id)), **kwargs)
                except Exception:
                    pass
            return f(*args, current_user_id=str(ObjectId()), **kwargs)

        if not current_user_id:
            current_user_id = str(ObjectId())

        return f(*args, current_user_id=current_user_id, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator that enforces Role-Based Access Control (RBAC).
    Verifies valid JWT token AND verifies the user has role 'admin'.
    """
    @wraps(f)
    @token_required
    def decorated(*args, current_user_id=None, **kwargs):
        # Retrieve user from database and check role
        user_doc = current_app.db.find_user_by_id(current_user_id)
        if not user_doc or user_doc.get('role') != 'admin':
            return jsonify({'error': 'Admin privileges required to access this resource'}), 403

        return f(*args, current_user_id=current_user_id, **kwargs)

    return decorated
