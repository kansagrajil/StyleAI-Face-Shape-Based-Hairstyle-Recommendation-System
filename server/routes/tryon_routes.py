"""
Virtual Try-On Routes.
Handles generating AI-powered virtual hairstyle try-on previews.
Endpoints: POST /api/tryon, GET /api/tryon/<id>
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from server.middleware.auth_middleware import token_required
from server.services.tryon_service import TryonService

tryon_bp = Blueprint('tryon', __name__)


@tryon_bp.route('/tryon', methods=['POST'])
@token_required
def create_tryon(current_user_id):
    """
    Generate a virtual try-on preview using Generative AI 4-stage pipeline.
    
    Body (JSON):
        analysis_id: str (required) — ID of the face analysis
        hairstyle_id: str (required) — ID of the hairstyle to try on
        provider: str (optional) — 'auto', 'gemini', 'stablediffusion', 'dalle', 'fallback'
    
    Returns:
        200: {tryon_id, preview_url, user_image, description, hairstyle_name, model_version, processing_time_ms, generated_at}
        400: Missing parameters
        404: Analysis or hairstyle not found
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    analysis_id = data.get('analysis_id')
    hairstyle_id = data.get('hairstyle_id')
    provider_choice = data.get('provider', 'auto')

    if not analysis_id or not hairstyle_id:
        return jsonify({'error': 'analysis_id and hairstyle_id are required'}), 400

    db = current_app.db

    # Verify analysis exists and belongs to user
    analysis = db.find_analysis_by_id(analysis_id)
    if not analysis or str(analysis['user_id']) != current_user_id:
        return jsonify({'error': 'Analysis not found'}), 404

    # Get hairstyle details
    hairstyle = db.find_hairstyle_by_id(hairstyle_id)
    if not hairstyle:
        return jsonify({'error': 'Hairstyle not found'}), 404

    # Generate text description using GenAI
    try:
        genai = current_app.get_genai_service()
        description = genai.generate_tryon_description(
            face_shape=analysis['face_shape'],
            hairstyle_name=hairstyle['name'],
            hairstyle_description=hairstyle['description']
        )
    except Exception as e:
        description = f"Visualize {hairstyle['name']} on your {analysis['face_shape']} face shape."

    # Determine appropriate API key for the chosen provider
    target_provider = (provider_choice if provider_choice != 'auto' else current_app.config.get('TRYON_PROVIDER', 'replicate')).lower()
    if target_provider in ('replicate', 'openai/gpt-image-2.5-flare', 'gpt-image-2.5-flare', 'flare'):
        provider_token = current_app.config.get('REPLICATE_API_TOKEN') or os.getenv('REPLICATE_API_TOKEN')
    elif target_provider == 'gemini':
        provider_token = current_app.config.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
    elif target_provider in ('comfyui', 'comfy_ui', 'sd1.5'):
        provider_token = current_app.config.get('COMFYUI_API_KEY') or os.getenv('COMFYUI_API_KEY')
    else:
        provider_token = None

    # Execute 4-Stage Virtual Hairstyle Try-On Pipeline
    tryon_service = TryonService(
        upload_folder=current_app.config['UPLOAD_FOLDER'],
        provider_type=provider_choice,
        api_key=provider_token
    )

    # Physical disk path for backend processing
    user_img_path = analysis.get('image_path', '')

    # Derive web-accessible relative URL for HTTP clients
    web_user_img = analysis.get('web_image_url') or analysis.get('thumbnail_path') or user_img_path
    if '\\uploads\\' in web_user_img or '/uploads/' in web_user_img:
        clean_rel = web_user_img.split('uploads')[-1].replace('\\', '/')
        web_user_img = f"/uploads{clean_rel}"

    pipeline_res = tryon_service.execute_tryon_pipeline(
        user_image_path=user_img_path,
        hairstyle_doc=hairstyle,
        face_shape=analysis['face_shape']
    )

    if not pipeline_res.get('success'):
        return jsonify({
            'error': pipeline_res.get('error', 'Virtual try-on processing failed'),
            'stage_logs': pipeline_res.get('stage_logs', [])
        }), 500

    preview_url = pipeline_res.get('preview_url', hairstyle['image_url'])

    # Save try-on record to MongoDB
    tryon_doc = {
        'analysis_id': ObjectId(analysis_id),
        'hairstyle_id': ObjectId(hairstyle_id),
        'user_id': ObjectId(current_user_id),
        'description': description,
        'hairstyle_name': hairstyle['name'],
        'hairstyle_image': hairstyle['image_url'],
        'user_image': web_user_img,
        'preview_url': preview_url,
        'prompt_used': pipeline_res.get('prompt_used', ''),
        'model_version': pipeline_res.get('model_version', 'v1.0'),
        'processing_time_ms': pipeline_res.get('processing_time_ms', 0),
        'face_shape': analysis['face_shape'],
        'status': 'completed',
        'created_at': datetime.now(timezone.utc)
    }

    tryon_id = db.create_tryon(tryon_doc)

    return jsonify({
        'tryon_id': str(tryon_id),
        'preview_url': preview_url,
        'user_image': web_user_img,
        'description': description,
        'hairstyle_name': hairstyle['name'],
        'hairstyle_image': hairstyle['image_url'],
        'face_shape': analysis['face_shape'],
        'model_version': tryon_doc['model_version'],
        'processing_time_ms': tryon_doc['processing_time_ms'],
        'generated_at': tryon_doc['created_at'].isoformat()
    }), 200


@tryon_bp.route('/tryon/<tryon_id>', methods=['GET'])
@token_required
def get_tryon(current_user_id, tryon_id):
    """
    Retrieve a try-on result by ID.
    """
    tryon = current_app.db.find_tryon_by_id(tryon_id)
    if not tryon or str(tryon['user_id']) != current_user_id:
        return jsonify({'error': 'Try-on result not found'}), 404

    user_img_val = tryon.get('user_image', '')
    if '\\uploads\\' in user_img_val or '/uploads/' in user_img_val:
        clean_rel = user_img_val.split('uploads')[-1].replace('\\', '/')
        user_img_val = f"/uploads{clean_rel}"

    return jsonify({
        'tryon_id': str(tryon['_id']),
        'preview_url': tryon.get('preview_url', tryon.get('hairstyle_image', '')),
        'user_image': user_img_val,
        'description': tryon['description'],
        'hairstyle_name': tryon.get('hairstyle_name', ''),
        'hairstyle_image': tryon.get('hairstyle_image', ''),
        'face_shape': tryon.get('face_shape', ''),
        'model_version': tryon.get('model_version', 'v1.0'),
        'processing_time_ms': tryon.get('processing_time_ms', 0),
        'status': tryon['status'],
        'generated_at': tryon['created_at'].isoformat()
    }), 200
