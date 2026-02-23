"""
Watchlist Entry model.

Represents a monitoring configuration for a client.
Defines what to watch for (case numbers, courts) and how to notify.
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.law_firm import LawFirm
    from app.models.detected_edict import DetectedEdict


# Default notification preferences
DEFAULT_NOTIFICATION_PREFERENCES: dict[str, Any] = {
    "channels": ["whatsapp", "email"],
    "immediate": True,
    "digest": False,
    "digest_frequency": "daily",  # daily, weekly
}


class WatchlistEntry(Base, TimestampMixin):
    """
    Watchlist entry for monitoring configuration.
    
    Defines:
    - Which client to monitor
    - Specific case numbers to watch (optional)
    - Specific courts to watch (optional)
    - Notification preferences
    """
    
    __tablename__ = "watchlist_entries"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    law_firm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("law_firms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_numbers: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        default=list,
        nullable=False,
        comment="Specific case numbers (Radicados) to watch",
    )
    court_ids: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        default=list,
        nullable=False,
        comment="Specific court identifiers to watch",
    )
    notification_preferences: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=lambda: DEFAULT_NOTIFICATION_PREFERENCES.copy(),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    
    # Relationships
    client: Mapped["Client"] = relationship(
        "Client",
        back_populates="watchlist_entries",
        lazy="selectin",
    )
    law_firm: Mapped["LawFirm"] = relationship(
        "LawFirm",
        back_populates="watchlist_entries",
        lazy="selectin",
    )
    detected_edicts: Mapped[list["DetectedEdict"]] = relationship(
        "DetectedEdict",
        back_populates="watchlist_entry",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    @property
    def notification_channels(self) -> list[str]:
        """Get list of notification channels."""
        return self.notification_preferences.get("channels", ["email"])
    
    @property
    def immediate_notifications(self) -> bool:
        """Check if immediate notifications are enabled."""
        return self.notification_preferences.get("immediate", True)
    
    def add_case_number(self, case_number: str) -> None:
        """Add a case number to watch."""
        if case_number and case_number not in self.case_numbers:
            self.case_numbers = [*self.case_numbers, case_number]
    
    def remove_case_number(self, case_number: str) -> None:
        """Remove a case number."""
        self.case_numbers = [c for c in self.case_numbers if c != case_number]
    
    def add_court_id(self, court_id: str) -> None:
        """Add a court ID to watch."""
        if court_id and court_id not in self.court_ids:
            self.court_ids = [*self.court_ids, court_id]
    
    def remove_court_id(self, court_id: str) -> None:
        """Remove a court ID."""
        self.court_ids = [c for c in self.court_ids if c != court_id]
    
    def __repr__(self) -> str:
        return f"<WatchlistEntry(id={self.id}, client_id={self.client_id})>"
    
    def __str__(self) -> str:
        return f"Watchlist for {self.client.full_name if self.client else self.client_id}"


# Import for relationships
from app.models.detected_edict import DetectedEdict
