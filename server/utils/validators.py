"""
Input Validation Helpers.
Provides common validation functions for API request data.
"""

import re


def validate_email(email):
    """
    Validate an email address format.
    
    Returns:
        tuple: (is_valid: bool, error: str or None)
    """
    if not email:
        return False, 'Email is required'

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, 'Invalid email format'

    return True, None


def validate_password(password):
    """
    Validate password strength.
    Requirements: min 8 chars, at least one uppercase, one lowercase, one digit.
    
    Returns:
        tuple: (is_valid: bool, error: str or None)
    """
    if not password:
        return False, 'Password is required'

    if len(password) < 8:
        return False, 'Password must be at least 8 characters'

    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'

    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'

    if not re.search(r'[0-9]', password):
        return False, 'Password must contain at least one digit'

    return True, None


def validate_gender(gender):
    """
    Validate the gender field.
    
    Returns:
        tuple: (is_valid: bool, error: str or None)
    """
    allowed = {'male', 'female', 'other', 'unisex'}
    if gender and gender.lower() not in allowed:
        return False, f'Gender must be one of: {", ".join(allowed)}'
    return True, None


def validate_face_shape(shape):
    """
    Validate a face shape value.
    
    Returns:
        tuple: (is_valid: bool, error: str or None)
    """
    allowed = {'oval', 'round', 'square', 'heart', 'oblong', 'diamond', 'triangle'}
    if shape and shape.lower() not in allowed:
        return False, f'Face shape must be one of: {", ".join(allowed)}'
    return True, None


def validate_pagination(page, limit):
    """
    Validate and sanitize pagination parameters.
    
    Returns:
        tuple: (page: int, limit: int)
    """
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1

    try:
        limit = max(1, min(50, int(limit)))  # Cap at 50
    except (TypeError, ValueError):
        limit = 10

    return page, limit
