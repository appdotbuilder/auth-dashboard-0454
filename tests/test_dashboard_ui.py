"""UI tests for dashboard functionality."""

import pytest
from nicegui.testing import User as TestUser
from nicegui import ui


@pytest.fixture()
def new_db():
    from app.database import reset_db

    reset_db()
    yield
    reset_db()


async def test_dashboard_requires_auth_redirect(user: TestUser) -> None:
    """Test that dashboard requires authentication and redirects to login."""
    await user.open("/dashboard")

    # Should be redirected to login page
    await user.should_see("Welcome Back")
    await user.should_see("Sign in to your account")


async def test_dashboard_protection_mechanism(user: TestUser) -> None:
    """Test that dashboard is properly protected."""
    # Try to access dashboard without authentication
    await user.open("/dashboard")

    # Should not see dashboard content, should see login form
    await user.should_see("Welcome Back")
    await user.should_not_see("Dashboard")  # Dashboard title should not be visible


async def test_ui_elements_structure(user: TestUser, new_db) -> None:
    """Test basic UI elements structure after redirect."""
    await user.open("/dashboard")

    # Should be redirected to login
    await user.should_see("Username")
    await user.should_see("Password")

    # Check essential form elements exist
    username_fields = list(user.find(ui.input).elements)
    assert len(username_fields) >= 2  # Username and password fields

    buttons = list(user.find(ui.button).elements)
    assert len(buttons) >= 1  # At least sign in button
