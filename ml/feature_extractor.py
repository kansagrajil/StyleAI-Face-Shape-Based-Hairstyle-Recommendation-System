"""
MediaPipe Face Mesh Landmark Feature Extractor.
Extracts 468 3D facial landmarks from image frames and computes
9 normalized geometric features for face shape classification.
"""

import math
import cv2
import numpy as np
import mediapipe as mp

# Target face shape categories
FACE_SHAPES = ['oval', 'round', 'square', 'heart', 'diamond', 'oblong', 'triangle']
NUM_CLASSES = len(FACE_SHAPES)

# Key MediaPipe Face Mesh landmark indices
LANDMARK_INDICES = {
    'jaw_left':         234,   # Left jaw point
    'jaw_right':        454,   # Right jaw point
    'forehead_left':    71,    # Left forehead boundary
    'forehead_right':   301,   # Right forehead boundary
    'chin':             152,   # Bottom of chin
    'forehead_top':     10,    # Top of forehead (hairline center)
    'cheekbone_left':   123,   # Left cheekbone
    'cheekbone_right':  352,   # Right cheekbone
    'jaw_angle_left':   172,   # Left jaw angle
    'jaw_angle_right':  397,   # Right jaw angle
    'chin_left':        148,   # Left chin curve
    'chin_right':       377,   # Right chin curve
    'nose_tip':         1,     # Nose tip
}

FEATURE_NAMES = [
    'jaw_width',
    'forehead_width',
    'face_length',
    'cheekbone_width',
    'width_to_length_ratio',
    'forehead_to_jaw_ratio',
    'cheekbone_to_jaw_ratio',
    'jaw_angle',
    'chin_roundness'
]


def euclidean_distance(p1, p2):
    """Compute 2D Euclidean distance between two landmark points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def compute_angle(p1, vertex, p2):
    """Compute angle in degrees at vertex formed by p1-vertex-p2."""
    v1 = np.array(p1[:2]) - np.array(vertex[:2])
    v2 = np.array(p2[:2]) - np.array(vertex[:2])

    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return math.degrees(math.acos(cos_angle))


class LandmarkExtractor:
    """Extracts MediaPipe landmarks and computes geometric feature vectors."""

    def __init__(self, static_image_mode=True, min_detection_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence
        )

    def extract_landmarks(self, image):
        """
        Extract 468 landmark coordinates [x, y, z] from image array.
        
        Args:
            image: numpy array (BGR or RGB image).
        
        Returns:
            list: List of 468 [x, y, z] coordinates normalized (0-1), or None if no face detected.
        """
        if isinstance(image, str):
            image = cv2.imread(image)

        if image is None:
            return None

        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_img = image

        results = self.face_mesh.process(rgb_img)
        if not results.multi_face_landmarks:
            return None

        face_landmarks = results.multi_face_landmarks[0]
        landmarks = [[lm.x, lm.y, lm.z] for lm in face_landmarks.landmark]
        return landmarks

    @staticmethod
    def compute_geometric_features(landmarks):
        """
        Compute 9 facial geometric feature ratios and angles from 468 landmarks.
        
        Returns:
            dict: Computed feature names and numerical values.
        """
        idx = LANDMARK_INDICES

        jaw_left = landmarks[idx['jaw_left']]
        jaw_right = landmarks[idx['jaw_right']]
        forehead_left = landmarks[idx['forehead_left']]
        forehead_right = landmarks[idx['forehead_right']]
        chin = landmarks[idx['chin']]
        forehead_top = landmarks[idx['forehead_top']]
        cheekbone_left = landmarks[idx['cheekbone_left']]
        cheekbone_right = landmarks[idx['cheekbone_right']]
        jaw_angle_left = landmarks[idx['jaw_angle_left']]
        jaw_angle_right = landmarks[idx['jaw_angle_right']]
        chin_left = landmarks[idx['chin_left']]
        chin_right = landmarks[idx['chin_right']]

        # Distance measurements
        jaw_width = euclidean_distance(jaw_left, jaw_right)
        forehead_width = euclidean_distance(forehead_left, forehead_right)
        face_length = euclidean_distance(forehead_top, chin)
        cheekbone_width = euclidean_distance(cheekbone_left, cheekbone_right)

        # Avoid zero division
        face_length_safe = max(face_length, 1e-6)
        jaw_width_safe = max(jaw_width, 1e-6)

        # Ratios
        width_to_length_ratio = jaw_width / face_length_safe
        forehead_to_jaw_ratio = forehead_width / jaw_width_safe
        cheekbone_to_jaw_ratio = cheekbone_width / jaw_width_safe

        # Jaw angle at chin
        jaw_angle = compute_angle(jaw_angle_left, chin, jaw_angle_right)

        # Chin roundness metric
        chin_mid_x = (chin_left[0] + chin_right[0]) / 2.0
        chin_mid_y = (chin_left[1] + chin_right[1]) / 2.0
        chin_width = euclidean_distance(chin_left, chin_right)
        chin_depth = euclidean_distance(chin, [chin_mid_x, chin_mid_y])
        chin_roundness = min(chin_depth / (chin_width + 1e-6), 1.0)

        return {
            'jaw_width': round(jaw_width, 6),
            'forehead_width': round(forehead_width, 6),
            'face_length': round(face_length, 6),
            'cheekbone_width': round(cheekbone_width, 6),
            'width_to_length_ratio': round(width_to_length_ratio, 4),
            'forehead_to_jaw_ratio': round(forehead_to_jaw_ratio, 4),
            'cheekbone_to_jaw_ratio': round(cheekbone_to_jaw_ratio, 4),
            'jaw_angle': round(jaw_angle, 2),
            'chin_roundness': round(chin_roundness, 4)
        }

    @staticmethod
    def get_feature_vector(features_dict):
        """Convert feature dict to 9-element numpy array in standard order."""
        return np.array([features_dict[name] for name in FEATURE_NAMES], dtype=np.float32)

    def extract_feature_vector(self, image):
        """Extract landmarks and return 9-element feature vector directly from image."""
        landmarks = self.extract_landmarks(image)
        if landmarks is None:
            return None
        features_dict = self.compute_geometric_features(landmarks)
        return self.get_feature_vector(features_dict)
