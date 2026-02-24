"""
Edict Guardian - FastAPI Application Entry Point.

Main application module that configures:
- FastAPI app instance
- Middleware (CORS, etc.)
- Router includes
- Lifecycle events
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import check_database_connection, close_db, init_db
from app.redis_client import check_redis_connection, close_redis
from app.api.v1.router import api_router
from app.middleware import RequestLoggingMiddleware, SlowRequestMiddleware
from app.exceptions import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"name": "%(name)s", "message": "%(message)s"}'
        if settings.log_format == "json"
        else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ),
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.app_env} mode")
    
    # Initialize database (for development/testing)
    if settings.is_development:
        logger.info("Initializing database tables")
        await init_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    await close_redis()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=(
        "Legal notification backend for scraping and analyzing "
        "Colombian legal gazettes and court edicts."
    ),
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add slow request detection middleware (threshold: 1 second)
app.add_middleware(SlowRequestMiddleware, threshold_ms=1000.0)

# Register exception handlers
register_exception_handlers(app)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check() -> dict:
    """Readiness check endpoint for Kubernetes."""
    # Check database connectivity
    db_healthy = await check_database_connection()
    
    # Check Redis connectivity
    redis_healthy = await check_redis_connection()
    
    # Determine overall status
    all_healthy = db_healthy and redis_healthy
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": {
            "database": "ok" if db_healthy else "error",
            "redis": "ok" if redis_healthy else "error",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
    )
