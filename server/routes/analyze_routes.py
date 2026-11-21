"""
Face Analysis Routes.
Handles image upload, face detection, shape classification, and recommendation generation.
Endpoint: POST /api/analyze, GET /api/analyze/<id>
"""

import time
import os
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from server.middleware.auth_middleware import token_required
from server.services.storage_service import StorageService
from server.services.recommendation_service import RecommendationService
from server.models.analysis import AnalysisModel
from server.utils.image_utils import validate_image_file

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_face(current_user_id):
    """
    Upload an image and analyze the face shape.
    
    Full pipeline:
        1. Validate and save the uploaded image
        2. Detect face and extract landmarks (OpenCV + MediaPipe)
        3. Classify face shape (TensorFlow or rule-based)
        4. Generate hairstyle recommendations (MongoDB catalog)
        5. Generate AI advice (Gemini API)
        6. Save analysis record to database
    """
    start_time = time.time()

    # ── Step 1: Validate and save image ───────────────────
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    is_valid, error = validate_image_file(file)
    if not is_valid:
        return jsonify({'error': error}), 400

    # Get optional parameters
    gender = request.form.get('gender', 'unisex')
    hair_type = request.form.get('hair_type', 'straight')
    hair_length = request.form.get('hair_length', None)
    category = request.form.get('category', None)
    maintenance_level = request.form.get('maintenance_level', None)

    # Save uploaded image with full step logging
    storage = StorageService(current_app.config['UPLOAD_FOLDER'])
    saved = storage.save_upload(file, current_user_id)
    if not saved or not os.path.exists(saved['image_path']):
        return jsonify({'error': 'Failed to save image file on server'}), 500

    physical_path = saved['image_path']
    current_app.logger.info(f"[analyze] Upload saved successfully. Physical path: '{physical_path}'")

    # ── Step 2: Face detection + landmark extraction ──────
    try:
        face_service = current_app.get_face_service()
        face_result = face_service.detect_and_extract(physical_path)
    except Exception as e:
        return jsonify({'error': f'Face detection failed: {type(e).__name__}: {str(e)}'}), 500

    if not face_result['success']:
        return jsonify({'error': face_result['error']}), 400

    landmarks = face_result['landmarks']

    # ── Step 3: Classify face shape ───────────────────────
    try:
        classifier = current_app.get_classifier_service()
        classification = classifier.classify(landmarks)
    except Exception as e:
        return jsonify({'error': f'Classification failed: {type(e).__name__}: {str(e)}'}), 500

    face_shape = classification['face_shape']
    confidence = classification['confidence']
    all_scores = classification['all_scores']

    # ── Step 4: Get hairstyle recommendations ─────────────
    try:
        rec_service = RecommendationService(current_app.db)
        recommendations = rec_service.get_recommendations(
            face_shape=face_shape,
            gender=gender,
            hair_type=hair_type,
            hair_length=hair_length,
            category=category,
            maintenance_level=maintenance_level,
            limit=10
        )
    except Exception as e:
        recommendations = []
        current_app.logger.error(f"[analyze] Recommendation error: {e}")

    # ── Step 5: Generate AI advice ────────────────────────
    ai_advice = ''
    try:
        genai = current_app.get_genai_service()
        advice_data = genai.generate_advice(face_shape, gender, hair_type)
        ai_advice = advice_data
    except Exception as e:
        current_app.logger.error(f"[analyze] GenAI advice error: {e}")
        ai_advice = {'explanation': f'Your face shape is {face_shape}.'}

    # ── Step 6: Save analysis to database ─────────────────
    processing_time = int((time.time() - start_time) * 1000)

    recommended_ids = [ObjectId(r['id']) for r in recommendations if ObjectId.is_valid(r.get('id', ''))]

    analysis_doc = AnalysisModel.create_document(
        user_id=ObjectId(current_user_id),
        image_path=saved['image_path'],
        web_image_url=saved.get('web_image_url', ''),
        thumbnail_path=saved.get('web_thumb_url', saved['thumbnail_path']),
        face_shape=face_shape,
        confidence=confidence,
        all_scores=all_scores,
        landmarks=landmarks,
        recommended_ids=recommended_ids,
        ai_advice=ai_advice if isinstance(ai_advice, str) else str(ai_advice),
        processing_time_ms=processing_time,
        model_version=classification.get('model_version', 'unknown')
    )

    analysis_id = current_app.db.create_analysis(analysis_doc)

    # ── Build response ────────────────────────────────────
    return jsonify({
        'analysis_id': str(analysis_id),
        'user_image': saved.get('web_thumb_url', saved.get('web_image_url', '')),
        'image_path': saved.get('web_image_url', ''),
        'thumbnail_path': saved.get('web_thumb_url', ''),
        'face_shape': face_shape,
        'confidence': confidence,
        'all_scores': all_scores,
        'landmarks_detected': len(landmarks),
        'recommendations': recommendations,
        'ai_advice': ai_advice,
        'processing_time_ms': processing_time,
        'created_at': analysis_doc['created_at'].isoformat()
    }), 200


@analyze_bp.route('/analyze/<analysis_id>', methods=['GET'])
@token_required
def get_analysis(current_user_id, analysis_id):
    """
    Retrieve a specific analysis by ID.
    """
    analysis = current_app.db.find_analysis_by_id(analysis_id)
    if not analysis or str(analysis['user_id']) != current_user_id:
        return jsonify({'error': 'Analysis not found'}), 404

    return jsonify(AnalysisModel.to_response(analysis)), 200
