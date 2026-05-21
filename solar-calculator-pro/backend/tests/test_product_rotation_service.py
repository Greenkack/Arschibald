"""
Tests for Product Rotation Service

Tests the critical product rotation logic for multi-PDF generation.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.product_rotation_service import (
    ProductRotationService,
    ProductCategory,
    RotationStrategy,
    get_product_rotation_service
)


@pytest.fixture
def mock_product_db():
    """Mock product database module"""
    mock_db = Mock()
    
    # Mock products for different categories
    mock_db.list_products = Mock(side_effect=lambda category=None: {
        "PV Module": [
            {
                "id": 1,
                "brand": "Brand A",
                "model_name": "Model A1",
                "category": "PV Module",
                "power_wp": 400,
                "efficiency": 20.5,
                "price_euro": 200.0,
                "voc_v": 48.0
            },
            {
                "id": 2,
                "brand": "Brand B",
                "model_name": "Model B1",
                "category": "PV Module",
                "power_wp": 410,
                "efficiency": 21.0,
                "price_euro": 220.0,
                "voc_v": 49.0
            },
            {
                "id": 3,
                "brand": "Brand C",
                "model_name": "Model C1",
                "category": "PV Module",
                "power_wp": 420,
                "efficiency": 21.5,
                "price_euro": 240.0,
                "voc_v": 50.0
            }
        ],
        "Inverter": [
            {
                "id": 10,
                "brand": "Inverter Brand A",
                "model_name": "Inverter A1",
                "category": "Inverter",
                "max_power_w": 5000,
                "max_dc_voltage": 600,
                "price_euro": 1500.0,
                "has_battery_support": True,
                "battery_voltage_v": 48
            },
            {
                "id": 11,
                "brand": "Inverter Brand B",
                "model_name": "Inverter B1",
                "category": "Inverter",
                "max_power_w": 6000,
                "max_dc_voltage": 650,
                "price_euro": 1800.0,
                "has_battery_support": True,
                "battery_voltage_v": 48
            }
        ],
        "Battery": [
            {
                "id": 20,
                "brand": "Battery Brand A",
                "model_name": "Battery A1",
                "category": "Battery",
                "capacity_kwh": 10,
                "voltage_v": 48,
                "price_euro": 5000.0
            },
            {
                "id": 21,
                "brand": "Battery Brand B",
                "model_name": "Battery B1",
                "category": "Battery",
                "capacity_kwh": 12,
                "voltage_v": 48,
                "price_euro": 6000.0
            }
        ]
    }.get(category, []))
    
    mock_db.get_product_by_id = Mock(side_effect=lambda pid: {
        1: {
            "id": 1,
            "brand": "Brand A",
            "model_name": "Model A1",
            "category": "PV Module",
            "power_wp": 400,
            "efficiency": 20.5,
            "price_euro": 200.0,
            "voc_v": 48.0
        },
        10: {
            "id": 10,
            "brand": "Inverter Brand A",
            "model_name": "Inverter A1",
            "category": "Inverter",
            "max_power_w": 5000,
            "max_dc_voltage": 600,
            "price_euro": 1500.0,
            "has_battery_support": True,
            "battery_voltage_v": 48
        },
        20: {
            "id": 20,
            "brand": "Battery Brand A",
            "model_name": "Battery A1",
            "category": "Battery",
            "capacity_kwh": 10,
            "voltage_v": 48,
            "price_euro": 5000.0
        }
    }.get(pid))
    
    return mock_db


@pytest.fixture
def service(mock_product_db):
    """Create service instance with mocked dependencies"""
    service = ProductRotationService()
    service._product_db_module = mock_product_db
    service._set_initialized(True)
    return service


class TestProductRotationService:
    """Test Product Rotation Service"""
    
    def test_initialization(self, service):
        """Test service initialization"""
        assert service.is_initialized
        assert service._product_db_module is not None
    
    def test_health_check(self, service):
        """Test health check"""
        result = service.health_check()
        assert result.is_healthy
    
    def test_reset_rotation_state(self, service):
        """Test resetting rotation state"""
        # Mark some brands and products as used
        service.mark_brand_used("pv_module", "Brand A")
        service.mark_product_used("pv_module", 1)
        
        # Verify they are marked
        assert service.is_brand_used("pv_module", "Brand A")
        assert service.is_product_used("pv_module", 1)
        
        # Reset
        service.reset_rotation_state()
        
        # Verify they are cleared
        assert not service.is_brand_used("pv_module", "Brand A")
        assert not service.is_product_used("pv_module", 1)
    
    def test_get_rotation_state(self, service):
        """Test getting rotation state"""
        # Mark some items as used
        service.mark_brand_used("pv_module", "Brand A")
        service.mark_brand_used("pv_module", "Brand B")
        service.mark_product_used("inverter", 10)
        
        state = service.get_rotation_state()
        
        assert "used_brands" in state
        assert "used_products" in state
        assert "pv_module" in state["used_brands"]
        assert "Brand A" in state["used_brands"]["pv_module"]
        assert "Brand B" in state["used_brands"]["pv_module"]
        assert "inverter" in state["used_products"]
        assert 10 in state["used_products"]["inverter"]
    
    def test_mark_and_check_brand_used(self, service):
        """Test marking and checking brand usage"""
        category = "pv_module"
        brand = "Brand A"
        
        # Initially not used
        assert not service.is_brand_used(category, brand)
        
        # Mark as used
        service.mark_brand_used(category, brand)
        
        # Now should be used
        assert service.is_brand_used(category, brand)
    
    def test_mark_and_check_product_used(self, service):
        """Test marking and checking product usage"""
        category = "pv_module"
        product_id = 1
        
        # Initially not used
        assert not service.is_product_used(category, product_id)
        
        # Mark as used
        service.mark_product_used(category, product_id)
        
        # Now should be used
        assert service.is_product_used(category, product_id)
    
    def test_select_rotated_product_avoid_brands(self, service):
        """Test selecting product with brand avoidance"""
        category = "pv_module"
        
        # First selection - should get any product
        product1 = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.AVOID_BRANDS.value
        )
        
        assert product1 is not None
        brand1 = product1.get("brand")
        
        # Second selection - should avoid first brand
        product2 = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.AVOID_BRANDS.value
        )
        
        assert product2 is not None
        brand2 = product2.get("brand")
        assert brand2 != brand1
    
    def test_select_rotated_product_avoid_products(self, service):
        """Test selecting product with product avoidance"""
        category = "pv_module"
        
        # First selection
        product1 = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.AVOID_PRODUCTS.value
        )
        
        assert product1 is not None
        id1 = product1["id"]
        
        # Second selection - should avoid first product
        product2 = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.AVOID_PRODUCTS.value
        )
        
        assert product2 is not None
        id2 = product2["id"]
        assert id2 != id1
    
    def test_select_rotated_product_avoid_both(self, service):
        """Test selecting product with both brand and product avoidance"""
        category = "pv_module"
        
        # First selection
        product1 = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.AVOID_BOTH.value
        )
        
        assert product1 is not None
        brand1 = product1.get("brand")
        id1 = product1["id"]
        
        # Second selection - should avoid both brand and product
        product2 = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.AVOID_BOTH.value
        )
        
        assert product2 is not None
        brand2 = product2.get("brand")
        id2 = product2["id"]
        assert brand2 != brand1
        assert id2 != id1
    
    def test_select_rotated_product_with_specs(self, service):
        """Test selecting product with specification requirements"""
        category = "pv_module"
        
        # Require minimum power
        required_specs = {
            "power_wp": {"min": 410}
        }
        
        product = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.AVOID_BOTH.value,
            required_specs=required_specs
        )
        
        assert product is not None
        assert product.get("power_wp", 0) >= 410
    
    def test_select_rotated_product_with_price_similar(self, service):
        """Test selecting product with similar price"""
        category = "pv_module"
        reference_product_id = 1  # Price: 200.0
        
        product = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.PRICE_SIMILAR.value,
            reference_product_id=reference_product_id,
            price_tolerance=0.2  # ±20%
        )
        
        assert product is not None
        # Price should be within 160-240 range (200 ± 20%)
        price = product.get("price_euro", 0)
        assert 160 <= price <= 240
    
    def test_select_product_set(self, service):
        """Test selecting a complete product set"""
        categories = ["pv_module", "inverter", "battery"]
        
        product_set = service.select_product_set(
            categories=categories,
            strategy=RotationStrategy.AVOID_BOTH.value
        )
        
        assert len(product_set) == 3
        assert "pv_module" in product_set
        assert "inverter" in product_set
        assert "battery" in product_set
        
        # All should have products
        assert product_set["pv_module"] is not None
        assert product_set["inverter"] is not None
        assert product_set["battery"] is not None
    
    def test_select_product_set_with_references(self, service):
        """Test selecting product set with reference products"""
        categories = ["pv_module", "inverter"]
        reference_products = {
            "pv_module": 1,  # Price: 200.0
            "inverter": 10   # Price: 1500.0
        }
        
        product_set = service.select_product_set(
            categories=categories,
            strategy=RotationStrategy.PRICE_SIMILAR.value,
            reference_products=reference_products,
            price_tolerance=0.3
        )
        
        assert len(product_set) == 2
        assert product_set["pv_module"] is not None
        assert product_set["inverter"] is not None
    
    def test_check_product_compatibility_compatible(self, service):
        """Test compatibility check with compatible products"""
        product_set = {
            "pv_module": {
                "id": 1,
                "voc_v": 48.0,
                "power_wp": 400
            },
            "inverter": {
                "id": 10,
                "max_dc_voltage": 600,
                "max_power_w": 5000,
                "has_battery_support": True,
                "battery_voltage_v": 48
            },
            "battery": {
                "id": 20,
                "voltage_v": 48
            }
        }
        
        report = service.check_product_compatibility(product_set)
        
        assert report["is_compatible"]
        assert len(report["issues"]) == 0
    
    def test_check_product_compatibility_voltage_mismatch(self, service):
        """Test compatibility check with voltage mismatch"""
        product_set = {
            "pv_module": {
                "id": 1,
                "voc_v": 700.0,  # Too high!
                "power_wp": 400
            },
            "inverter": {
                "id": 10,
                "max_dc_voltage": 600,
                "max_power_w": 5000
            }
        }
        
        report = service.check_product_compatibility(product_set)
        
        assert not report["is_compatible"]
        assert len(report["issues"]) > 0
        assert any("voltage" in issue["type"] for issue in report["issues"])
    
    def test_check_product_compatibility_battery_not_supported(self, service):
        """Test compatibility check when battery not supported"""
        product_set = {
            "battery": {
                "id": 20,
                "voltage_v": 48
            },
            "inverter": {
                "id": 10,
                "has_battery_support": False  # No battery support!
            }
        }
        
        report = service.check_product_compatibility(product_set)
        
        assert not report["is_compatible"]
        assert len(report["issues"]) > 0
        assert any("battery_not_supported" in issue["type"] for issue in report["issues"])
    
    def test_multiple_rotations(self, service):
        """Test multiple rotations to ensure variety"""
        category = "pv_module"
        
        # Select 3 products in sequence
        products = []
        for i in range(3):
            product = service.select_rotated_product(
                category=category,
                strategy=RotationStrategy.AVOID_BOTH.value
            )
            assert product is not None
            products.append(product)
        
        # All should be different brands
        brands = [p.get("brand") for p in products]
        assert len(set(brands)) == 3
        
        # All should be different products
        ids = [p["id"] for p in products]
        assert len(set(ids)) == 3
    
    def test_rotation_exhaustion_fallback(self, service):
        """Test fallback when rotation options are exhausted"""
        category = "pv_module"
        
        # Mark all brands as used
        service.mark_brand_used(category, "Brand A")
        service.mark_brand_used(category, "Brand B")
        service.mark_brand_used(category, "Brand C")
        
        # Should still return a product (fallback to any)
        product = service.select_rotated_product(
            category=category,
            strategy=RotationStrategy.AVOID_BRANDS.value
        )
        
        assert product is not None
    
    def test_singleton_instance(self, mock_product_db):
        """Test singleton pattern"""
        # Reset singleton
        import backend.services.product_rotation_service as prs
        prs._product_rotation_service = None
        
        # Create first instance
        service1 = ProductRotationService()
        service1._product_db_module = mock_product_db
        service1._set_initialized(True)
        prs._product_rotation_service = service1
        
        # Get second instance - should be same
        service2 = get_product_rotation_service()
        
        assert service1 is service2
        
        # Clean up
        prs._product_rotation_service = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
