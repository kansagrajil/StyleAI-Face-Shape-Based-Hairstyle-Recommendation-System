"""
Admin Panel Routes.
Provides REST API endpoints for system analytics, user management, hairstyle CRUD,
face shape category rules, and uploaded image management.
All endpoints require authentication and role == 'admin'.
"""

from flask import Blueprint, request, jsonify, current_app
from server.middleware.auth_middleware import admin_required
from server.services.admin_service import AdminService
from server.models.hairstyle import HairstyleModel
from server.services.recommendation_service import RecommendationService

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics(current_user_id):
    """Get system analytics and dashboard KPIs."""
    admin_svc = AdminService(current_app.db, current_app.config['UPLOAD_FOLDER'])
    stats = admin_svc.get_system_analytics()
    return jsonify(stats), 200


# ── User Management Endpoints ───────────────────────────────

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users(current_user_id):
    """List users with search, filter, and pagination."""
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))

    admin_svc = AdminService(current_app.db)
    users, total = admin_svc.find_users(search_query=search or None, role=role or None, page=page, limit=limit)

    return jsonify({
        'users': users,
        'total': total,
        'page': page,
        'limit': limit
    }), 200


@admin_bp.route('/users/<user_id>', methods=['PATCH'])
@admin_required
def update_user(current_user_id, user_id):
    """Update user role or active status."""
    data = request.get_json() or {}
    role = data.get('role')
    is_active = data.get('is_active')

    admin_svc = AdminService(current_app.db)
    result = admin_svc.update_user_status_or_role(user_id, role=role, is_active=is_active)

    if not result or result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'updated': True}), 200


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user_id, user_id):
    """Delete a user account and associated history."""
    if user_id == current_user_id:
        return jsonify({'error': 'You cannot delete your own admin account'}), 400

    admin_svc = AdminService(current_app.db)
    result = admin_svc.delete_user(user_id)

    if result.deleted_count == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'deleted': True}), 200


# ── Hairstyle CRUD Endpoints ─────────────────────────────────

@admin_bp.route('/hairstyles', methods=['POST'])
@admin_required
def create_hairstyle(current_user_id):
    """Create a new hairstyle entry."""
    data = request.get_json() or {}
    if not data.get('name') or not data.get('slug'):
        return jsonify({'error': 'Name and slug are required'}), 400

    admin_svc = AdminService(current_app.db)
    try:
        hs_id = admin_svc.create_hairstyle(data)
        return jsonify({'created': True, 'hairstyle_id': hs_id}), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create hairstyle: {str(e)}'}), 400


@admin_bp.route('/hairstyles/<hairstyle_id>', methods=['PUT'])
@admin_required
def update_hairstyle(current_user_id, hairstyle_id):
    """Update an existing hairstyle entry."""
    data = request.get_json() or {}
    admin_svc = AdminService(current_app.db)
    result = admin_svc.update_hairstyle(hairstyle_id, data)

    if result.matched_count == 0:
        return jsonify({'error': 'Hairstyle not found'}), 404

    return jsonify({'updated': True}), 200


@admin_bp.route('/hairstyles/<hairstyle_id>', methods=['DELETE'])
@admin_required
def delete_hairstyle(current_user_id, hairstyle_id):
    """Delete a hairstyle entry."""
    admin_svc = AdminService(current_app.db)
    result = admin_svc.delete_hairstyle(hairstyle_id)

    if result.deleted_count == 0:
        return jsonify({'error': 'Hairstyle not found'}), 404

    return jsonify({'deleted': True}), 200


# ── Face Shape Categories & Rules ────────────────────────────

@admin_bp.route('/face-shapes', methods=['GET'])
@admin_required
def get_face_shapes(current_user_id):
    """Get 6 face shape target categories & definitions."""
    shapes = [
        {'shape': 'oval', 'name': 'Oval', 'ratio_bounds': 'W:L 0.68-0.75', 'description': 'Balanced facial proportions, gently curved jawline.'},
        {'shape': 'round', 'name': 'Round', 'ratio_bounds': 'W:L > 0.80', 'description': 'Soft rounded curves, width nearly equal to length.'},
        {'shape': 'square', 'name': 'Square', 'ratio_bounds': 'W:L 0.75-0.85', 'description': 'Strong angular jawline, forehead width equals jaw width.'},
        {'shape': 'heart', 'name': 'Heart', 'ratio_bounds': 'Forehead:Jaw > 1.25', 'description': 'Wide forehead and cheekbones tapering to a pointed chin.'},
        {'shape': 'diamond', 'name': 'Diamond', 'ratio_bounds': 'Cheekbone:Jaw > 1.20', 'description': 'Prominent wide cheekbones with narrow forehead and chin.'},
        {'shape': 'oblong', 'name': 'Oblong', 'ratio_bounds': 'W:L < 0.60', 'description': 'Long face shape with uniform width across forehead and jaw.'}
    ]
    return jsonify({'face_shapes': shapes}), 200


@admin_bp.route('/rules', methods=['GET'])
@admin_required
def get_rules(current_user_id):
    """Get shape affinity matrix and recommendation ranking weights."""
    return jsonify({
        'affinity_matrix': RecommendationService.SHAPE_AFFINITY,
        'ranking_weights': {
            'shape_weight': 0.85,
            'rating_weight': 0.08,
            'popularity_weight': 0.05,
            'preference_bonus': 0.05
        }
    }), 200


# ── Uploaded Image Storage ───────────────────────────────────

@admin_bp.route('/images', methods=['GET'])
@admin_required
def list_images(current_user_id):
    """List uploaded image files."""
    admin_svc = AdminService(current_app.db, current_app.config['UPLOAD_FOLDER'])
    files = admin_svc.list_uploaded_images()
    return jsonify({'images': files}), 200


@admin_bp.route('/images/<path:filename>', methods=['DELETE'])
@admin_required
def delete_image(current_user_id, filename):
    """Delete an uploaded image file."""
    admin_svc = AdminService(current_app.db, current_app.config['UPLOAD_FOLDER'])
    deleted = admin_svc.delete_uploaded_image(filename)

    if not deleted:
        return jsonify({'error': 'Image file not found'}), 404

    return jsonify({'deleted': True}), 200
