"""
Tests for Admin Panel endpoints and Role-Based Access Control (RBAC).
"""

import pytest


@pytest.fixture
def admin_user(app):
    """Fixture to create an admin user document and token."""
    from server.models.user import UserModel
    from server.services.auth_service import AuthService
    with app.app_context():
        db = app.db
        existing = db.find_user_by_email("admin@example.com")
        if existing:
            user_id = existing['_id']
            db.db.users.update_one({'_id': user_id}, {'$set': {'role': 'admin'}})
        else:
            doc = UserModel.create_document(
                name="Admin User",
                email="admin@example.com",
                password_hash="$2b$12$eImiTXuWVxfM37uY4JANjO.gL",
                gender="female",
                role="admin"
            )
            user_id = db.create_user(doc)

        auth_svc = AuthService(app.config['JWT_SECRET'])
        token = auth_svc.generate_token(str(user_id), role="admin")
        return str(user_id), {'Authorization': f'Bearer {token}'}


class TestAdminRBAC:
    """Test Role-Based Access Control on admin routes."""

    def test_analytics_requires_auth(self, client):
        """Should return 401 when no token is provided."""
        res = client.get('/api/admin/analytics')
        assert res.status_code == 401

    def test_analytics_forbidden_for_regular_user(self, client, auth_headers):
        """Should return 403 for non-admin user."""
        res = client.get('/api/admin/analytics', headers=auth_headers)
        assert res.status_code == 403
        assert 'Admin privileges required' in res.get_json()['error']

    def test_analytics_success_for_admin(self, client, admin_user):
        """Should return 200 and stats for admin user."""
        user_id, headers = admin_user
        res = client.get('/api/admin/analytics', headers=headers)
        data = res.get_json()

        assert res.status_code == 200
        assert 'total_users' in data
        assert 'total_scans' in data
        assert 'face_shape_distribution' in data


class TestAdminUserManagement:
    """Test admin user directory & role management."""

    def test_list_users_for_admin(self, client, admin_user):
        """Should list user directory."""
        _, headers = admin_user
        res = client.get('/api/admin/users', headers=headers)
        data = res.get_json()

        assert res.status_code == 200
        assert 'users' in data
        assert data['total'] >= 1

    def test_update_user_role(self, client, admin_user):
        """Admin should be able to update a user's role."""
        from server.models.user import UserModel
        db = client.application.db
        normal_user_doc = UserModel.create_document(
            name="Normal User",
            email="normal@example.com",
            password_hash="pass",
            role="user"
        )
        normal_user_id = str(db.create_user(normal_user_doc))

        _, admin_headers = admin_user
        res = client.patch(
            f'/api/admin/users/{normal_user_id}',
            json={'role': 'admin'},
            headers=admin_headers
        )
        assert res.status_code == 200
        assert res.get_json()['updated'] is True

        # Verify updated in DB
        updated = db.find_user_by_id(normal_user_id)
        assert updated['role'] == 'admin'


class TestAdminHairstyleCRUD:
    """Test admin hairstyle catalog CRUD."""

    def test_create_and_delete_hairstyle(self, client, admin_user):
        """Admin should be able to create, update, and delete hairstyles."""
        _, headers = admin_user

        # 1. Create
        create_res = client.post('/api/admin/hairstyles', json={
            'name': 'Test Admin Pompadour',
            'slug': 'test-admin-pompadour',
            'gender': 'male',
            'hair_length': 'short',
            'category': 'modern',
            'popularity': 90,
            'face_shapes': ['oval', 'round'],
            'image_url': 'http://example.com/pomp.jpg',
            'description': 'Classic admin pompadour'
        }, headers=headers)

        assert create_res.status_code == 201
        hs_id = create_res.get_json()['hairstyle_id']

        # 2. Update
        update_res = client.put(f'/api/admin/hairstyles/{hs_id}', json={
            'name': 'Updated Admin Pompadour',
            'slug': 'test-admin-pompadour',
            'gender': 'male',
            'hair_length': 'medium',
            'popularity': 95,
            'face_shapes': ['oval', 'round', 'square'],
            'image_url': 'http://example.com/pomp.jpg',
            'description': 'Updated description'
        }, headers=headers)

        assert update_res.status_code == 200

        # 3. Delete
        del_res = client.delete(f'/api/admin/hairstyles/{hs_id}', headers=headers)
        assert del_res.status_code == 200
        assert del_res.get_json()['deleted'] is True
