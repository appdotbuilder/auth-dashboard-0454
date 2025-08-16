"""Dashboard service for generating dashboard data and content."""

from datetime import datetime
from typing import Optional

from app.models import User, UserResponse, DashboardData


def get_session_duration(last_login: Optional[datetime]) -> str:
    """Calculate session duration from last login."""
    if last_login is None:
        return "Unknown"

    duration = datetime.utcnow() - last_login

    if duration.total_seconds() < 60:
        return f"{int(duration.total_seconds())} seconds"
    elif duration.total_seconds() < 3600:
        return f"{int(duration.total_seconds() / 60)} minutes"
    else:
        hours = int(duration.total_seconds() / 3600)
        minutes = int((duration.total_seconds() % 3600) / 60)
        return f"{hours}h {minutes}m"


def generate_welcome_message(user: User) -> str:
    """Generate personalized welcome message."""
    current_hour = datetime.utcnow().hour

    if 5 <= current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    return f"{greeting}, {user.full_name}! Welcome to your dashboard."


def get_dashboard_data(user: User) -> DashboardData:
    """Generate comprehensive dashboard data for the user."""
    user_response = UserResponse(
        id=user.id if user.id else 0,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_authenticated=user.is_authenticated,
        last_login=user.last_login,
        created_at=user.created_at,
    )

    return DashboardData(
        user_info=user_response,
        login_time=user.last_login if user.last_login else datetime.utcnow(),
        session_duration=get_session_duration(user.last_login),
        welcome_message=generate_welcome_message(user),
    )


def get_user_statistics(user: User) -> dict:
    """Get user-specific statistics for dashboard."""
    stats = {
        "account_age_days": (datetime.utcnow() - user.created_at).days,
        "total_logins": "N/A",  # Would need login history tracking
        "last_activity": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "Never",
        "account_status": "Active" if user.is_active else "Inactive",
    }

    return stats
