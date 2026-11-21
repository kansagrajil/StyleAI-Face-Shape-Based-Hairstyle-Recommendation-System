"""
Validator Utility Tests.
Tests input validation helpers for email, password, gender, face shape, and pagination.
"""

import pytest
from server.utils.validators import (
    validate_email,
    validate_password,
    validate_gender,
    validate_face_shape,
    validate_pagination
)


class TestEmailValidation:
    """Tests for email format validation."""

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "test.user@domain.co",
        "a@b.io",
        "user+tag@company.org",
    ])
    def test_valid_emails(self, email):
        valid, err = validate_email(email)
        assert valid is True
        assert err is None

    @pytest.mark.parametrize("email", [
        "",
        "not-an-email",
        "@missing.com",
        "user@",
        "user@.com",
    ])
    def test_invalid_emails(self, email):
        valid, err = validate_email(email)
        assert valid is False
        assert err is not None


class TestPasswordValidation:
    """Tests for password strength validation."""

    @pytest.mark.parametrize("password", [
        "StrongP1",
        "MyPass123",
        "Valid1Password",
    ])
    def test_valid_passwords(self, password):
        valid, err = validate_password(password)
        assert valid is True

    @pytest.mark.parametrize("password,reason", [
        ("", "empty"),
        ("Short1", "too short"),
        ("alllowercase1", "no uppercase"),
        ("ALLUPPERCASE1", "no lowercase"),
        ("NoDigitsHere", "no digits"),
    ])
    def test_invalid_passwords(self, password, reason):
        valid, err = validate_password(password)
        assert valid is False, f"Should reject: {reason}"


class TestGenderValidation:
    """Tests for gender enum validation."""

    @pytest.mark.parametrize("gender", ["male", "female", "other", "unisex", ""])
    def test_valid_genders(self, gender):
        valid, _ = validate_gender(gender)
        assert valid is True

    def test_invalid_gender(self):
        valid, err = validate_gender("alien")
        assert valid is False


class TestFaceShapeValidation:
    """Tests for face shape enum validation."""

    @pytest.mark.parametrize("shape", [
        "oval", "round", "square", "heart", "oblong", "diamond", "triangle"
    ])
    def test_valid_shapes(self, shape):
        valid, _ = validate_face_shape(shape)
        assert valid is True

    def test_invalid_shape(self):
        valid, err = validate_face_shape("hexagon")
        assert valid is False


class TestPaginationValidation:
    """Tests for pagination parameter sanitization."""

    def test_default_values(self):
        page, limit = validate_pagination(None, None)
        assert page == 1
        assert limit == 10

    def test_valid_values(self):
        page, limit = validate_pagination(3, 25)
        assert page == 3
        assert limit == 25

    def test_negative_page_clamps_to_one(self):
        page, limit = validate_pagination(-5, 10)
        assert page == 1

    def test_limit_capped_at_50(self):
        page, limit = validate_pagination(1, 100)
        assert limit == 50

    def test_string_inputs(self):
        page, limit = validate_pagination("2", "15")
        assert page == 2
        assert limit == 15

    def test_garbage_inputs(self):
        page, limit = validate_pagination("abc", "xyz")
        assert page == 1
        assert limit == 10
