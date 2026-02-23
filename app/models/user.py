"""
User model.

Represents a staff member of a law firm who can:
- Manage clients and watchlist entries
- Receive notifications
- Access the dashboard
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.law_firm import LawFirm
    from app.models.notification import Notification


class UserRole(str, Enum):
    """User roles for access control."""
    ADMIN = "admin"      # Full access to law firm settings
    EDITOR = "editor"    # Can manage clients and watchlist
    VIEWER = "viewer"    # Read-only access


class User(Base, TimestampMixin):
    """
    User entity (law firm staff member).
    
    Users belong to a law firm and have role-based access control.
    """
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    law_firm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("law_firms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default=UserRole.VIEWER.value,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    law_firm: Mapped["LawFirm"] = relationship(
        "LawFirm",
        back_populates="users",
        lazy="selectin",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN.value
    
    @property
    def is_editor(self) -> bool:
        """Check if user can edit."""
        return self.role in (UserRole.ADMIN.value, UserRole.EDITOR.value)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def __str__(self) -> str:
        return self.email
