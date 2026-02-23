"""
Pytest Configuration and Fixtures.

Provides common fixtures for testing.
"""

import os
import pytest
from typing import Generator

# Set test environment before importing app
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32ch"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-testing-32ch"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"


@pytest.fixture
def sample_legal_text() -> str:
    """
    Sample Colombian legal document text for testing.
    """
    return """
    REPÚBLICA DE COLOMBIA
    RAMA JUDICIAL DEL PODER PÚBLICO
    
    JUZGADO PRIMERO CIVIL DEL CIRCUITO DE BOGOTÁ
    
    EDICTO
    
    El Juzgado Primero Civil del Circuito de Bogotá, por medio del presente edicto,
    notifica a:
    
    JOSÉ MARÍA RODRÍGUEZ GARCÍA
    Identificado con Cédula de Ciudadanía No. 12345678
    
    Y a la empresa:
    
    EMPRESA DE TRANSPORTE DEL SUR S.A.S.
    NIT: 900123456-7
    
    Sobre el proceso judicial con Radicado No. 2023-00123-45-67-890-12
    
    Se les notifica que se ha admitido la demanda presentada en su contra por
    MARÍA FERNANDA LÓPEZ PÉREZ, identificada con CC 87654321.
    
    El proceso corresponde a un juicio ejecutivo singular por obligación de pagar
    la suma de $50.000.000 COP.
    
    Se concede un término de cinco (5) días para presentar respuesta a la demanda.
    
    Dado en Bogotá D.C., a los quince (15) días del mes de marzo de dos mil veintitrés.
    
    El Juez,
    CARLOS ANDRÉS PÉREZ MARTÍNEZ
    """


@pytest.fixture
def sample_radicado() -> str:
    """Sample radicado for testing."""
    return "2023-00123-45-67-890-12"


@pytest.fixture
def sample_nit() -> str:
    """Sample NIT for testing."""
    return "900123456-7"


@pytest.fixture
def sample_cedula() -> str:
    """Sample cédula for testing."""
    return "12345678"
