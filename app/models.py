from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)  # Store hashed passwords only
    full_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    is_authenticated: bool = Field(default=False)  # Track login state
    last_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    session_token: str = Field(max_length=255, unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6)  # Plain password for validation
    full_name: str = Field(max_length=100)


class UserLogin(SQLModel, table=False):
    username: str = Field(max_length=50)
    password: str = Field(min_length=1)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class UserResponse(SQLModel, table=False):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    is_authenticated: bool
    last_login: Optional[datetime]
    created_at: datetime


class DashboardData(SQLModel, table=False):
    """Schema for dashboard content"""

    user_info: UserResponse
    login_time: datetime
    session_duration: str
    welcome_message: str
