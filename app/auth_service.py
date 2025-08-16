"""Authentication service for user management and session handling."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import select

from app.database import get_session
from app.models import User, UserSession, UserCreate, UserLogin


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    try:
        salt, stored_hash = password_hash.split(":")
        password_hash_check = hashlib.sha256((password + salt).encode()).hexdigest()
        return stored_hash == password_hash_check
    except ValueError:
        # Log the error for debugging
        import logging

        logging.info(f"Invalid password hash format: {password_hash}")
        return False


def create_user(user_data: UserCreate) -> Optional[User]:
    """Create a new user with hashed password."""
    with get_session() as session:
        # Check if username or email already exists
        existing_user = session.exec(
            select(User).where((User.username == user_data.username) | (User.email == user_data.email))
        ).first()

        if existing_user:
            return None

        password_hash = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def authenticate_user(login_data: UserLogin) -> Optional[User]:
    """Authenticate user with username and password."""
    with get_session() as session:
        user = session.exec(select(User).where(User.username == login_data.username)).first()

        if user is None or not user.is_active:
            return None

        if not verify_password(login_data.password, user.password_hash):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        user.is_authenticated = True
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def create_session(user_id: int) -> Optional[UserSession]:
    """Create a new session for the user."""
    with get_session() as session:
        # Deactivate existing sessions for the user
        existing_sessions = session.exec(
            select(UserSession).where(UserSession.user_id == user_id, UserSession.is_active)
        ).all()

        for existing_session in existing_sessions:
            existing_session.is_active = False
            session.add(existing_session)

        # Create new session
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        user_session = UserSession(user_id=user_id, session_token=session_token, expires_at=expires_at)
        session.add(user_session)
        session.commit()
        session.refresh(user_session)
        return user_session


def validate_session(session_token: Optional[str]) -> Optional[User]:
    """Validate session token and return user if valid."""
    if not session_token:
        return None

    with get_session() as session:
        user_session = session.exec(
            select(UserSession).where(
                UserSession.session_token == session_token,
                UserSession.is_active,
                UserSession.expires_at > datetime.utcnow(),
            )
        ).first()

        if user_session is None:
            return None

        user = session.get(User, user_session.user_id)
        if user is None or not user.is_active:
            return None

        return user


def logout_user(session_token: Optional[str]) -> bool:
    """Logout user by deactivating session."""
    if not session_token:
        return False

    with get_session() as session:
        user_session = session.exec(
            select(UserSession).where(UserSession.session_token == session_token, UserSession.is_active)
        ).first()

        if user_session is None:
            return False

        user_session.is_active = False
        session.add(user_session)

        # Update user authentication status
        user = session.get(User, user_session.user_id)
        if user:
            user.is_authenticated = False
            session.add(user)

        session.commit()
        return True


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID."""
    with get_session() as session:
        return session.get(User, user_id)


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    with get_session() as session:
        return session.exec(select(User).where(User.username == username)).first()
