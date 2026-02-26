"""
API v1 Router.

Aggregates all v1 API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import clients, documents

api_router = APIRouter()

# Include endpoint routers
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
