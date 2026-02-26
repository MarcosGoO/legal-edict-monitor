"""
Services package for Edict Guardian.

This package contains the core business logic services:
- OCR: Smart OCR wrapper for PDF processing
- Parser: Colombian entity extraction
- Crawler: Portal crawling logic
- Matcher: Watchlist matching engine
- Notifier: Notification dispatch
"""

from app.services.ocr import OCREngine, OCRResult, SmartOCRService
from app.services.parser import ColombianEntityParser, EntityType, ParseResult

__all__ = [
    "SmartOCRService",
    "OCRResult",
    "OCREngine",
    "ColombianEntityParser",
    "ParseResult",
    "EntityType",
]
