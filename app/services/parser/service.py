"""
Colombian Entity Parser Service.

Main service for extracting entities from Colombian legal documents.
Combines regex-based extraction for IDs with NLP for names.
"""

import logging
import time
from typing import Any

from app.config import settings
from app.services.parser.base import (
    EntityType,
    ExtractedEntity,
    ParseResult,
)
from app.services.parser.patterns import compile_patterns
from app.services.parser.validators import (
    normalize_cedula,
    normalize_name,
    normalize_nit,
    normalize_radicado,
    validate_cedula_format,
    validate_nit_check_digit,
    validate_radicado_structure,
)

logger = logging.getLogger(__name__)


class ColombianEntityParser:
    """
    Parser for Colombian legal document entities.
    
    Combines regex-based extraction for IDs with NLP for names.
    
    Usage:
        parser = ColombianEntityParser()
        result = parser.parse(document_text)
        for entity in result.entities:
            print(f"{entity.entity_type}: {entity.normalized_value}")
    """

    # Spanish name prefixes to handle
    NAME_PREFIXES = {
        "del", "de", "la", "las", "los", "y", "e",
        "van", "von", "di", "da", "dos", "das"
    }

    # Common Colombian first names for validation
    COMMON_FIRST_NAMES = {
        "jose", "maria", "carlos", "andres", "david", "luis",
        "juan", "miguel", "fernando", "javier", "daniel",
        "alejandro", "ricardo", "eduardo", "jorge", "diego",
        "camilo", "sergio", "andrea", "patricia", "lucia",
        "monica", "claudia", "diana", "paola", "natalia",
    }

    def __init__(
        self,
        spacy_model: str | None = None,
        confidence_threshold: float = 0.7,
    ):
        """
        Initialize the parser.
        
        Args:
            spacy_model: spaCy model name (default from settings)
            confidence_threshold: Minimum confidence for entities
        """
        self.spacy_model = spacy_model or settings.spacy_model
        self.confidence_threshold = confidence_threshold
        self.compiled_patterns = compile_patterns()

        # Lazy load spaCy model
        self._nlp: Any = None

    @property
    def nlp(self) -> Any:
        """Get or load spaCy model (lazy load)."""
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load(self.spacy_model)
                logger.info(f"Loaded spaCy model: {self.spacy_model}")
            except OSError:
                logger.warning(
                    f"spaCy model {self.spacy_model} not found, "
                    "falling back to es_core_news_sm"
                )
                try:
                    import spacy
                    self._nlp = spacy.load("es_core_news_sm")
                    self.spacy_model = "es_core_news_sm"
                except OSError:
                    logger.error(
                        "No spaCy Spanish model found. "
                        "Install with: python -m spacy download es_core_news_sm"
                    )
                    self._nlp = None
        return self._nlp

    def parse(self, text: str) -> ParseResult:
        """
        Parse document text and extract all entities.
        
        Process:
        1. Extract IDs using regex (Radicado, NIT, Cédula)
        2. Extract names using spaCy NER
        3. Validate and normalize all entities
        4. Deduplicate results
        
        Args:
            text: Document text to parse
            
        Returns:
            ParseResult with all extracted entities
        """
        start_time = time.time()

        entities: list[ExtractedEntity] = []

        # Phase 1: Regex extraction for IDs
        entities.extend(self._extract_with_regex(text))

        # Phase 2: NLP extraction for names
        entities.extend(self._extract_names_with_nlp(text))

        # Phase 3: Normalize and validate
        entities = [self._normalize_entity(e) for e in entities]
        entities = [e for e in entities if self._validate_entity(e)]

        # Phase 4: Deduplicate
        entities = self._deduplicate_entities(entities)

        processing_time = (time.time() - start_time) * 1000

        return ParseResult(
            entities=entities,
            text_length=len(text),
            processing_time_ms=processing_time,
            nlp_model=self.spacy_model,
        )

    def _extract_with_regex(self, text: str) -> list[ExtractedEntity]:
        """Extract entities using compiled regex patterns."""
        entities = []

        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    raw_value = match.group(0)

                    # Get context (50 chars before and after)
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    entity = ExtractedEntity(
                        entity_type=entity_type,
                        raw_value=raw_value,
                        normalized_value=raw_value,
                        confidence=0.95,  # High confidence for regex matches
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=context,
                    )
                    entities.append(entity)

        return entities

    def _extract_names_with_nlp(self, text: str) -> list[ExtractedEntity]:
        """Extract person names using spaCy NER."""
        entities = []

        if self.nlp is None:
            logger.warning("spaCy model not available, skipping name extraction")
            return entities

        doc = self.nlp(text)

        for ent in doc.ents:
            if ent.label_ == "PER":  # Person entity
                # Get context
                start = max(0, ent.start_char - 50)
                end = min(len(text), ent.end_char + 50)
                context = text[start:end]

                # Calculate confidence based on entity characteristics
                confidence = self._calculate_name_confidence(ent.text)

                entity = ExtractedEntity(
                    entity_type=EntityType.NOMBRE,
                    raw_value=ent.text,
                    normalized_value=normalize_name(ent.text),
                    confidence=confidence,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    context=context,
                    metadata={
                        "spacy_label": ent.label_,
                        "token_count": len(ent),
                    },
                )
                entities.append(entity)

        return entities

    def _calculate_name_confidence(self, name: str) -> float:
        """
        Calculate confidence score for extracted name.
        
        Factors:
        - Number of words (2-4 is typical for Colombian names)
        - Presence of common first names
        - Absence of numbers or special characters
        """
        words = name.lower().split()

        if len(words) < 2 or len(words) > 6:
            return 0.5

        # Check for common first names
        has_common_name = any(w in self.COMMON_FIRST_NAMES for w in words)

        # Check for invalid characters
        has_numbers = any(c.isdigit() for c in name)
        has_special = any(
            not c.isalnum() and c not in " áéíóúñüÁÉÍÓÚÑÜ"
            for c in name
        )

        confidence = 0.7
        if has_common_name:
            confidence += 0.15
        if has_numbers:
            confidence -= 0.3
        if has_special:
            confidence -= 0.2

        return min(max(confidence, 0.0), 1.0)

    def _normalize_entity(self, entity: ExtractedEntity) -> ExtractedEntity:
        """Normalize entity value based on type."""
        if entity.entity_type == EntityType.RADICADO:
            entity.normalized_value = normalize_radicado(entity.raw_value)

        elif entity.entity_type == EntityType.NIT:
            entity.normalized_value = normalize_nit(entity.raw_value)

        elif entity.entity_type == EntityType.CEDULA:
            entity.normalized_value = normalize_cedula(entity.raw_value)

        elif entity.entity_type == EntityType.NOMBRE:
            entity.normalized_value = normalize_name(entity.raw_value)

        return entity

    def _validate_entity(self, entity: ExtractedEntity) -> bool:
        """Validate entity based on type-specific rules."""
        if entity.entity_type == EntityType.RADICADO:
            return validate_radicado_structure(entity.normalized_value)

        elif entity.entity_type == EntityType.NIT:
            return validate_nit_check_digit(entity.normalized_value)

        elif entity.entity_type == EntityType.CEDULA:
            return validate_cedula_format(entity.normalized_value)

        elif entity.entity_type == EntityType.NOMBRE:
            return entity.confidence >= self.confidence_threshold

        return True

    def _deduplicate_entities(
        self,
        entities: list[ExtractedEntity],
    ) -> list[ExtractedEntity]:
        """Remove duplicate entities, keeping highest confidence."""
        seen: dict[tuple[EntityType, str], ExtractedEntity] = {}

        for entity in entities:
            key = (entity.entity_type, entity.normalized_value)

            if key not in seen or entity.confidence > seen[key].confidence:
                seen[key] = entity

        return list(seen.values())

    def extract_radicados(self, text: str) -> list[str]:
        """
        Extract only radicados from text.
        
        Convenience method for quick extraction.
        
        Args:
            text: Document text
            
        Returns:
            List of normalized radicados
        """
        result = self.parse(text)
        return [e.normalized_value for e in result.radicados]

    def extract_nits(self, text: str) -> list[str]:
        """
        Extract only NITs from text.
        
        Args:
            text: Document text
            
        Returns:
            List of normalized NITs
        """
        result = self.parse(text)
        return [e.normalized_value for e in result.nits]

    def extract_cedulas(self, text: str) -> list[str]:
        """
        Extract only cédulas from text.
        
        Args:
            text: Document text
            
        Returns:
            List of normalized cédulas
        """
        result = self.parse(text)
        return [e.normalized_value for e in result.cedulas]

    def extract_names(self, text: str) -> list[str]:
        """
        Extract only names from text.
        
        Args:
            text: Document text
            
        Returns:
            List of normalized names
        """
        result = self.parse(text)
        return [e.normalized_value for e in result.names]
