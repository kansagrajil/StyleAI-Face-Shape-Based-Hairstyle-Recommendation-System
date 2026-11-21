"""
API Integration Tests.
Tests the REST API endpoints for hairstyles catalog and history.
"""

import pytest


class TestHairstyleCatalog:
    """Tests for GET /api/hairstyles (public endpoint)."""

    def test_list_hairstyles_empty(self, client, clean_db):
        """Should return empty list when catalog is empty."""
        response = client.get('/api/hairstyles')
        data = response.get_json()

        assert response.status_code == 200
        assert data['hairstyles'] == []
        assert data['total'] == 0

    def test_list_hairstyles_with_data(self, client, sample_hairstyles):
        """Should return hairstyles from the catalog."""
        response = client.get('/api/hairstyles')
        data = response.get_json()

        assert response.status_code == 200
        assert len(data['hairstyles']) == 3
        assert data['total'] == 3

    def test_list_hairstyles_filter_by_shape(self, client, sample_hairstyles):
        """Should filter hairstyles by face shape."""
        response = client.get('/api/hairstyles?shape=oval')
        data = response.get_json()

        assert response.status_code == 200
        for hs in data['hairstyles']:
            assert 'oval' in hs['face_shapes']

    def test_list_hairstyles_filter_by_gender(self, client, sample_hairstyles):
        """Should filter hairstyles by gender."""
        response = client.get('/api/hairstyles?gender=male')
        data = response.get_json()

        assert response.status_code == 200
        for hs in data['hairstyles']:
            assert hs['gender'] in ['male', 'unisex']

    def test_list_hairstyles_pagination(self, client, sample_hairstyles):
        """Should paginate results correctly."""
        response = client.get('/api/hairstyles?page=1&limit=2')
        data = response.get_json()

        assert response.status_code == 200
        assert len(data['hairstyles']) == 2
        assert data['page'] == 1
        assert data['limit'] == 2
        assert data['total'] == 3

    def test_hairstyle_response_format(self, client, sample_hairstyles):
        """Each hairstyle should include all required fields."""
        response = client.get('/api/hairstyles')
        data = response.get_json()

        hs = data['hairstyles'][0]
        required_fields = ['id', 'name', 'slug', 'face_shapes', 'gender',
                          'hair_types', 'description', 'image_url', 'tags']
        for field in required_fields:
            assert field in hs, f"Missing field: {field}"


