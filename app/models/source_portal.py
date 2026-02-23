"""
Source Portal model.

Represents a court portal or official diary that the system crawls
for legal documents.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.raw_document import RawDocument
    from app.models.crawl_log import CrawlLog


class PortalType(str, Enum):
    """Types of legal portals in Colombia."""
    RAMA_JUDICIAL = "rama_judicial"
    SUPERSOCIEDADES = "supersociedades"
    SUPERSALUD = "supersalud"
    TRIBUNAL_ADM = "tribunal_administrativo"
    VIRTUAL_BOARD = "virtual_board"
    CUSTOM = "custom"


class SourcePortal(Base, TimestampMixin):
    """
    Source portal configuration.
    
    Defines a court portal or official source to crawl:
    - URL and authentication
    - Crawl schedule
    - Parsing configuration
    """
    
    __tablename__ = "source_portals"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    portal_type: Mapped[str] = mapped_column(
        String(50),
        default=PortalType.CUSTOM.value,
        nullable=False,
    )
    base_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Portal-specific configuration (headers, auth, selectors)",
    )
    crawl_schedule: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Cron expression for crawl schedule",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    last_crawled: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Relationships
    raw_documents: Mapped[list["RawDocument"]] = relationship(
        "RawDocument",
        back_populates="source_portal",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    crawl_logs: Mapped[list["CrawlLog"]] = relationship(
        "CrawlLog",
        back_populates="source_portal",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    @property
    def selectors(self) -> dict[str, str]:
        """Get CSS selectors for parsing."""
        return self.config.get("selectors", {})
    
    @property
    def auth_config(self) -> dict[str, Any]:
        """Get authentication configuration."""
        return self.config.get("auth", {})
    
    @property
    def requires_auth(self) -> bool:
        """Check if portal requires authentication."""
        return bool(self.auth_config)
    
    def update_last_crawled(self) -> None:
        """Update last crawled timestamp."""
        self.last_crawled = datetime.utcnow()
    
    def set_error(self, error: str) -> None:
        """Record last error."""
        self.last_error = error
    
    def clear_error(self) -> None:
        """Clear last error."""
        self.last_error = None
    
    def __repr__(self) -> str:
        return f"<SourcePortal(id={self.id}, name='{self.name}')>"
    
    def __str__(self) -> str:
        return self.name


# Import for relationships
from app.models.crawl_log import CrawlLog
from app.models.raw_document import RawDocument
