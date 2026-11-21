"""
Analysis result data model.
Defines the schema for face shape analysis records stored in MongoDB.
"""

from datetime import datetime, timezone


class AnalysisModel:
    """Schema and helpers for the analyses collection."""

    COLLECTION = 'analyses'

    @staticmethod
    def create_document(user_id, image_path, thumbnail_path, face_shape,
                        confidence, all_scores, landmarks, recommended_ids,
                        ai_advice, processing_time_ms, model_version='v1.0',
                        recommendations=None, selected_hairstyle=None,
                        web_image_url=None):
        """
        Build a new analysis document storing both physical file path and web URL.
        
        Args:
            user_id: ObjectId of the user.
            image_path: Physical absolute disk path to the uploaded image.
            thumbnail_path: Path/URL to the thumbnail image.
            face_shape: Detected face shape string (oval, round, square, heart, diamond, oblong).
            confidence: Confidence score (0-1).
            all_scores: Dict of shape → confidence for all classes.
            landmarks: List of [x, y, z] landmark coordinates.
            recommended_ids: List of hairstyle ObjectIds.
            ai_advice: Generated text advice or dict.
            processing_time_ms: Time taken to process (milliseconds).
            model_version: Version of the ML model used.
            recommendations: Optional list of detailed recommendation summary dicts.
            selected_hairstyle: Optional user-chosen hairstyle dict.
            web_image_url: Optional web-accessible URL for client HTTP serving.
        
        Returns:
            dict: Analysis document.
        """
        return {
            'user_id': user_id,
            'image_path': image_path,
            'web_image_url': web_image_url or image_path,
            'thumbnail_path': thumbnail_path or image_path,
            'face_shape': face_shape,
            'confidence': confidence,
            'all_scores': all_scores,
            'landmarks': landmarks,
            'recommended_ids': recommended_ids,
            'recommendations': recommendations or [],
            'selected_hairstyle': selected_hairstyle or None,
            'ai_advice': ai_advice,
            'metadata': {
                'processing_time_ms': processing_time_ms,
                'model_version': model_version
            },
            'created_at': datetime.now(timezone.utc)
        }

    @staticmethod
    def to_response(doc):
        """Serialize an analysis document for API response."""
        return {
            'analysis_id': str(doc['_id']),
            'image_path': doc.get('web_image_url', doc.get('image_path', '')),
            'thumbnail_path': doc.get('thumbnail_path', doc.get('web_image_url', doc.get('image_path', ''))),
            'face_shape': doc['face_shape'],
            'confidence': doc['confidence'],
            'all_scores': doc.get('all_scores', {}),
            'landmarks_detected': len(doc.get('landmarks', [])),
            'recommendations': doc.get('recommendations', []),
            'selected_hairstyle': doc.get('selected_hairstyle', None),
            'ai_advice': doc.get('ai_advice', ''),
            'metadata': doc.get('metadata', {}),
            'created_at': doc['created_at'].isoformat()
        }
