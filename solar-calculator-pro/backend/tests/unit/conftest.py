"""
Task 21: Backend Unit Tests - Test Fixtures and Configuration
=============================================================
Shared fixtures and configuration for unit tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from decimal import Decimal


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock database connection."""
    db = Mock()
    db.execute = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    db.close = Mock()
    return db


@pytest.fixture
def mock_async_db():
    """Mock async database connection."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    return db


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def test_user():
    """Standard test user."""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now()
    }


@pytest.fixture
def admin_user():
    """Admin test user."""
    return {
        "id": 2,
        "email": "admin@example.com",
        "username": "admin",
        "is_active": True,
        "is_admin": True,
        "created_at": datetime.now()
    }


# ============================================================================
# Project Fixtures
# ============================================================================

@pytest.fixture
def test_project():
    """Standard test project."""
    return {
        "id": 1,
        "user_id": 1,
        "name": "Test Solar Project",
        "customer_name": "Max Mustermann",
        "address": "Musterstraße 123, 12345 Berlin",
        "roof_area": 50.0,
        "roof_type": "gable",
        "roof_angle": 30,
        "orientation": "south",
        "status": "draft",
        "created_at": datetime.now()
    }


# ============================================================================
# Product Fixtures
# ============================================================================

@pytest.fixture
def test_pv_module():
    """Test PV module product."""
    return {
        "id": 1,
        "name": "Solar Module 400W",
        "category": "pv_module",
        "manufacturer": "SolarTech",
        "model": "ST-400M",
        "power_wp": 400,
        "efficiency": 0.21,
        "price": Decimal("250.00"),
        "is_active": True
    }


@pytest.fixture
def test_inverter():
    """Test inverter product."""
    return {
        "id": 2,
        "name": "Hybrid Inverter 10kW",
        "category": "inverter",
        "manufacturer": "InverterCo",
        "model": "HI-10K",
        "power_kw": 10,
        "price": Decimal("2500.00"),
        "is_active": True
    }


@pytest.fixture
def test_battery():
    """Test battery product."""
    return {
        "id": 3,
        "name": "Battery Storage 10.2kWh",
        "category": "battery",
        "manufacturer": "BYD",
        "model": "HVS 10.2",
        "capacity_kwh": 10.2,
        "price": Decimal("5500.00"),
        "is_active": True
    }


# ============================================================================
# Price Matrix Fixtures
# ============================================================================

@pytest.fixture
def test_price_matrix():
    """Test price matrix."""
    return {
        "id": 1,
        "name": "Standard Price Matrix 2025",
        "is_active": True,
        "headers": ["kein Speicher", "BYD 5.1", "BYD 7.7", "BYD 10.2"],
        "rows": {
            10: [8500, 11500, 13000, 14500],
            12: [9500, 12500, 14000, 15500],
            14: [10500, 13500, 15000, 16500],
            16: [11500, 14500, 16000, 17500],
            18: [12500, 15500, 17000, 18500],
            20: [13500, 16500, 18000, 19500],
        }
    }


# ============================================================================
# Calculation Fixtures
# ============================================================================

@pytest.fixture
def solar_calculation_input():
    """Standard solar calculation input."""
    return {
        "roof_area": 50.0,
        "roof_type": "gable",
        "roof_angle": 30,
        "orientation": "south",
        "location": {
            "latitude": 51.1657,
            "longitude": 10.4515,
            "city": "Berlin"
        },
        "annual_consumption_kwh": 4500,
        "module_type": "monocrystalline",
        "module_power_wp": 400,
        "electricity_price_kwh": 0.35
    }


@pytest.fixture
def heatpump_calculation_input():
    """Standard heat pump calculation input."""
    return {
        "building_type": "single_family",
        "living_area_m2": 150,
        "construction_year": 2000,
        "insulation_level": "medium",
        "current_heating": "gas",
        "annual_heating_kwh": 15000,
        "location": {
            "climate_zone": "moderate"
        }
    }


# ============================================================================
# API Fixtures
# ============================================================================

@pytest.fixture
def auth_headers():
    """Authentication headers for API requests."""
    return {
        "Authorization": "Bearer test_token_123",
        "Content-Type": "application/json"
    }


@pytest.fixture
def api_client():
    """Mock API client."""
    client = Mock()
    client.get = Mock()
    client.post = Mock()
    client.put = Mock()
    client.delete = Mock()
    return client


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def app_config():
    """Application configuration for testing."""
    return {
        "DEBUG": True,
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30
    }


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_token(user_id: int, is_admin: bool = False) -> str:
    """Create a test JWT token."""
    return f"test_token_user_{user_id}_admin_{is_admin}"


def create_test_session(user_id: int) -> dict:
    """Create a test session."""
    return {
        "session_id": f"session_{user_id}_{datetime.now().timestamp()}",
        "user_id": user_id,
        "created_at": datetime.now(),
        "is_valid": True
    }