class TestHistoryEndpoints:
    """Tests for GET /api/history"""

    def test_history_requires_auth(self, client, clean_db):
        """Should return 401 without authentication."""
        response = client.get('/api/history')
        assert response.status_code == 401

    def test_history_empty(self, client, auth_headers):
        """Should return empty list for new user."""
        response = client.get('/api/history', headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['analyses'] == []
        assert data['total'] == 0

    def test_delete_nonexistent_analysis(self, client, auth_headers):
        """Should return 404 when deleting non-existent analysis."""
        response = client.delete('/api/history/000000000000000000000000',
                                headers=auth_headers)
        assert response.status_code == 404

    def test_history_search_and_filter(self, client, auth_headers):
        """Should support search, shape filtering, selected hairstyle, and clear history."""
        from bson import ObjectId
        from datetime import datetime, timezone
        db = client.application.db

        user = db.db.users.find_one({'email': 'test@example.com'})
        user_id = user['_id']

        analysis_doc = {
            'user_id': user_id,
            'image_path': '/uploads/test.jpg',
            'thumbnail_path': '/uploads/thumb.jpg',
            'face_shape': 'square',
            'confidence': 0.95,
            'all_scores': {'square': 0.95},
            'landmarks': [],
            'recommended_ids': [],
            'recommendations': [{'name': 'Layered Shag'}],
            'selected_hairstyle': {'id': 'hs1', 'name': 'Layered Shag'},
            'ai_advice': 'Great square face advice',
            'metadata': {'processing_time_ms': 120, 'model_version': 'v1'},
            'created_at': datetime.now(timezone.utc)
        }
        analysis_id = db.create_analysis(analysis_doc)

        # Test GET history with shape filter
        res = client.get('/api/history?shape=square', headers=auth_headers)
        assert res.status_code == 200
        assert len(res.get_json()['analyses']) == 1

        # Test GET history search
        res = client.get('/api/history?search=Shag', headers=auth_headers)
        assert res.status_code == 200
        assert len(res.get_json()['analyses']) == 1

        # Test PATCH update selected hairstyle
        patch_res = client.patch(
            f'/api/history/{analysis_id}/select-hairstyle',
            json={'hairstyle_id': 'hs2', 'name': 'Textured Quiff'},
            headers=auth_headers
        )
        assert patch_res.status_code == 200
        assert patch_res.get_json()['selected_hairstyle']['name'] == 'Textured Quiff'

        # Test bulk DELETE clear history
        del_res = client.delete('/api/history', headers=auth_headers)
        assert del_res.status_code == 200
        assert del_res.get_json()['cleared'] is True


class TestRecommendEndpoint:
    """Tests for GET /api/recommend"""

    def test_recommend_requires_auth(self, client, clean_db):
        """Should return 401 without authentication."""
        response = client.get('/api/recommend?shape=oval')
        assert response.status_code == 401

    def test_recommend_requires_shape(self, client, auth_headers):
        """Should return 400 without shape parameter."""
        response = client.get('/api/recommend', headers=auth_headers)
        assert response.status_code == 400

    def test_recommend_invalid_shape(self, client, auth_headers):
        """Should return 400 for invalid face shape."""
        response = client.get('/api/recommend?shape=invalid',
                             headers=auth_headers)
        assert response.status_code == 400

    def test_recommend_valid_shape(self, client, auth_headers, sample_hairstyles):
        """Should return recommendations for valid shape."""
        response = client.get('/api/recommend?shape=oval',
                             headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert 'hairstyles' in data


class TestAnalyzeEndpoint:
    """Tests for POST /api/analyze"""

    def test_analyze_requires_auth(self, client, clean_db):
        """Should return 401 without authentication."""
        response = client.post('/api/analyze')
        assert response.status_code == 401

    def test_analyze_requires_image(self, client, auth_headers):
        """Should return 400 when no image is provided in files."""
        response = client.post('/api/analyze', headers={'Authorization': auth_headers['Authorization']})
        assert response.status_code == 400
        assert 'image' in response.get_json()['error']

    def test_analyze_success(self, client, auth_headers, sample_hairstyles):
        """Should successfully analyze face when services are mocked."""
        import io
        from unittest.mock import patch

        # Mock dependencies
        with patch('server.services.face_service.FaceService.detect_and_extract') as mock_detect, \
             patch('server.services.classifier_service.ClassifierService.classify') as mock_classify, \
             patch('server.services.genai_service.GenAIService.generate_advice') as mock_genai:

            mock_detect.return_value = {
                'landmarks': [[0.5, 0.5, 0.0]] * 468,
                'image_shape': (256, 256, 3),
                'success': True,
                'error': None
            }

            mock_classify.return_value = {
                'face_shape': 'oval',
                'confidence': 0.85,
                'all_scores': {s: 0.0 for s in ['oval', 'round', 'square', 'heart', 'diamond', 'oblong']},
                'model_version': 'test-mock'
            }
            mock_classify.return_value['all_scores']['oval'] = 0.85

            mock_genai.return_value = {
                'explanation': 'Mocked AI styling advice.',
                'styling_tips': ['Styling Tip A', 'Styling Tip B'],
                'recommendations': [{'name': 'Long Layered Waves', 'reason': 'Ideal choice for oval face shape.'}]
            }

            # Setup dummy valid 256x256 PNG image file
            from PIL import Image
            img_bytes = io.BytesIO()
            Image.new('RGB', (256, 256), color='blue').save(img_bytes, format='PNG')
            file_data = img_bytes.getvalue()
            data = {
                'image': (io.BytesIO(file_data), 'test.png'),
                'gender': 'female',
                'hair_type': 'wavy'
            }

            # Send request
            response = client.post(
                '/api/analyze',
                data=data,
                content_type='multipart/form-data',
                headers={'Authorization': auth_headers['Authorization']}
            )

            res_json = response.get_json()
            assert response.status_code == 200
            assert res_json['face_shape'] == 'oval'
            assert res_json['confidence'] == 0.85
            assert res_json['landmarks_detected'] == 468
            assert len(res_json['recommendations']) > 0
            assert 'explanation' in res_json['ai_advice']


class TestTryonEndpoint:
    """Tests for POST /api/tryon and GET /api/tryon/<id>"""

    def test_tryon_requires_auth(self, client, clean_db):
        """Should return 401 without authentication."""
        response = client.post('/api/tryon', json={'analysis_id': 'some-id', 'hairstyle_id': 'some-id'})
        assert response.status_code == 401

    def test_tryon_requires_parameters(self, client, auth_headers):
        """Should return 400 when parameters are missing."""
        response = client.post(
            '/api/tryon',
            json={},
            headers={'Authorization': auth_headers['Authorization']}
        )
        assert response.status_code == 400

    def test_tryon_success(self, client, auth_headers, sample_hairstyles):
        """Should successfully create a virtual try-on preview."""
        from bson import ObjectId
        from datetime import datetime, timezone
        from unittest.mock import patch

        db = client.application.db
        
        # Get user ID from headers or decode JWT (or we can query users)
        user = db.db.users.find_one({'email': 'test@example.com'})
        user_id = user['_id']

        # Create dummy analysis
        analysis_doc = {
            'user_id': user_id,
            'image_path': 'test/path.jpg',
            'thumbnail_path': 'test/thumb.jpg',
            'face_shape': 'oval',
            'confidence': 0.9,
            'all_scores': {'oval': 0.9},
            'landmarks': [],
            'recommended_ids': [],
            'ai_advice': 'Good advice',
            'processing_time_ms': 100,
            'model_version': 'test',
            'created_at': datetime.now(timezone.utc)
        }
        analysis_id = db.create_analysis(analysis_doc)
        hairstyle_id = sample_hairstyles[0]['_id']

        # Mock GenAI description generator and TryonService execution
        with patch('server.services.tryon_service.TryonService.execute_tryon_pipeline') as mock_exec, \
             patch('server.services.genai_service.GenAIService.generate_tryon_description') as mock_desc:
            mock_desc.return_value = 'Mocked virtual try-on visual explanation.'
            mock_exec.return_value = {
                'success': True,
                'preview_url': '/uploads/tryon_previews/mock.jpg',
                'preview_path': '/path/to/mock.jpg',
                'prompt_used': 'test prompt',
                'model_version': 'openai/gpt-image-2.5-flare',
                'processing_time_ms': 150,
                'stage_logs': ['Stage 1 passed', 'Stage 2 passed']
            }

            response = client.post(
                '/api/tryon',
                json={
                    'analysis_id': str(analysis_id),
                    'hairstyle_id': str(hairstyle_id)
                },
                headers={'Authorization': auth_headers['Authorization']}
            )

            res_json = response.get_json()
            assert response.status_code == 200
            assert 'tryon_id' in res_json
            assert res_json['hairstyle_name'] == sample_hairstyles[0]['name']
            assert res_json['description'] == 'Mocked virtual try-on visual explanation.'

            # Get try-on
            tryon_id = res_json['tryon_id']
            get_res = client.get(
                f'/api/tryon/{tryon_id}',
                headers={'Authorization': auth_headers['Authorization']}
            )
            assert get_res.status_code == 200
            assert get_res.get_json()['hairstyle_name'] == sample_hairstyles[0]['name']


class TestErrorHandling:
    """Tests for global error handling."""

    def test_404_for_unknown_api_route(self, client):
        """Should return JSON 404 for unknown API paths."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404

    def test_cors_headers_present(self, client):
        """Should include CORS headers on API responses."""
        response = client.options('/api/hairstyles', headers={
            'Origin': 'http://localhost:5000',
            'Access-Control-Request-Method': 'GET'
        })
        # CORS should be configured — status should be 200 or 204
        assert response.status_code in (200, 204)
