"""
OCR Engine implementations.
"""

from app.services.ocr.engines.native import NativePDFEngine
from app.services.ocr.engines.tesseract import TesseractEngine

__all__ = [
    "NativePDFEngine",
    "TesseractEngine",
]

# Optional: AWS Textract
try:
    from app.services.ocr.engines.textract import TextractEngine
    __all__.append("TextractEngine")
except ImportError:
    pass
