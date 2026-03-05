"""
JWT Authentication Service.

Provides:
- Password hashing and verification via bcrypt
- JWT access/refresh token creation and verification
- Current user extraction from token
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# bcrypt context — cost factor handled by passlib defaults
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Return bcrypt hash of *plain* password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return _pwd_context.verify(plain, hashed)


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
