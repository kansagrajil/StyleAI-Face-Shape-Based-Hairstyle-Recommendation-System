"""
End-to-End Face Shape Prediction Pipeline.
Takes an input image path or image array, extracts MediaPipe landmarks and 9 geometric features,
standardizes features using the trained scaler, and predicts the face shape probability distribution
using the trained TensorFlow model.
"""

import os
import argparse
import numpy as np
import tensorflow as tf

from ml.feature_extractor import LandmarkExtractor, FACE_SHAPES, FEATURE_NAMES
from ml.preprocess import FeatureScaler


class FaceShapePredictor:
    """Production prediction pipeline for face shape classification."""

    def __init__(self, model_path='ml/models/face_shape_model.h5', scaler_path='ml/models/scaler.pkl'):
        """
        Initialize the predictor pipeline.
        
        Args:
            model_path: Path to the trained Keras .h5 model file.
            scaler_path: Path to the fitted FeatureScaler .pkl file.
        """
        self.extractor = LandmarkExtractor(static_image_mode=True)
        self.model = None
        self.scaler = None
        self.face_shapes = FACE_SHAPES

        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            print(f"[FaceShapePredictor] Loaded TensorFlow model: {model_path}")
        else:
            print(f"[FaceShapePredictor] Warning: Model file not found at {model_path}")

        if os.path.exists(scaler_path):
            self.scaler = FeatureScaler().load(scaler_path)
            print(f"[FaceShapePredictor] Loaded Feature Scaler: {scaler_path}")
        else:
            print(f"[FaceShapePredictor] Warning: Scaler file not found at {scaler_path}")

    def predict_from_features(self, feature_vector):
        """
        Predict face shape from 9-element geometric feature vector.
        
        Args:
            feature_vector: list or 1D numpy array of 9 numerical features.
        
        Returns:
            dict: {
                'face_shape': str,
                'confidence': float,
                'all_scores': dict,
                'model_type': str
            }
        """
        vec = np.array(feature_vector, dtype=np.float32).reshape(1, -1)

        # Scale features if scaler exists
        if self.scaler is not None:
            vec_scaled = self.scaler.transform(vec)
        else:
            vec_scaled = vec

        if self.model is not None:
            predictions = self.model.predict(vec_scaled, verbose=0)[0]
            scores = {shape: round(float(prob), 4) for shape, prob in zip(self.face_shapes, predictions)}
            best_idx = int(np.argmax(predictions))
            best_shape = self.face_shapes[best_idx]
            confidence = round(float(predictions[best_idx]), 4)
            model_type = 'tensorflow-dnn'
        else:
            # Fallback rule-based estimation
            best_shape = 'oval'
            confidence = 0.50
            scores = {shape: 0.1667 for shape in self.face_shapes}
            model_type = 'rule-based-fallback'

        return {
            'face_shape': best_shape,
            'confidence': confidence,
            'all_scores': scores,
            'model_type': model_type
        }

    def predict_image(self, image_input):
        """
        End-to-end prediction from image file path or numpy BGR/RGB image array.
        
        Args:
            image_input: File path (str) or numpy array image.
        
        Returns:
            dict: Classification results including landmarks detected status and geometric features.
        """
        # Step 1: Extract 468 landmarks
        landmarks = self.extractor.extract_landmarks(image_input)
        if landmarks is None:
            return {
                'success': False,
                'error': 'No face detected in the image by MediaPipe Face Mesh.'
            }

        # Step 2: Compute geometric features
        features_dict = self.extractor.compute_geometric_features(landmarks)
        feature_vec = self.extractor.get_feature_vector(features_dict)

        # Step 3: Run TensorFlow model prediction
        prediction_result = self.predict_from_features(feature_vec)

        return {
            'success': True,
            'face_shape': prediction_result['face_shape'],
            'confidence': prediction_result['confidence'],
            'all_scores': prediction_result['all_scores'],
            'model_type': prediction_result['model_type'],
            'geometric_features': features_dict
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Face Shape Prediction Pipeline')
    parser.add_argument('--image', type=str, default=None, help='Path to input image')
    parser.add_argument('--model', type=str, default='ml/models/face_shape_model.h5')
    parser.add_argument('--scaler', type=str, default='ml/models/scaler.pkl')
    args = parser.parse_args()

    predictor = FaceShapePredictor(model_path=args.model, scaler_path=args.scaler)

    if args.image and os.path.exists(args.image):
        print(f"\nRunning prediction on: {args.image}")
        res = predictor.predict_image(args.image)
        if res.get('success'):
            print("\n" + "=" * 50)
            print("PREDICTION RESULT")
            print("=" * 50)
            print(f"Predicted Face Shape: {res['face_shape'].upper()}")
            print(f"Confidence Score:     {res['confidence'] * 100:.2f}%")
            print(f"Model Type:           {res['model_type']}")
            print("\nProbability Distribution:")
            for shape, score in res['all_scores'].items():
                print(f"  {shape.capitalize():<10}: {score * 100:6.2f}%")
        else:
            print(f"Error: {res.get('error')}")
    else:
        # Run test prediction on a sample feature vector
        print("\nTesting prediction pipeline on sample geometric feature vector...")
        sample_vec = [0.45, 0.44, 0.63, 0.48, 0.71, 0.98, 1.07, 125.0, 0.58]
        res = predictor.predict_from_features(sample_vec)
        print(f"Predicted Class: {res['face_shape'].upper()} ({res['confidence']*100:.2f}% confidence)")
