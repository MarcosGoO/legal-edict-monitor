"""
Caching Service for OCR Results.

Provides Redis-based caching to avoid re-processing the same documents.
Uses document hash as cache key for deduplication.
"""

import hashlib
import json
import logging
from typing import Any, Optional

from app.redis_client import get_redis_client

logger = logging.getLogger(__name__)

# Cache key prefix for OCR results
OCR_CACHE_PREFIX = "ocr:result:"
# Default TTL for cached results (24 hours)
DEFAULT_CACHE_TTL = 86400


class CacheService:
    """
    Redis-based caching service for OCR results.
    
    Usage:
        cache = CacheService()
        
        # Cache OCR result
        await cache.set_ocr_result(document_hash, result_dict)
        
        # Retrieve cached result
        result = await cache.get_ocr_result(document_hash)
    """
    
    def __init__(self, ttl: int = DEFAULT_CACHE_TTL):
        """
        Initialize cache service.
        
        Args:
            ttl: Time-to-live for cached items in seconds
        """
        self.ttl = ttl
    
    @staticmethod
    def compute_document_hash(content: bytes) -> str:
        """
        Compute SHA-256 hash of document content.
        
        Args:
            content: Document bytes
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content).hexdigest()
    
    def _get_cache_key(self, document_hash: str) -> str:
        """Generate cache key for document."""
        return f"{OCR_CACHE_PREFIX}{document_hash}"
    
    async def get_ocr_result(self, document_hash: str) -> Optional[dict[str, Any]]:
        """
        Retrieve cached OCR result.
        
        Args:
            document_hash: SHA-256 hash of document
            
        Returns:
            Cached result dictionary or None if not found
        """
        try:
            client = await get_redis_client()
            cache_key = self._get_cache_key(document_hash)
            
            cached = await client.get(cache_key)
            
            if cached:
                logger.info(f"Cache hit for document {document_hash[:16]}...")
                return json.loads(cached)
            
            logger.debug(f"Cache miss for document {document_hash[:16]}...")
            return None
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None
    
    async def set_ocr_result(
        self,
        document_hash: str,
        result: dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache OCR result.
        
        Args:
            document_hash: SHA-256 hash of document
            result: OCR result dictionary to cache
            ttl: Optional custom TTL (uses default if not provided)
            
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            client = await get_redis_client()
            cache_key = self._get_cache_key(document_hash)
            
            # Serialize result
            serialized = json.dumps(result, default=str)
            
            # Set with TTL
            await client.setex(
                cache_key,
                ttl or self.ttl,
                serialized,
            )
            
            logger.info(
                f"Cached OCR result for document {document_hash[:16]}... "
                f"(TTL: {ttl or self.ttl}s)"
            )
            return True
            
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
            return False
    
    async def delete_ocr_result(self, document_hash: str) -> bool:
        """
        Delete cached OCR result.
        
        Args:
            document_hash: SHA-256 hash of document
            
        Returns:
            True if deleted, False if not found or error
        """
        try:
            client = await get_redis_client()
            cache_key = self._get_cache_key(document_hash)
            
            deleted = await client.delete(cache_key)
            return deleted > 0
            
        except Exception as e:
            logger.warning(f"Cache deletion failed: {e}")
            return False
    
    async def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            client = await get_redis_client()
            
            # Get all OCR cache keys
            keys = []
            async for key in client.scan_iter(match=f"{OCR_CACHE_PREFIX}*"):
                keys.append(key)
            
            # Get info
            info = await client.info("memory")
            
            return {
                "cached_documents": len(keys),
                "used_memory": info.get("used_memory_human", "unknown"),
                "cache_prefix": OCR_CACHE_PREFIX,
            }
            
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {
                "cached_documents": 0,
                "error": str(e),
            }
    
    async def clear_all_cache(self) -> int:
        """
        Clear all cached OCR results.
        
        Returns:
            Number of keys deleted
        """
        try:
            client = await get_redis_client()
            
            keys = []
            async for key in client.scan_iter(match=f"{OCR_CACHE_PREFIX}*"):
                keys.append(key)
            
            if keys:
                deleted = await client.delete(*keys)
                logger.info(f"Cleared {deleted} cached OCR results")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")
            return 0


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create cache service instance."""
    global _cache_service
    
    if _cache_service is None:
        _cache_service = CacheService()
    
    return _cache_service
