from app.database import create_tables
from nicegui import ui
import app.login
import app.dashboard


def startup() -> None:
    # this function is called before the first request
    create_tables()

    # Initialize application modules
    app.login.create()
    app.dashboard.create()

    @ui.page("/")
    def index():
        """Redirect to dashboard or login based on authentication status."""
        from app.auth_middleware import get_current_user

        user = get_current_user()
        if user:
            ui.navigate.to("/dashboard")
        else:
            ui.navigate.to("/login")
