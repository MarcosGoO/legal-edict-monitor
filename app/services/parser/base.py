"""
Entity Parser Base Classes and Types.

Defines the core data structures for entity extraction.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntityType(str, Enum):
    """Types of entities that can be extracted from Colombian legal documents."""
    RADICADO = "radicado"       # 23-digit case number
    NIT = "nit"                 # Tax ID: 123456789-0
    CEDULA = "cedula"           # Colombian ID: 6-12 digits
    NOMBRE = "nombre"           # Person name
    COURT_ID = "court_id"       # Court identifier
    COMPANY = "company"         # Company name
    ADDRESS = "address"         # Address
    PHONE = "phone"             # Phone number


@dataclass
class ExtractedEntity:
    """
    Represents an entity extracted from a document.
    
    Stores the raw value, normalized value for matching,
    confidence score, and position information.
    """
    entity_type: EntityType
    raw_value: str
    normalized_value: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_high_confidence(self) -> bool:
        """Check if confidence is above threshold."""
        return self.confidence >= 0.8

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "type": self.entity_type.value,
            "raw": self.raw_value,
            "normalized": self.normalized_value,
            "confidence": self.confidence,
            "position": (self.start_pos, self.end_pos),
            "context": self.context[:100] if self.context else "",
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return (
            f"<ExtractedEntity(type={self.entity_type.value}, "
            f"value='{self.normalized_value[:20]}...', "
            f"confidence={self.confidence:.2f})>"
        )


@dataclass
class ParseResult:
    """
    Result of entity parsing from a document.
    
    Contains all extracted entities and processing metadata.
    """
    entities: list[ExtractedEntity]
    text_length: int
    processing_time_ms: float
    nlp_model: str

    @property
    def radicados(self) -> list[ExtractedEntity]:
        """Get all radicado entities."""
        return [e for e in self.entities if e.entity_type == EntityType.RADICADO]

    @property
    def nits(self) -> list[ExtractedEntity]:
        """Get all NIT entities."""
        return [e for e in self.entities if e.entity_type == EntityType.NIT]

    @property
    def cedulas(self) -> list[ExtractedEntity]:
        """Get all cédula entities."""
        return [e for e in self.entities if e.entity_type == EntityType.CEDULA]

    @property
    def names(self) -> list[ExtractedEntity]:
        """Get all name entities."""
        return [e for e in self.entities if e.entity_type == EntityType.NOMBRE]

    @property
    def court_ids(self) -> list[ExtractedEntity]:
        """Get all court ID entities."""
        return [e for e in self.entities if e.entity_type == EntityType.COURT_ID]

    @property
    def entity_count(self) -> int:
        """Total number of entities."""
        return len(self.entities)

    def get_entities_by_type(self, entity_type: EntityType) -> list[ExtractedEntity]:
        """Get entities of a specific type."""
        return [e for e in self.entities if e.entity_type == entity_type]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "entity_count": self.entity_count,
            "entities": [e.to_dict() for e in self.entities],
            "text_length": self.text_length,
            "processing_time_ms": self.processing_time_ms,
            "nlp_model": self.nlp_model,
            "summary": {
                "radicados": len(self.radicados),
                "nits": len(self.nits),
                "cedulas": len(self.cedulas),
                "names": len(self.names),
                "court_ids": len(self.court_ids),
            },
        }
