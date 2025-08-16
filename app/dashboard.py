"""Dashboard interface module."""

from nicegui import ui

from app.auth_middleware import require_auth, get_current_user, logout_current_user
from app.auth_service import logout_user
from app.dashboard_service import get_dashboard_data, get_user_statistics
from nicegui import app


def create():
    """Create the dashboard page."""

    @ui.page("/dashboard")
    @require_auth
    def dashboard_page():
        user = get_current_user()
        if user is None:
            return

        # Get dashboard data
        dashboard_data = get_dashboard_data(user)
        user_stats = get_user_statistics(user)

        # Apply modern theme colors
        ui.colors(
            primary="#2563eb",
            secondary="#64748b",
            accent="#10b981",
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
            info="#3b82f6",
        )

        with ui.column().classes("w-full min-h-screen bg-gray-50"):
            # Header with navigation
            create_header(user, dashboard_data)

            # Main content
            with ui.row().classes("w-full flex-1 p-6 gap-6"):
                # Main dashboard content
                with ui.column().classes("flex-1 gap-6"):
                    # Welcome section
                    create_welcome_section(dashboard_data)

                    # Metrics cards
                    create_metrics_section(user_stats)

                    # Activity section
                    create_activity_section(dashboard_data)

                # Sidebar
                create_sidebar(user, dashboard_data)


def create_header(user, dashboard_data):
    """Create the dashboard header with navigation."""
    with ui.row().classes("w-full bg-white shadow-sm px-6 py-4 justify-between items-center"):
        # Logo and title
        with ui.row().classes("items-center gap-4"):
            ui.icon("dashboard", size="2rem").classes("text-primary")
            ui.label("Dashboard").classes("text-2xl font-bold text-gray-800")

        # User menu
        with ui.row().classes("items-center gap-4"):
            ui.label(f"Welcome, {user.full_name}").classes("text-gray-600")

            # User avatar and menu
            with ui.button(icon="account_circle", color="primary").props("round"):
                with ui.menu():
                    ui.menu_item("Profile", lambda: ui.notify("Profile page coming soon!", type="info"))
                    ui.menu_item("Settings", lambda: ui.notify("Settings page coming soon!", type="info"))
                    ui.separator()
                    ui.menu_item("Logout", on_click=handle_logout)


def create_welcome_section(dashboard_data):
    """Create the welcome section."""
    with ui.card().classes("w-full p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl shadow-lg"):
        ui.label(dashboard_data.welcome_message).classes("text-2xl font-bold mb-2")
        ui.label(f"Session started: {dashboard_data.login_time.strftime('%Y-%m-%d %H:%M:%S')}").classes("text-blue-100")
        ui.label(f"Active for: {dashboard_data.session_duration}").classes("text-blue-100")


def create_metrics_section(user_stats):
    """Create the metrics cards section."""
    ui.label("Account Overview").classes("text-xl font-semibold text-gray-800 mb-4")

    with ui.row().classes("w-full gap-4"):
        # Account age card
        create_metric_card(
            title="Account Age",
            value=f"{user_stats['account_age_days']} days",
            icon="calendar_today",
            color="bg-blue-500",
        )

        # Account status card
        status_color = "bg-green-500" if user_stats["account_status"] == "Active" else "bg-red-500"
        create_metric_card(
            title="Account Status", value=user_stats["account_status"], icon="verified_user", color=status_color
        )

        # Last activity card
        create_metric_card(
            title="Last Activity", value=user_stats["last_activity"], icon="access_time", color="bg-purple-500"
        )


def create_metric_card(title: str, value: str, icon: str, color: str):
    """Create a metric card component."""
    with ui.card().classes(f"p-6 text-white rounded-xl shadow-lg hover:shadow-xl transition-shadow {color}"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.column().classes("gap-2"):
                ui.label(title).classes("text-sm opacity-90")
                ui.label(value).classes("text-xl font-bold")
            ui.icon(icon, size="2rem").classes("opacity-80")


def create_activity_section(dashboard_data):
    """Create the activity section."""
    ui.label("Recent Activity").classes("text-xl font-semibold text-gray-800 mb-4")

    with ui.card().classes("w-full p-6 rounded-xl shadow-lg"):
        # Sample activity data
        activities = [
            {"time": "2 minutes ago", "action": "Logged in successfully", "icon": "login"},
            {"time": "1 hour ago", "action": "Profile updated", "icon": "edit"},
            {"time": "1 day ago", "action": "Password changed", "icon": "security"},
            {"time": "3 days ago", "action": "Email verified", "icon": "verified"},
        ]

        for activity in activities:
            with ui.row().classes("items-center gap-4 py-3 border-b border-gray-100 last:border-b-0"):
                ui.icon(activity["icon"]).classes("text-gray-500")
                with ui.column().classes("flex-1"):
                    ui.label(activity["action"]).classes("text-gray-800")
                    ui.label(activity["time"]).classes("text-sm text-gray-500")


def create_sidebar(user, dashboard_data):
    """Create the dashboard sidebar."""
    with ui.card().classes("w-80 h-fit p-6 rounded-xl shadow-lg"):
        ui.label("Quick Actions").classes("text-lg font-semibold text-gray-800 mb-4")

        # Quick action buttons
        actions = [
            {"label": "Update Profile", "icon": "person", "color": "primary"},
            {"label": "Change Password", "icon": "lock", "color": "secondary"},
            {"label": "View Settings", "icon": "settings", "color": "info"},
            {"label": "Help & Support", "icon": "help", "color": "warning"},
        ]

        for action in actions:
            ui.button(
                action["label"],
                icon=action["icon"],
                on_click=lambda label=action["label"]: ui.notify(f"{label} clicked!", type="info"),
            ).classes("w-full mb-2 justify-start").props(f"color={action['color']} outline")

        ui.separator().classes("my-4")

        # User info section
        ui.label("Account Details").classes("text-lg font-semibold text-gray-800 mb-4")

        info_items = [
            {"label": "Username", "value": user.username},
            {"label": "Email", "value": user.email},
            {"label": "Member since", "value": user.created_at.strftime("%B %Y")},
        ]

        for item in info_items:
            with ui.row().classes("justify-between items-center py-2"):
                ui.label(item["label"]).classes("text-gray-600")
                ui.label(item["value"]).classes("text-gray-800 font-medium")


async def handle_logout():
    """Handle user logout."""
    try:
        # Get session token
        session_token = app.storage.user.get("session_token")

        if session_token:
            # Logout from backend
            logout_user(session_token)

        # Clear local session
        logout_current_user()

        ui.notify("Logged out successfully", type="positive")
        ui.navigate.to("/login")

    except Exception as e:
        ui.notify(f"Logout error: {str(e)}", type="negative")
