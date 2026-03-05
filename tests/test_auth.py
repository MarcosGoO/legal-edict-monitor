"""
Tests for Authentication Endpoints and JWT utilities.

NOTE: The in-memory _users store in auth.py persists for the lifetime of the
process. Each test uses a unique email (via uuid suffix) to avoid collisions.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def unique_email(prefix: str = "user") -> str:
    """Generate a unique email for each test run."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.com"


def register_and_login(client: TestClient, email: str, password: str = "testpassword1") -> dict:
    """Register a user and return the login token response dict."""
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert r.status_code == 201, f"Register failed: {r.text}"
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()


def auth_headers(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": unique_email("reg"), "password": "strongpass1", "full_name": "New User"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["role"] == "editor"
        assert "id" in data

    def test_register_duplicate_email(self, client):
        email = unique_email("dup")
        payload = {"email": email, "password": "strongpass1"}
        client.post("/api/v1/auth/register", json=payload)
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409

    def test_register_short_password(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": unique_email("short"), "password": "abc"},
        )
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "strongpass1"},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success(self, client):
        email = unique_email("login")
        tokens = register_and_login(client, email)
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] > 0

    def test_login_wrong_password(self, client):
        email = unique_email("wrongpw")
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "correct_pass1"},
        )
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "wrong_pass"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": unique_email("ghost"), "password": "doesntmatter"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------

class TestMe:
    def test_me_authenticated(self, client):
        email = unique_email("me")
        tokens = register_and_login(client, email)
        resp = client.get("/api/v1/auth/me", headers=auth_headers(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == email

    def test_me_unauthenticated(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer this.is.not.valid"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------

class TestRefresh:
    def test_refresh_success(self, client):
        email = unique_email("refresh")
        tokens = register_and_login(client, email)
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert resp.status_code == 200
        new_tokens = resp.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["token_type"] == "bearer"

    def test_refresh_with_access_token_fails(self, client):
        email = unique_email("refreshfail")
        tokens = register_and_login(client, email)
        resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["access_token"]},  # wrong token type
        )
        assert resp.status_code == 401
