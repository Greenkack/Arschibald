"""
Tests for accessory and optional component pricing calculations

Tests the enhanced accessory pricing functionality including:
- Individual accessory pricing with quantities
- Accessory categorization and pricing rules
- Real-time price updates for accessories
- Custom component pricing
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory
    from solar_calculator_pricing_integration import (
        SolarCalculatorPricingIntegration,
        get_pricing_display_for_ui,
        update_pricing_in_session_state,
    )
    PRICING_INTEGRATION_AVAILABLE = True
except ImportError as e:
    PRICING_INTEGRATION_AVAILABLE = False
    print(f"Warning: Pricing integration not available for testing: {e}")


class TestAccessoryPricingCalculations:
    """Test accessory and optional component pricing calculations"""

    def setup_method(self):
        """Set up test fixtures"""
        if not PRICING_INTEGRATION_AVAILABLE:
            pytest.skip("Pricing integration not available")

        self.integration = SolarCalculatorPricingIntegration()

        # Mock product database responses
        self.mock_products = {
            "Test Wallbox 11kW": {
                "id": 101,
                "model_name": "Test Wallbox 11kW",
                "category": "Wallbox",
                "brand": "ChargePoint",
                "price_euro": 800.0,
                "calculate_per": "Stück",
                "warranty_years": 5,
                "technology": "AC",
                "feature": "Smart Charging"
            },
            "Test EMS Pro": {
                "id": 102,
                "model_name": "Test EMS Pro",
                "category": "Energiemanagementsystem",
                "brand": "EMS Brand",
                "price_euro": 1500.0,
                "calculate_per": "Stück",
                "warranty_years": 10,
                "technology": "IoT",
                "feature": "Cloud Management"
            },
            "Test Optimizer": {
                "id": 103,
                "model_name": "Test Optimizer",
                "category": "Leistungsoptimierer",
                "brand": "SolarEdge",
                "price_euro": 45.0,
                "calculate_per": "Stück",
                "warranty_years": 25,
                "technology": "DC",
                "feature": "Module Level Monitoring"
            },
            "Test Solar Carport": {
                "id": 104,
                "model_name": "Test Solar Carport",
                "category": "Carport",
                "brand": "Carport Systems",
                "price_euro": 8500.0,
                "calculate_per": "pauschal",
                "warranty_years": 15,
                "technology": "Aluminum",
                "feature": "Weather Resistant"
            }
        }

        # Mock margin calculations
        self.mock_margins = {
            101: {"selling_price_net": 1000.0, "margin_percent": 25.0},
            102: {"selling_price_net": 1800.0, "margin_percent": 20.0},
            103: {"selling_price_net": 55.0, "margin_percent": 22.2},
            104: {"selling_price_net": 10200.0, "margin_percent": 20.0}
        }

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    def test_wallbox_pricing_with_quantity(
            self,
            mock_calc_price,
            mock_selling_price,
            mock_get_product):
        """Test wallbox pricing with quantity selection"""
        # Setup mocks
        product = self.mock_products["Test Wallbox 11kW"]
        mock_get_product.return_value = product
        mock_selling_price.return_value = self.mock_margins[101]
        mock_calc_price.side_effect = lambda base_price, quantity, **kwargs: base_price * quantity

        # Test data with multiple wallboxes
        project_details = {
            "include_additional_components": True,
            "selected_wallbox_name": "Test Wallbox 11kW",
            "selected_wallbox_quantity": 3
        }

        # Calculate pricing
        result = self.integration.calculate_component_pricing(project_details)

        # Verify results
        assert not result.get("error")
        assert len(result["components"]) == 1

        wallbox_comp = result["components"][0]
        assert wallbox_comp["component_type"] == "wallbox"
        assert wallbox_comp["quantity"] == 3
        assert wallbox_comp["unit_price"] == 1000.0
        assert wallbox_comp["total_price"] == 3000.0
        assert wallbox_comp["category"] == "Ladeinfrastruktur"
        assert wallbox_comp["is_optional"] is True

        # Verify dynamic keys
        keys = wallbox_comp["dynamic_keys"]
        assert "WALLBOX_QUANTITY" in keys
        assert keys["WALLBOX_QUANTITY"] == 3
        assert "WALLBOX_TOTAL_PRICE" in keys
        assert keys["WALLBOX_TOTAL_PRICE"] == 3000.0

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    def test_optimizer_pricing_with_quantity(
            self,
            mock_calc_price,
            mock_selling_price,
            mock_get_product):
        """Test optimizer pricing with quantity selection"""
        # Setup mocks
        product = self.mock_products["Test Optimizer"]
        mock_get_product.return_value = product
        mock_selling_price.return_value = self.mock_margins[103]
        mock_calc_price.side_effect = lambda base_price, quantity, **kwargs: base_price * quantity

        # Test data with multiple optimizers
        project_details = {
            "include_additional_components": True,
            "selected_optimizer_name": "Test Optimizer",
            "selected_optimizer_quantity": 20
        }

        # Calculate pricing
        result = self.integration.calculate_component_pricing(project_details)

        # Verify results
        assert not result.get("error")
        assert len(result["components"]) == 1

        optimizer_comp = result["components"][0]
        assert optimizer_comp["component_type"] == "optimizer"
        assert optimizer_comp["quantity"] == 20
        assert optimizer_comp["unit_price"] == 55.0
        assert optimizer_comp["total_price"] == 1100.0
        assert optimizer_comp["category"] == "Energiemanagement"

        # Verify pricing rules
        pricing_rules = optimizer_comp["pricing_rules"]
        assert pricing_rules["supports_quantity"] is True
        assert pricing_rules["bulk_discount"]["threshold"] == 10
        assert pricing_rules["bulk_discount"]["discount_percent"] == 3

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    def test_ems_single_quantity_pricing(
            self,
            mock_calc_price,
            mock_selling_price,
            mock_get_product):
        """Test EMS pricing (typically single quantity)"""
        # Setup mocks
        product = self.mock_products["Test EMS Pro"]
        mock_get_product.return_value = product
        mock_selling_price.return_value = self.mock_margins[102]
        mock_calc_price.side_effect = lambda base_price, quantity, **kwargs: base_price * quantity

        # Test data with EMS
        project_details = {
            "include_additional_components": True,
            "selected_ems_name": "Test EMS Pro"
        }

        # Calculate pricing
        result = self.integration.calculate_component_pricing(project_details)

        # Verify results
        assert not result.get("error")
        assert len(result["components"]) == 1

        ems_comp = result["components"][0]
        assert ems_comp["component_type"] == "ems"
        assert ems_comp["quantity"] == 1
        assert ems_comp["unit_price"] == 1800.0
        assert ems_comp["total_price"] == 1800.0
        assert ems_comp["category"] == "Energiemanagement"

        # Verify pricing rules
        pricing_rules = ems_comp["pricing_rules"]
        assert pricing_rules["supports_quantity"] is False
        assert pricing_rules["max_quantity"] == 1

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    def test_carport_pauschal_pricing(
            self,
            mock_calc_price,
            mock_selling_price,
            mock_get_product):
        """Test carport pricing with pauschal calculation method"""
        # Setup mocks
        product = self.mock_products["Test Solar Carport"]
        mock_get_product.return_value = product
        mock_selling_price.return_value = self.mock_margins[104]
        mock_calc_price.side_effect = lambda base_price, quantity, **kwargs: base_price  # pauschal

        # Test data with carport
        project_details = {
            "include_additional_components": True,
            "selected_carport_name": "Test Solar Carport"
        }

        # Calculate pricing
        result = self.integration.calculate_component_pricing(project_details)

        # Verify results
        assert not result.get("error")
        assert len(result["components"]) == 1

        carport_comp = result["components"][0]
        assert carport_comp["component_type"] == "carport"
        assert carport_comp["quantity"] == 1
        assert carport_comp["unit_price"] == 10200.0
        assert carport_comp["total_price"] == 10200.0
        assert carport_comp["calculate_per"] == "pauschal"
        assert carport_comp["category"] == "Bauliche Erweiterungen"

        # Verify pricing rules
        pricing_rules = carport_comp["pricing_rules"]
        assert pricing_rules["installation_required"] is True
        assert pricing_rules["requires_building_permit"] is True
        assert pricing_rules["foundation_required"] is True

    def test_custom_component_pricing(self):
        """Test custom 'Sonstiges' component pricing"""
        # Test data with custom component
        project_details = {
            "include_additional_components": True,
            "additional_other_custom": "Spezielle Verkabelung",
            "additional_other_price": 450.0
        }

        # Calculate pricing
        result = self.integration.calculate_component_pricing(project_details)

        # Verify results
        assert not result.get("error")
        assert len(result["components"]) == 1

        custom_comp = result["components"][0]
        assert custom_comp["component_type"] == "custom"
        assert custom_comp["model_name"] == "Spezielle Verkabelung"
        assert custom_comp["quantity"] == 1
        assert custom_comp["unit_price"] == 450.0
        assert custom_comp["total_price"] == 450.0
        assert custom_comp["calculate_per"] == "pauschal"
        assert custom_comp["category"] == "Sonstige Komponenten"
        assert custom_comp["is_custom"] is True

        # Verify dynamic keys
        keys = custom_comp["dynamic_keys"]
        assert "CUSTOM_DESCRIPTION" in keys
        assert keys["CUSTOM_DESCRIPTION"] == "Spezielle Verkabelung"
        assert "CUSTOM_PRICE" in keys
        assert keys["CUSTOM_PRICE"] == 450.0

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    def test_multiple_accessories_categorization(
            self, mock_calc_price, mock_selling_price, mock_get_product):
        """Test multiple accessories with proper categorization"""
        # Setup mocks for multiple products
        def mock_get_product_side_effect(model_name):
            return self.mock_products.get(model_name)

        def mock_selling_price_side_effect(product_id):
            return self.mock_margins.get(product_id)

        mock_get_product.side_effect = mock_get_product_side_effect
        mock_selling_price.side_effect = mock_selling_price_side_effect
        mock_calc_price.side_effect = lambda base_price, quantity, **kwargs: base_price * quantity

        # Test data with multiple accessories
        project_details = {
            "include_additional_components": True,
            "selected_wallbox_name": "Test Wallbox 11kW",
            "selected_wallbox_quantity": 2,
            "selected_ems_name": "Test EMS Pro",
            "selected_optimizer_name": "Test Optimizer",
            "selected_optimizer_quantity": 15,
            "additional_other_custom": "Monitoring System",
            "additional_other_price": 300.0
        }

        # Calculate pricing
        result = self.integration.calculate_component_pricing(project_details)

        # Verify results
        assert not result.get("error")
        assert len(result["components"]) == 4

        # Get display data for categorization
        display_data = self.integration.get_pricing_display_data(
            project_details)

        # Verify categorization
        categories = display_data["display_components_by_category"]
        assert "Ladeinfrastruktur" in categories
        assert "Energiemanagement" in categories
        assert "Sonstige Komponenten" in categories

        # Verify category totals
        assert len(categories["Ladeinfrastruktur"]["components"]) == 1
        assert len(categories["Energiemanagement"]["components"]) == 2
        assert len(categories["Sonstige Komponenten"]["components"]) == 1

        # Verify total calculations
        expected_total = (2 * 1000.0) + 1800.0 + (15 * 55.0) + 300.0  # 4925.0
        assert display_data["total_price"] == expected_total
        assert display_data["optional_components_total"] == expected_total

    def test_accessory_pricing_rules_validation(self):
        """Test accessory-specific pricing rules"""
        # Test wallbox rules
        wallbox_rules = self.integration._get_accessory_pricing_rules(
            "wallbox", {})
        assert wallbox_rules["supports_quantity"] is True
        assert wallbox_rules["max_quantity"] == 20
        assert wallbox_rules["bulk_discount"]["threshold"] == 3
        assert wallbox_rules["installation_required"] is True
        assert wallbox_rules["requires_electrical_permit"] is True

        # Test optimizer rules
        optimizer_rules = self.integration._get_accessory_pricing_rules(
            "optimizer", {})
        assert optimizer_rules["supports_quantity"] is True
        assert optimizer_rules["bulk_discount"]["threshold"] == 10
        assert optimizer_rules["installation_labor_hours"] == 0.5

        # Test carport rules
        carport_rules = self.integration._get_accessory_pricing_rules(
            "carport", {})
        assert carport_rules["supports_quantity"] is False
        assert carport_rules["installation_required"] is True
        assert carport_rules["requires_building_permit"] is True
        assert carport_rules["foundation_required"] is True

        # Test EMS rules
        ems_rules = self.integration._get_accessory_pricing_rules("ems", {})
        assert ems_rules["supports_quantity"] is False
        assert ems_rules["max_quantity"] == 1

    def test_empty_custom_component_handling(self):
        """Test handling of empty custom component fields"""
        # Test with empty description
        project_details = {
            "include_additional_components": True,
            "additional_other_custom": "",
            "additional_other_price": 100.0
        }

        result = self.integration.calculate_component_pricing(project_details)
        assert len(result["components"]) == 0

        # Test with zero price
        project_details = {
            "include_additional_components": True,
            "additional_other_custom": "Test Component",
            "additional_other_price": 0.0
        }

        result = self.integration.calculate_component_pricing(project_details)
        assert len(result["components"]) == 0

    def test_pricing_cache_with_accessories(self):
        """Test pricing cache functionality with accessory changes"""
        project_details = {
            "include_additional_components": True,
            "selected_wallbox_name": "Test Wallbox 11kW",
            "selected_wallbox_quantity": 1
        }

        # First calculation should not use cache
        with patch('solar_calculator_pricing_integration.get_product_by_model_name') as mock_get_product:
            mock_get_product.return_value = self.mock_products["Test Wallbox 11kW"]

            result1 = self.integration.calculate_component_pricing(
                project_details)
            assert mock_get_product.call_count == 1

            # Second calculation with same data should use cache
            result2 = self.integration.get_cached_pricing(project_details)
            assert result2 is not None
            assert result2["base_price"] == result1["base_price"]

        # Change quantity should invalidate cache
        project_details["selected_wallbox_quantity"] = 2
        cached_result = self.integration.get_cached_pricing(project_details)
        assert cached_result is None

    @patch('solar_calculator_pricing_integration.STREAMLIT_AVAILABLE', True)
    def test_session_state_update_with_accessories(self):
        """Test session state updates with accessory pricing"""
        with patch('solar_calculator_pricing_integration.st') as mock_st:
            # Create a mock session state that supports both dict and attribute
            # access
            class MockSessionState:
                def __init__(self):
                    self._data = {}

                def __contains__(self, key):
                    return key in self._data

                def __getitem__(self, key):
                    return self._data[key]

                def __setitem__(self, key, value):
                    self._data[key] = value

                def __getattr__(self, name):
                    return self._data.get(name)

                def __setattr__(self, name, value):
                    if name.startswith('_'):
                        super().__setattr__(name, value)
                    else:
                        self._data[name] = value

                def update(self, other):
                    self._data.update(other)

            mock_st.session_state = MockSessionState()

            project_details = {
                "include_additional_components": True,
                "selected_wallbox_name": "Test Wallbox 11kW",
                "selected_wallbox_quantity": 2
            }

            with patch('solar_calculator_pricing_integration.get_product_by_model_name') as mock_get_product:
                with patch('solar_calculator_pricing_integration.calculate_selling_price') as mock_selling_price:
                    with patch('solar_calculator_pricing_integration.calculate_price_by_method') as mock_calc_price:
                        mock_get_product.return_value = self.mock_products["Test Wallbox 11kW"]
                        mock_selling_price.return_value = self.mock_margins[101]
                        mock_calc_price.side_effect = lambda base_price, quantity, **kwargs: base_price * quantity

                        # Update session state
                        update_pricing_in_session_state(project_details)

                        # Verify session state was updated
                        assert 'pricing_data' in mock_st.session_state
                        assert 'dynamic_keys' in mock_st.session_state

                        pricing_data = mock_st.session_state['pricing_data']['pv_system_pricing']
                        assert len(pricing_data['components']) == 1
                        assert pricing_data['components'][0]['quantity'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
