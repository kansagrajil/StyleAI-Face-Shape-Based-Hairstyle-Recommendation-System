"""
Classifier Service Tests.
Tests the rule-based face shape classification fallback.
"""

import pytest
from server.services.classifier_service import ClassifierService


@pytest.fixture
def classifier():
    """Create a ClassifierService with no model (rule-based mode)."""
    return ClassifierService(model_path=None)


def _make_landmarks_with_features(jaw_w, forehead_w, face_len, cheek_w,
                                   jaw_angle_offset=0.0, chin_depth=0.05):
    """
    Build synthetic landmarks that produce the desired geometric measurements.
    Positions key landmarks to approximate target feature values.
    """
    landmarks = [[0.5, 0.5, 0.0]] * 468

    half_jaw = jaw_w / 2
    half_fore = forehead_w / 2
    half_cheek = cheek_w / 2

    landmarks[234] = [0.5 - half_jaw, 0.55, 0.0]    # jaw_left
    landmarks[454] = [0.5 + half_jaw, 0.55, 0.0]    # jaw_right
    landmarks[71]  = [0.5 - half_fore, 0.35, 0.0]   # forehead_left
    landmarks[301] = [0.5 + half_fore, 0.35, 0.0]   # forehead_right
    landmarks[10]  = [0.5, 0.5 - face_len / 2, 0.0] # forehead_top
    landmarks[152] = [0.5, 0.5 + face_len / 2, 0.0] # chin
    landmarks[123] = [0.5 - half_cheek, 0.48, 0.0]  # cheekbone_left
    landmarks[352] = [0.5 + half_cheek, 0.48, 0.0]  # cheekbone_right
    landmarks[172] = [0.5 - half_jaw + 0.05, 0.5 + face_len / 2 - 0.10 + jaw_angle_offset, 0.0]
    landmarks[397] = [0.5 + half_jaw - 0.05, 0.5 + face_len / 2 - 0.10 + jaw_angle_offset, 0.0]
    landmarks[148] = [0.5 - 0.06, 0.5 + face_len / 2 - chin_depth, 0.0]
    landmarks[377] = [0.5 + 0.06, 0.5 + face_len / 2 - chin_depth, 0.0]

    return landmarks


class TestRuleBasedClassifier:
    """Tests for the rule-based fallback classification."""

    def test_classifier_uses_rule_based(self, classifier):
        """Classifier without model should use rule-based mode."""
        assert classifier.model is None
        assert classifier.model_version == 'rule-based-v1.0'

    def test_classify_returns_required_fields(self, classifier):
        """Classification result should have all required fields."""
        landmarks = _make_landmarks_with_features(0.40, 0.36, 0.60, 0.42)
        result = classifier.classify(landmarks)

        assert 'face_shape' in result
        assert 'confidence' in result
        assert 'all_scores' in result
        assert 'model_version' in result

    def test_classify_shape_is_valid(self, classifier):
        """Detected shape should be one of the 7 valid categories."""
        valid_shapes = {'oval', 'round', 'square', 'heart', 'oblong', 'diamond', 'triangle'}
        landmarks = _make_landmarks_with_features(0.40, 0.36, 0.60, 0.42)
        result = classifier.classify(landmarks)

        assert result['face_shape'] in valid_shapes

    def test_confidence_in_range(self, classifier):
        """Confidence should be between 0 and 1."""
        landmarks = _make_landmarks_with_features(0.40, 0.36, 0.60, 0.42)
        result = classifier.classify(landmarks)

        assert 0 <= result['confidence'] <= 1.0

    def test_all_scores_sum_approximately_one(self, classifier):
        """All scores should sum to approximately 1.0."""
        landmarks = _make_landmarks_with_features(0.40, 0.36, 0.60, 0.42)
        result = classifier.classify(landmarks)

        total = sum(result['all_scores'].values())
        assert abs(total - 1.0) < 0.01, f"Scores sum to {total}, expected ~1.0"

    def test_round_face_detection(self, classifier):
        """Wide face relative to length should classify as round."""
        # Round: width ≈ length, W:L > 0.80
        landmarks = _make_landmarks_with_features(
            jaw_w=0.50, forehead_w=0.48, face_len=0.55, cheek_w=0.50,
            chin_depth=0.02  # round chin
        )
        result = classifier.classify(landmarks)
        # Round should score highly
        assert result['all_scores']['round'] > 0

    def test_heart_face_detection(self, classifier):
        """Wide forehead + narrow jaw should classify as heart."""
        landmarks = _make_landmarks_with_features(
            jaw_w=0.28, forehead_w=0.44, face_len=0.60, cheek_w=0.36,
            chin_depth=0.02
        )
        result = classifier.classify(landmarks)
        assert result['all_scores']['heart'] > 0

    def test_oblong_face_detection(self, classifier):
        """Very long face should classify as oblong."""
        landmarks = _make_landmarks_with_features(
            jaw_w=0.30, forehead_w=0.30, face_len=0.70, cheek_w=0.32
        )
        result = classifier.classify(landmarks)
        assert result['all_scores']['oblong'] > 0

    def test_triangle_face_detection(self, classifier):
        """Wide jaw + narrow forehead should classify as triangle without KeyError."""
        landmarks = _make_landmarks_with_features(
            jaw_w=0.48, forehead_w=0.32, face_len=0.60, cheek_w=0.38
        )
        result = classifier.classify(landmarks)
        assert 'triangle' in result['all_scores']
        assert result['all_scores']['triangle'] > 0
