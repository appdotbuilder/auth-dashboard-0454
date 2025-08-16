"""Tests for authentication middleware logic (non-UI parts)."""

import pytest

from app.auth_service import create_user, create_session
from app.models import UserCreate


@pytest.fixture()
def new_db():
    from app.database import reset_db

    reset_db()
    yield
    reset_db()


def test_middleware_integration_with_real_auth(new_db):
    """Test middleware integration with real authentication service."""
    # Create user
    user_data = UserCreate(
        username="middlewareuser", email="middleware@example.com", password="password123", full_name="Middleware User"
    )
    user = create_user(user_data)
    assert user is not None
    assert user.id is not None

    # Create session
    session = create_session(user.id)
    assert session is not None

    # Test session validation
    from app.auth_service import validate_session

    validated_user = validate_session(session.session_token)
    assert validated_user is not None
    assert validated_user.id == user.id


def test_auth_flow_edge_cases(new_db):
    """Test authentication edge cases."""
    # Test with None session token
    from app.auth_service import validate_session

    result = validate_session(None)
    assert result is None

    # Test with empty session token
    result = validate_session("")
    assert result is None

    # Test with malformed session token
    result = validate_session("malformed_token_123")
    assert result is None


def test_multiple_sessions_per_user(new_db):
    """Test creating multiple sessions for the same user."""
    user_data = UserCreate(
        username="multisession", email="multi@example.com", password="password123", full_name="Multi Session User"
    )
    user = create_user(user_data)
    assert user is not None
    assert user.id is not None

    # Create first session
    session1 = create_session(user.id)
    assert session1 is not None

    # Create second session (should deactivate first)
    session2 = create_session(user.id)
    assert session2 is not None

    # Tokens should be different
    assert session1.session_token != session2.session_token

    # Second session should be valid
    from app.auth_service import validate_session

    validated_user = validate_session(session2.session_token)
    assert validated_user is not None
