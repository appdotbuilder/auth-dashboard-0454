"""Tests for dashboard service."""

from datetime import datetime, timedelta

from app.dashboard_service import (
    get_session_duration,
    generate_welcome_message,
    get_dashboard_data,
    get_user_statistics,
)
from app.models import User


def test_get_session_duration_none():
    """Test session duration with None last_login."""
    duration = get_session_duration(None)
    assert duration == "Unknown"


def test_get_session_duration_basic():
    """Test session duration calculation."""
    # Test with a known time difference
    now = datetime.utcnow()

    # 30 seconds ago
    last_login = now - timedelta(seconds=30)
    duration = get_session_duration(last_login)
    # Should contain seconds
    assert "seconds" in duration

    # 5 minutes ago
    last_login = now - timedelta(minutes=5)
    duration = get_session_duration(last_login)
    # Should contain minutes
    assert "minutes" in duration

    # 2 hours ago
    last_login = now - timedelta(hours=2)
    duration = get_session_duration(last_login)
    # Should contain hours
    assert "h" in duration


def test_generate_welcome_message_basic():
    """Test basic welcome message generation."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hash",
        full_name="Test User",
        created_at=datetime.utcnow(),
    )

    message = generate_welcome_message(user)

    # Should contain user's name and welcoming text
    assert "Test User" in message
    assert "Welcome" in message or "Good" in message
    assert "dashboard" in message


def test_get_dashboard_data():
    """Test dashboard data generation."""
    last_login = datetime.utcnow() - timedelta(minutes=30)
    user = User(
        id=1,
        username="dashuser",
        email="dash@example.com",
        password_hash="hash",
        full_name="Dashboard User",
        is_active=True,
        is_authenticated=True,
        last_login=last_login,
        created_at=datetime.utcnow() - timedelta(days=7),
    )

    dashboard_data = get_dashboard_data(user)

    assert dashboard_data.user_info.username == "dashuser"
    assert dashboard_data.user_info.full_name == "Dashboard User"
    assert dashboard_data.user_info.is_active
    assert dashboard_data.user_info.is_authenticated
    assert dashboard_data.login_time == last_login
    assert "Dashboard User" in dashboard_data.welcome_message
    assert dashboard_data.session_duration != "Unknown"


def test_get_dashboard_data_no_last_login():
    """Test dashboard data with no last login."""
    user = User(
        id=2,
        username="newuser",
        email="new@example.com",
        password_hash="hash",
        full_name="New User",
        is_active=True,
        is_authenticated=False,
        last_login=None,
        created_at=datetime.utcnow(),
    )

    dashboard_data = get_dashboard_data(user)

    assert dashboard_data.user_info.username == "newuser"
    assert dashboard_data.login_time is not None  # Should use current time
    assert dashboard_data.session_duration == "Unknown"


def test_get_user_statistics():
    """Test user statistics generation."""
    created_date = datetime.utcnow() - timedelta(days=15)
    last_login = datetime.utcnow() - timedelta(hours=2)

    user = User(
        id=3,
        username="statsuser",
        email="stats@example.com",
        password_hash="hash",
        full_name="Stats User",
        is_active=True,
        is_authenticated=True,
        last_login=last_login,
        created_at=created_date,
    )

    stats = get_user_statistics(user)

    assert stats["account_age_days"] == 15
    assert stats["account_status"] == "Active"
    assert stats["total_logins"] == "N/A"
    assert last_login.strftime("%Y-%m-%d %H:%M:%S") in stats["last_activity"]


def test_get_user_statistics_inactive():
    """Test statistics for inactive user."""
    user = User(
        id=4,
        username="inactive",
        email="inactive@example.com",
        password_hash="hash",
        full_name="Inactive User",
        is_active=False,
        is_authenticated=False,
        last_login=None,
        created_at=datetime.utcnow() - timedelta(days=30),
    )

    stats = get_user_statistics(user)

    assert stats["account_age_days"] == 30
    assert stats["account_status"] == "Inactive"
    assert stats["last_activity"] == "Never"


def test_get_user_statistics_no_id():
    """Test statistics for user without ID."""
    user = User(
        username="noid",
        email="noid@example.com",
        password_hash="hash",
        full_name="No ID User",
        created_at=datetime.utcnow(),
    )

    dashboard_data = get_dashboard_data(user)

    # Should handle None ID gracefully
    assert dashboard_data.user_info.id == 0  # Default value
    assert dashboard_data.user_info.username == "noid"


def test_welcome_message_consistency():
    """Test welcome message consistency."""
    user = User(
        username="timeuser",
        email="time@example.com",
        password_hash="hash",
        full_name="Time User",
        created_at=datetime.utcnow(),
    )

    # Generate message multiple times - should always be consistent
    message1 = generate_welcome_message(user)
    message2 = generate_welcome_message(user)

    # Both should contain user name
    assert "Time User" in message1
    assert "Time User" in message2
    # Both should contain greeting
    assert any(word in message1 for word in ["Welcome", "Good morning", "Good afternoon", "Good evening"])
    assert any(word in message2 for word in ["Welcome", "Good morning", "Good afternoon", "Good evening"])
