"""Tests for Calculate Per Integration with Product Database

Tests the integration between the calculate_per engine and existing product features.
"""

from typing import Any
from unittest.mock import patch

import pytest


# Mock the database functions to avoid dependency issues
def mock_get_product_by_id(product_id: int) -> dict[str, Any]:
    """Mock product data for testing"""
    products = {
        1: {  # PV Module
            'id': 1,
            'category': 'Modul',
            'model_name': 'SolarTech ST-400',
            'brand': 'SolarTech',
            'price_euro': 180.0,
            'calculate_per': 'Stück',
            'capacity_w': 400.0,
            'technology': 'Monokristallin',
            'feature': 'Halbzellen',
            'design': 'All-Black',
            'efficiency_percent': 20.5,
            'warranty_years': 25
        },
        2: {  # Inverter
            'id': 2,
            'category': 'Wechselrichter',
            'model_name': 'InverterPro IP-8000',
            'brand': 'InverterPro',
            'price_euro': 1200.0,
            'calculate_per': 'Stück',
            'power_kw': 8.0,
            'technology': 'String',
            'feature': 'WiFi',
            'warranty_years': 10
        },
        3: {  # Cable
            'id': 3,
            'category': 'Kabel',
            'model_name': 'CableTech CT-6mm',
            'brand': 'CableTech',
            'price_euro': 8.50,
            'calculate_per': 'Meter',
            'length_m': 1.0,
            'technology': 'DC'
        },
        4: {  # Installation Service
            'id': 4,
            'category': 'Dienstleistung',
            'model_name': 'Installation Standard',
            'brand': 'InstallPro',
            'price_euro': 2500.0,
            'calculate_per': 'pauschal',
            'labor_hours': 16.0
        },
        5: {  # Mounting System (per kWp)
            'id': 5,
            'category': 'Montagesystem',
            'model_name': 'MountTech MT-Roof',
            'brand': 'MountTech',
            'price_euro': 120.0,
            'calculate_per': 'kWp',
            'technology': 'Aufdach'
        }
    }
    return products.get(product_id)


def mock_get_product_by_model_name(model_name: str) -> dict[str, Any]:
    """Mock product lookup by model name"""
    products = {
        'SolarTech ST-400': mock_get_product_by_id(1),
        'InverterPro IP-8000': mock_get_product_by_id(2),
        'CableTech CT-6mm': mock_get_product_by_id(3),
        'Installation Standard': mock_get_product_by_id(4),
        'MountTech MT-Roof': mock_get_product_by_id(5)
    }
    return products.get(model_name)

# Patch the imports in product_db


@pytest.fixture(autouse=True)
def mock_product_db():
    """Mock product database functions"""
    with patch('product_db.get_product_by_id', side_effect=mock_get_product_by_id), \
            patch('product_db.get_product_by_model_name', side_effect=mock_get_product_by_model_name):
        yield


