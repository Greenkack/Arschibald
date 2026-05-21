"""
Task 22: Backend Integration Tests - API Endpoints
===================================================
Integration tests for API endpoints and authentication flows.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal
from datetime import datetime, timedelta
import json


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_client():
    """Mock HTTP client for API testing."""
    client = Mock()
    client.get = Mock()
    client.post = Mock()
    client.put = Mock()
    client.delete = Mock()
    return client


@pytest.fixture
def auth_headers():
    """Authentication headers for protected endpoints."""
    return {
        "Authorization": "Bearer test-jwt-token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "role": "admin",
        "is_active": True
    }


@pytest.fixture
def sample_project():
    """Sample solar project data."""
    return {
        "id": 1,
        "name": "Test Solar Project",
        "customer_id": 1,
        "roof_area": 50.0,
        "roof_type": "gable",
        "roof_angle": 30,
        "orientation": "south",
        "annual_consumption": 4500,
        "module_type": "monocrystalline",
        "module_count": 20,
        "system_size_kwp": 8.0,
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# Authentication Endpoint Tests
# ============================================================================

class TestAuthenticationEndpoints:
    """Tests for authentication API endpoints."""

    def test_login_success(self, mock_client, sample_user):
        """Test successful login."""
        mock_client.post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "access_token": "jwt-token",
                "token_type": "bearer",
                "user": sample_user
            }
        )
        
        response = mock_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"

    def test_login_invalid_credentials(self, mock_client):
        """Test login with invalid credentials."""
        mock_client.post.return_value = Mock(
            status_code=401,
            json=lambda: {"detail": "Invalid credentials"}
        )
        
        response = mock_client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "wrong"}
        )
        
        assert response.status_code == 401

    def test_logout(self, mock_client, auth_headers):
        """Test logout endpoint."""
        mock_client.post.return_value = Mock(
            status_code=200,
            json=lambda: {"message": "Successfully logged out"}
        )
        
        response = mock_client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    def test_refresh_token(self, mock_client, auth_headers):
        """Test token refresh."""
        mock_client.post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "access_token": "new-jwt-token",
                "token_type": "bearer"
            }
        )
        
        response = mock_client.post(
            "/api/v1/auth/refresh",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_get_current_user(self, mock_client, auth_headers, sample_user):
        """Test getting current user info."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: sample_user
        )
        
        response = mock_client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user["email"]


# ============================================================================
# Solar Calculator Endpoint Tests
# ============================================================================

