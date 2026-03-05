"""
FastAPI Dependencies — Authentication & Authorization.

Provides reusable Depends() callables:
- get_current_user  → extracts and validates the JWT from the Authorization header
- require_admin     → same, but also enforces admin role
- require_editor    → same, but enforces admin or editor role
"""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.auth import decode_access_token

# HTTPBearer extracts the token from "Authorization: Bearer <token>"
# auto_error=False lets us return a cleaner 401 instead of a 403
_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    """Lightweight representation of the authenticated user extracted from JWT."""
    id: str
    email: str
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_editor(self) -> bool:
        return self.role in ("admin", "editor")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    """
    FastAPI dependency — extract and validate the JWT access token.

    Returns a CurrentUser on success.
    Raises HTTP 401 on any auth failure (missing token, bad signature, expired).
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")

    if not user_id or not email or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(id=user_id, email=email, role=role)


def require_editor(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Dependency — authenticated user with editor or admin role."""
    if not user.is_editor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions (editor role required)",
        )
    return user


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Dependency — authenticated user with admin role."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions (admin role required)",
        )
    return user
