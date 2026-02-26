"""
Native PDF Engine.

Extracts text directly from PDFs that have embedded text.
Uses PyMuPDF (fitz) for fast extraction.
"""

import logging
from pathlib import Path

from app.services.ocr.base import (
    OCREngine,
    OCREngineBase,
    OCRResult,
)

logger = logging.getLogger(__name__)


class NativePDFEngine(OCREngineBase):
    """
    Native PDF text extraction engine.
    
    Extracts text directly from PDFs with embedded text layers.
    Fast and accurate for digital-born PDFs.
    """

    async def is_available(self) -> bool:
        """Check if PyMuPDF is available."""
        try:
            import fitz  # noqa: F401
            return True
        except ImportError:
            return False

    async def extract_text(self, pdf_path: Path) -> OCRResult:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            OCRResult with extracted text
        """
        import fitz

        doc = fitz.open(pdf_path)
        page_count = len(doc)

        pages_text: list[str] = []
        total_chars = 0

        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text()
            pages_text.append(text)
            total_chars += len(text)

        doc.close()

        # Combine all text
        full_text = "\n\n".join(pages_text)
        word_count = len(full_text.split())

        # Calculate confidence based on text density
        confidence = self._calculate_confidence(
            full_text,
            total_chars,
            word_count,
        )

        return OCRResult(
            text=full_text,
            engine_used=OCREngine.NATIVE,
            confidence=confidence,
            pages_processed=page_count,
            is_searchable=True,
            metadata={
                "total_chars": total_chars,
                "pages_text_length": [len(t) for t in pages_text],
            },
        )
