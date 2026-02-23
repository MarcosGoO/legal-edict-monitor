"""
Colombian Entity Parser Package.

Provides entity extraction for Colombian legal documents:
- Radicado (23-digit case number)
- NIT (Tax ID)
- Cédula (Colombian ID)
- Person names (using NLP)
"""

from app.services.parser.base import EntityType, ExtractedEntity, ParseResult
from app.services.parser.service import ColombianEntityParser

__all__ = [
    "ColombianEntityParser",
    "EntityType",
    "ExtractedEntity",
    "ParseResult",
]
