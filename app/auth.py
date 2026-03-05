"""
JWT Authentication Service.

Provides:
- Password hashing and verification via bcrypt (direct, no passlib)
- JWT access/refresh token creation and verification
"""

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import settings


# ---------------------------------------------------------------------------
# Password helpers (bcrypt direct — passlib 1.7.4 is incompatible with bcrypt>=4)
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Return bcrypt hash of *plain* password."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def _create_token(subject: str, extra_claims: dict[str, Any], expires_delta: timedelta) -> str:
    """Create a signed JWT with *subject* and *extra_claims*."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        **extra_claims,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, email: str, role: str) -> str:
    """Create a short-lived access token."""
    return _create_token(
        subject=user_id,
        extra_claims={"email": email, "role": role, "type": "access"},
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token."""
    return _create_token(
        subject=user_id,
        extra_claims={"type": "refresh"},
        expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify an access token.

    Raises:
        JWTError: if the token is invalid, expired, or not an access token.
    """
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != "access":
        raise JWTError("Not an access token")
    return payload
