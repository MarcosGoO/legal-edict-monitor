"""
Raw Document model.

Represents a PDF document ingested from a source portal.
Tracks processing status and stores metadata.
"""

import uuid
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.source_portal import SourcePortal
    from app.models.extracted_entity import ExtractedEntity
    from app.models.detected_edict import DetectedEdict


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RawDocument(Base, TimestampMixin):
    """
    Raw document (PDF) ingested from a source portal.
    
    Tracks:
    - Source URL and file hash (for deduplication)
    - S3 storage location
    - Processing status
    - Extracted text and metadata
    """
    
    __tablename__ = "raw_documents"
    __table_args__ = (
        UniqueConstraint(
            "file_hash",
            name="uq_raw_document_hash",
        ),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    source_portal_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_portals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="Original URL where document was found",
    )
    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment="SHA-256 hash of file content",
    )
    s3_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="S3 storage path",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=DocumentStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    published_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Date document was published",
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional metadata (title, author, etc.)",
    )
    
    # Relationships
    source_portal: Mapped["SourcePortal | None"] = relationship(
        "SourcePortal",
        back_populates="raw_documents",
        lazy="selectin",
    )
    extracted_entities: Mapped[list["ExtractedEntity"]] = relationship(
        "ExtractedEntity",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    detected_edicts: Mapped[list["DetectedEdict"]] = relationship(
        "DetectedEdict",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    @property
    def is_pending(self) -> bool:
        return self.status == DocumentStatus.PENDING.value
    
    @property
    def is_processing(self) -> bool:
        return self.status == DocumentStatus.PROCESSING.value
    
    @property
    def is_processed(self) -> bool:
        return self.status == DocumentStatus.PROCESSED.value
    
    @property
    def is_failed(self) -> bool:
        return self.status == DocumentStatus.FAILED.value
    
    def mark_processing(self) -> None:
        """Mark document as being processed."""
        self.status = DocumentStatus.PROCESSING.value
    
    def mark_processed(self) -> None:
        """Mark document as successfully processed."""
        self.status = DocumentStatus.PROCESSED.value
        self.processed_at = datetime.utcnow()
        self.error_message = None
    
    def mark_failed(self, error: str) -> None:
        """Mark document as failed."""
        self.status = DocumentStatus.FAILED.value
        self.error_message = error
    
    def __repr__(self) -> str:
        return f"<RawDocument(id={self.id}, hash='{self.file_hash[:8]}...', status='{self.status}')>"
    
    def __str__(self) -> str:
        return f"Document {self.file_hash[:8]}"


# Import for relationships
from app.models.detected_edict import DetectedEdict
from app.models.extracted_entity import ExtractedEntity
