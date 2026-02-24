"""
Redis client configuration and utilities.

This module provides:
- Redis connection pool
- Health check functions
- Caching utilities
"""

import logging
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import RedisError

from app.config import settings

logger = logging.getLogger(__name__)

# Redis connection pool (lazy initialization)
_redis_pool: Optional[redis.ConnectionPool] = None


def get_redis_pool() -> redis.ConnectionPool:
    """
    Get or create Redis connection pool.
    
    Returns:
        Redis connection pool instance
    """
    global _redis_pool
    
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=10,
        )
        logger.info(f"Created Redis connection pool: {settings.redis_url}")
    
    return _redis_pool


async def get_redis_client() -> redis.Redis:
    """
    Get Redis client instance.
    
    Returns:
        Redis client instance
    """
    return redis.Redis(connection_pool=get_redis_pool())


async def close_redis() -> None:
    """Close Redis connection pool."""
    global _redis_pool
    
    if _redis_pool is not None:
        await _redis_pool.disconnect()
        _redis_pool = None
        logger.info("Closed Redis connection pool")


async def check_redis_connection() -> bool:
    """
    Check if Redis connection is healthy.
    
    Returns:
        True if connection is healthy, False otherwise.
    """
    try:
        client = await get_redis_client()
        await client.ping()
        return True
    except RedisError as e:
        logger.warning(f"Redis health check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking Redis: {e}")
        return False


async def get_redis_info() -> dict:
    """
    Get Redis server information.
    
    Returns:
        Dictionary with Redis info or error details
    """
    try:
        client = await get_redis_client()
        info = await client.info()
        return {
            "connected": True,
            "version": info.get("redis_version", "unknown"),
            "used_memory": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
        }
    except RedisError as e:
        return {
            "connected": False,
            "error": str(e),
        }
