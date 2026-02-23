"""
OCR Base Classes and Types.

Defines the core data structures and abstract base class for OCR engines.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class OCREngine(str, Enum):
    """Available OCR engines."""
    NATIVE = "native"       # Direct text extraction from PDF
    TESSERACT = "tesseract"  # Local Tesseract OCR
    TEXTRACT = "textract"   # AWS Textract
    EASYOCR = "easyocr"     # EasyOCR (GPU-accelerated)


@dataclass
class OCRResult:
    """
    Result of OCR processing.
    
    Contains extracted text, metadata, and quality metrics.
    """
    text: str
    engine_used: OCREngine
    confidence: float
    pages_processed: int
    is_searchable: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def word_count(self) -> int:
        """Count words in extracted text."""
        return len(self.text.split())
    
    @property
    def character_count(self) -> int:
        """Count characters in extracted text."""
        return len(self.text)
    
    @property
    def is_quality_acceptable(self) -> bool:
        """Check if extraction quality meets minimum threshold."""
        # Minimum 50 words and confidence >= 0.7
        return self.confidence >= 0.7 and self.word_count >= 50
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text_length": self.character_count,
            "word_count": self.word_count,
            "engine_used": self.engine_used.value,
            "confidence": self.confidence,
            "pages_processed": self.pages_processed,
            "is_searchable": self.is_searchable,
            "metadata": self.metadata,
        }


@dataclass
class PDFAnalysis:
    """
    Analysis of PDF structure.
    
    Used to determine the best extraction strategy.
    """
    has_text_layer: bool
    page_count: int
    is_scanned: bool
    estimated_quality: float
    recommended_engine: OCREngine
    text_sample: str = ""
    
    @property
    def needs_ocr(self) -> bool:
        """Check if OCR is needed."""
        return not self.has_text_layer or self.is_scanned
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "has_text_layer": self.has_text_layer,
            "page_count": self.page_count,
            "is_scanned": self.is_scanned,
            "estimated_quality": self.estimated_quality,
            "recommended_engine": self.recommended_engine.value,
        }


class OCREngineBase(ABC):
    """
    Abstract base class for OCR engines.
    
    All OCR engine implementations must inherit from this class
    and implement the extract_text method.
    """
    
    @abstractmethod
    async def extract_text(self, pdf_path: Path) -> OCRResult:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            OCRResult with extracted text and metadata
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the OCR engine is available.
        
        Returns:
            True if the engine can be used, False otherwise
        """
        pass
    
    def _calculate_confidence(self, text: str, char_count: int, word_count: int) -> float:
        """
        Calculate a confidence score based on text characteristics.
        
        Args:
            text: Extracted text
            char_count: Character count
            word_count: Word count
            
        Returns:
            Confidence score between 0 and 1
        """
        if not text or char_count == 0:
            return 0.0
        
        # Base confidence on text density
        avg_word_length = char_count / max(word_count, 1)
        
        # Typical Spanish word length is 4-6 characters
        if 3 <= avg_word_length <= 8:
            length_score = 1.0
        elif 2 <= avg_word_length <= 10:
            length_score = 0.8
        else:
            length_score = 0.5
        
        # Check for common Spanish words
        common_words = {"de", "la", "el", "en", "que", "y", "a", "del", "se", "los"}
        words = set(text.lower().split())
        common_found = len(words & common_words)
        vocabulary_score = min(common_found / 5, 1.0)
        
        # Combine scores
        return (length_score * 0.5 + vocabulary_score * 0.5)
