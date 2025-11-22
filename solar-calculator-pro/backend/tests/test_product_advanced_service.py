"""
Tests for Product Advanced Service

Tests for advanced product management features.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.services.product_advanced_service import (
    ProductAdvancedService,
    ProductLifecycleStatus,
    ProductAvailabilityStatus,
    get_product_advanced_service
)


@pytest.fixture
def mock_product_db():
    """Mock product_db module"""
    with patch('backend.services.product_advanced_service.product_db') as mock:
        mock.DB_AVAILABLE = True
        mock.get_product_by_id = Mock()
        mock.update_product = Mock()
        mock.list_products = Mock()
        mock.get_pricing_history = Mock()
        mock.calculate_enhanced_product_pricing = Mock()
        yield mock


@pytest.fixture
def service(mock_product_db):
    """Create ProductAdvancedService instance"""
    service = ProductAdvancedService()
    service._product_db_module = mock_product_db
    service._set_initialized(True)
    return service


@pytest.fixture
def sample_product():
    """Sample product data"""
    return {
        "id": 1,
        "model_name": "Test Module 400W",
        "brand": "TestBrand",
        "category": "Solar Modules",
        "power_wp": 400,
        "efficiency": 20.5,
        "price_euro": 250.0,
        "lifecycle_status": "active",
        "version": 1,
        "stock_quantity": 100,
        "reorder_point": 20,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }


# ==================== Lifecycle Management Tests ====================

def test_get_product_lifecycle(service, mock_product_db, sample_product):
    """Test getting product lifecycle"""
    mock_product_db.get_product_by_id.return_value = sample_product
    
    lifecycle = service.get_product_lifecycle(1)
    
    assert lifecycle["product_id"] == 1
    assert lifecycle["status"] == "active"
    assert lifecycle["version"] == 1
    assert lifecycle["is_active"] is True
    mock_product_db.get_product_by_id.assert_called_once_with(1)


def test_get_product_lifecycle_not_found(service, mock_product_db):
    """Test getting lifecycle for non-existent product"""
    mock_product_db.get_product_by_id.return_value = None
    
    with pytest.raises(ValueError, match="Product 999 not found"):
        service.get_product_lifecycle(999)


def test_update_product_lifecycle(service, mock_product_db, sample_product):
    """Test updating product lifecycle"""
    mock_product_db.get_product_by_id.return_value = sample_product
    mock_product_db.update_product.return_value = True
    
    lifecycle = service.update_product_lifecycle(1, "discontinued", "End of life")
    
    assert lifecycle["status"] == "active"  # Returns current after update
    mock_product_db.update_product.assert_called_once()
    update_call = mock_product_db.update_product.call_args[0]
    assert update_call[0] == 1
    assert update_call[1]["lifecycle_status"] == "discontinued"


def test_update_product_lifecycle_invalid_status(service, mock_product_db, sample_product):
    """Test updating with invalid status"""
    mock_product_db.get_product_by_id.return_value = sample_product
    
    with pytest.raises(ValueError, match="Invalid lifecycle status"):
        service.update_product_lifecycle(1, "invalid_status")


# ==================== Versioning Tests ====================

def test_create_product_version(service, mock_product_db, sample_product):
    """Test creating product version"""
    mock_product_db.get_product_by_id.return_value = sample_product
    mock_product_db.update_product.return_value = True
    
    changes = {"price_euro": 260.0, "efficiency": 21.0}
    version = service.create_product_version(1, changes, "Price and efficiency update")
    
    assert version["product_id"] == 1
    assert version["version"] == 2
    assert version["previous_version"] == 1
    assert "changes" in version
    mock_product_db.update_product.assert_called_once()


def test_get_product_version_history(service, mock_product_db, sample_product):
    """Test getting version history"""
    mock_product_db.get_product_by_id.return_value = sample_product
    
    versions = service.get_product_version_history(1, limit=10)
    
    assert len(versions) == 1  # Mock returns 1 version
    assert versions[0]["version"] == 1


# ==================== Comparison Tests ====================

def test_compare_products(service, mock_product_db):
    """Test product comparison"""
    product1 = {
        "id": 1,
        "model_name": "Module A",
        "brand": "Brand A",
        "category": "Solar Modules",
        "power_wp": 400,
        "efficiency": 20.5,
        "price_euro": 250.0
    }
    product2 = {
        "id": 2,
        "model_name": "Module B",
        "brand": "Brand B",
        "category": "Solar Modules",
        "power_wp": 450,
        "efficiency": 21.0,
        "price_euro": 280.0
    }
    
    mock_product_db.get_product_by_id.side_effect = [product1, product2]
    
    comparison = service.compare_products([1, 2], ["power_wp", "efficiency", "price_euro"])
    
    assert comparison["summary"]["total_products"] == 2
    assert "power_wp" in comparison["attributes"]
    assert comparison["attributes"]["power_wp"]["has_differences"] is True


def test_compare_products_insufficient_products(service):
    """Test comparison with insufficient products"""
    with pytest.raises(ValueError, match="At least 2 products required"):
        service.compare_products([1])


# ==================== Recommendation Tests ====================

def test_get_product_recommendations(service, mock_product_db):
    """Test getting product recommendations"""
    products = [
        {
            "id": 1,
            "model_name": "Module 400W",
            "power_wp": 400,
            "efficiency": 20.5,
            "price_euro": 250.0,
            "lifecycle_status": "active"
        },
        {
            "id": 2,
            "model_name": "Module 450W",
            "power_wp": 450,
            "efficiency": 21.0,
            "price_euro": 280.0,
            "lifecycle_status": "active"
        }
    ]
    mock_product_db.list_products.return_value = products
    
    context = {
        "required_power": 420,
        "budget": 270.0
    }
    
    recommendations = service.get_product_recommendations(context, limit=5)
    
    assert len(recommendations) <= 5
    assert all("recommendation_score" in r for r in recommendations)
    assert all("recommendation_reasons" in r for r in recommendations)


def test_get_product_recommendations_no_products(service, mock_product_db):
    """Test recommendations with no products"""
    mock_product_db.list_products.return_value = []
    
    recommendations = service.get_product_recommendations({}, limit=5)
    
    assert recommendations == []


# ==================== Availability Tests ====================

def test_get_product_availability(service, mock_product_db, sample_product):
    """Test getting product availability"""
    mock_product_db.get_product_by_id.return_value = sample_product
    
    availability = service.get_product_availability(1)
    
    assert availability["product_id"] == 1
    assert availability["status"] == "in_stock"
    assert availability["stock_quantity"] == 100
    assert availability["is_available"] is True


def test_get_product_availability_low_stock(service, mock_product_db, sample_product):
    """Test availability with low stock"""
    sample_product["stock_quantity"] = 15
    mock_product_db.get_product_by_id.return_value = sample_product
    
    availability = service.get_product_availability(1)
    
    assert availability["status"] == "low_stock"


def test_get_product_availability_out_of_stock(service, mock_product_db, sample_product):
    """Test availability when out of stock"""
    sample_product["stock_quantity"] = 0
    mock_product_db.get_product_by_id.return_value = sample_product
    
    availability = service.get_product_availability(1)
    
    assert availability["status"] == "out_of_stock"
    assert availability["is_available"] is False


def test_update_product_availability(service, mock_product_db, sample_product):
    """Test updating product availability"""
    mock_product_db.get_product_by_id.return_value = sample_product
    mock_product_db.update_product.return_value = True
    
    availability = service.update_product_availability(
        1,
        stock_quantity=50,
        reorder_point=15
    )
    
    mock_product_db.update_product.assert_called_once()
    update_data = mock_product_db.update_product.call_args[0][1]
    assert update_data["stock_quantity"] == 50
    assert update_data["reorder_point"] == 15


# ==================== Supplier Tests ====================

def test_get_product_suppliers(service, mock_product_db, sample_product):
    """Test getting product suppliers"""
    mock_product_db.get_product_by_id.return_value = sample_product
    
    suppliers = service.get_product_suppliers(1)
    
    assert len(suppliers) > 0
    assert suppliers[0]["product_id"] == 1
    assert "supplier_name" in suppliers[0]


def test_add_product_supplier(service, mock_product_db, sample_product):
    """Test adding product supplier"""
    mock_product_db.get_product_by_id.return_value = sample_product
    
    supplier_data = {
        "supplier_name": "Test Supplier",
        "unit_price": 200.0,
        "minimum_order_quantity": 10
    }
    
    supplier = service.add_product_supplier(1, supplier_data)
    
    assert supplier["supplier_name"] == "Test Supplier"
    assert supplier["product_id"] == 1


def test_add_product_supplier_missing_name(service, mock_product_db, sample_product):
    """Test adding supplier without name"""
    mock_product_db.get_product_by_id.return_value = sample_product
    
    with pytest.raises(ValueError, match="Supplier name is required"):
        service.add_product_supplier(1, {})


# ==================== Pricing History Tests ====================

def test_get_pricing_history(service, mock_product_db):
    """Test getting pricing history"""
    history = [
        {"product_id": 1, "price_euro": 250.0, "changed_at": "2024-01-01T00:00:00"},
        {"product_id": 1, "price_euro": 260.0, "changed_at": "2024-02-01T00:00:00"}
    ]
    mock_product_db.get_pricing_history.return_value = history
    
    result = service.get_pricing_history(1, limit=50)
    
    assert len(result) == 2
    assert result[0]["price_euro"] == 250.0


def test_analyze_pricing_trends(service, mock_product_db):
    """Test analyzing pricing trends"""
    history = [
        {"product_id": 1, "price_euro": 250.0, "changed_at": "2024-01-01T00:00:00"},
        {"product_id": 1, "price_euro": 260.0, "changed_at": "2024-02-01T00:00:00"},
        {"product_id": 1, "price_euro": 270.0, "changed_at": "2024-03-01T00:00:00"}
    ]
    mock_product_db.get_pricing_history.return_value = history
    
    analysis = service.analyze_pricing_trends(1, period_days=90)
    
    assert analysis["has_data"] is True
    assert analysis["current_price"] == 270.0
    assert analysis["min_price"] == 250.0
    assert analysis["max_price"] == 270.0
    assert analysis["trend"] == "increasing"


def test_analyze_pricing_trends_no_data(service, mock_product_db):
    """Test analyzing trends with no data"""
    mock_product_db.get_pricing_history.return_value = []
    
    analysis = service.analyze_pricing_trends(1)
    
    assert analysis["has_data"] is False


# ==================== Performance Analytics Tests ====================

def test_get_product_performance(service, mock_product_db, sample_product):
    """Test getting product performance"""
    mock_product_db.get_product_by_id.return_value = sample_product
    
    performance = service.get_product_performance(1, period_days=30)
    
    assert performance["product_id"] == 1
    assert "metrics" in performance
    assert "trends" in performance
    assert "rankings" in performance


def test_get_category_performance(service, mock_product_db):
    """Test getting category performance"""
    products = [
        {"id": 1, "model_name": "Module A", "brand": "Brand A"},
        {"id": 2, "model_name": "Module B", "brand": "Brand B"}
    ]
    mock_product_db.list_products.return_value = products
    mock_product_db.get_product_by_id.side_effect = products
    
    performance = service.get_category_performance("Solar Modules", period_days=30, limit=10)
    
    assert performance["has_data"] is True
    assert performance["category"] == "Solar Modules"
    assert "totals" in performance
    assert "top_products" in performance


# ==================== Price Matrix Integration Tests ====================

def test_get_product_pricing_from_matrix(service, mock_product_db, sample_product):
    """Test getting pricing from matrix"""
    mock_product_db.get_product_by_id.return_value = sample_product
    mock_product_db.calculate_enhanced_product_pricing.return_value = {
        "base_price": 250.0,
        "total_price": 275.0,
        "quantity": 1
    }
    
    pricing = service.get_product_pricing_from_matrix(1, quantity=1)
    
    assert "base_price" in pricing
    assert "total_price" in pricing
    mock_product_db.calculate_enhanced_product_pricing.assert_called_once()


def test_get_bulk_pricing(service, mock_product_db):
    """Test getting bulk pricing"""
    products = [
        {"id": 1, "model_name": "Module A", "price_euro": 250.0},
        {"id": 2, "model_name": "Module B", "price_euro": 280.0}
    ]
    
    mock_product_db.get_product_by_id.side_effect = products
    mock_product_db.calculate_enhanced_product_pricing.side_effect = [
        {"total_price": 250.0},
        {"total_price": 280.0}
    ]
    
    pricing = service.get_bulk_pricing([1, 2], [1, 1])
    
    assert pricing["product_count"] == 2
    assert pricing["total_quantity"] == 2
    assert "subtotal" in pricing
    assert "total_price" in pricing


def test_get_bulk_pricing_with_discount(service, mock_product_db):
    """Test bulk pricing with discount"""
    products = [{"id": i, "model_name": f"Module {i}", "price_euro": 250.0} for i in range(1, 11)]
    
    mock_product_db.get_product_by_id.side_effect = products
    mock_product_db.calculate_enhanced_product_pricing.side_effect = [
        {"total_price": 250.0} for _ in range(10)
    ]
    
    pricing = service.get_bulk_pricing(list(range(1, 11)), [1] * 10)
    
    assert pricing["product_count"] == 10
    assert pricing["bulk_discount_percent"] == 5  # 10+ products = 5% discount
    assert pricing["bulk_discount"] > 0


# ==================== Service Initialization Tests ====================

def test_service_initialization():
    """Test service initialization"""
    with patch('backend.services.product_advanced_service.product_db'):
        service = ProductAdvancedService()
        assert service.service_name == "product_advanced"
        assert not service.is_initialized


def test_health_check_healthy(service, mock_product_db):
    """Test health check when healthy"""
    result = service.health_check()
    
    assert result.status == "healthy"


def test_health_check_not_initialized():
    """Test health check when not initialized"""
    service = ProductAdvancedService()
    
    result = service.health_check()
    
    assert result.status == "unhealthy"
    assert "not initialized" in result.message.lower()


# ==================== Helper Method Tests ====================

def test_format_attribute_value(service):
    """Test attribute value formatting"""
    assert service._format_attribute_value("price_euro", 250.50) == "€250.50"
    assert service._format_attribute_value("efficiency", 20.5) == "20.5%"
    assert service._format_attribute_value("power_wp", 400) == "400W"
    assert service._format_attribute_value("unknown", None) == "N/A"


def test_calculate_recommendation_score(service):
    """Test recommendation score calculation"""
    product = {
        "lifecycle_status": "active",
        "power_wp": 400,
        "efficiency": 20.5,
        "price_euro": 250.0,
        "brand": "TestBrand"
    }
    
    context = {
        "required_power": 400,
        "budget": 260.0,
        "preferred_brands": ["TestBrand"]
    }
    
    score = service._calculate_recommendation_score(product, context)
    
    assert score > 0
    assert isinstance(score, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
