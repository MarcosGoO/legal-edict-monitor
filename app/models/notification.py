"""
Notification model.

Tracks notifications sent to users about detected edicts.
Supports multiple channels: WhatsApp, Email, SMS.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.detected_edict import DetectedEdict
    from app.models.user import User


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"


class NotificationStatus(str, Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Notification(Base, TimestampMixin):
    """
    Notification record.
    
    Tracks:
    - Which edict triggered the notification
    - Which user should receive it
    - Channel (WhatsApp, Email, SMS)
    - Delivery status
    - External IDs for tracking
    """
    
    __tablename__ = "notifications"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    detected_edict_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("detected_edicts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=NotificationStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="External message ID (Twilio, SendGrid, etc.)",
    )
    recipient: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Recipient address (phone, email)",
    )
    subject: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Full message payload",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    detected_edict: Mapped["DetectedEdict"] = relationship(
        "DetectedEdict",
        back_populates="notifications",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        lazy="selectin",
    )
    
    @property
    def is_pending(self) -> bool:
        return self.status == NotificationStatus.PENDING.value
    
    @property
    def is_sent(self) -> bool:
        return self.status in (
            NotificationStatus.SENT.value,
            NotificationStatus.DELIVERED.value,
            NotificationStatus.READ.value,
        )
    
    @property
    def is_delivered(self) -> bool:
        return self.status in (
            NotificationStatus.DELIVERED.value,
            NotificationStatus.READ.value,
        )
    
    @property
    def is_failed(self) -> bool:
        return self.status == NotificationStatus.FAILED.value
    
    def mark_sent(self, external_id: str | None = None) -> None:
        """Mark notification as sent."""
        self.status = NotificationStatus.SENT.value
        self.sent_at = datetime.utcnow()
        if external_id:
            self.external_id = external_id
        self.error_message = None
    
    def mark_delivered(self) -> None:
        """Mark notification as delivered."""
        self.status = NotificationStatus.DELIVERED.value
        self.delivered_at = datetime.utcnow()
    
    def mark_read(self) -> None:
        """Mark notification as read."""
        self.status = NotificationStatus.READ.value
        self.read_at = datetime.utcnow()
    
    def mark_failed(self, error: str) -> None:
        """Mark notification as failed."""
        self.status = NotificationStatus.FAILED.value
        self.error_message = error
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, channel='{self.channel}', status='{self.status}')>"
    
    def __str__(self) -> str:
        return f"{self.channel.upper()} notification to {self.recipient}"
