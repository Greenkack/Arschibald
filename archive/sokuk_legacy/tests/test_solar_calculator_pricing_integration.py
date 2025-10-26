"""
Tests for Solar Calculator Pricing Integration

Tests the integration between the solar calculator component selection
and the enhanced pricing system with calculate_per support.
"""

from unittest.mock import patch

import pytest

# Import the module under test
try:
    from solar_calculator_pricing_integration import (
        SolarCalculatorPricingIntegration,
        get_pricing_display_for_ui,
        integrate_pricing_with_solar_calculator,
        update_pricing_in_session_state,
    )
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False


@pytest.fixture
def sample_project_details():
    """Sample project details for testing"""
    return {
        # Module selection
        "selected_module_name": "Test Module 400W",
        "module_quantity": 20,
        "selected_module_capacity_w": 400.0,
        "anlage_kwp": 8.0,

        # Inverter selection
        "selected_inverter_name": "Test Inverter 8kW",
        "selected_inverter_quantity": 1,
        "selected_inverter_power_kw": 8.0,

        # Storage selection
        "include_storage": True,
        "selected_storage_name": "Test Battery 10kWh",
        "selected_storage_storage_power_kw": 10.0,

        # Additional components
        "include_additional_components": True,
        "selected_wallbox_name": "Test Wallbox 11kW",
        "selected_ems_name": "Test EMS System",
        "selected_optimizer_name": None,
        "selected_carport_name": None,
        "selected_notstrom_name": None,
        "selected_tierabwehr_name": None
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing"""
    return {
        "module": {
            "id": 1,
            "model_name": "Test Module 400W",
            "category": "Modul",
            "brand": "Test Brand",
            "price_euro": 180.0,
            "capacity_w": 400.0,
            "calculate_per": "Stück",
            "purchase_price_net": 150.0,
            "margin_type": "percentage",
            "margin_value": 20.0,
            "technology": "Monokristallin",
            "feature": "Bifacial",
            "design": "All-Black",
            "efficiency_percent": 21.5,
            "warranty_years": 25
        },
        "inverter": {
            "id": 2,
            "model_name": "Test Inverter 8kW",
            "category": "Wechselrichter",
            "brand": "Test Inverter Brand",
            "price_euro": 1200.0,
            "power_kw": 8.0,
            "calculate_per": "Stück",
            "purchase_price_net": 1000.0,
            "margin_type": "percentage",
            "margin_value": 20.0,
            "technology": "String",
            "feature": "MPPT",
            "warranty_years": 10
        },
        "storage": {
            "id": 3,
            "model_name": "Test Battery 10kWh",
            "category": "Batteriespeicher",
            "brand": "Test Battery Brand",
            "price_euro": 4500.0,
            "storage_power_kw": 10.0,
            "calculate_per": "Stück",
            "purchase_price_net": 3800.0,
            "margin_type": "percentage",
            "margin_value": 18.4,
            "technology": "LiFePO4",
            "feature": "High Voltage",
            "max_cycles": 6000,
            "warranty_years": 10
        },
        "wallbox": {
            "id": 4,
            "model_name": "Test Wallbox 11kW",
            "category": "Wallbox",
            "brand": "Test Wallbox Brand",
            "price_euro": 800.0,
            "power_kw": 11.0,
            "calculate_per": "Stück",
            "purchase_price_net": 650.0,
            "margin_type": "percentage",
            "margin_value": 23.1,
            "technology": "AC",
            "feature": "Smart Charging",
            "warranty_years": 3
        },
        "ems": {
            "id": 5,
            "model_name": "Test EMS System",
            "category": "Energiemanagementsystem",
            "brand": "Test EMS Brand",
            "price_euro": 1500.0,
            "calculate_per": "pauschal",
            "purchase_price_net": 1200.0,
            "margin_type": "fixed",
            "margin_value": 300.0,
            "technology": "Smart Grid",
            "feature": "Load Management",
            "warranty_years": 5
        }
    }


@pytest.fixture
def mock_product_db_functions(sample_product_data):
    """Mock product database functions"""
    def mock_get_product_by_model_name(model_name):
        for product in sample_product_data.values():
            if product["model_name"] == model_name:
                return product
        return None

    def mock_get_product_by_id(product_id):
        for product in sample_product_data.values():
            if product["id"] == product_id:
                return product
        return None

    def mock_calculate_price_by_method(
            base_price,
            quantity,
            calculate_per,
            product_specs=None):
        if calculate_per == "Stück":
            return base_price * quantity
        if calculate_per == "pauschal":
            return base_price
        if calculate_per == "Meter":
            return base_price * quantity
        if calculate_per == "kWp":
            if product_specs and "capacity_w" in product_specs:
                kwp = product_specs["capacity_w"] / 1000.0
                return base_price * kwp * quantity
            return base_price * quantity
        return base_price * quantity

    def mock_calculate_selling_price(product_id):
        product = mock_get_product_by_id(product_id)
        if not product:
            return None

        purchase_price = product.get("purchase_price_net", 0.0)
        margin_type = product.get("margin_type", "percentage")
        margin_value = product.get("margin_value", 0.0)

        if margin_type == "percentage":
            margin_amount = purchase_price * (margin_value / 100.0)
            selling_price = purchase_price + margin_amount
        elif margin_type == "fixed":
            margin_amount = margin_value
            selling_price = purchase_price + margin_amount
        else:
            margin_amount = 0.0
            selling_price = purchase_price

        return {
            "purchase_price_net": purchase_price,
            "margin_type": margin_type,
            "margin_value": margin_value,
            "margin_amount": margin_amount,
            "selling_price_net": selling_price,
            "margin_percentage": (
                margin_amount /
                purchase_price *
                100.0) if purchase_price > 0 else 0.0,
            "source": "calculated"}

    return {
        "get_product_by_model_name": mock_get_product_by_model_name,
        "get_product_by_id": mock_get_product_by_id,
        "calculate_price_by_method": mock_calculate_price_by_method,
        "calculate_selling_price": mock_calculate_selling_price
    }


@pytest.mark.skipif(not INTEGRATION_AVAILABLE,
                    reason="Integration module not available")
class TestSolarCalculatorPricingIntegration:
    """Test cases for solar calculator pricing integration"""

    def test_initialization(self):
        """Test integration class initialization"""
        integration = SolarCalculatorPricingIntegration()

        assert integration is not None
        assert hasattr(integration, 'pricing_engine')
        assert hasattr(integration, 'key_manager')
        assert hasattr(integration, 'current_pricing_data')
        assert isinstance(integration.current_pricing_data, dict)

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    def test_module_pricing_calculation(
            self,
            mock_calc_selling,
            mock_calc_price,
            mock_get_product,
            sample_project_details,
            sample_product_data,
            mock_product_db_functions):
        """Test PV module pricing calculation with calculate_per support"""
        # Setup mocks
        mock_get_product.side_effect = mock_product_db_functions["get_product_by_model_name"]
        mock_calc_price.side_effect = mock_product_db_functions["calculate_price_by_method"]
        mock_calc_selling.side_effect = mock_product_db_functions["calculate_selling_price"]

        integration = SolarCalculatorPricingIntegration()

        # Test module pricing calculation
        module_pricing = integration._calculate_module_pricing(
            sample_project_details)

        assert module_pricing is not None
        assert module_pricing["component_type"] == "pv_module"
        assert module_pricing["model_name"] == "Test Module 400W"
        assert module_pricing["quantity"] == 20
        assert module_pricing["calculate_per"] == "Stück"
        assert module_pricing["total_price"] > 0
        assert "dynamic_keys" in module_pricing
        assert "product_specs" in module_pricing
        assert "margin_info" in module_pricing

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    def test_inverter_pricing_calculation(
            self,
            mock_calc_selling,
            mock_calc_price,
            mock_get_product,
            sample_project_details,
            sample_product_data,
            mock_product_db_functions):
        """Test inverter pricing calculation"""
        # Setup mocks
        mock_get_product.side_effect = mock_product_db_functions["get_product_by_model_name"]
        mock_calc_price.side_effect = mock_product_db_functions["calculate_price_by_method"]
        mock_calc_selling.side_effect = mock_product_db_functions["calculate_selling_price"]

        integration = SolarCalculatorPricingIntegration()

        # Test inverter pricing calculation
        inverter_pricing = integration._calculate_inverter_pricing(
            sample_project_details)

        assert inverter_pricing is not None
        assert inverter_pricing["component_type"] == "inverter"
        assert inverter_pricing["model_name"] == "Test Inverter 8kW"
        assert inverter_pricing["quantity"] == 1
        assert inverter_pricing["calculate_per"] == "Stück"
        assert inverter_pricing["total_price"] > 0
        assert "dynamic_keys" in inverter_pricing

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    def test_storage_pricing_calculation(
            self,
            mock_calc_selling,
            mock_calc_price,
            mock_get_product,
            sample_project_details,
            sample_product_data,
            mock_product_db_functions):
        """Test battery storage pricing calculation"""
        # Setup mocks
        mock_get_product.side_effect = mock_product_db_functions["get_product_by_model_name"]
        mock_calc_price.side_effect = mock_product_db_functions["calculate_price_by_method"]
        mock_calc_selling.side_effect = mock_product_db_functions["calculate_selling_price"]

        integration = SolarCalculatorPricingIntegration()

        # Test storage pricing calculation
        storage_pricing = integration._calculate_storage_pricing(
            sample_project_details)

        assert storage_pricing is not None
        assert storage_pricing["component_type"] == "storage"
        assert storage_pricing["model_name"] == "Test Battery 10kWh"
        assert storage_pricing["quantity"] >= 1
        assert storage_pricing["calculate_per"] == "Stück"
        assert storage_pricing["total_price"] > 0
        assert storage_pricing["desired_capacity"] == 10.0
        assert "dynamic_keys" in storage_pricing

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    def test_additional_components_pricing(
            self,
            mock_calc_selling,
            mock_calc_price,
            mock_get_product,
            sample_project_details,
            sample_product_data,
            mock_product_db_functions):
        """Test additional components pricing calculation"""
        # Setup mocks
        mock_get_product.side_effect = mock_product_db_functions["get_product_by_model_name"]
        mock_calc_price.side_effect = mock_product_db_functions["calculate_price_by_method"]
        mock_calc_selling.side_effect = mock_product_db_functions["calculate_selling_price"]

        integration = SolarCalculatorPricingIntegration()

        # Test additional components pricing
        additional_components = integration._calculate_additional_components_pricing(
            sample_project_details)

        assert isinstance(additional_components, list)
        assert len(additional_components) >= 2  # wallbox and ems

        # Check wallbox pricing
        wallbox_comp = next(
            (comp for comp in additional_components if comp["component_type"] == "wallbox"),
            None)
        assert wallbox_comp is not None
        assert wallbox_comp["model_name"] == "Test Wallbox 11kW"
        assert wallbox_comp["quantity"] == 1
        assert wallbox_comp["total_price"] > 0

        # Check EMS pricing (pauschal calculation)
        ems_comp = next(
            (comp for comp in additional_components if comp["component_type"] == "ems"),
            None)
        assert ems_comp is not None
        assert ems_comp["model_name"] == "Test EMS System"
        assert ems_comp["calculate_per"] == "pauschal"
        assert ems_comp["total_price"] > 0

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    def test_complete_pricing_calculation(
            self,
            mock_calc_selling,
            mock_calc_price,
            mock_get_product,
            sample_project_details,
            sample_product_data,
            mock_product_db_functions):
        """Test complete pricing calculation for all components"""
        # Setup mocks
        mock_get_product.side_effect = mock_product_db_functions["get_product_by_model_name"]
        mock_calc_price.side_effect = mock_product_db_functions["calculate_price_by_method"]
        mock_calc_selling.side_effect = mock_product_db_functions["calculate_selling_price"]

        integration = SolarCalculatorPricingIntegration()

        # Test complete pricing calculation
        pricing_result = integration.calculate_component_pricing(
            sample_project_details)

        assert pricing_result is not None
        assert "components" in pricing_result
        assert "base_price" in pricing_result
        assert "dynamic_keys" in pricing_result
        assert "calculation_timestamp" in pricing_result

        components = pricing_result["components"]
        assert len(components) >= 4  # module, inverter, storage, wallbox, ems

        # Verify total price is sum of component prices
        expected_total = sum(comp["total_price"] for comp in components)
        assert abs(pricing_result["base_price"] - expected_total) < 0.01

        # Verify dynamic keys are generated
        dynamic_keys = pricing_result["dynamic_keys"]
        assert len(dynamic_keys) > 0
        assert "PV_SYSTEM_BASE_PRICE" in dynamic_keys
        assert "PV_MODULE_TOTAL_PRICE" in dynamic_keys
        assert "INVERTER_TOTAL_PRICE" in dynamic_keys

    def test_calculate_per_methods(self, mock_product_db_functions):
        """Test different calculate_per calculation methods"""
        calc_method = mock_product_db_functions["calculate_price_by_method"]

        # Test per piece calculation
        result = calc_method(100.0, 5, "Stück")
        assert result == 500.0

        # Test per meter calculation
        result = calc_method(10.0, 50, "Meter")
        assert result == 500.0

        # Test lump sum calculation
        result = calc_method(1000.0, 3, "pauschal")
        assert result == 1000.0  # Quantity ignored for lump sum

        # Test kWp calculation
        product_specs = {"capacity_w": 400.0}
        result = calc_method(200.0, 10, "kWp", product_specs)
        expected = 200.0 * 0.4 * 10  # 200 * (400W/1000) * 10
        assert result == expected

    @patch('solar_calculator_pricing_integration.get_product_by_model_name')
    @patch('solar_calculator_pricing_integration.calculate_price_by_method')
    @patch('solar_calculator_pricing_integration.calculate_selling_price')
    def test_pricing_display_data(
            self,
            mock_calc_selling,
            mock_calc_price,
            mock_get_product,
            sample_project_details,
            sample_product_data,
            mock_product_db_functions):
        """Test pricing display data formatting"""
        # Setup mocks
        mock_get_product.side_effect = mock_product_db_functions["get_product_by_model_name"]
        mock_calc_price.side_effect = mock_product_db_functions["calculate_price_by_method"]
        mock_calc_selling.side_effect = mock_product_db_functions["calculate_selling_price"]

        integration = SolarCalculatorPricingIntegration()

        # Test pricing display data
        display_data = integration.get_pricing_display_data(
            sample_project_details)

        assert display_data is not None
        assert "display_components" in display_data
        assert "total_price" in display_data
        assert "formatted_total" in display_data

        display_components = display_data["display_components"]
        assert len(display_components) > 0

        # Check component display format
        for comp in display_components:
            assert "name" in comp
            assert "type" in comp
            assert "quantity" in comp
            assert "calculate_per" in comp
            assert "formatted_unit_price" in comp
            assert "formatted_total_price" in comp
            assert "€" in comp["formatted_unit_price"]
            assert "€" in comp["formatted_total_price"]

    def test_pricing_cache_functionality(self, sample_project_details):
        """Test pricing cache functionality"""
        integration = SolarCalculatorPricingIntegration()

        # Initially no cached data
        cached_data = integration.get_cached_pricing(sample_project_details)
        assert cached_data is None

        # Set some cached data
        integration.current_pricing_data = {
            "components": [],
            "base_price": 1000.0,
            "project_details_hash": integration._hash_project_details(sample_project_details)
        }

        # Should return cached data for same project details
        cached_data = integration.get_cached_pricing(sample_project_details)
        assert cached_data is not None
        assert cached_data["base_price"] == 1000.0

        # Should return None for different project details
        different_details = sample_project_details.copy()
        different_details["module_quantity"] = 30
        cached_data = integration.get_cached_pricing(different_details)
        assert cached_data is None

        # Test cache clearing
        integration.clear_pricing_cache()
        cached_data = integration.get_cached_pricing(sample_project_details)
        assert cached_data is None

    def test_validation_configuration(self):
        """Test pricing configuration validation"""
        integration = SolarCalculatorPricingIntegration()

        validation_result = integration.validate_pricing_configuration()

        assert "is_valid" in validation_result
        assert "errors" in validation_result
        assert "warnings" in validation_result
        assert isinstance(validation_result["errors"], list)
        assert isinstance(validation_result["warnings"], list)

    def test_currency_formatting(self):
        """Test German currency formatting"""
        integration = SolarCalculatorPricingIntegration()

        # Test various amounts
        assert integration._format_currency(1234.56) == "1.234,56 €"
        assert integration._format_currency(0.0) == "0,00 €"
        assert integration._format_currency(999.99) == "999,99 €"
        assert integration._format_currency(10000.0) == "10.000,00 €"

    def test_project_details_hashing(self, sample_project_details):
        """Test project details hashing for cache management"""
        integration = SolarCalculatorPricingIntegration()

        # Same details should produce same hash
        hash1 = integration._hash_project_details(sample_project_details)
        hash2 = integration._hash_project_details(sample_project_details)
        assert hash1 == hash2

        # Different details should produce different hash
        different_details = sample_project_details.copy()
        different_details["module_quantity"] = 30
        hash3 = integration._hash_project_details(different_details)
        assert hash1 != hash3


@pytest.mark.skipif(not INTEGRATION_AVAILABLE,
                    reason="Integration module not available")
class TestIntegrationFunctions:
    """Test standalone integration functions"""

    @patch('solar_calculator_pricing_integration.solar_pricing_integration')
    def test_integrate_pricing_with_solar_calculator(
            self, mock_integration, sample_project_details):
        """Test main integration function"""
        mock_integration.calculate_component_pricing.return_value = {
            "components": [],
            "base_price": 1000.0,
            "dynamic_keys": {}
        }

        result = integrate_pricing_with_solar_calculator(
            sample_project_details)

        assert result is not None
        assert "components" in result
        assert "base_price" in result
        mock_integration.calculate_component_pricing.assert_called_once_with(
            sample_project_details)

    @patch('solar_calculator_pricing_integration.solar_pricing_integration')
    def test_get_pricing_display_for_ui(
            self, mock_integration, sample_project_details):
        """Test pricing display function"""
        mock_integration.get_pricing_display_data.return_value = {
            "display_components": [],
            "total_price": 1000.0,
            "formatted_total": "1.000,00 €"
        }

        result = get_pricing_display_for_ui(sample_project_details)

        assert result is not None
        assert "display_components" in result
        assert "formatted_total" in result
        mock_integration.get_pricing_display_data.assert_called_once_with(
            sample_project_details)

    @patch('solar_calculator_pricing_integration.solar_pricing_integration')
    def test_update_pricing_in_session_state(
            self, mock_integration, sample_project_details):
        """Test session state update function"""
        update_pricing_in_session_state(sample_project_details)

        mock_integration.update_session_state_pricing.assert_called_once_with(
            sample_project_details)


if __name__ == "__main__":
    pytest.main([__file__])
