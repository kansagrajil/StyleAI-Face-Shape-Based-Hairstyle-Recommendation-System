"""
Landmark Utility Functions.
Computes geometric features from MediaPipe's 468 facial landmarks
for face shape classification and generates precision hair-region masks.
"""

import math
import numpy as np


# Key MediaPipe Face Mesh landmark indices
# Reference: https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
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
    'left_eye':         33,    # Left eye outer corner
    'right_eye':        263,   # Right eye outer corner
}

# Eyebrow and forehead boundary polygon indices for hairline separation
FOREHEAD_BOUNDARY_INDICES = [71, 109, 10, 338, 301, 297, 334, 296, 336, 9, 107, 66, 105, 67]


def _distance(p1, p2):
    """
    Euclidean distance between two 2D/3D points.
    
    Args:
        p1: [x, y] or [x, y, z] coordinate.
        p2: [x, y] or [x, y, z] coordinate.
    
    Returns:
        float: Euclidean distance.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1[:2], p2[:2])))


def _angle(p1, vertex, p2):
    """
    Compute the angle (in degrees) at 'vertex' formed by p1-vertex-p2.
    
    Args:
        p1: First point [x, y].
        vertex: Vertex point [x, y].
        p2: Second point [x, y].
    
    Returns:
        float: Angle in degrees.
    """
    v1 = np.array(p1[:2]) - np.array(vertex[:2])
    v2 = np.array(p2[:2]) - np.array(vertex[:2])

    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return math.degrees(math.acos(cos_angle))


def compute_geometric_features(landmarks):
    """
    Compute geometric features from 468 MediaPipe landmarks for face shape classification.
    
    Args:
        landmarks: List of 468 [x, y, z] landmark coordinates (normalized 0-1).
    
    Returns:
        dict: Computed geometric feature values.
    """
    idx = LANDMARK_INDICES

    # Extract key points
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
    jaw_width = _distance(jaw_left, jaw_right)
    forehead_width = _distance(forehead_left, forehead_right)
    face_length = _distance(forehead_top, chin)
    cheekbone_width = _distance(cheekbone_left, cheekbone_right)

    face_length = max(face_length, 1e-6)
    jaw_width = max(jaw_width, 1e-6)

    width_to_length_ratio = jaw_width / face_length
    forehead_to_jaw_ratio = forehead_width / jaw_width
    cheekbone_to_jaw_ratio = cheekbone_width / jaw_width

    jaw_angle = _angle(jaw_angle_left, chin, jaw_angle_right)

    chin_mid_x = (chin_left[0] + chin_right[0]) / 2
    chin_mid_y = (chin_left[1] + chin_right[1]) / 2
    chin_width = _distance(chin_left, chin_right)
    chin_depth = _distance(chin, [chin_mid_x, chin_mid_y])

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


def generate_hair_region_mask(landmarks, image_width, image_height):
    """
    Generate a binary mask separating the scalp/hair region from the face oval.
    Hair region = 255, Face/eyes/nose/lips/beard = 0.
    
    Args:
        landmarks: List of 468 [x, y, z] normalized landmark coordinates.
        image_width: Width of target image in pixels.
        image_height: Height of target image in pixels.
    
    Returns:
        numpy.ndarray: Binary mask of shape (H, W), dtype uint8.
    """
    import cv2
    mask = np.zeros((image_height, image_width), dtype=np.uint8)

    if not landmarks or len(landmarks) < 468:
        # Fallback mask covering upper 40% of head if landmarks missing
        cv2.rectangle(mask, (0, 0), (image_width, int(image_height * 0.42)), 255, -1)
        return mask

    # Extract forehead boundary points in pixel coordinates
    boundary_pts = []
    for idx in FOREHEAD_BOUNDARY_INDICES:
        lm = landmarks[idx]
        px = int(lm[0] * image_width)
        py = int(lm[1] * image_height)
        boundary_pts.append([px, py])

    # Find forehead top landmark (point #10)
    top_lm = landmarks[LANDMARK_INDICES['forehead_top']]
    top_px = int(top_lm[0] * image_width)
    top_py = int(top_lm[1] * image_height)

    # Hair crown extends above forehead top point
    crown_py = max(0, top_py - int(image_height * 0.25))

    # Construct hair region polygon (top image border down to forehead boundary)
    poly = [[0, 0], [image_width - 1, 0]]
    for pt in reversed(boundary_pts):
        poly.append(pt)

    poly_arr = np.array([poly], dtype=np.int32)
    cv2.fillPoly(mask, poly_arr, 255)

    return mask
