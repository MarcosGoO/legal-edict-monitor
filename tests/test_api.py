"""
Tests for API Endpoints.

Tests the FastAPI endpoints using TestClient.
All protected endpoints require an authenticated user — the `auth_client`
fixture handles registration and token injection automatically.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Unauthenticated test client."""
    return TestClient(app)


@pytest.fixture
def auth_client():
    """
    Test client pre-authenticated as an editor user.

    Returns a (TestClient, headers) tuple. Uses a unique email per fixture
    call so parallel/repeated test runs don't collide on the in-memory store.
    """
    tc = TestClient(app)
    email = f"apitest_{uuid.uuid4().hex[:8]}@example.com"

    # Register + login
    tc.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "testpassword1", "full_name": "API Tester"},
    )
    resp = tc.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "testpassword1"},
    )
    tokens = resp.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    return tc, headers


class TestHealthEndpoints:
    """Tests for health check endpoints — public, no auth required."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data

    def test_readiness_check(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestDocumentEndpoints:
    """Tests for document processing endpoints (authentication required)."""

    def test_get_entity_types_unauthenticated(self, client):
        """Protected endpoint — must return 401 without token."""
        response = client.get("/api/v1/documents/entity-types")
        assert response.status_code == 401

    def test_get_entity_types(self, auth_client):
        tc, headers = auth_client
        response = tc.get("/api/v1/documents/entity-types", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "entity_types" in data
        types = [t["type"] for t in data["entity_types"]]
        assert "radicado" in types
        assert "nit" in types
        assert "cedula" in types
        assert "nombre" in types

    def test_parse_text(self, auth_client):
        tc, headers = auth_client
        payload = {
            "text": (
                "El radicado 2023-00123-45-67-890-12 corresponde al proceso "
                "seguido por JOSÉ MARÍA RODRÍGUEZ con CC 12345678."
            )
        }
        response = tc.post("/api/v1/documents/parse-text", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] is not None
        assert data["result"]["entity_count"] >= 1

    def test_parse_text_unauthenticated(self, client):
        payload = {"text": "El radicado 2023-00123-45-67-890-12 corresponde al proceso."}
        response = client.post("/api/v1/documents/parse-text", json=payload)
        assert response.status_code == 401

    def test_parse_text_empty(self, auth_client):
        tc, headers = auth_client
        response = tc.post("/api/v1/documents/parse-text", json={"text": ""}, headers=headers)
        assert response.status_code == 422

    def test_process_document_no_file(self, auth_client):
        tc, headers = auth_client
        response = tc.post("/api/v1/documents/process", headers=headers)
        assert response.status_code == 422


class TestClientEndpoints:
    """Tests for client management endpoints (authentication required)."""

    def test_list_clients_unauthenticated(self, client):
        response = client.get("/api/v1/clients")
        assert response.status_code == 401

    def test_list_clients(self, auth_client):
        tc, headers = auth_client
        response = tc.get("/api/v1/clients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "clients" in data
        assert "total" in data
        assert "page" in data

    def test_create_client(self, auth_client):
        tc, headers = auth_client
        payload = {
            "full_name": "JOSÉ MARÍA RODRÍGUEZ GARCÍA",
            "document_type": "CC",
            "document_number": "12345678",
        }
        response = tc.post("/api/v1/clients", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == payload["full_name"]
        assert data["document_type"] == payload["document_type"]

    def test_create_client_unauthenticated(self, client):
        payload = {"full_name": "Test Client", "document_type": "CC"}
        response = client.post("/api/v1/clients", json=payload)
        assert response.status_code == 401

    def test_get_client_not_found(self, auth_client):
        tc, headers = auth_client
        response = tc.get("/api/v1/clients/non-existent-id", headers=headers)
        assert response.status_code == 404
