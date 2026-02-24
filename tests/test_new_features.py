"""
Tests for New Features.

Tests for:
- Input validation helpers
- Request logging middleware
- Database connectivity check
- Redis connectivity check
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.parser.input_validation import (
    validate_colombian_cedula,
    validate_colombian_nit,
    validate_colombian_radicado,
    validate_document_type,
    validate_document_number,
)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestInputValidationCedula:
    """Tests for Cédula validation."""
    
    def test_validate_valid_cedula(self):
        """Test valid cédula validation."""
        result = validate_colombian_cedula("12345678")
        assert result == "12345678"
    
    def test_validate_cedula_with_formatting(self):
        """Test cédula with formatting characters."""
        result = validate_colombian_cedula("CC 12.345.678")
        assert result == "12345678"
    
    def test_validate_cedula_six_digits(self):
        """Test minimum length cédula (6 digits)."""
        result = validate_colombian_cedula("123456")
        assert result == "123456"
    
    def test_validate_cedula_twelve_digits(self):
        """Test maximum length cédula (12 digits)."""
        result = validate_colombian_cedula("123456789012")
        assert result == "123456789012"
    
    def test_validate_cedula_too_short(self):
        """Test cédula with too few digits."""
        with pytest.raises(ValueError) as exc_info:
            validate_colombian_cedula("12345")
        assert "6-12 digits" in str(exc_info.value)
    
    def test_validate_cedula_too_long(self):
        """Test cédula with too many digits."""
        with pytest.raises(ValueError) as exc_info:
            validate_colombian_cedula("1234567890123")
        assert "6-12 digits" in str(exc_info.value)
    
    def test_validate_empty_cedula(self):
        """Test empty cédula returns as-is."""
        result = validate_colombian_cedula("")
        assert result == ""


class TestInputValidationNit:
    """Tests for NIT validation."""
    
    def test_validate_valid_nit(self):
        """Test valid NIT validation."""
        # NIT 900123456-8 is valid (check digit calculation)
        result = validate_colombian_nit("9001234568")
        assert result == "900123456-8"
    
    def test_validate_nit_without_hyphen(self):
        """Test NIT without hyphen."""
        result = validate_colombian_nit("9001234568")
        assert result == "900123456-8"
    
    def test_validate_nit_wrong_check_digit(self):
        """Test NIT with wrong check digit."""
        with pytest.raises(ValueError) as exc_info:
            validate_colombian_nit("9001234567")
        assert "check digit" in str(exc_info.value).lower()
    
    def test_validate_nit_wrong_length(self):
        """Test NIT with wrong length."""
        with pytest.raises(ValueError) as exc_info:
            validate_colombian_nit("90012345")
        assert "10 digits" in str(exc_info.value)
    
    def test_validate_empty_nit(self):
        """Test empty NIT returns as-is."""
        result = validate_colombian_nit("")
        assert result == ""


class TestInputValidationRadicado:
    """Tests for Radicado validation."""
    
    def test_validate_valid_radicado(self):
        """Test valid radicado validation."""
        # 23 digits radicado
        result = validate_colombian_radicado("20230012345678901234567")
        # Should normalize to standard format
        assert "2023" in result
    
    def test_validate_radicado_digits_only(self):
        """Test radicado with digits only."""
        result = validate_colombian_radicado("20230012345678901234567")
        assert "2023" in result
    
    def test_validate_radicado_invalid_year(self):
        """Test radicado with invalid year."""
        with pytest.raises(ValueError) as exc_info:
            validate_colombian_radicado("19990012345678901234567")
        assert "year" in str(exc_info.value).lower()
    
    def test_validate_radicado_wrong_length(self):
        """Test radicado with wrong length."""
        with pytest.raises(ValueError) as exc_info:
            validate_colombian_radicado("2023001234567")
        assert "23 digits" in str(exc_info.value)
    
    def test_validate_empty_radicado(self):
        """Test empty radicado returns as-is."""
        result = validate_colombian_radicado("")
        assert result == ""


class TestInputValidationDocumentType:
    """Tests for document type validation."""
    
    def test_validate_valid_types(self):
        """Test all valid document types."""
        for doc_type in ["CC", "CE", "NIT", "PP", "TI"]:
            result = validate_document_type(doc_type)
            assert result == doc_type
    
    def test_validate_lowercase_type(self):
        """Test lowercase document type is normalized."""
        result = validate_document_type("cc")
        assert result == "CC"
    
    def test_validate_invalid_type(self):
        """Test invalid document type."""
        with pytest.raises(ValueError) as exc_info:
            validate_document_type("XYZ")
        assert "Invalid document type" in str(exc_info.value)


class TestInputValidationDocumentNumber:
    """Tests for document number validation by type."""
    
    def test_validate_cc_document(self):
        """Test CC document number validation."""
        result = validate_document_number("CC", "12345678")
        assert result == "12345678"
    
    def test_validate_nit_document(self):
        """Test NIT document number validation."""
        result = validate_document_number("NIT", "9001234568")
        assert result == "900123456-8"
    
    def test_validate_ce_document(self):
        """Test CE document number validation."""
        result = validate_document_number("CE", "1234567890")
        assert result == "1234567890"


class TestRequestLoggingMiddleware:
    """Tests for request logging middleware."""
    
    def test_request_id_in_response(self, client):
        """Test that request ID is added to response headers."""
        response = client.get("/health")
        
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0
    
    def test_request_id_preserved_if_provided(self, client):
        """Test that provided request ID is preserved."""
        custom_id = "custom-request-id-12345"
        response = client.get(
            "/health",
            headers={"X-Request-ID": custom_id}
        )
        
        assert response.headers["X-Request-ID"] == custom_id
    
    def test_health_endpoint_still_works(self, client):
        """Test that health endpoint still works with middleware."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestDatabaseHealthCheck:
    """Tests for database connectivity check."""
    
    @pytest.mark.asyncio
    async def test_check_database_connection_success(self):
        """Test successful database connection check."""
        from app.database import check_database_connection
        
        with patch("app.database.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.execute = AsyncMock()
            mock_engine.connect = MagicMock(return_value=mock_conn)
            mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_engine.connect.return_value.__aexit__ = AsyncMock()
            
            result = await check_database_connection()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_database_connection_failure(self):
        """Test failed database connection check."""
        from app.database import check_database_connection
        
        with patch("app.database.engine") as mock_engine:
            mock_engine.connect = MagicMock(side_effect=Exception("Connection failed"))
            
            result = await check_database_connection()
            assert result is False


class TestRedisHealthCheck:
    """Tests for Redis connectivity check."""
    
    @pytest.mark.asyncio
    async def test_check_redis_connection_success(self):
        """Test successful Redis connection check."""
        from app.redis_client import check_redis_connection
        
        with patch("app.redis_client.get_redis_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(return_value=True)
            mock_get_client.return_value = mock_client
            
            result = await check_redis_connection()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_redis_connection_failure(self):
        """Test failed Redis connection check."""
        from app.redis_client import check_redis_connection
        
        with patch("app.redis_client.get_redis_client") as mock_get_client:
            from redis.exceptions import RedisError
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(side_effect=RedisError("Connection refused"))
            mock_get_client.return_value = mock_client
            
            result = await check_redis_connection()
            assert result is False


class TestReadinessEndpoint:
    """Tests for the enhanced readiness endpoint."""
    
    def test_readiness_returns_checks(self, client):
        """Test that readiness endpoint returns health checks."""
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]
    
    def test_readiness_status_values(self, client):
        """Test that readiness status can be ready or not_ready."""
        response = client.get("/ready")
        
        data = response.json()
        assert data["status"] in ["ready", "not_ready"]
        
        # Check values should be ok or error
        for check_name, check_value in data["checks"].items():
            assert check_value in ["ok", "error"]
