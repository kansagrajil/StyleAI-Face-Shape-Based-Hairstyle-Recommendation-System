


"""
Authentication Routes.
Handles user registration, login, logout, password reset, and profile retrieval.
Endpoints:
  - POST /api/auth/register
  - POST /api/auth/login
  - POST /api/auth/logout
  - GET  /api/auth/profile
  - PUT  /api/auth/profile
  - POST /api/auth/forgot-password
  - POST /api/auth/reset-password
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from server.models.user import UserModel, User
from server.services.auth_service import AuthService
from server.middleware.auth_middleware import token_required
from server.utils.validators import validate_email, validate_password, validate_gender

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    gender = data.get('gender', 'other').lower()

    # Validate inputs
    if not name or len(name) < 2:
        return jsonify({'error': 'Name must be at least 2 characters'}), 400

    valid, err = validate_email(email)
    if not valid:
        return jsonify({'error': err}), 400

    valid, err = validate_password(password)
    if not valid:
        return jsonify({'error': err}), 400

    valid, err = validate_gender(gender)
    if not valid:
        return jsonify({'error': err}), 400

    # Check if email already exists
    db = current_app.db
    if db.find_user_by_email(email):
        return jsonify({'error': 'An account with this email already exists'}), 409

    # Hash password and create user
    auth_service = AuthService(
        current_app.config['JWT_SECRET'],
        current_app.config['JWT_EXPIRY_HOURS']
    )
    password_hash = auth_service.hash_password(password)
    user_doc = UserModel.create_document(name, email, password_hash, gender)
    user_id = db.create_user(user_doc)
    user_doc['_id'] = user_id

    # Log user in via Flask-Login
    user_obj = User(user_doc)
    login_user(user_obj)

    # Generate token
    token = auth_service.generate_token(user_id)

    return jsonify({
        'user_id': str(user_id),
        'token': token,
        'name': name
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Find user
    db = current_app.db
    user_doc = db.find_user_by_email(email)
    if not user_doc:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Verify password
    auth_service = AuthService(
        current_app.config['JWT_SECRET'],
        current_app.config['JWT_EXPIRY_HOURS']
    )
    if not auth_service.verify_password(password, user_doc['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Log user in via Flask-Login
    user_obj = User(user_doc)
    login_user(user_obj)

    # Generate token
    token = auth_service.generate_token(user_doc['_id'])

    return jsonify({
        'user_id': str(user_doc['_id']),
        'token': token,
        'name': user_doc['name']
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout the current user session via Flask-Login.
    """
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    """
    Get the current user's profile.
    """
    user = current_app.db.find_user_by_id(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(UserModel.to_response(user)), 200


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    """
    Update the current user's profile and preferences.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    gender = data.get('gender')
    preferences = data.get('preferences')

    update_fields = {}
    if gender:
        valid, err = validate_gender(gender)
        if not valid:
            return jsonify({'error': err}), 400
        update_fields['gender'] = gender.lower()

    if preferences and isinstance(preferences, dict):
        update_fields['preferences'] = preferences

    if update_fields:
        current_app.db.update_user(current_user_id, update_fields)

    user = current_app.db.find_user_by_id(current_user_id)
    return jsonify(UserModel.to_response(user)), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Generate a password reset token for a registered email.
    """
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'error': 'Email address is required'}), 400

    email = data.get('email', '').strip().lower()
    user_doc = current_app.db.find_user_by_email(email)
    if not user_doc:
        # Avoid user enumeration by returning standard success message
        return jsonify({'message': 'If your email is registered, a password reset link has been generated.'}), 200

    auth_service = AuthService(current_app.config['JWT_SECRET'])
    reset_token = auth_service.generate_reset_token(user_doc['_id'])

    return jsonify({
        'message': 'Password reset token generated.',
        'reset_token': reset_token
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset user password using a valid reset token.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    reset_token = data.get('reset_token', '')
    new_password = data.get('new_password', '')

    if not reset_token or not new_password:
        return jsonify({'error': 'Reset token and new password are required'}), 400

    valid, err = validate_password(new_password)
    if not valid:
        return jsonify({'error': err}), 400

    auth_service = AuthService(current_app.config['JWT_SECRET'])
    try:
        user_id = auth_service.decode_reset_token(reset_token)
    except Exception as e:
        return jsonify({'error': 'Invalid or expired reset token'}), 400

    # Update password hash in MongoDB
    password_hash = auth_service.hash_password(new_password)
    current_app.db.update_user(user_id, {'password_hash': password_hash})

    return jsonify({'message': 'Password reset successful. You can now log in.'}), 200


