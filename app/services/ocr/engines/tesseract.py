"""
Tesseract OCR Engine.

Local OCR processing using Tesseract with Spanish language support.
Optimized for Colombian legal documents.
"""

import io
import logging
from pathlib import Path
from typing import Any

from PIL import Image

from app.services.ocr.base import (
    OCREngine,
    OCREngineBase,
    OCRResult,
)

logger = logging.getLogger(__name__)


class TesseractEngine(OCREngineBase):
    """
    Tesseract OCR engine for local processing.
    
    Optimized for Spanish legal documents with custom configuration.
    """
    
    # Tesseract configuration for Spanish legal documents
    TESSERACT_CONFIG = (
        "--oem 3 "          # LSTM neural net engine
        "--psm 6 "          # Assume uniform block of text
        "--dpi 300"         # High DPI for better accuracy
    )
    
    def __init__(self, language: str = "spa"):
        """
        Initialize Tesseract engine.
        
        Args:
            language: OCR language code (default: spa for Spanish)
        """
        self.language = language
    
    async def is_available(self) -> bool:
        """Check if Tesseract is installed and configured."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            return False
    
    async def extract_text(self, pdf_path: Path) -> OCRResult:
        """
        Extract text using Tesseract OCR.
        
        Process:
        1. Convert PDF pages to images
        2. Run OCR on each image
        3. Aggregate results with confidence scores
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            OCRResult with extracted text and confidence
        """
        import pytesseract
        
        # Convert PDF to images
        images = await self._pdf_to_images(pdf_path)
        
        if not images:
            logger.warning(f"No images extracted from {pdf_path}")
            return OCRResult(
                text="",
                engine_used=OCREngine.TESSERACT,
                confidence=0.0,
                pages_processed=0,
                is_searchable=False,
                metadata={"error": "No images extracted"},
            )
        
        # Process each page
        pages_text: list[str] = []
        all_confidences: list[float] = []
        pages_metadata: list[dict[str, Any]] = []
        
        for i, image in enumerate(images):
            try:
                # Run OCR with confidence data
                data = pytesseract.image_to_data(
                    image,
                    lang=self.language,
                    output_type=pytesseract.Output.DICT,
                    config=self.TESSERACT_CONFIG,
                )
                
                # Extract text and calculate confidence
                text_parts: list[str] = []
                confidences: list[int] = []
                
                for j, text in enumerate(data["text"]):
                    if text.strip():
                        text_parts.append(text)
                        conf = data["conf"][j]
                        if conf > 0:  # Valid confidence
                            confidences.append(conf)
                
                page_text = " ".join(text_parts)
                pages_text.append(page_text)
                
                # Calculate page confidence
                page_conf = sum(confidences) / len(confidences) if confidences else 0
                all_confidences.append(page_conf / 100)  # Normalize to 0-1
                
                pages_metadata.append({
                    "page": i + 1,
                    "text_length": len(page_text),
                    "word_count": len(text_parts),
                    "confidence": page_conf / 100,
                })
                
                logger.debug(
                    f"Page {i + 1}: {len(text_parts)} words, "
                    f"confidence={page_conf:.1f}%"
                )
                
            except Exception as e:
                logger.error(f"Error processing page {i + 1}: {e}")
                pages_text.append("")
                all_confidences.append(0.0)
                pages_metadata.append({
                    "page": i + 1,
                    "error": str(e),
                })
        
        # Calculate average confidence
        avg_confidence = (
            sum(all_confidences) / len(all_confidences)
            if all_confidences
            else 0.0
        )
        
        # Combine all text
        full_text = "\n\n".join(pages_text)
        
        return OCRResult(
            text=full_text,
            engine_used=OCREngine.TESSERACT,
            confidence=avg_confidence,
            pages_processed=len(images),
            is_searchable=False,
            metadata={
                "language": self.language,
                "pages": pages_metadata,
                "pages_text_length": [len(t) for t in pages_text],
            },
        )
    
    async def _pdf_to_images(
        self,
        pdf_path: Path,
        dpi: int = 300,
    ) -> list[Image.Image]:
        """
        Convert PDF pages to PIL Images.
        
        Uses PyMuPDF for high-quality rendering.
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for rendering
            
        Returns:
            List of PIL Images
        """
        import fitz  # PyMuPDF
        
        images: list[Image.Image] = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Render page to image
                zoom = dpi / 72  # Scale factor
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                images.append(image)
            
            doc.close()
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise
        
        return images
