"""
Law Firm model.

Represents a law firm that uses the Edict Guardian service.
Each law firm can have multiple users and clients.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class LawFirm(Base, TimestampMixin):
    """
    Law firm entity.
    
    A law firm is the primary account holder that:
    - Has multiple users (staff members)
    - Manages clients (people/entities to monitor)
    - Receives notifications when matches are found
    """
    
    __tablename__ = "law_firms"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    nit: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
        comment="Colombian Tax ID (NIT)",
    )
    contact_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    contact_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    
    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="law_firm",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    clients: Mapped[list["Client"]] = relationship(
        "Client",
        back_populates="law_firm",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    watchlist_entries: Mapped[list["WatchlistEntry"]] = relationship(
        "WatchlistEntry",
        back_populates="law_firm",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<LawFirm(id={self.id}, name='{self.name}')>"
    
    def __str__(self) -> str:
        return self.name


# Import related models for relationships
from app.models.client import Client
from app.models.user import User
from app.models.watchlist_entry import WatchlistEntry
