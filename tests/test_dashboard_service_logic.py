"""Additional tests for dashboard service logic."""

from datetime import datetime, timedelta

from app.dashboard_service import (
    get_session_duration,
    generate_welcome_message,
    get_dashboard_data,
    get_user_statistics,
)
from app.models import User


def test_session_duration_edge_cases():
    """Test session duration calculation edge cases."""
    now = datetime.utcnow()

    # Test exactly 1 minute
    last_login = now - timedelta(seconds=60)
    duration = get_session_duration(last_login)
    assert "1 minutes" in duration

    # Test exactly 1 hour
    last_login = now - timedelta(seconds=3600)
    duration = get_session_duration(last_login)
    assert "1h 0m" in duration

    # Test mixed hours and minutes
    last_login = now - timedelta(hours=1, minutes=30, seconds=45)
    duration = get_session_duration(last_login)
    assert "1h 30m" in duration


def test_welcome_message_edge_hours():
    """Test welcome message for edge hours."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hash",
        full_name="Test User",
        created_at=datetime.utcnow(),
    )

    # Test 5 AM (morning start)
    test_time = datetime(2024, 1, 1, 5, 0, 0)

    # Mock datetime.utcnow in the function
    import app.dashboard_service

    original_datetime = app.dashboard_service.datetime

    class MockDateTime:
        @staticmethod
        def utcnow():
            return test_time

    app.dashboard_service.datetime = MockDateTime

    try:
        message = generate_welcome_message(user)
        assert "Good morning" in message
    finally:
        app.dashboard_service.datetime = original_datetime

    # Test 12 PM (afternoon start)
    test_time = datetime(2024, 1, 1, 12, 0, 0)
    app.dashboard_service.datetime = MockDateTime

    try:
        message = generate_welcome_message(user)
        assert "Good afternoon" in message
    finally:
        app.dashboard_service.datetime = original_datetime


def test_user_statistics_comprehensive():
    """Test comprehensive user statistics generation."""
    # User created 100 days ago
    created_date = datetime.utcnow() - timedelta(days=100)
    last_login = datetime.utcnow() - timedelta(hours=5, minutes=30)

    user = User(
        id=5,
        username="statstest",
        email="stats@example.com",
        password_hash="hash",
        full_name="Stats Test User",
        is_active=True,
        is_authenticated=True,
        last_login=last_login,
        created_at=created_date,
    )

    stats = get_user_statistics(user)

    assert stats["account_age_days"] == 100
    assert stats["account_status"] == "Active"
    assert stats["total_logins"] == "N/A"

    # Check last activity format
    expected_time = last_login.strftime("%Y-%m-%d %H:%M:%S")
    assert expected_time in stats["last_activity"]


def test_dashboard_data_with_zero_id():
    """Test dashboard data generation when user ID is 0."""
    user = User(
        id=0,  # Edge case
        username="zeroid",
        email="zero@example.com",
        password_hash="hash",
        full_name="Zero ID User",
        is_active=True,
        is_authenticated=True,
        last_login=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    dashboard_data = get_dashboard_data(user)

    assert dashboard_data.user_info.id == 0
    assert dashboard_data.user_info.username == "zeroid"
    assert dashboard_data.welcome_message
    assert dashboard_data.session_duration


def test_dashboard_data_future_login():
    """Test dashboard data with edge case future login time."""
    # Future login time (shouldn't happen in real app, but test resilience)
    future_time = datetime.utcnow() + timedelta(minutes=5)

    user = User(
        id=6,
        username="futureuser",
        email="future@example.com",
        password_hash="hash",
        full_name="Future User",
        is_active=True,
        is_authenticated=True,
        last_login=future_time,
        created_at=datetime.utcnow() - timedelta(days=1),
    )

    dashboard_data = get_dashboard_data(user)

    # Should handle gracefully
    assert dashboard_data.user_info.username == "futureuser"
    assert dashboard_data.login_time == future_time


def test_user_statistics_brand_new_user():
    """Test statistics for brand new user (0 days old)."""
    user = User(
        id=7,
        username="newuser",
        email="new@example.com",
        password_hash="hash",
        full_name="New User",
        is_active=True,
        is_authenticated=False,
        last_login=None,
        created_at=datetime.utcnow(),  # Created right now
    )

    stats = get_user_statistics(user)

    assert stats["account_age_days"] == 0
    assert stats["account_status"] == "Active"
    assert stats["last_activity"] == "Never"
