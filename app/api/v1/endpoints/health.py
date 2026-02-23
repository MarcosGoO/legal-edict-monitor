"""
Health Check Endpoints.

Provides health and readiness checks for monitoring.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health() -> dict:
    """
    Health check endpoint.
    
    Returns basic health status.
    """
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict:
    """
    Readiness check endpoint.
    
    Checks if all dependencies are available.
    """
    # TODO: Add actual dependency checks
    checks = {
        "database": "ok",
        "redis": "ok",
        "ocr": "ok",
    }
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return {
        "status": "ready" if all_ok else "not_ready",
        "checks": checks,
    }
