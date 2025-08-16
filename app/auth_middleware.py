"""Authentication middleware for protecting routes and managing sessions."""

from functools import wraps
from typing import Optional, Callable

from nicegui import app, ui

from app.auth_service import validate_session
from app.models import User


def get_current_user() -> Optional[User]:
    """Get the current authenticated user from session storage."""
    session_token = app.storage.user.get("session_token")
    if not session_token:
        return None

    return validate_session(session_token)


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication for a page."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is None:
            # Store the intended destination
            request_url = getattr(ui.context.client, "request", None)
            if request_url and hasattr(request_url, "url"):
                app.storage.user["redirect_after_login"] = request_url.url.path
            ui.navigate.to("/login")
            return None
        return func(*args, **kwargs)

    return wrapper


def login_user(session_token: str) -> None:
    """Store session token in user storage."""
    app.storage.user["session_token"] = session_token


def logout_current_user() -> None:
    """Clear session from user storage."""
    if "session_token" in app.storage.user:
        del app.storage.user["session_token"]
    if "redirect_after_login" in app.storage.user:
        del app.storage.user["redirect_after_login"]


def get_redirect_url() -> str:
    """Get the URL to redirect to after login."""
    return app.storage.user.get("redirect_after_login", "/dashboard")
