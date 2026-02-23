"""
Services package for Edict Guardian.

This package contains the core business logic services:
- OCR: Smart OCR wrapper for PDF processing
- Parser: Colombian entity extraction
- Crawler: Portal crawling logic
- Matcher: Watchlist matching engine
- Notifier: Notification dispatch
"""

from app.services.ocr import SmartOCRService, OCRResult, OCREngine
from app.services.parser import ColombianEntityParser, ParseResult, EntityType

__all__ = [
    "SmartOCRService",
    "OCRResult",
    "OCREngine",
    "ColombianEntityParser",
    "ParseResult",
    "EntityType",
]
