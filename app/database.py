"""
Database configuration and session management.

This module provides:
- Async engine configuration
- Session factory
- Base model class
- Dependency injection for FastAPI
"""

import logging
import ssl as ssl_module
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

logger = logging.getLogger(__name__)

# Naming convention for constraints (useful for migrations)
convention: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all database models."""

    metadata = metadata

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


# Build SSL context for asyncpg (Neon, Supabase, RDS all require TLS).
# asyncpg does NOT accept ssl="require" (that's psycopg2/libpq syntax).
# create_default_context() enables CERT_REQUIRED + hostname verification by default,
# which protects against MitM attacks. Neon's certificates are signed by a well-known
# CA so no custom CA bundle is needed.
_ssl_context = ssl_module.create_default_context()

# NullPool: no persistent connection pool.
# Ideal for Render free tier (cold-start) + Neon serverless pooler.
# Opens a fresh connection per request instead of keeping a pool alive.
engine = create_async_engine(
    settings.async_database_url,
    poolclass=NullPool,
    echo=settings.debug,
    future=True,
    connect_args={"ssl": _ssl_context},
)

# Create session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables. Used for testing."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


async def check_database_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        True if connection is healthy, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {type(e).__name__}: {e}")
        return False
