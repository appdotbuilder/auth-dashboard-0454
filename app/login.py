"""Login interface module."""

from nicegui import ui

from app.auth_service import authenticate_user, create_session
from app.auth_middleware import login_user, get_redirect_url, get_current_user
from app.models import UserLogin


def create():
    """Create the login page."""

    @ui.page("/login")
    def login_page():
        # Check if user is already logged in
        if get_current_user():
            ui.navigate.to("/dashboard")
            return

        with ui.column().classes("w-full h-screen bg-gradient-to-br from-blue-50 to-indigo-100"):
            # Center the login form
            with ui.row().classes("w-full h-full justify-center items-center"):
                with ui.card().classes("w-96 p-8 shadow-2xl rounded-xl bg-white"):
                    # Header
                    ui.label("Welcome Back").classes("text-3xl font-bold text-center text-gray-800 mb-2")
                    ui.label("Sign in to your account").classes("text-center text-gray-600 mb-8")

                    # Login form
                    username_input = (
                        ui.input(label="Username", placeholder="Enter your username")
                        .classes("w-full mb-4")
                        .props("outlined")
                    )

                    password_input = (
                        ui.input(
                            label="Password",
                            placeholder="Enter your password",
                            password=True,
                            password_toggle_button=True,
                        )
                        .classes("w-full mb-6")
                        .props("outlined")
                    )

                    # Error message placeholder
                    error_label = ui.label().classes("text-red-500 text-sm mb-4 text-center")
                    error_label.visible = False

                    # Login button
                    login_button = ui.button(
                        "Sign In",
                        on_click=lambda: handle_login(
                            username_input.value, password_input.value, error_label, login_button
                        ),
                    ).classes(
                        "w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition-colors"
                    )

                    # Demo account info
                    with ui.expansion("Demo Account", icon="info").classes("w-full mt-6 bg-gray-50 rounded-lg"):
                        ui.label("For testing purposes:").classes("text-sm text-gray-600 mb-2")
                        ui.label("Username: demo").classes("text-sm font-mono bg-gray-100 px-2 py-1 rounded")
                        ui.label("Password: demo123").classes("text-sm font-mono bg-gray-100 px-2 py-1 rounded mt-1")

                        # Create demo account button
                        ui.button("Create Demo Account", on_click=lambda: create_demo_account(error_label)).classes(
                            "w-full mt-3 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded text-sm"
                        )

                    # Handle Enter key
                    password_input.on(
                        "keydown.enter",
                        lambda: handle_login(username_input.value, password_input.value, error_label, login_button),
                    )


async def handle_login(username: str, password: str, error_label, login_button):
    """Handle user login attempt."""
    # Clear previous errors
    error_label.visible = False
    login_button.props("loading")

    try:
        # Validate inputs
        if not username.strip() or not password.strip():
            show_error(error_label, "Please enter both username and password")
            return

        # Attempt authentication
        login_data = UserLogin(username=username.strip(), password=password)
        user = authenticate_user(login_data)

        if user is None:
            show_error(error_label, "Invalid username or password")
            return

        if user.id is None:
            show_error(error_label, "Authentication error occurred")
            return

        # Create session
        session = create_session(user.id)
        if session is None:
            show_error(error_label, "Failed to create session")
            return

        # Store session and redirect
        login_user(session.session_token)
        ui.notify("Login successful! Welcome back.", type="positive")

        # Redirect to intended page or dashboard
        redirect_url = get_redirect_url()
        ui.navigate.to(redirect_url)

    except Exception as e:
        show_error(error_label, f"Login error: {str(e)}")
    finally:
        login_button.props(remove="loading")


def show_error(error_label, message: str):
    """Show error message to user."""
    error_label.set_text(message)
    error_label.visible = True


def create_demo_account(error_label):
    """Create a demo account for testing."""
    from app.auth_service import create_user
    from app.models import UserCreate

    try:
        demo_user = UserCreate(username="demo", email="demo@example.com", password="demo123", full_name="Demo User")

        user = create_user(demo_user)
        if user:
            ui.notify("Demo account created successfully! You can now log in.", type="positive")
        else:
            show_error(error_label, "Demo account already exists or creation failed")

    except Exception as e:
        show_error(error_label, f"Failed to create demo account: {str(e)}")
