"""
Database models for Edict Guardian.

This package contains all SQLAlchemy ORM models:
- LawFirm: Law firm entities
- User: Law firm staff users
- Client: People/entities to monitor
- WatchlistEntry: Monitoring configuration
- SourcePortal: Court portal configuration
- RawDocument: Ingested PDF documents
- ExtractedEntity: Entities extracted from documents
- DetectedEdict: Matched edicts
- Notification: Notification records
- CrawlLog: Crawler audit trail
"""

from app.models.base import TimestampMixin
from app.models.client import Client
from app.models.crawl_log import CrawlLog
from app.models.detected_edict import DetectedEdict
from app.models.extracted_entity import ExtractedEntity
from app.models.law_firm import LawFirm
from app.models.notification import Notification
from app.models.raw_document import RawDocument
from app.models.source_portal import SourcePortal
from app.models.user import User
from app.models.watchlist_entry import WatchlistEntry

__all__ = [
    "TimestampMixin",
    "LawFirm",
    "User",
    "Client",
    "WatchlistEntry",
    "SourcePortal",
    "RawDocument",
    "ExtractedEntity",
    "DetectedEdict",
    "Notification",
    "CrawlLog",
]
