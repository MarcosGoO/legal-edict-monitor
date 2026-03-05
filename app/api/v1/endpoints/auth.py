"""
Authentication Endpoints.

Provides:
- POST /auth/register  — create a new user account
- POST /auth/login     — obtain access + refresh tokens
- POST /auth/refresh   — exchange refresh token for new access token
- GET  /auth/me        — return info about the current user
"""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.v1.deps import CurrentUser, get_current_user
from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# In-memory user store (dev/demo — replace with DB queries when DB is wired)
# ---------------------------------------------------------------------------
# Key: email (lowercase)
# Value: dict with id, email, password_hash, role, full_name
_users: dict[str, dict] = {}


def _get_user_by_email(email: str) -> dict | None:
    return _users.get(email.lower())


def _get_user_by_id(user_id: str) -> dict | None:
    for u in _users.values():
        if u["id"] == user_id:
            return u
    return None


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "abogado@firma.com",
                "password": "mi_contrasena_segura",
                "full_name": "Carlos Andrés Pérez",
            }
        }
    )

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(None, max_length=255)


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "abogado@firma.com", "password": "mi_contrasena_segura"}
        }
    )

    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class MeResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    role: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=MeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(body: RegisterRequest) -> MeResponse:
    """
    Create a new user account.

    In the full implementation this writes to the database.
    For now users are stored in memory (sufficient for testing and demo).
    """
    email = body.email.lower()

    if _get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password_hash": hash_password(body.password),
        "full_name": body.full_name,
        "role": "editor",  # default role for self-registration
    }
    _users[email] = user

    logger.info(f"New user registered: {email}")

    return MeResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain tokens",
)
async def login(body: LoginRequest) -> TokenResponse:
    """
    Authenticate with email + password and receive JWT tokens.

    Returns an access token (short-lived) and a refresh token (long-lived).
    """
    from app.config import settings

    email = body.email.lower()
    user = _get_user_by_email(email)

    # Constant-time rejection: always run bcrypt even when user doesn't exist
    # to avoid a timing oracle on email enumeration.
    # Pre-computed bcrypt hash of the string "dummy" (cost 12).
    _DUMMY_HASH = "$2b$12$YMV7aIjaWt5pWhseaEI8JOy..2XGjzL3kzmEnjsk9b6X40aZTVvGS"
    stored_hash = user["password_hash"] if user else _DUMMY_HASH

    password_ok = verify_password(body.password, stored_hash)

    if not user or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user["role"],
    )
    refresh_token = create_refresh_token(user_id=user["id"])

    logger.info(f"User logged in: {email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh(body: RefreshRequest) -> TokenResponse:
    """
    Exchange a valid refresh token for a new access token + refresh token pair.
    """
    from app.config import settings

    try:
        payload = decode_access_token.__wrapped__ if hasattr(decode_access_token, "__wrapped__") else None
        # Decode without type check — refresh tokens have type="refresh"
        from jose import jwt as _jwt
        payload = _jwt.decode(
            body.refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "refresh":
            raise JWTError("Not a refresh token")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = _get_user_by_id(user_id) if user_id else None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user["role"],
    )
    new_refresh = create_refresh_token(user_id=user["id"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Get current user info",
)
async def me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> MeResponse:
    """Return profile information for the authenticated user."""
    user = _get_user_by_id(current_user.id)
    full_name = user["full_name"] if user else None

    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=full_name,
        role=current_user.role,
    )