class TestCalculatePerIntegration:
    """Test calculate_per integration with product database"""

    def test_calculate_price_by_method_enhanced(self):
        """Test enhanced calculate_price_by_method function"""
        from product_db import calculate_price_by_method

        # Test basic per piece calculation
        result = calculate_price_by_method(180.0, 20, "Stück")
        assert result == 3600.0

        # Test per meter calculation
        result = calculate_price_by_method(8.50, 50.0, "Meter")
        assert result == 425.0

        # Test lump sum calculation
        result = calculate_price_by_method(2500.0, 3, "pauschal")
        assert result == 2500.0

    def test_calculate_price_by_method_with_features(self):
        """Test calculate_price_by_method with product features"""
        from product_db import calculate_price_by_method

        # Test with HJT technology premium
        product_specs = {
            'capacity_w': 400.0,
            'technology': 'HJT',
            'category': 'Modul'
        }

        result = calculate_price_by_method(180.0, 1, "Stück", product_specs)
        assert result == 230.0  # 180 + 50 (HJT premium)

    def test_calculate_price_by_method_per_kwp_with_specs(self):
        """Test per kWp calculation with product specifications"""
        from product_db import calculate_price_by_method

        product_specs = {
            'capacity_w': 400.0,
            'category': 'Modul'
        }

        # 25 modules × 400W = 10kWp, 10kWp × 150€/kWp = 1500€
        result = calculate_price_by_method(150.0, 25, "kWp", product_specs)
        assert result == 1500.0

    def test_calculate_enhanced_product_pricing(self):
        """Test enhanced product pricing calculation"""
        from product_db import calculate_enhanced_product_pricing

        # Test with PV module
        product = mock_get_product_by_id(1)
        result = calculate_enhanced_product_pricing(product, 20)

        assert result['success']
        assert result['product_id'] == 1
        assert result['model_name'] == 'SolarTech ST-400'
        assert result['calculation_method'] == 'Stück'
        assert result['quantity'] == 20
        assert result['base_price'] == 180.0

        # Should have feature adjustments
        assert len(result['price_adjustments']) > 0
        assert 'feature_Halbzellen' in result['price_adjustments']
        assert 'design_All-Black' in result['price_adjustments']

        # Total should include base price + adjustments × quantity
        expected_base = 180.0 * 20  # 3600
        adjustments_per_unit = sum(result['price_adjustments'].values())  # 70
        expected_total = expected_base + \
            (adjustments_per_unit * 20)  # 3600 + 1400 = 5000
        assert result['total_price'] == expected_total

    def test_calculate_enhanced_product_pricing_cable(self):
        """Test enhanced pricing for cable (per meter)"""
        from product_db import calculate_enhanced_product_pricing

        product = mock_get_product_by_id(3)
        result = calculate_enhanced_product_pricing(product, 75.0)

        assert result['success']
        assert result['calculation_method'] == 'Meter'
        assert result['total_price'] == 637.5  # 8.50 × 75

    def test_calculate_enhanced_product_pricing_service(self):
        """Test enhanced pricing for service (lump sum)"""
        from product_db import calculate_enhanced_product_pricing

        product = mock_get_product_by_id(4)
        result = calculate_enhanced_product_pricing(
            product, 2)  # Quantity should be ignored

        assert result['success']
        assert result['calculation_method'] == 'pauschal'
        assert result['total_price'] == 2500.0  # Lump sum, quantity ignored

    def test_calculate_enhanced_product_pricing_per_kwp(self):
        """Test enhanced pricing for mounting system (per kWp)"""
        from product_db import calculate_enhanced_product_pricing

        product = mock_get_product_by_id(5)
        system_context = {'system_capacity_kwp': 10.0}

        result = calculate_enhanced_product_pricing(product, 1, system_context)

        assert result['success']
        assert result['calculation_method'] == 'kWp'
        assert result['total_price'] == 1200.0  # 120 × 10kWp

    def test_get_product_pricing_breakdown(self):
        """Test getting pricing breakdown by product ID"""
        from product_db import get_product_pricing_breakdown

        result = get_product_pricing_breakdown(1, 10)

        assert result is not None
        assert result['success']
        assert result['product_id'] == 1
        assert result['quantity'] == 10

    def test_get_product_pricing_breakdown_not_found(self):
        """Test pricing breakdown for non-existent product"""
        from product_db import get_product_pricing_breakdown

        result = get_product_pricing_breakdown(999, 10)
        assert result is None

    def test_calculate_system_pricing(self):
        """Test complete system pricing calculation"""
        from product_db import calculate_system_pricing

        components = [
            {'product_id': 1, 'quantity': 25},  # 25 PV modules
            {'product_id': 2, 'quantity': 1},   # 1 inverter
            {'product_id': 3, 'quantity': 50.0},  # 50m cable
            {'product_id': 4, 'quantity': 1},   # Installation service
        ]

        system_context = {'system_capacity_kwp': 10.0}

        result = calculate_system_pricing(components, system_context)

        assert result['success']
        assert result['component_count'] == 4
        assert len(result['components']) == 4
        assert result['total_final_price'] > 0

        # Check that all components are included
        component_categories = [comp['category']
                                for comp in result['components']]
        assert 'Modul' in component_categories
        assert 'Wechselrichter' in component_categories
        assert 'Kabel' in component_categories
        assert 'Dienstleistung' in component_categories

    def test_calculate_system_pricing_with_model_names(self):
        """Test system pricing using model names instead of IDs"""
        from product_db import calculate_system_pricing

        components = [
            {'model_name': 'SolarTech ST-400', 'quantity': 20},
            {'model_name': 'InverterPro IP-8000', 'quantity': 1},
        ]

        result = calculate_system_pricing(components)

        assert result['success']
        assert result['component_count'] == 2

    def test_validate_calculate_per_integration(self):
        """Test integration validation function"""
        from product_db import validate_calculate_per_integration

        result = validate_calculate_per_integration()

        assert result['success']
        assert 'supported_methods' in result
        assert 'test_results' in result
        assert 'summary' in result

        # Check that basic tests pass
        summary = result['summary']
        assert summary['total_tests'] > 0
        assert summary['passed_tests'] > 0
        assert summary['success_rate'] > 0

    def test_enhanced_pricing_with_system_context(self):
        """Test enhanced pricing with comprehensive system context"""
        from product_db import calculate_enhanced_product_pricing

        product = mock_get_product_by_id(1)  # PV module
        system_context = {
            'system_capacity_kwp': 10.0,
            'installation_area_m2': 60.0,
            'labor_hours': 16.0
        }

        result = calculate_enhanced_product_pricing(
            product, 25, system_context)

        assert result['success']
        assert 'context_used' in result

        context = result['context_used']
        assert context['technology'] == 'Monokristallin'
        assert context['feature'] == 'Halbzellen'
        assert context['design'] == 'All-Black'
        assert context['category'] == 'Modul'

    def test_error_handling_invalid_product(self):
        """Test error handling for invalid product data"""
        from product_db import calculate_enhanced_product_pricing

        # Product with no price
        invalid_product = {
            'id': 999,
            'model_name': 'Invalid Product',
            'price_euro': 0.0,
            'calculate_per': 'Stück'
        }

        result = calculate_enhanced_product_pricing(invalid_product, 1)

        assert result['success'] == False
        assert 'error' in result
        assert 'Invalid base price' in result['error']

    def test_fallback_to_legacy_calculation(self):
        """Test fallback to legacy calculation when enhanced engine fails"""
        from product_db import _legacy_calculate_price_by_method

        # Test legacy function directly
        result = _legacy_calculate_price_by_method(180.0, 20, "Stück")
        assert result == 3600.0

        result = _legacy_calculate_price_by_method(8.50, 50, "Meter")
        assert result == 425.0

        result = _legacy_calculate_price_by_method(2500.0, 3, "pauschal")
        assert result == 2500.0


