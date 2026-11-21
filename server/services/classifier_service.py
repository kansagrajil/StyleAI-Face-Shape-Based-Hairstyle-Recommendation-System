"""
Face Shape Classification Service.
Uses geometric features derived from MediaPipe landmarks to classify
the face shape via a TensorFlow/Keras model. Also includes a
rule-based fallback classifier for use when no trained model is available.
"""

import os
import numpy as np
from server.utils.landmark_utils import compute_geometric_features

# Face shape labels (must match model training order)
FACE_SHAPE_LABELS = ['oval', 'round', 'square', 'heart', 'diamond', 'oblong', 'triangle']


class ClassifierService:
    """TensorFlow face shape classification with rule-based fallback."""

    def __init__(self, model_path=None, scaler_path='ml/models/scaler.pkl'):
        """
        Load the TensorFlow model and scaler if available, otherwise use rule-based classifier.
        
        Args:
            model_path: Path to the saved Keras model (.h5 or SavedModel directory).
            scaler_path: Path to the saved FeatureScaler .pkl file.
        """
        self.model = None
        self.scaler = None
        self.model_version = 'rule-based-v1.0'

        if scaler_path and os.path.exists(scaler_path):
            try:
                from ml.preprocess import FeatureScaler
                self.scaler = FeatureScaler().load(scaler_path)
            except Exception as e:
                print(f"[ClassifierService] Scaler load notice: {e}")

        if model_path and os.path.exists(model_path):
            try:
                import tensorflow as tf
                self.model = tf.keras.models.load_model(model_path)
                self.model_version = 'tf-dnn-v1.0'
                print(f"[ClassifierService] Loaded TensorFlow model from {model_path}")
            except Exception as e:
                print(f"[ClassifierService] Failed to load model: {e}. Using rule-based fallback.")
        else:
            print("[ClassifierService] No model file found. Using rule-based fallback classifier.")

    def classify(self, landmarks):
        """
        Classify face shape from landmarks.
        
        Args:
            landmarks: List of 468 [x, y, z] landmark coordinates.
        
        Returns:
            dict: {
                'face_shape': str,
                'confidence': float,
                'all_scores': {shape: confidence, ...},
                'model_version': str
            }
        """
        # Step 1: Compute geometric features from landmarks
        features = compute_geometric_features(landmarks)

        if self.model is not None:
            return self._classify_with_model(features)
        else:
            return self._classify_rule_based(features)

    def _classify_with_model(self, features):
        """
        Classify using the trained TensorFlow model.
        
        Args:
            features: Dict of geometric features.
        
        Returns:
            dict: Classification result.
        """
        # Convert feature dict to numpy array in the expected order
        feature_vector = np.array([[
            features['jaw_width'],
            features['forehead_width'],
            features['face_length'],
            features['cheekbone_width'],
            features['width_to_length_ratio'],
            features['forehead_to_jaw_ratio'],
            features['cheekbone_to_jaw_ratio'],
            features['jaw_angle'],
            features['chin_roundness']
        ]], dtype=np.float32)

        # Scale features if scaler is present
        if self.scaler is not None:
            feature_vector = self.scaler.transform(feature_vector)

        # Run inference
        predictions = self.model.predict(feature_vector, verbose=0)[0]

        # Build results
        all_scores = {
            label: round(float(score), 4)
            for label, score in zip(FACE_SHAPE_LABELS, predictions)
        }
        best_idx = int(np.argmax(predictions))

        return {
            'face_shape': FACE_SHAPE_LABELS[best_idx],
            'confidence': round(float(predictions[best_idx]), 4),
            'all_scores': all_scores,
            'model_version': self.model_version
        }

    def _classify_rule_based(self, features):
        """
        Rule-based face shape classification using geometric ratios.
        This serves as a fallback when no trained model is available.
        
        The rules are derived from facial geometry research:
        - Oval: balanced proportions (W:L ≈ 0.66-0.75)
        - Round: width ≈ length (W:L > 0.80)
        - Square: strong jaw, W:L ≈ 0.75-0.85, jaw ≈ forehead
        - Heart: wide forehead, narrow jaw (forehead:jaw > 1.25)
        - Oblong: long face (W:L < 0.60)
        - Diamond: wide cheekbones, narrow forehead & jaw
        - Triangle: wide jaw, narrow forehead (jaw:forehead > 1.15)
        
        Args:
            features: Dict of geometric features.
        
        Returns:
            dict: Classification result with scores.
        """
        wl_ratio = features['width_to_length_ratio']
        fj_ratio = features['forehead_to_jaw_ratio']
        cj_ratio = features['cheekbone_to_jaw_ratio']
        chin = features['chin_roundness']

        scores = {shape: 0.0 for shape in FACE_SHAPE_LABELS}

        # Oblong: very long face
        if wl_ratio < 0.60:
            scores['oblong'] += 0.5

        # Round: width ≈ length, soft jawline
        if wl_ratio > 0.80:
            scores['round'] += 0.4
            if chin > 0.5:
                scores['round'] += 0.2

        # Oval: balanced proportions
        if 0.62 <= wl_ratio <= 0.78:
            scores['oval'] += 0.4
            if 0.90 <= fj_ratio <= 1.10:
                scores['oval'] += 0.2

        # Square: strong jaw, forehead ≈ jaw
        if 0.70 <= wl_ratio <= 0.85 and 0.90 <= fj_ratio <= 1.10:
            scores['square'] += 0.3
            if chin < 0.4:
                scores['square'] += 0.2

        # Heart: wide forehead, narrow chin
        if fj_ratio > 1.25:
            scores['heart'] += 0.4
            if chin > 0.5:
                scores['heart'] += 0.2

        # Diamond: cheekbones wider than both forehead and jaw
        if cj_ratio > 1.15 and fj_ratio < 1.10:
            scores['diamond'] += 0.4

        # Triangle: wide jaw, narrow forehead
        if fj_ratio < 0.85:
            scores['triangle'] += 0.4

        # Normalize scores to sum to 1.0
        total = sum(scores.values())
        if total > 0:
            scores = {k: round(v / total, 4) for k, v in scores.items()}
        else:
            # Default to oval if no rules match
            scores['oval'] = 1.0

        best_shape = max(scores, key=scores.get)

        return {
            'face_shape': best_shape,
            'confidence': scores[best_shape],
            'all_scores': scores,
            'model_version': self.model_version
        }
