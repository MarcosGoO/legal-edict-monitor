"""
Client Management Endpoints.

Provides endpoints for managing clients and watchlist entries.
"""

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ClientCreate(BaseModel):
    """Request model for creating a client."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "JOSÉ MARÍA RODRÍGUEZ GARCÍA",
                "document_type": "CC",
                "document_number": "12345678",
                "nit": None,
                "aliases": ["JOSE MARIA RODRIGUEZ"],
                "notes": "Client since 2023",
            }
        }
    )

    full_name: str = Field(..., min_length=2, max_length=500)
    document_type: str | None = Field(None, pattern="^(CC|CE|NIT|PP|TI)$")
    document_number: str | None = Field(None, max_length=20)
    nit: str | None = Field(None, max_length=20)
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None


class ClientResponse(BaseModel):
    """Response model for a client."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "full_name": "JOSÉ MARÍA RODRÍGUEZ GARCÍA",
                "document_type": "CC",
                "document_number": "12345678",
                "nit": None,
                "aliases": ["JOSE MARIA RODRIGUEZ"],
                "is_active": True,
            }
        }
    )

    id: str
    full_name: str
    document_type: str | None = None
    document_number: str | None = None
    nit: str | None = None
    aliases: list[str] = []
    is_active: bool = True


class ClientListResponse(BaseModel):
    """Response model for client list."""
    clients: list[ClientResponse]
    total: int
    page: int
    page_size: int


class WatchlistCreate(BaseModel):
    """Request model for creating a watchlist entry."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_id": "123e4567-e89b-12d3-a456-426614174000",
                "case_numbers": ["2023-00123-45-67-890-12"],
                "court_ids": [],
                "notification_preferences": {
                    "channels": ["whatsapp", "email"],
                    "immediate": True,
                },
            }
        }
    )

    client_id: str
    case_numbers: list[str] = Field(default_factory=list)
    court_ids: list[str] = Field(default_factory=list)
    notification_preferences: dict = Field(
        default_factory=lambda: {
            "channels": ["whatsapp", "email"],
            "immediate": True,
        }
    )


class WatchlistResponse(BaseModel):
    """Response model for a watchlist entry."""
    id: str
    client_id: str
    case_numbers: list[str]
    court_ids: list[str]
    is_active: bool


# ============================================================================
# Endpoints
# ============================================================================

@router.get(
    "",
    response_model=ClientListResponse,
    summary="List clients",
    description="Get paginated list of clients for the current law firm.",
)
async def list_clients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    search: str | None = Query(None, description="Search by name or document"),
) -> ClientListResponse:
    """
    List clients.
    
    Returns a paginated list of clients for the current law firm.
    Supports filtering by active status and searching by name or document.
    """
    # TODO: Implement actual database query
    # For now, return empty list
    return ClientListResponse(
        clients=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a client",
    description="Create a new client to monitor.",
)
async def create_client(client: ClientCreate) -> ClientResponse:
    """
    Create a client.
    
    Creates a new client entry for monitoring.
    The client will be added to the watchlist for matching.
    """
    # TODO: Implement actual database creation
    # For now, return mock response
    return ClientResponse(
        id=str(uuid.uuid4()),
        full_name=client.full_name,
        document_type=client.document_type,
        document_number=client.document_number,
        nit=client.nit,
        aliases=client.aliases,
        is_active=True,
    )


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get a client",
    description="Get details of a specific client.",
)
async def get_client(client_id: str) -> ClientResponse:
    """
    Get a client by ID.
    
    Returns the details of a specific client.
    """
    # TODO: Implement actual database query
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Client {client_id} not found",
    )


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Update a client",
    description="Update client information.",
)
async def update_client(
    client_id: str,
    client: ClientCreate,
) -> ClientResponse:
    """
    Update a client.
    
    Updates the information of an existing client.
    """
    # TODO: Implement actual database update
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Client {client_id} not found",
    )


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a client",
    description="Remove a client from monitoring.",
)
async def delete_client(client_id: str) -> None:
    """
    Delete a client.
    
    Removes a client and all associated watchlist entries.
    """
    # TODO: Implement actual database deletion
    pass


# ============================================================================
# Watchlist Endpoints
# ============================================================================

@router.post(
    "/{client_id}/watchlist",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create watchlist entry",
    description="Add a watchlist entry for a client.",
)
async def create_watchlist_entry(
    client_id: str,
    watchlist: WatchlistCreate,
) -> WatchlistResponse:
    """
    Create a watchlist entry.
    
    Adds monitoring configuration for a client.
    """
    # TODO: Implement actual database creation
    return WatchlistResponse(
        id=str(uuid.uuid4()),
        client_id=client_id,
        case_numbers=watchlist.case_numbers,
        court_ids=watchlist.court_ids,
        is_active=True,
    )


@router.get(
    "/{client_id}/watchlist",
    response_model=list[WatchlistResponse],
    summary="Get watchlist entries",
    description="Get all watchlist entries for a client.",
)
async def get_watchlist_entries(client_id: str) -> list[WatchlistResponse]:
    """
    Get watchlist entries for a client.
    """
    # TODO: Implement actual database query
    return []
