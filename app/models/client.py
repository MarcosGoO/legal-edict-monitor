"""
Client model.

Represents a person or entity that a law firm wants to monitor
for mentions in legal documents.
"""

import uuid
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.law_firm import LawFirm
    from app.models.watchlist_entry import WatchlistEntry
    from app.models.detected_edict import DetectedEdict


class DocumentType(str, Enum):
    """Colombian document types."""
    CC = "CC"      # Cédula de Ciudadanía
    CE = "CE"      # Cédula de Extranjería
    NIT = "NIT"    # Número de Identificación Tributaria
    PP = "PP"      # Pasaporte
    TI = "TI"      # Tarjeta de Identidad


class Client(Base, TimestampMixin):
    """
    Client entity (person/company to monitor).
    
    A client is someone that a law firm wants to track for
    mentions in legal gazettes and court edicts.
    
    The client can be:
    - A person (with Cédula/CE/PP)
    - A company (with NIT)
    - Both (person with company interests)
    """
    
    __tablename__ = "clients"
    __table_args__ = (
        UniqueConstraint(
            "law_firm_id",
            "document_type",
            "document_number",
            name="uq_client_document",
        ),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    law_firm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("law_firms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        comment="Full name or company name",
    )
    document_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Type of document (CC, CE, NIT, PP, TI)",
    )
    document_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="Document number (Cédula, NIT, etc.)",
    )
    nit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        comment="NIT for companies (separate from personal document)",
    )
    aliases: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Alternative names for matching",
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
    law_firm: Mapped["LawFirm"] = relationship(
        "LawFirm",
        back_populates="clients",
        lazy="selectin",
    )
    watchlist_entries: Mapped[list["WatchlistEntry"]] = relationship(
        "WatchlistEntry",
        back_populates="client",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    detected_edicts: Mapped[list["DetectedEdict"]] = relationship(
        "DetectedEdict",
        back_populates="client",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    @property
    def display_name(self) -> str:
        """Get display name with document info."""
        if self.document_number:
            return f"{self.full_name} ({self.document_type}: {self.document_number})"
        return self.full_name
    
    def add_alias(self, alias: str) -> None:
        """Add an alias for matching."""
        if alias and alias not in self.aliases:
            self.aliases = [*self.aliases, alias]
    
    def remove_alias(self, alias: str) -> None:
        """Remove an alias."""
        self.aliases = [a for a in self.aliases if a != alias]
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.full_name}')>"
    
    def __str__(self) -> str:
        return self.full_name


# Import for relationships
from app.models.detected_edict import DetectedEdict
from app.models.watchlist_entry import WatchlistEntry