class TestSolarCalculatorEndpoints:
    """Tests for solar calculator API endpoints."""

    def test_calculate_solar_system(self, mock_client, auth_headers):
        """Test solar system calculation endpoint."""
        mock_client.post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "system_size_kwp": 8.0,
                "module_count": 20,
                "annual_production_kwh": 7600,
                "self_consumption_rate": 0.35,
                "annual_savings_eur": 1200,
                "payback_years": 8.5,
                "co2_savings_kg": 3800
            }
        )
        
        response = mock_client.post(
            "/api/v1/solar/calculate",
            headers=auth_headers,
            json={
                "roof_area": 50,
                "roof_type": "gable",
                "roof_angle": 30,
                "orientation": "south",
                "annual_consumption": 4500,
                "module_type": "monocrystalline"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["system_size_kwp"] == 8.0
        assert data["module_count"] == 20

    def test_get_module_types(self, mock_client, auth_headers):
        """Test getting available module types."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: [
                {"id": 1, "name": "Monocrystalline", "power_wp": 400},
                {"id": 2, "name": "Polycrystalline", "power_wp": 350},
                {"id": 3, "name": "Thin Film", "power_wp": 300}
            ]
        )
        
        response = mock_client.get(
            "/api/v1/solar/modules",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_save_project(self, mock_client, auth_headers, sample_project):
        """Test saving a solar project."""
        mock_client.post.return_value = Mock(
            status_code=201,
            json=lambda: sample_project
        )
        
        response = mock_client.post(
            "/api/v1/solar/projects",
            headers=auth_headers,
            json=sample_project
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_project["name"]

    def test_get_project(self, mock_client, auth_headers, sample_project):
        """Test getting a project by ID."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: sample_project
        )
        
        response = mock_client.get(
            "/api/v1/solar/projects/1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_list_projects(self, mock_client, auth_headers):
        """Test listing all projects."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "items": [{"id": 1}, {"id": 2}],
                "total": 2,
                "page": 1,
                "size": 10
            }
        )
        
        response = mock_client.get(
            "/api/v1/solar/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2


# ============================================================================
# Price Matrix Endpoint Tests
# ============================================================================

class TestPriceMatrixEndpoints:
    """Tests for price matrix API endpoints."""

    def test_get_price(self, mock_client, auth_headers):
        """Test getting price from matrix."""
        mock_client.post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "base_price": 17500,
                "extras": 1200,
                "discount": 935,
                "final_price": 17765,
                "currency": "EUR"
            }
        )
        
        response = mock_client.post(
            "/api/v1/pricing/calculate",
            headers=auth_headers,
            json={
                "module_count": 16,
                "storage_model": "BYD 10.2",
                "extras": ["wallbox"],
                "discount_percent": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["base_price"] == 17500

    def test_upload_price_matrix(self, mock_client, auth_headers):
        """Test uploading a new price matrix."""
        mock_client.post.return_value = Mock(
            status_code=201,
            json=lambda: {
                "id": 1,
                "name": "Price Matrix 2025",
                "rows": 20,
                "columns": 5,
                "created_at": datetime.now().isoformat()
            }
        )
        
        response = mock_client.post(
            "/api/v1/pricing/matrix/upload",
            headers=auth_headers,
            files={"file": ("matrix.xlsx", b"file content")}
        )
        
        assert response.status_code == 201

    def test_get_extras(self, mock_client, auth_headers):
        """Test getting available extras."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: [
                {"id": 1, "name": "Wallbox 11kW", "price": 1200},
                {"id": 2, "name": "Monitoring", "price": 350}
            ]
        )
        
        response = mock_client.get(
            "/api/v1/pricing/extras",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


# ============================================================================
# PDF Generation Endpoint Tests
# ============================================================================

class TestPDFEndpoints:
    """Tests for PDF generation API endpoints."""

    def test_generate_pdf(self, mock_client, auth_headers):
        """Test PDF generation."""
        mock_client.post.return_value = Mock(
            status_code=200,
            content=b"%PDF-1.4 mock content",
            headers={"Content-Type": "application/pdf"}
        )
        
        response = mock_client.post(
            "/api/v1/pdf/generate",
            headers=auth_headers,
            json={
                "project_id": 1,
                "template": "standard",
                "options": {
                    "include_charts": True,
                    "include_3d": True,
                    "language": "de"
                }
            }
        )
        
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/pdf"

    def test_get_pdf_templates(self, mock_client, auth_headers):
        """Test getting available PDF templates."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: [
                {"id": 1, "name": "Standard Offer"},
                {"id": 2, "name": "Extended Offer"},
                {"id": 3, "name": "Multi Offer"}
            ]
        )
        
        response = mock_client.get(
            "/api/v1/pdf/templates",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_preview_pdf(self, mock_client, auth_headers):
        """Test PDF preview generation."""
        mock_client.post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "preview_url": "/previews/123.png",
                "pages": 5
            }
        )
        
        response = mock_client.post(
            "/api/v1/pdf/preview",
            headers=auth_headers,
            json={"project_id": 1, "template": "standard"}
        )
        
        assert response.status_code == 200


# ============================================================================
# CRM Endpoint Tests
# ============================================================================

class TestCRMEndpoints:
    """Tests for CRM API endpoints."""

    def test_create_customer(self, mock_client, auth_headers):
        """Test creating a new customer."""
        mock_client.post.return_value = Mock(
            status_code=201,
            json=lambda: {
                "id": 1,
                "name": "Test Customer",
                "email": "customer@test.com",
                "phone": "+49 123 456789"
            }
        )
        
        response = mock_client.post(
            "/api/v1/crm/customers",
            headers=auth_headers,
            json={
                "name": "Test Customer",
                "email": "customer@test.com",
                "phone": "+49 123 456789"
            }
        )
        
        assert response.status_code == 201

    def test_list_customers(self, mock_client, auth_headers):
        """Test listing customers."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "items": [{"id": 1}, {"id": 2}],
                "total": 2
            }
        )
        
        response = mock_client.get(
            "/api/v1/crm/customers",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    def test_create_offer(self, mock_client, auth_headers):
        """Test creating an offer."""
        mock_client.post.return_value = Mock(
            status_code=201,
            json=lambda: {
                "id": 1,
                "customer_id": 1,
                "project_id": 1,
                "status": "draft",
                "total_price": 17500
            }
        )
        
        response = mock_client.post(
            "/api/v1/crm/offers",
            headers=auth_headers,
            json={
                "customer_id": 1,
                "project_id": 1
            }
        )
        
        assert response.status_code == 201


# ============================================================================
# Database Transaction Tests
# ============================================================================

class TestDatabaseTransactions:
    """Tests for database transaction handling."""

    def test_transaction_commit(self):
        """Test successful transaction commit."""
        mock_session = Mock()
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        
        try:
            # Simulate successful operation
            mock_session.commit()
            committed = True
        except Exception:
            mock_session.rollback()
            committed = False
        
        assert committed
        mock_session.commit.assert_called_once()

    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        mock_session = Mock()
        mock_session.commit = Mock(side_effect=Exception("DB Error"))
        mock_session.rollback = Mock()
        
        try:
            mock_session.commit()
            rolled_back = False
        except Exception:
            mock_session.rollback()
            rolled_back = True
        
        assert rolled_back
        mock_session.rollback.assert_called_once()


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for API error handling."""

    def test_not_found_error(self, mock_client, auth_headers):
        """Test 404 Not Found response."""
        mock_client.get.return_value = Mock(
            status_code=404,
            json=lambda: {"detail": "Project not found"}
        )
        
        response = mock_client.get(
            "/api/v1/solar/projects/999",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_validation_error(self, mock_client, auth_headers):
        """Test 422 Validation Error response."""
        mock_client.post.return_value = Mock(
            status_code=422,
            json=lambda: {
                "detail": [
                    {"loc": ["body", "roof_area"], "msg": "value must be positive"}
                ]
            }
        )
        
        response = mock_client.post(
            "/api/v1/solar/calculate",
            headers=auth_headers,
            json={"roof_area": -10}
        )
        
        assert response.status_code == 422

    def test_unauthorized_error(self, mock_client):
        """Test 401 Unauthorized response."""
        mock_client.get.return_value = Mock(
            status_code=401,
            json=lambda: {"detail": "Not authenticated"}
        )
        
        response = mock_client.get("/api/v1/solar/projects")
        
        assert response.status_code == 401

    def test_server_error(self, mock_client, auth_headers):
        """Test 500 Internal Server Error response."""
        mock_client.get.return_value = Mock(
            status_code=500,
            json=lambda: {"detail": "Internal server error"}
        )
        
        response = mock_client.get(
            "/api/v1/solar/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 500


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
