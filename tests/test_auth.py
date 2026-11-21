"""
Authentication Route Tests.
Tests user registration, login, and profile retrieval.
"""

import pytest


class TestRegister:
    """Tests for POST /api/auth/register"""

    def test_register_success(self, client, clean_db):
        """Should create a new user and return token."""
        response = client.post('/api/auth/register', json={
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'password': 'StrongPass1',
            'gender': 'female'
        })
        data = response.get_json()

        assert response.status_code == 201
        assert 'token' in data
        assert 'user_id' in data
        assert data['name'] == 'Jane Doe'

    def test_register_duplicate_email(self, client, clean_db):
        """Should reject duplicate email addresses."""
        user_data = {
            'name': 'User One',
            'email': 'dupe@example.com',
            'password': 'StrongPass1',
            'gender': 'female'
        }
        client.post('/api/auth/register', json=user_data)
        response = client.post('/api/auth/register', json=user_data)

        assert response.status_code == 409
        assert 'already exists' in response.get_json()['error']

    def test_register_missing_name(self, client, clean_db):
        """Should reject registration without a name."""
        response = client.post('/api/auth/register', json={
            'name': '',
            'email': 'noname@example.com',
            'password': 'StrongPass1'
        })
        assert response.status_code == 400

    def test_register_invalid_email(self, client, clean_db):
        """Should reject invalid email format."""
        response = client.post('/api/auth/register', json={
            'name': 'Test',
            'email': 'not-an-email',
            'password': 'StrongPass1'
        })
        assert response.status_code == 400
        assert 'email' in response.get_json()['error'].lower()

    def test_register_weak_password(self, client, clean_db):
        """Should reject passwords that don't meet requirements."""
        response = client.post('/api/auth/register', json={
            'name': 'Test',
            'email': 'weak@example.com',
            'password': 'short'
        })
        assert response.status_code == 400
        assert 'password' in response.get_json()['error'].lower()

    def test_register_no_body(self, client, clean_db):
        """Should return 400 when no body is provided."""
        response = client.post('/api/auth/register',
                               content_type='application/json')
        assert response.status_code == 400


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client, clean_db):
        """Should return token on valid credentials."""
        # Register first
        client.post('/api/auth/register', json={
            'name': 'Login Test',
            'email': 'login@example.com',
            'password': 'StrongPass1',
            'gender': 'male'
        })

        # Login
        response = client.post('/api/auth/login', json={
            'email': 'login@example.com',
            'password': 'StrongPass1'
        })
        data = response.get_json()

        assert response.status_code == 200
        assert 'token' in data
        assert data['name'] == 'Login Test'

    def test_login_wrong_password(self, client, clean_db):
        """Should reject incorrect password."""
        client.post('/api/auth/register', json={
            'name': 'Test',
            'email': 'wrong@example.com',
            'password': 'StrongPass1'
        })
        response = client.post('/api/auth/login', json={
            'email': 'wrong@example.com',
            'password': 'WrongPassword1'
        })

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client, clean_db):
        """Should reject login for non-existent email."""
        response = client.post('/api/auth/login', json={
            'email': 'ghost@example.com',
            'password': 'Whatever1'
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, client, clean_db):
        """Should return 400 when fields are missing."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com'
        })
        assert response.status_code == 400


class TestProfile:
    """Tests for GET /api/auth/profile"""

    def test_get_profile_authenticated(self, client, auth_headers):
        """Should return user profile when authenticated."""
        response = client.get('/api/auth/profile', headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['name'] == 'Test User'
        assert data['email'] == 'test@example.com'
        assert 'password' not in str(data)  # Ensure no password leak

    def test_get_profile_no_token(self, client, clean_db):
        """Should return 401 without auth token."""
        response = client.get('/api/auth/profile')
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client, clean_db):
        """Should return 401 with invalid token."""
        response = client.get('/api/auth/profile', headers={
            'Authorization': 'Bearer invalid.token.here'
        })
        assert response.status_code == 401
