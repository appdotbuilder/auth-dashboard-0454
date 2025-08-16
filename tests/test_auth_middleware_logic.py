"""Tests for authentication middleware logic without UI context."""

import pytest
from datetime import datetime

from app.auth_service import create_user, create_session, validate_session
from app.models import UserCreate


@pytest.fixture()
def new_db():
    from app.database import reset_db

    reset_db()
    yield
    reset_db()


def test_validate_session_integration(new_db):
    """Test session validation with real database."""
    # Create user
    user_data = UserCreate(
        username="sessiontest", email="session@example.com", password="password123", full_name="Session Test User"
    )
    user = create_user(user_data)
    assert user is not None
    assert user.id is not None

    # Create session
    session = create_session(user.id)
    assert session is not None

    # Validate session
    validated_user = validate_session(session.session_token)
    assert validated_user is not None
    assert validated_user.id == user.id
    assert validated_user.username == user.username


def test_validate_session_invalid_token(new_db):
    """Test validation with invalid token."""
    result = validate_session("invalid_token_12345")
    assert result is None


def test_validate_session_empty_token(new_db):
    """Test validation with empty token."""
    result = validate_session("")
    assert result is None

    result = validate_session("")
    assert result is None


def test_user_authentication_flow(new_db):
    """Test complete user authentication flow."""
    # Create user
    user_data = UserCreate(
        username="flowtest", email="flow@example.com", password="password123", full_name="Flow Test User"
    )
    user = create_user(user_data)
    assert user is not None
    assert user.id is not None

    # Create session
    session = create_session(user.id)
    assert session is not None
    assert session.is_active
    assert len(session.session_token) > 10

    # Validate session works
    validated_user = validate_session(session.session_token)
    assert validated_user is not None
    assert validated_user.username == "flowtest"

    # Logout user
    from app.auth_service import logout_user

    result = logout_user(session.session_token)
    assert result

    # Session should no longer be valid
    validated_user = validate_session(session.session_token)
    assert validated_user is None


def test_session_expiration_logic(new_db):
    """Test session creation with proper expiration."""
    user_data = UserCreate(
        username="expirytest", email="expiry@example.com", password="password123", full_name="Expiry Test User"
    )
    user = create_user(user_data)
    assert user is not None
    assert user.id is not None

    session = create_session(user.id)
    assert session is not None

    # Session should expire in the future
    from datetime import timedelta

    expected_min_expiry = datetime.utcnow() + timedelta(hours=23)
    expected_max_expiry = datetime.utcnow() + timedelta(hours=25)

    assert expected_min_expiry < session.expires_at < expected_max_expiry
