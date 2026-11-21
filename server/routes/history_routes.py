"""
History Routes.
Provides endpoints for viewing, searching, filtering, selecting hairstyles, and deleting past face analyses.
Endpoints:
  GET /api/history
  GET /api/history/<id>
  PATCH /api/history/<id>/select-hairstyle
  DELETE /api/history/<id>
  DELETE /api/history
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from server.middleware.auth_middleware import token_required
from server.models.analysis import AnalysisModel
from server.utils.validators import validate_pagination

history_bp = Blueprint('history', __name__)


@history_bp.route('/history', methods=['GET'])
@token_required
def get_history(current_user_id):
    """
    Get paginated analysis history for the current user with search & filters.
    
    Query Params:
        search: str (optional) — search text in face shape, hairstyles, AI advice
        shape: str (optional) — filter by face shape (oval, round, square, heart, diamond, oblong)
        start_date: str (optional) — ISO format date string
        end_date: str (optional) — ISO format date string
        page: int (optional, default 1)
        limit: int (optional, default 10, max 50)
    
    Returns:
        200: {analyses: [...], total, page, limit}
    """
    search_query = request.args.get('search', '').strip()
    face_shape = request.args.get('shape', '').strip()
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 10)

    page, limit = validate_pagination(page, limit)

    start_dt = None
    end_dt = None
    try:
        if start_date_str:
            start_dt = datetime.fromisoformat(start_date_str)
        if end_date_str:
            end_dt = datetime.fromisoformat(end_date_str)
    except Exception:
        pass

    analyses, total = current_app.db.find_analyses_by_user(
        current_user_id,
        search_query=search_query or None,
        face_shape=face_shape or None,
        start_date=start_dt,
        end_date=end_dt,
        page=page,
        limit=limit
    )

    return jsonify({
        'analyses': [AnalysisModel.to_response(a) for a in analyses],
        'total': total,
        'page': page,
        'limit': limit
    }), 200


@history_bp.route('/history/<analysis_id>', methods=['GET'])
@token_required
def get_history_detail(current_user_id, analysis_id):
    """
    Retrieve details for a single analysis history record.
    """
    analysis = current_app.db.find_analysis_by_id(analysis_id)
    if not analysis or str(analysis['user_id']) != current_user_id:
        return jsonify({'error': 'Analysis history record not found'}), 404

    return jsonify(AnalysisModel.to_response(analysis)), 200


@history_bp.route('/history/<analysis_id>/select-hairstyle', methods=['PATCH'])
@token_required
def update_selected_hairstyle(current_user_id, analysis_id):
    """
    Save or update the user's chosen hairstyle for a specific analysis record.
    
    Body (JSON):
        hairstyle_id: str (required)
        name: str (required)
        image_url: str (optional)
    """
    data = request.get_json() or {}
    hairstyle_id = data.get('hairstyle_id')
    name = data.get('name')

    if not hairstyle_id or not name:
        return jsonify({'error': 'hairstyle_id and name are required'}), 400

    selected_doc = {
        'id': hairstyle_id,
        'name': name,
        'image_url': data.get('image_url', '')
    }

    result = current_app.db.update_analysis_selected_hairstyle(
        analysis_id=analysis_id,
        user_id=current_user_id,
        selected_hairstyle_doc=selected_doc
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Analysis record not found'}), 404

    return jsonify({'updated': True, 'selected_hairstyle': selected_doc}), 200


@history_bp.route('/history/<analysis_id>', methods=['DELETE'])
@token_required
def delete_analysis(current_user_id, analysis_id):
    """
    Delete a single analysis history record.
    """
    result = current_app.db.delete_analysis(analysis_id, current_user_id)

    if result.deleted_count == 0:
        return jsonify({'error': 'Analysis not found or not authorized'}), 404

    return jsonify({'deleted': True}), 200


@history_bp.route('/history', methods=['DELETE'])
@token_required
def clear_history(current_user_id):
    """
    Bulk clear all analysis history records for the current user.
    """
    result = current_app.db.clear_user_history(current_user_id)
    return jsonify({'deleted_count': result.deleted_count, 'cleared': True}), 200
