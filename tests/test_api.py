"""
Tests for API Endpoints.

Tests the FastAPI endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
    
    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestDocumentEndpoints:
    """Tests for document processing endpoints."""
    
    def test_get_entity_types(self, client):
        """Test getting supported entity types."""
        response = client.get("/api/v1/documents/entity-types")
        
        assert response.status_code == 200
        data = response.json()
        assert "entity_types" in data
        
        # Check that expected types are present
        types = [t["type"] for t in data["entity_types"]]
        assert "radicado" in types
        assert "nit" in types
        assert "cedula" in types
        assert "nombre" in types
    
    def test_parse_text(self, client):
        """Test text parsing endpoint."""
        payload = {
            "text": (
                "El radicado 2023-00123-45-67-890-12 corresponde al proceso "
                "seguido por JOSÉ MARÍA RODRÍGUEZ con CC 12345678."
            )
        }
        
        response = client.post(
            "/api/v1/documents/parse-text",
            json=payload,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] is not None
        assert data["result"]["entity_count"] >= 1
    
    def test_parse_text_empty(self, client):
        """Test parsing empty text."""
        payload = {"text": ""}
        
        response = client.post(
            "/api/v1/documents/parse-text",
            json=payload,
        )
        
        # Should fail validation
        assert response.status_code == 422
    
    def test_process_document_no_file(self, client):
        """Test document processing without file."""
        response = client.post("/api/v1/documents/process")
        
        # Should fail - no file provided
        assert response.status_code == 422


class TestClientEndpoints:
    """Tests for client management endpoints."""
    
    def test_list_clients(self, client):
        """Test listing clients."""
        response = client.get("/api/v1/clients")
        
        assert response.status_code == 200
        data = response.json()
        assert "clients" in data
        assert "total" in data
        assert "page" in data
    
    def test_create_client(self, client):
        """Test creating a client."""
        payload = {
            "full_name": "JOSÉ MARÍA RODRÍGUEZ GARCÍA",
            "document_type": "CC",
            "document_number": "12345678",
        }
        
        response = client.post(
            "/api/v1/clients",
            json=payload,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == payload["full_name"]
        assert data["document_type"] == payload["document_type"]
    
    def test_get_client_not_found(self, client):
        """Test getting non-existent client."""
        response = client.get("/api/v1/clients/non-existent-id")
        
        assert response.status_code == 404
