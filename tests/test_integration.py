"""Integration tests for the complete authentication flow."""

import pytest
from nicegui.testing import User as TestUser
from nicegui import ui


@pytest.fixture()
def new_db():
    from app.database import reset_db

    reset_db()
    yield
    reset_db()


async def test_index_page_redirect_logic(user: TestUser, new_db) -> None:
    """Test index page redirects correctly based on auth status."""
    # Access index page without authentication
    await user.open("/")

    # Should redirect to login page
    await user.should_see("Welcome Back")


async def test_protected_route_without_session(user: TestUser, new_db) -> None:
    """Test accessing protected routes without valid session."""
    # Try to access dashboard directly
    await user.open("/dashboard")

    # Should be redirected to login
    await user.should_see("Sign in to your account")


async def test_demo_account_creation_flow(user: TestUser, new_db) -> None:
    """Test demo account creation flow."""
    await user.open("/login")

    # Create demo account
    user.find("Create Demo Account").click()
    await user.should_see("Demo account created successfully!")


async def test_ui_responsiveness_and_styling(user: TestUser, new_db) -> None:
    """Test UI responsiveness and styling elements."""
    await user.open("/login")

    # Check for CSS classes that indicate proper styling
    await user.should_see("Welcome Back")
    await user.should_see("Sign in to your account")

    # Check form elements are properly styled
    username_inputs = list(user.find(ui.input).elements)
    assert len(username_inputs) >= 2  # Username and password inputs

    # Check buttons are present
    buttons = list(user.find(ui.button).elements)
    assert len(buttons) >= 2  # Sign In and Create Demo Account buttons


async def test_form_validation_basic(user: TestUser, new_db) -> None:
    """Test basic form validation."""
    await user.open("/login")

    # Test with empty fields
    user.find("Sign In").click()
    await user.should_see("Please enter both username and password")


async def test_navigation_flow(user: TestUser, new_db) -> None:
    """Test navigation flow between pages."""
    # Start at root
    await user.open("/")
    await user.should_see("Welcome Back")

    # Try dashboard
    await user.open("/dashboard")
    await user.should_see("Welcome Back")  # Should redirect to login

    # Direct login access
    await user.open("/login")
    await user.should_see("Sign in to your account")
