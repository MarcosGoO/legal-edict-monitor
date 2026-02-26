"""
Colombian Entity Validators.

Validation functions for Colombian legal entities:
- NIT check digit validation
- Radicado structure validation
- Cédula format validation
"""

import re


def validate_nit_check_digit(nit: str) -> bool:
    """
    Validate Colombian NIT check digit.
    
    Algorithm:
    1. Take first 9 digits
    2. Multiply by weights: 41, 37, 29, 23, 19, 17, 13, 7, 3
    3. Sum products
    4. Check digit = (11 - (sum % 11)) % 11
    5. If result >= 10, check digit = 0
    
    Example:
        NIT: 900123456-7
        Calculation:
        9*41 + 0*37 + 0*29 + 1*23 + 2*19 + 3*17 + 4*13 + 5*7 + 6*3
        = 369 + 0 + 0 + 23 + 38 + 51 + 52 + 35 + 18
        = 586
        586 % 11 = 3
        11 - 3 = 8
        8 % 11 = 8 (should match check digit)
    
    Args:
        nit: NIT string (with or without hyphen)
        
    Returns:
        True if check digit is valid
    """
    # Extract digits only
    digits = re.sub(r'\D', '', nit)

    if len(digits) != 10:
        return False

    # Weights for each position
    weights = [41, 37, 29, 23, 19, 17, 13, 7, 3]

    # Calculate weighted sum
    total = sum(
        int(d) * w
        for d, w in zip(digits[:9], weights)
    )

    # Calculate check digit
    check = (11 - (total % 11)) % 11

    # If result >= 10, check digit is 0
    if check >= 10:
        check = 0

    return check == int(digits[9])


def validate_radicado_structure(radicado: str) -> bool:
    """
    Validate radicado structure.
    
    Colombian Radicado format (23 digits):
    - Digits 1-4: Year (YYYY)
    - Digits 5-9: Sequential number
    - Digits 10-11: Department code
    - Digits 12-15: City code
    - Digits 16-18: Court code
    - Digits 19-23: Sequential within court
    
    Note: This validates structure, not legal validity.
    
    Args:
        radicado: Radicado string
        
    Returns:
        True if structure is valid
    """
    # Extract digits only
    digits = re.sub(r'\D', '', radicado)

    if len(digits) != 23:
        return False

    # Validate year (reasonable range)
    year = int(digits[0:4])
    if not (2000 <= year <= 2030):
        return False

    # All should be digits (already checked by regex)
    return True


def validate_cedula_format(cedula: str) -> bool:
    """
    Validate Cédula de Ciudadanía format.
    
    Colombian Cédula de Ciudadanía:
    - Length: 6-12 digits
    - All numeric
    
    Args:
        cedula: Cédula string
        
    Returns:
        True if format is valid
    """
    # Extract digits only
    digits = re.sub(r'\D', '', cedula)

    # Check length
    if not (6 <= len(digits) <= 12):
        return False

    # Check all digits
    return digits.isdigit()


def normalize_radicado(radicado: str) -> str:
    """
    Normalize radicado to standard format.
    
    Standard: XXXX-XXXXX-XX-XXXX-XXX (23 digits with hyphens)
    
    Args:
        radicado: Radicado string in any format
        
    Returns:
        Normalized radicado
    """
    # Remove all non-digits
    digits = re.sub(r'\D', '', radicado)

    if len(digits) == 23:
        # Format: YYYY-NNNNN-PP-CCCC-SSS (complete 23 digits)
        return (
            f"{digits[0:4]}-{digits[4:9]}-{digits[9:11]}-"
            f"{digits[11:15]}-{digits[15:23]}"
        )

    # Return as-is if not 23 digits
    return digits


def normalize_nit(nit: str) -> str:
    """
    Normalize NIT to standard format.
    
    Standard: XXXXXXXXX-X (9 digits + check digit)
    
    Args:
        nit: NIT string in any format
        
    Returns:
        Normalized NIT
    """
    # Extract digits
    digits = re.sub(r'\D', '', nit)

    if len(digits) == 10:
        # Format with hyphen
        return f"{digits[0:9]}-{digits[9]}"

    return digits


def normalize_cedula(cedula: str) -> str:
    """
    Normalize Cédula to digits only.
    
    Removes prefixes like CC, C.C., etc.
    
    Args:
        cedula: Cédula string in any format
        
    Returns:
        Normalized Cédula (digits only)
    """
    return re.sub(r'\D', '', cedula)


def normalize_name(name: str) -> str:
    """
    Normalize person name.
    
    - Uppercase
    - Normalize unicode (remove accents for matching)
    - Clean whitespace
    
    Args:
        name: Name string
        
    Returns:
        Normalized name
    """
    import unicodedata

    # Normalize unicode
    name = unicodedata.normalize('NFKD', name)

    # Uppercase and clean whitespace
    name = ' '.join(name.upper().split())

    return name


def extract_nit_parts(nit: str) -> tuple[str, str] | None:
    """
    Extract NIT parts (base and check digit).
    
    Args:
        nit: NIT string
        
    Returns:
        Tuple of (base, check_digit) or None if invalid
    """
    digits = re.sub(r'\D', '', nit)

    if len(digits) == 10:
        return (digits[:9], digits[9])

    return None
