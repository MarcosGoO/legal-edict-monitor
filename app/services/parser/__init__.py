"""
Colombian Entity Parser Package.

Provides entity extraction for Colombian legal documents:
- Radicado (23-digit case number)
- NIT (Tax ID)
- Cédula (Colombian ID)
- Person names (using NLP)
"""

from app.services.parser.base import EntityType, ExtractedEntity, ParseResult
from app.services.parser.input_validation import (
    CedulaField,
    DocumentTypeField,
    NitField,
    RadicadoField,
    validate_colombian_cedula,
    validate_colombian_nit,
    validate_colombian_radicado,
    validate_document_number,
    validate_document_type,
)
from app.services.parser.service import ColombianEntityParser

__all__ = [
    "ColombianEntityParser",
    "EntityType",
    "ExtractedEntity",
    "ParseResult",
    # Input validation helpers
    "CedulaField",
    "NitField",
    "RadicadoField",
    "DocumentTypeField",
    "validate_colombian_cedula",
    "validate_colombian_nit",
    "validate_colombian_radicado",
    "validate_document_type",
    "validate_document_number",
]
