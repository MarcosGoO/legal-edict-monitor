"""
Input Validation Helpers for Colombian Documents.

Provides Pydantic validators and helper functions for validating
Colombian document numbers in API requests.
"""

import re
from typing import Annotated

from pydantic import BeforeValidator, Field


def validate_colombian_cedula(value: str) -> str:
    """
    Validate and normalize a Colombian Cédula de Ciudadanía.
    
    Args:
        value: Raw cédula string
        
    Returns:
        Normalized cédula (digits only)
        
    Raises:
        ValueError: If format is invalid
    """
    if not value:
        return value

    # Extract digits
    digits = re.sub(r'\D', '', value)

    # Validate length
    if not (6 <= len(digits) <= 12):
        raise ValueError(
            f"Cédula must have 6-12 digits, got {len(digits)}"
        )

    return digits


def validate_colombian_nit(value: str) -> str:
    """
    Validate and normalize a Colombian NIT.
    
    Args:
        value: Raw NIT string
        
    Returns:
        Normalized NIT (XXXXXXXXX-X format)
        
    Raises:
        ValueError: If format or check digit is invalid
    """
    if not value:
        return value

    # Extract digits
    digits = re.sub(r'\D', '', value)

    # Validate length
    if len(digits) != 10:
        raise ValueError(
            f"NIT must have 10 digits (9 + check digit), got {len(digits)}"
        )

    # Validate check digit
    weights = [41, 37, 29, 23, 19, 17, 13, 7, 3]
    total = sum(int(d) * w for d, w in zip(digits[:9], weights))
    check = (11 - (total % 11)) % 11
    if check >= 10:
        check = 0

    if check != int(digits[9]):
        raise ValueError(
            f"Invalid NIT check digit. Expected {check}, got {digits[9]}"
        )

    # Return normalized format
    return f"{digits[:9]}-{digits[9]}"


def validate_colombian_radicado(value: str) -> str:
    """
    Validate and normalize a Colombian Radicado (case number).
    
    Args:
        value: Raw radicado string
        
    Returns:
        Normalized radicado (XXXX-XXXXX-XX-XXXX-XXX format)
        
    Raises:
        ValueError: If format is invalid
    """
    if not value:
        return value

    # Extract digits
    digits = re.sub(r'\D', '', value)

    # Validate length
    if len(digits) != 23:
        raise ValueError(
            f"Radicado must have 23 digits, got {len(digits)}"
        )

    # Validate year
    year = int(digits[0:4])
    if not (2000 <= year <= 2030):
        raise ValueError(
            f"Invalid radicado year: {year}. Must be between 2000 and 2030"
        )

    # Return normalized format
    return (
        f"{digits[0:4]}-{digits[4:9]}-{digits[9:11]}-"
        f"{digits[11:15]}-{digits[15:18]}"
    )


def validate_document_type(value: str) -> str:
    """
    Validate document type.
    
    Args:
        value: Document type string
        
    Returns:
        Uppercase document type
        
    Raises:
        ValueError: If type is invalid
    """
    if not value:
        return value

    valid_types = {"CC", "CE", "NIT", "PP", "TI"}
    upper_value = value.upper()

    if upper_value not in valid_types:
        raise ValueError(
            f"Invalid document type: {value}. "
            f"Must be one of: {', '.join(sorted(valid_types))}"
        )

    return upper_value


# Pydantic types for reuse in models
CedulaField = Annotated[
    str,
    Field(max_length=20, description="Colombian Cédula de Ciudadanía"),
    BeforeValidator(validate_colombian_cedula),
]

NitField = Annotated[
    str,
    Field(max_length=20, description="Colombian NIT (Tax ID)"),
    BeforeValidator(validate_colombian_nit),
]

RadicadoField = Annotated[
    str,
    Field(max_length=30, description="Colombian Radicado (case number)"),
    BeforeValidator(validate_colombian_radicado),
]

DocumentTypeField = Annotated[
    str,
    Field(description="Document type (CC, CE, NIT, PP, TI)"),
    BeforeValidator(validate_document_type),
]


def validate_document_number(document_type: str, document_number: str) -> str:
    """
    Validate a document number based on its type.
    
    Args:
        document_type: Type of document (CC, CE, NIT, PP, TI)
        document_number: Document number to validate
        
    Returns:
        Normalized document number
        
    Raises:
        ValueError: If document number is invalid for the type
    """
    if not document_number:
        return document_number

    doc_type = document_type.upper() if document_type else ""

    if doc_type == "CC":
        return validate_colombian_cedula(document_number)
    elif doc_type == "NIT":
        return validate_colombian_nit(document_number)
    elif doc_type in {"CE", "PP", "TI"}:
        # For these types, just clean and return
        return re.sub(r'\D', '', document_number)

    # Unknown type, return as-is
    return document_number
