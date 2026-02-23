"""
Tests for Colombian Entity Parser.

Tests entity extraction from Colombian legal documents.
"""

import pytest

from app.services.parser import ColombianEntityParser, EntityType
from app.services.parser.validators import (
    normalize_cedula,
    normalize_nit,
    normalize_radicado,
    validate_cedula_format,
    validate_nit_check_digit,
    validate_radicado_structure,
)


class TestColombianEntityParser:
    """Tests for ColombianEntityParser."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return ColombianEntityParser()
    
    def test_extract_radicado_standard(self, parser, sample_legal_text):
        """Test extraction of standard radicado format."""
        result = parser.parse(sample_legal_text)
        
        radicados = result.radicados
        assert len(radicados) >= 1
        
        # Check first radicado
        radicado = radicados[0]
        assert radicado.entity_type == EntityType.RADICADO
        assert "2023" in radicado.normalized_value
    
    def test_extract_radicado_continuous(self, parser):
        """Test extraction of continuous radicado format."""
        text = "El radicado 20230012345678901234567 corresponde a..."
        result = parser.parse(text)
        
        assert len(result.radicados) == 1
    
    def test_extract_nit_with_label(self, parser, sample_legal_text):
        """Test NIT extraction with label."""
        result = parser.parse(sample_legal_text)
        
        nits = result.nits
        assert len(nits) >= 1
        
        nit = nits[0]
        assert nit.entity_type == EntityType.NIT
    
    def test_extract_cedula_with_prefix(self, parser, sample_legal_text):
        """Test cédula extraction with CC prefix."""
        result = parser.parse(sample_legal_text)
        
        cedulas = result.cedulas
        assert len(cedulas) >= 1
    
    def test_extract_court_id(self, parser, sample_legal_text):
        """Test court identifier extraction."""
        result = parser.parse(sample_legal_text)
        
        court_ids = result.court_ids
        assert len(court_ids) >= 1
        
        court = court_ids[0]
        assert "Juzgado" in court.raw_value
    
    def test_deduplication(self, parser):
        """Test entity deduplication."""
        text = "CC 12345678 y C.C. 12345678 son el mismo documento"
        result = parser.parse(text)
        
        # Should only have one cédula after deduplication
        assert len(result.cedulas) == 1
    
    def test_empty_text(self, parser):
        """Test parsing empty text."""
        result = parser.parse("")
        
        assert result.entity_count == 0
        assert result.text_length == 0
    
    def test_no_entities(self, parser):
        """Test text with no entities."""
        text = "Este es un texto sin entidades legales colombianas."
        result = parser.parse(text)
        
        # Should have no ID entities
        assert len(result.radicados) == 0
        assert len(result.nits) == 0
        assert len(result.cedulas) == 0
    
    def test_convenience_methods(self, parser, sample_legal_text):
        """Test convenience extraction methods."""
        radicados = parser.extract_radicados(sample_legal_text)
        assert isinstance(radicados, list)
        
        nits = parser.extract_nits(sample_legal_text)
        assert isinstance(nits, list)
        
        cedulas = parser.extract_cedulas(sample_legal_text)
        assert isinstance(cedulas, list)


class TestValidators:
    """Tests for entity validators."""
    
    def test_validate_nit_check_digit_valid(self):
        """Test NIT validation with valid check digit."""
        # Known valid NITs
        assert validate_nit_check_digit("900123456-7") is True
    
    def test_validate_nit_check_digit_invalid(self):
        """Test NIT validation with invalid check digit."""
        # Invalid check digit
        assert validate_nit_check_digit("900123456-0") is False
    
    def test_validate_nit_wrong_length(self):
        """Test NIT validation with wrong length."""
        assert validate_nit_check_digit("12345") is False
    
    def test_validate_radicado_structure_valid(self):
        """Test radicado validation with valid structure."""
        assert validate_radicado_structure("2023-00123-45-67-890-12") is True
        assert validate_radicado_structure("20230012345678901234567") is True
    
    def test_validate_radicado_invalid_year(self):
        """Test radicado validation with invalid year."""
        # Year too old
        assert validate_radicado_structure("1999-00123-45-67-890-12") is False
        
        # Year in future
        assert validate_radicado_structure("2050-00123-45-67-890-12") is False
    
    def test_validate_radicado_wrong_length(self):
        """Test radicado validation with wrong length."""
        assert validate_radicado_structure("2023-00123") is False
    
    def test_validate_cedula_format_valid(self):
        """Test cédula validation with valid format."""
        assert validate_cedula_format("12345678") is True
        assert validate_cedula_format("1234567") is True
        assert validate_cedula_format("123456789") is True
    
    def test_validate_cedula_format_invalid(self):
        """Test cédula validation with invalid format."""
        # Too short
        assert validate_cedula_format("12345") is False
        
        # Too long
        assert validate_cedula_format("1234567890123") is False
        
        # Contains letters
        assert validate_cedula_format("12345abc") is False


class TestNormalizers:
    """Tests for entity normalizers."""
    
    def test_normalize_radicado_with_hyphens(self):
        """Test radicado normalization with hyphens."""
        result = normalize_radicado("2023-00123-45-67-890-12")
        assert "2023" in result
    
    def test_normalize_radicado_continuous(self):
        """Test radicado normalization for continuous format."""
        result = normalize_radicado("20230012345678901234567")
        assert "2023" in result
    
    def test_normalize_nit_with_hyphen(self):
        """Test NIT normalization with hyphen."""
        result = normalize_nit("900123456-7")
        assert result == "900123456-7"
    
    def test_normalize_nit_without_hyphen(self):
        """Test NIT normalization without hyphen."""
        result = normalize_nit("9001234567")
        assert result == "900123456-7"
    
    def test_normalize_cedula_with_prefix(self):
        """Test cédula normalization with prefix."""
        result = normalize_cedula("CC 12345678")
        assert result == "12345678"
    
    def test_normalize_cedula_digits_only(self):
        """Test cédula normalization with digits only."""
        result = normalize_cedula("12345678")
        assert result == "12345678"
