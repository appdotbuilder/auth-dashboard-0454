"""UI tests for login functionality."""

import pytest
from nicegui.testing import User as TestUser
from nicegui import ui

from app.models import UserCreate
from app.auth_service import create_user


@pytest.fixture()
def new_db():
    from app.database import reset_db

    reset_db()
    yield
    reset_db()


async def test_login_page_loads(user: TestUser) -> None:
    """Test that login page loads correctly."""
    await user.open("/login")

    # Check for main elements
    await user.should_see("Welcome Back")
    await user.should_see("Sign in to your account")
    await user.should_see("Username")
    await user.should_see("Password")
    await user.should_see("Sign In")


async def test_demo_account_section(user: TestUser) -> None:
    """Test demo account information section."""
    await user.open("/login")

    # Check for demo account section
    await user.should_see("Demo Account")
    await user.should_see("Username: demo")
    await user.should_see("Password: demo123")
    await user.should_see("Create Demo Account")


async def test_create_demo_account(user: TestUser, new_db) -> None:
    """Test creating demo account."""
    await user.open("/login")

    # Click create demo account button
    user.find("Create Demo Account").click()

    # Should see success notification
    await user.should_see("Demo account created successfully!")


async def test_create_demo_account_duplicate(user: TestUser, new_db) -> None:
    """Test creating demo account when it already exists."""
    # Create demo user first
    demo_user = UserCreate(username="demo", email="demo@example.com", password="demo123", full_name="Demo User")
    create_user(demo_user)

    await user.open("/login")

    # Try to create demo account again
    user.find("Create Demo Account").click()

    # Should see error message
    await user.should_see("Demo account already exists")


async def test_login_empty_fields(user: TestUser, new_db) -> None:
    """Test login with empty fields."""
    await user.open("/login")

    # Try to login without entering credentials
    user.find("Sign In").click()

    # Should see error message
    await user.should_see("Please enter both username and password")


async def test_basic_form_elements(user: TestUser) -> None:
    """Test basic form elements are present and functional."""
    await user.open("/login")

    # Find form elements
    inputs = list(user.find(ui.input).elements)
    assert len(inputs) >= 2  # Username and password inputs

    buttons = list(user.find(ui.button).elements)
    assert len(buttons) >= 1  # At least sign in button

    # Test that we can interact with form elements
    await user.should_see("Username")
    await user.should_see("Password")
    await user.should_see("Sign In")
