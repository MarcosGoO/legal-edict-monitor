"""
OCR Service Package.

Provides intelligent OCR processing for PDF documents:
- Automatic detection of text vs scanned documents
- Multiple OCR engine support (Tesseract, AWS Textract)
- Confidence-based fallback
"""

from app.services.ocr.base import OCREngine, OCRResult, PDFAnalysis
from app.services.ocr.service import SmartOCRService

__all__ = [
    "SmartOCRService",
    "OCREngine",
    "OCRResult",
    "PDFAnalysis",
]
