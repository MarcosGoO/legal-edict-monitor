"""
Extracted Entity model.

Represents an entity (name, ID, case number) extracted from a document
using OCR and NLP processing.
"""

import uuid
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.raw_document import RawDocument


class EntityType(str, Enum):
    """Types of entities that can be extracted."""
    RADICADO = "radicado"       # 23-digit case number
    NIT = "nit"                 # Tax ID
    CEDULA = "cedula"           # Colombian ID
    NOMBRE = "nombre"           # Person name
    COURT_ID = "court_id"       # Court identifier
    COMPANY = "company"         # Company name
    ADDRESS = "address"         # Address
    PHONE = "phone"             # Phone number


class ExtractedEntity(Base, TimestampMixin):
    """
    Entity extracted from a document.
    
    Stores:
    - Entity type (radicado, NIT, cédula, name, etc.)
    - Raw value as found in document
    - Normalized value for matching
    - Confidence score from extraction
    - Position in document
    """
    
    __tablename__ = "extracted_entities"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "entity_type",
            "normalized_value",
            name="uq_extracted_entity",
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
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    raw_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Original value as found in document",
    )
    normalized_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
        comment="Normalized value for matching",
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    start_position: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Start position in document text",
    )
    end_position: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="End position in document text",
    )
    context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Surrounding text for context",
    )
    metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    
    # Relationships
    document: Mapped["RawDocument"] = relationship(
        "RawDocument",
        back_populates="extracted_entities",
        lazy="selectin",
    )
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if confidence is above threshold."""
        return self.confidence_score >= 0.8
    
    @property
    def display_value(self) -> str:
        """Get display value with type."""
        return f"{self.entity_type.upper()}: {self.normalized_value}"
    
    def __repr__(self) -> str:
        return f"<ExtractedEntity(id={self.id}, type='{self.entity_type}', value='{self.normalized_value[:20]}...')>"
    
    def __str__(self) -> str:
        return self.display_value
