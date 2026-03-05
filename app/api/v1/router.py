"""
API v1 Router.

Aggregates all v1 API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, clients, documents

api_router = APIRouter()

# Auth endpoints — public (no authentication required)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
)

# Protected endpoints — require valid JWT
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

api_router.include_router(
    clients.router,
    prefix="/clients",
    tags=["Clients"],
)