class TestFeatureIntegrationScenarios:
    """Test real-world feature integration scenarios"""

    def test_premium_pv_module_scenario(self):
        """Test premium PV module with multiple features"""
        from product_db import calculate_enhanced_product_pricing

        premium_module = {
            'id': 100,
            'category': 'Modul',
            'model_name': 'Premium HJT Module',
            'brand': 'PremiumSolar',
            'price_euro': 220.0,
            'calculate_per': 'Stück',
            'capacity_w': 450.0,
            'technology': 'HJT',
            'feature': 'Bifazial',
            'design': 'All-Black',
            'upgrade': 'Premium',
            'efficiency_percent': 22.8,
            'warranty_years': 30
        }

        result = calculate_enhanced_product_pricing(premium_module, 20)

        assert result['success']

        # Should have multiple adjustments
        adjustments = result['price_adjustments']
        assert 'technology_HJT' in adjustments
        assert 'feature_Bifazial' in adjustments
        assert 'design_All-Black' in adjustments
        assert 'upgrade_Premium' in adjustments
        assert 'efficiency_22.8%' in adjustments

        # Total adjustments: HJT(50) + Bifazial(50) + All-Black(25) + Premium(100) + High-Eff(50) = 275 per module
        # Total: (220 + 275) × 20 = 9900
        assert result['total_price'] == 9900.0

    def test_inverter_with_features_scenario(self):
        """Test inverter with advanced features"""
        from product_db import calculate_enhanced_product_pricing

        advanced_inverter = {
            'id': 101,
            'category': 'Wechselrichter',
            'model_name': 'Advanced String Inverter',
            'brand': 'InverterTech',
            'price_euro': 1500.0,
            'calculate_per': 'Stück',
            'power_kw': 10.0,
            'technology': 'String',
            'feature': 'Notstrom',
            'design': 'Outdoor',
            'upgrade': 'Service Plus',
            'warranty_years': 15
        }

        result = calculate_enhanced_product_pricing(advanced_inverter, 1)

        assert result['success']

        # Should have feature adjustments
        adjustments = result['price_adjustments']
        assert 'feature_Notstrom' in adjustments
        assert 'design_Outdoor' in adjustments
        assert 'upgrade_Service Plus' in adjustments

        # Total adjustments: Notstrom(150) + Outdoor(75) + Service Plus(200) = 425
        # Total: 1500 + 425 = 1925
        assert result['total_price'] == 1925.0

    def test_mixed_system_calculation(self):
        """Test complete system with mixed calculation methods"""
        from product_db import calculate_system_pricing

        # Mock products for this test
        def mock_mixed_products(product_id):
            products = {
                201: {  # Premium modules (per piece)
                    'id': 201,
                    'category': 'Modul',
                    'model_name': 'Premium Module',
                    'price_euro': 200.0,
                    'calculate_per': 'Stück',
                    'capacity_w': 400.0,
                    'technology': 'HJT',
                    'efficiency_percent': 22.0
                },
                202: {  # Mounting system (per kWp)
                    'id': 202,
                    'category': 'Montagesystem',
                    'model_name': 'Roof Mounting',
                    'price_euro': 100.0,
                    'calculate_per': 'kWp'
                },
                203: {  # DC Cable (per meter)
                    'id': 203,
                    'category': 'Kabel',
                    'model_name': 'DC Cable 6mm',
                    'price_euro': 9.0,
                    'calculate_per': 'Meter'
                },
                204: {  # Installation (lump sum)
                    'id': 204,
                    'category': 'Dienstleistung',
                    'model_name': 'Professional Installation',
                    'price_euro': 3000.0,
                    'calculate_per': 'pauschal',
                    'labor_hours': 20.0
                }
            }
            return products.get(product_id)

        with patch('product_db.get_product_by_id', side_effect=mock_mixed_products):
            components = [
                {'product_id': 201, 'quantity': 25},    # 25 modules
                {'product_id': 202, 'quantity': 1},     # Mounting for system
                {'product_id': 203, 'quantity': 80.0},  # 80m cable
                {'product_id': 204, 'quantity': 1},     # Installation service
            ]

            system_context = {'system_capacity_kwp': 10.0}  # 25 × 400W = 10kWp

            result = calculate_system_pricing(components, system_context)

            assert result['success']
            assert result['component_count'] == 4

            # Verify different calculation methods were used
            methods_used = [comp['calculation_method']
                            for comp in result['components']]
            assert 'Stück' in methods_used
            assert 'kWp' in methods_used
            assert 'Meter' in methods_used
            assert 'pauschal' in methods_used


if __name__ == "__main__":
    pytest.main([__file__])
