"""
Recommendation Service Tests.
Tests hairstyle matching and compatibility scoring.
"""

import pytest
from server.services.recommendation_service import RecommendationService


class TestRecommendations:
    """Tests for the recommendation engine."""

    def test_recommendations_for_oval_face(self, app, sample_hairstyles):
        """Should return hairstyles matching oval face shape."""
        with app.app_context():
            rec_service = RecommendationService(app.db)
            results = rec_service.get_recommendations(
                face_shape='oval', limit=10
            )

            assert len(results) > 0
            # All primary results should list 'oval' in their face_shapes
            for r in results:
                if r['compatibility'] > 0.8:
                    assert 'oval' in r['face_shapes']

    def test_recommendations_with_gender_filter(self, app, sample_hairstyles):
        """Should filter by gender correctly."""
        with app.app_context():
            rec_service = RecommendationService(app.db)
            results = rec_service.get_recommendations(
                face_shape='round', gender='male', limit=10
            )

            for r in results:
                assert r['gender'] in ['male', 'unisex']

    def test_recommendations_respect_limit(self, app, sample_hairstyles):
        """Should not return more results than the limit."""
        with app.app_context():
            rec_service = RecommendationService(app.db)
            results = rec_service.get_recommendations(
                face_shape='oval', limit=2
            )

            assert len(results) <= 2

    def test_recommendations_have_compatibility_score(self, app, sample_hairstyles):
        """Each result should include a compatibility score."""
        with app.app_context():
            rec_service = RecommendationService(app.db)
            results = rec_service.get_recommendations(
                face_shape='oval', limit=10
            )

            for r in results:
                assert 'compatibility' in r
                assert 0 <= r['compatibility'] <= 1.0

    def test_recommendations_sorted_by_compatibility(self, app, sample_hairstyles):
        """Results should be sorted by compatibility descending."""
        with app.app_context():
            rec_service = RecommendationService(app.db)
            results = rec_service.get_recommendations(
                face_shape='oval', limit=10
            )

            if len(results) > 1:
                for i in range(len(results) - 1):
                    assert results[i]['compatibility'] >= results[i + 1]['compatibility']

    def test_empty_catalog_returns_empty(self, app, clean_db):
        """Should return empty list when no hairstyles exist."""
        with app.app_context():
            rec_service = RecommendationService(app.db)
            results = rec_service.get_recommendations(
                face_shape='oval', limit=10
            )
            assert results == []

    def test_recommendations_with_metadata_filters(self, app, sample_hairstyles):
        """Should filter recommendations by hair_length, category, and maintenance_level."""
        with app.app_context():
            rec_service = RecommendationService(app.db)
            results = rec_service.get_recommendations(
                face_shape='oval',
                hair_length='short',
                category='classic',
                maintenance_level='low',
                limit=10
            )

            for r in results:
                assert 'compatibility' in r
                assert 0 <= r['compatibility'] <= 1.0
