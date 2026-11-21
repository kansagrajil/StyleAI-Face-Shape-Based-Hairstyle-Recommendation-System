"""
Recommendation & Hairstyle Catalog Routes.
Provides endpoints for browsing the hairstyle catalog and getting
filtered recommendations by face shape.
Endpoints: GET /api/recommend, GET /api/hairstyles, GET /api/hairstyles/<id>
"""

from flask import Blueprint, request, jsonify, current_app
from server.services.recommendation_service import RecommendationService
from server.models.hairstyle import HairstyleModel
from server.middleware.auth_middleware import token_required
from server.utils.validators import validate_face_shape, validate_pagination

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/recommend', methods=['GET'])
@token_required
def get_recommendations(current_user_id):
    """
    Get hairstyle recommendations filtered by face shape and preference metadata.
    
    Query Params:
        shape: str (required) — face shape to match
        gender: str (optional) — male, female, unisex
        hair_type: str (optional) — straight, wavy, curly, coily
        hair_length: str (optional) — short, medium, long
        category: str (optional) — classic, modern, edgy, formal, casual, trending
        maintenance_level: str (optional) — low, medium, high
        min_popularity: int (optional) — 0-100
        limit: int (optional, default 10, max 50)
    
    Returns:
        200: {hairstyles: [{id, name, image_url, compatibility, ...}]}
        400: Invalid face shape
    """
    shape = request.args.get('shape', '').lower()
    gender = request.args.get('gender', '')
    hair_type = request.args.get('hair_type', '')
    hair_length = request.args.get('hair_length', '')
    category = request.args.get('category', '')
    maintenance_level = request.args.get('maintenance_level', '')
    min_popularity = request.args.get('min_popularity', None)
    limit = request.args.get('limit', 10)

    # Validate face shape
    valid, err = validate_face_shape(shape)
    if not valid or not shape:
        return jsonify({'error': err or 'Face shape parameter is required'}), 400

    _, limit = validate_pagination(1, limit)

    rec_service = RecommendationService(current_app.db)
    results = rec_service.get_recommendations(
        face_shape=shape,
        gender=gender or None,
        hair_type=hair_type or None,
        hair_length=hair_length or None,
        category=category or None,
        maintenance_level=maintenance_level or None,
        min_popularity=min_popularity,
        limit=limit
    )

    return jsonify({'hairstyles': results}), 200


@recommend_bp.route('/hairstyles', methods=['GET'])
def list_hairstyles():
    """
    Browse the hairstyle catalog with multi-criteria metadata filters.
    
    Query Params:
        shape: str (optional) — filter by face shape
        gender: str (optional) — filter by gender
        hair_type: str (optional) — filter by hair texture
        hair_length: str (optional) — filter by length
        category: str (optional) — filter by style category
        maintenance_level: str (optional) — filter by maintenance
        min_popularity: int (optional) — min popularity threshold
        page: int (optional, default 1)
        limit: int (optional, default 20, max 50)
    
    Returns:
        200: {hairstyles: [...], total, page, limit}
    """
    shape = request.args.get('shape', '')
    gender = request.args.get('gender', '')
    hair_type = request.args.get('hair_type', '')
    hair_length = request.args.get('hair_length', '')
    category = request.args.get('category', '')
    maintenance_level = request.args.get('maintenance_level', '')
    min_popularity = request.args.get('min_popularity', None)
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 20)

    page, limit = validate_pagination(page, limit)

    hairstyles, total = current_app.db.find_hairstyles(
        face_shape=shape or None,
        gender=gender or None,
        hair_type=hair_type or None,
        hair_length=hair_length or None,
        category=category or None,
        maintenance_level=maintenance_level or None,
        min_popularity=min_popularity,
        page=page,
        limit=limit
    )

    return jsonify({
        'hairstyles': [HairstyleModel.to_response(hs) for hs in hairstyles],
        'total': total,
        'page': page,
        'limit': limit
    }), 200


@recommend_bp.route('/hairstyles/<hairstyle_id>', methods=['GET'])
def get_hairstyle(hairstyle_id):
    """
    Get details for a specific hairstyle (public endpoint).
    """
    hs = current_app.db.find_hairstyle_by_id(hairstyle_id)
    if not hs:
        return jsonify({'error': 'Hairstyle not found'}), 404

    current_app.db.increment_view_count(hairstyle_id)
    return jsonify(HairstyleModel.to_response(hs)), 200
