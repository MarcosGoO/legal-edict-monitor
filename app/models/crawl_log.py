"""
Crawl Log model.

Tracks crawler execution for monitoring and debugging.
Provides audit trail for document ingestion.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.source_portal import SourcePortal


class CrawlType(str, Enum):
    """Types of crawl execution."""
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    BACKFILL = "backfill"


class CrawlStatus(str, Enum):
    """Crawl execution status."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlLog(Base, TimestampMixin):
    """
    Crawl execution log.
    
    Tracks:
    - Which portal was crawled
    - Execution timing
    - Documents found and processed
    - Errors and warnings
    """
    
    __tablename__ = "crawl_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    source_portal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_portals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crawl_type: Mapped[str] = mapped_column(
        String(50),
        default=CrawlType.SCHEDULED.value,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=CrawlStatus.RUNNING.value,
        nullable=False,
        index=True,
    )
    documents_found: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    documents_new: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="New documents not seen before",
    )
    documents_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Documents successfully processed",
    )
    documents_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    matches_found: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Watchlist matches found",
    )
    error_details: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    warnings: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    source_portal: Mapped["SourcePortal"] = relationship(
        "SourcePortal",
        back_populates="crawl_logs",
        lazy="selectin",
    )
    
    @property
    def is_running(self) -> bool:
        return self.status == CrawlStatus.RUNNING.value
    
    @property
    def is_completed(self) -> bool:
        return self.status == CrawlStatus.COMPLETED.value
    
    @property
    def is_failed(self) -> bool:
        return self.status == CrawlStatus.FAILED.value
    
    @property
    def duration_seconds(self) -> float | None:
        """Calculate crawl duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings = [*self.warnings, warning]
    
    def add_error(self, error: str, details: dict[str, Any] | None = None) -> None:
        """Add an error with optional details."""
        self.error_details = {
            **self.error_details,
            "last_error": error,
            "errors": self.error_details.get("errors", []) + [error],
        }
        if details:
            self.error_details = {**self.error_details, **details}
    
    def mark_completed(self) -> None:
        """Mark crawl as completed."""
        self.status = CrawlStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str) -> None:
        """Mark crawl as failed."""
        self.status = CrawlStatus.FAILED.value
        self.completed_at = datetime.utcnow()
        self.add_error(error)
    
    def __repr__(self) -> str:
        return f"<CrawlLog(id={self.id}, portal_id={self.source_portal_id}, status='{self.status}')>"
    
    def __str__(self) -> str:
        portal_name = self.source_portal.name if self.source_portal else "Unknown"
        return f"Crawl of {portal_name} ({self.status})"
