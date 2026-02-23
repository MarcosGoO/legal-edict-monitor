"""
Detected Edict model.

Represents a match between a document and a client on the watchlist.
This is the core entity that triggers notifications.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.raw_document import RawDocument
    from app.models.client import Client
    from app.models.watchlist_entry import WatchlistEntry
    from app.models.notification import Notification


class MatchType(str, Enum):
    """Types of matches."""
    DOCUMENT_NUMBER = "document_number"  # Cédula or NIT match
    NAME = "name"                        # Name match (fuzzy)
    CASE_NUMBER = "case_number"          # Radicado match
    COURT_ID = "court_id"                # Court ID match


class EdictStatus(str, Enum):
    """Status of detected edict."""
    PENDING = "pending"          # Not yet notified
    NOTIFIED = "notified"        # Notification sent
    ACKNOWLEDGED = "acknowledged"  # User acknowledged
    DISMISSED = "dismissed"      # User dismissed


class DetectedEdict(Base, TimestampMixin):
    """
    Detected edict (match between document and client).
    
    When a document contains entities that match a client on the watchlist,
    a DetectedEdict is created to track the match and trigger notifications.
    """
    
    __tablename__ = "detected_edicts"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "client_id",
            name="uq_detected_edict",
        ),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("raw_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    watchlist_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("watchlist_entries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    match_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of match that triggered detection",
    )
    match_confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    matched_entities: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Entities that matched (type -> value)",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=EdictStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Relationships
    document: Mapped["RawDocument"] = relationship(
        "RawDocument",
        back_populates="detected_edicts",
        lazy="selectin",
    )
    client: Mapped["Client"] = relationship(
        "Client",
        back_populates="detected_edicts",
        lazy="selectin",
    )
    watchlist_entry: Mapped["WatchlistEntry | None"] = relationship(
        "WatchlistEntry",
        back_populates="detected_edicts",
        lazy="selectin",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="detected_edict",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    @property
    def is_pending(self) -> bool:
        return self.status == EdictStatus.PENDING.value
    
    @property
    def is_notified(self) -> bool:
        return self.status == EdictStatus.NOTIFIED.value
    
    @property
    def is_acknowledged(self) -> bool:
        return self.status == EdictStatus.ACKNOWLEDGED.value
    
    def mark_notified(self) -> None:
        """Mark edict as notified."""
        self.status = EdictStatus.NOTIFIED.value
        self.notified_at = datetime.utcnow()
    
    def acknowledge(self, notes: str | None = None) -> None:
        """Acknowledge the edict."""
        self.status = EdictStatus.ACKNOWLEDGED.value
        self.acknowledged_at = datetime.utcnow()
        if notes:
            self.notes = notes
    
    def dismiss(self, notes: str | None = None) -> None:
        """Dismiss the edict."""
        self.status = EdictStatus.DISMISSED.value
        if notes:
            self.notes = notes
    
    def get_matched_entity_values(self) -> list[str]:
        """Get list of matched entity values."""
        return list(self.matched_entities.values())
    
    def __repr__(self) -> str:
        return f"<DetectedEdict(id={self.id}, client_id={self.client_id}, status='{self.status}')>"
    
    def __str__(self) -> str:
        client_name = self.client.full_name if self.client else "Unknown"
        return f"Edict for {client_name}"


# Import for relationships
from app.models.notification import Notification
