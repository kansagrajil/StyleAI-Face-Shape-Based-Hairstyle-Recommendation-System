"""
Face Service & Landmark Utility Tests.
Tests geometric feature computation from synthetic landmarks.
"""

import pytest
import math
from server.utils.landmark_utils import compute_geometric_features, _distance, _angle


class TestLandmarkDistance:
    """Tests for the Euclidean distance helper."""

    def test_distance_same_point(self):
        """Distance from a point to itself should be zero."""
        assert _distance([0.5, 0.5], [0.5, 0.5]) == 0.0

    def test_distance_known_values(self):
        """Distance should match expected Euclidean distance."""
        d = _distance([0, 0], [3, 4])
        assert abs(d - 5.0) < 1e-6

    def test_distance_3d_uses_2d(self):
        """Distance should only use x, y (ignore z)."""
        d = _distance([0, 0, 100], [3, 4, 200])
        assert abs(d - 5.0) < 1e-6


class TestLandmarkAngle:
    """Tests for the angle computation helper."""

    def test_right_angle(self):
        """90-degree angle at the origin."""
        angle = _angle([1, 0], [0, 0], [0, 1])
        assert abs(angle - 90.0) < 1e-3

    def test_straight_angle(self):
        """180-degree angle (straight line)."""
        angle = _angle([-1, 0], [0, 0], [1, 0])
        assert abs(angle - 180.0) < 0.01

    def test_acute_angle(self):
        """45-degree angle."""
        angle = _angle([1, 0], [0, 0], [1, 1])
        assert abs(angle - 45.0) < 1e-3


class TestGeometricFeatures:
    """Tests for the full geometric feature extraction."""

    @staticmethod
    def _make_fake_landmarks():
        """
        Create a synthetic set of 468 landmarks for a roughly oval face.
        Only the key landmark indices are positioned meaningfully.
        """
        # Default all landmarks to center of face
        landmarks = [[0.5, 0.5, 0.0]] * 468

        # Position key landmarks for an oval-ish face
        landmarks[234] = [0.30, 0.55, 0.0]   # jaw_left
        landmarks[454] = [0.70, 0.55, 0.0]   # jaw_right
        landmarks[71]  = [0.32, 0.35, 0.0]   # forehead_left
        landmarks[301] = [0.68, 0.35, 0.0]   # forehead_right
        landmarks[152] = [0.50, 0.85, 0.0]   # chin
        landmarks[10]  = [0.50, 0.15, 0.0]   # forehead_top
        landmarks[123] = [0.28, 0.48, 0.0]   # cheekbone_left
        landmarks[352] = [0.72, 0.48, 0.0]   # cheekbone_right
        landmarks[172] = [0.35, 0.70, 0.0]   # jaw_angle_left
        landmarks[397] = [0.65, 0.70, 0.0]   # jaw_angle_right
        landmarks[148] = [0.42, 0.80, 0.0]   # chin_left
        landmarks[377] = [0.58, 0.80, 0.0]   # chin_right
        landmarks[1]   = [0.50, 0.55, 0.0]   # nose_tip

        return landmarks

    def test_features_returns_all_keys(self):
        """Should return all expected feature keys."""
        landmarks = self._make_fake_landmarks()
        features = compute_geometric_features(landmarks)

        expected_keys = [
            'jaw_width', 'forehead_width', 'face_length', 'cheekbone_width',
            'width_to_length_ratio', 'forehead_to_jaw_ratio',
            'cheekbone_to_jaw_ratio', 'jaw_angle', 'chin_roundness'
        ]
        for key in expected_keys:
            assert key in features, f"Missing feature: {key}"

    def test_features_are_numeric(self):
        """All feature values should be valid numbers."""
        landmarks = self._make_fake_landmarks()
        features = compute_geometric_features(landmarks)

        for key, value in features.items():
            assert isinstance(value, (int, float)), f"{key} is not numeric: {value}"
            assert not math.isnan(value), f"{key} is NaN"
            assert not math.isinf(value), f"{key} is infinite"

    def test_ratios_are_positive(self):
        """All ratio features should be positive."""
        landmarks = self._make_fake_landmarks()
        features = compute_geometric_features(landmarks)

        for key in ['width_to_length_ratio', 'forehead_to_jaw_ratio', 'cheekbone_to_jaw_ratio']:
            assert features[key] > 0, f"{key} should be positive, got {features[key]}"

    def test_oval_shape_ratios(self):
        """Synthetic oval landmarks should produce balanced ratios."""
        landmarks = self._make_fake_landmarks()
        features = compute_geometric_features(landmarks)

        # For our synthetic oval, width:length should be moderate
        assert 0.4 < features['width_to_length_ratio'] < 0.9
        # Forehead and jaw should be roughly similar
        assert 0.7 < features['forehead_to_jaw_ratio'] < 1.3
