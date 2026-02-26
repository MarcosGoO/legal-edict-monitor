"""
Colombian Entity Patterns.

Regex patterns for extracting Colombian legal entities:
- Radicado (23-digit case number)
- NIT (Tax ID)
- Cédula (Colombian ID)
- Court identifiers
"""

import re
from dataclasses import dataclass

from app.services.parser.base import EntityType


@dataclass
class EntityPattern:
    """Regex pattern for entity extraction."""
    entity_type: EntityType
    pattern: str
    description: str
    example: str
    group: int = 0  # Which regex group to extract


# Colombian legal document patterns
COLOMBIAN_PATTERNS: list[EntityPattern] = [
    # ========================================================================
    # RADICADO: 23-digit case number
    # Format: YYYY-NNNNN-PP-CCCC-SSS
    # Example: 2023-00123-45-67-890-12
    # ========================================================================
    EntityPattern(
        entity_type=EntityType.RADICADO,
        pattern=(
            r'\b(\d{4}[-\s]?\d{5}[-\s]?\d{2}[-\s]?\d{4}[-\s]?\d{3})\b'
        ),
        description="23-digit case number with hyphens or spaces",
        example="2023-00123-45-67-890-12",
    ),
    EntityPattern(
        entity_type=EntityType.RADICADO,
        pattern=r'\b(\d{23})\b',
        description="23-digit case number (continuous)",
        example="20230012345678901234567",
    ),

    # ========================================================================
    # NIT: Tax identification number
    # Format: 123456789-0 or 1234567890
    # Validation: Check digit algorithm
    # ========================================================================
    EntityPattern(
        entity_type=EntityType.NIT,
        pattern=r'\b(?:NIT|Nit)\s*[:.]?\s*(\d{9})[-\s]?(\d)\b',
        description="NIT with label and check digit",
        example="NIT: 900123456-7",
    ),
    EntityPattern(
        entity_type=EntityType.NIT,
        pattern=r'\b(\d{9})[-\s](\d)\b',
        description="NIT format without label",
        example="900123456-7",
    ),

    # ========================================================================
    # CÉDULA: Colombian ID (6-12 digits)
    # Often appears with prefixes like CC, C.C., Cédula
    # ========================================================================
    EntityPattern(
        entity_type=EntityType.CEDULA,
        pattern=(
            r'\b(?:CC|C\.C\.|Cédula|Cedula|C\.C)\s*[:.]?\s*(\d{6,12})\b'
        ),
        description="Cédula with prefix",
        example="CC 12345678",
    ),
    EntityPattern(
        entity_type=EntityType.CEDULA,
        pattern=(
            r'\b(?:identificado|identificada|identificación|ID)\s*(?:con|:)?\s*'
            r'(?:CC|C\.C\.|Cédula)?\s*[:.]?\s*(\d{6,12})\b'
        ),
        description="Cédula in identification context",
        example="identificado con CC 12345678",
    ),

    # ========================================================================
    # COURT ID: Court identifiers
    # Format: Juzgado X, Tribunal Y, Sala Z, etc.
    # ========================================================================
    EntityPattern(
        entity_type=EntityType.COURT_ID,
        pattern=(
            r'\b(Juzgado\s+(?:\w+\s+)*?(?:N°|No\.?|Número)?\s*\d+)'
        ),
        description="Juzgado court identifier",
        example="Juzgado Primero Civil del Circuito",
    ),
    EntityPattern(
        entity_type=EntityType.COURT_ID,
        pattern=(
            r'\b(Tribunal\s+(?:\w+\s+)*?(?:N°|No\.?|Número)?\s*\d+)'
        ),
        description="Tribunal court identifier",
        example="Tribunal Superior de Bogotá",
    ),
    EntityPattern(
        entity_type=EntityType.COURT_ID,
        pattern=(
            r'\b(Sala\s+(?:\w+\s+)*?(?:N°|No\.?|Número)?\s*\d+)'
        ),
        description="Sala court identifier",
        example="Sala Civil",
    ),
]


def compile_patterns() -> dict[EntityType, list[re.Pattern]]:
    """
    Compile all patterns into regex objects.
    
    Returns:
        Dictionary mapping entity types to compiled patterns
    """
    compiled: dict[EntityType, list[re.Pattern]] = {}

    for pattern in COLOMBIAN_PATTERNS:
        if pattern.entity_type not in compiled:
            compiled[pattern.entity_type] = []

        compiled[pattern.entity_type].append(
            re.compile(pattern.pattern, re.IGNORECASE | re.MULTILINE)
        )

    return compiled


def get_pattern_examples() -> dict[EntityType, list[str]]:
    """
    Get example values for each entity type.
    
    Returns:
        Dictionary mapping entity types to example lists
    """
    examples: dict[EntityType, list[str]] = {}

    for pattern in COLOMBIAN_PATTERNS:
        if pattern.entity_type not in examples:
            examples[pattern.entity_type] = []
        examples[pattern.entity_type].append(pattern.example)

    return examples
