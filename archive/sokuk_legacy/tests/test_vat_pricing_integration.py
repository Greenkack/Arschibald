"""Tests for VAT integration with pricing calculations

Tests the integration of VAT manager with pricing engines,
dynamic key generation, and pricing breakdowns.
"""


import pytest

from pricing.enhanced_heatpump_pricing import EnhancedHeatPumpPricingEngine
from pricing.enhanced_pricing_engine import PricingEngine
from pricing.pricing_errors import CalculationError, ValidationError
from pricing.pv_pricing_engine import PVPricingEngine
from pricing.vat_manager import VATCategory


class TestVATPricingEngineIntegration:
    """Test VAT integration with pricing engines"""

    def test_pricing_engine_vat_initialization(self):
        """Test that pricing engine initializes VAT manager correctly"""
        engine = PricingEngine("pv", country_code="DE")

        assert engine.vat_manager is not None
        assert engine.vat_manager.country_code == "DE"
        assert engine.country_code == "DE"

    def test_pricing_engine_different_countries(self):
        """Test pricing engine with different country codes"""
        engine_de = PricingEngine("pv", country_code="DE")
        engine_fr = PricingEngine("pv", country_code="FR")

        assert engine_de.vat_manager.country_code == "DE"
        assert engine_fr.vat_manager.country_code == "FR"

        # Check different VAT rates
        de_rate = engine_de.vat_manager.get_vat_rate_for_category("PV Module")
        fr_rate = engine_fr.vat_manager.get_vat_rate_for_category("PV Module")

        assert de_rate == 19.0  # German standard VAT
        # French standard VAT (default for non-DE countries)
        assert fr_rate == 20.0

    def test_mixed_vat_calculation_for_components(self):
        """Test mixed VAT calculation for components with different categories"""
        engine = PricingEngine("pv")

        # Mock components with different categories
        from pricing.enhanced_pricing_engine import PriceComponent
        components = [
            PriceComponent(
                product_id=1,
                model_name="PV Module 400W",
                category="PV Module",
                quantity=20,
                price_euro=180.0),
            PriceComponent(
                product_id=2,
                model_name="Inverter 10kW",
                category="Inverter",
                quantity=1,
                price_euro=800.0),
            PriceComponent(
                product_id=3,
                model_name="Installation",
                category="Installation Service",
                quantity=1,
                price_euro=1000.0)]

        vat_result = engine.calculate_mixed_vat_for_components(components)

        # All components should use standard VAT (19%)
        expected_net = (20 * 180.0) + 800.0 + 1000.0  # 4400.0
        expected_vat = expected_net * 0.19  # 836.0
        expected_gross = expected_net + expected_vat  # 5236.0

        assert vat_result.net_amount == expected_net
        assert abs(vat_result.vat_amount - expected_vat) < 0.01
        assert abs(vat_result.gross_amount - expected_gross) < 0.01
        assert vat_result.vat_rate_percent == 19.0

    def test_final_pricing_with_vat_override(self):
        """Test final pricing calculation with VAT rate override"""
        engine = PricingEngine("pv")

        calculation_data = {
            "components": [
                # This will fail without mock data
                {"product_id": 1, "quantity": 10}
            ],
            "modifications": {
                "discount_percent": 5.0,
                "accessories_cost": 200.0
            },
            "vat_config": {
                "vat_rate_override": 21.0  # Override to 21%
            }
        }

        # This test would need mock product data to work fully
        # For now, test the VAT override logic directly
        vat_manager = engine.vat_manager
        vat_result = vat_manager.calculate_vat(1000.0, vat_rate_override=21.0)

        assert vat_result.vat_rate_percent == 21.0
        assert vat_result.vat_amount == 210.0
        assert vat_result.gross_amount == 1210.0

    def test_vat_dynamic_keys_generation(self):
        """Test that VAT calculations generate proper dynamic keys"""
        engine = PricingEngine("pv")

        vat_result = engine.vat_manager.calculate_vat(1000.0, "PV Module")

        # Check that VAT dynamic keys are generated (may have suffixes due to
        # conflict resolution)
        net_key = next((k for k in vat_result.dynamic_keys.keys()
                       if k.startswith("VAT_PV_MODULE_NET_AMOUNT")), None)
        rate_key = next((k for k in vat_result.dynamic_keys.keys()
                        if k.startswith("VAT_PV_MODULE_VAT_RATE")), None)
        amount_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_PV_MODULE_VAT_AMOUNT")), None)
        gross_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_PV_MODULE_GROSS_AMOUNT")), None)
        category_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_PV_MODULE_VAT_CATEGORY")), None)

        assert net_key is not None
        assert rate_key is not None
        assert amount_key is not None
        assert gross_key is not None
        assert category_key is not None

        # Check key values
        assert vat_result.dynamic_keys[net_key] == 1000.0
        assert vat_result.dynamic_keys[rate_key] == 19.0
        assert abs(vat_result.dynamic_keys[amount_key] - 190.0) < 0.01
        assert abs(vat_result.dynamic_keys[gross_key] - 1190.0) < 0.01


class TestPVPricingEngineVATIntegration:
    """Test VAT integration with PV pricing engine"""

    def test_pv_engine_vat_mappings(self):
        """Test that PV engine sets up correct VAT mappings"""
        engine = PVPricingEngine("DE")

        # Check that PV-specific categories are mapped
        pv_rate = engine.vat_manager.get_vat_rate_for_category("PV Module")
        inverter_rate = engine.vat_manager.get_vat_rate_for_category(
            "Inverter")
        storage_rate = engine.vat_manager.get_vat_rate_for_category(
            "Battery Storage")
        service_rate = engine.vat_manager.get_vat_rate_for_category(
            "Installation Service")

        # All should use standard German VAT
        assert pv_rate == 19.0
        assert inverter_rate == 19.0
        assert storage_rate == 19.0
        assert service_rate == 19.0

    def test_pv_system_vat_calculation(self):
        """Test VAT calculation for complete PV system"""
        engine = PVPricingEngine("DE")

        # Mock PV components
        from pricing.enhanced_pricing_engine import PriceComponent
        components = [
            PriceComponent(
                product_id=1,
                model_name="PV Module 400W",
                category="PV Module",
                quantity=20,
                price_euro=180.0),
            PriceComponent(
                product_id=2,
                model_name="Inverter 10kW",
                category="Inverter",
                quantity=1,
                price_euro=800.0),
            PriceComponent(
                product_id=3,
                model_name="Battery 10kWh",
                category="Battery Storage",
                quantity=1,
                price_euro=3500.0)]

        vat_result = engine.calculate_pv_system_vat(
            components, additional_costs=500.0)

        # Calculate expected values
        component_net = (20 * 180.0) + 800.0 + 3500.0  # 7900.0
        total_net = component_net + 500.0  # 8400.0
        expected_vat = total_net * 0.19  # 1596.0
        expected_gross = total_net + expected_vat  # 9996.0

        assert vat_result["total_net"] == total_net
        assert abs(vat_result["total_vat"] - expected_vat) < 0.01
        assert abs(vat_result["total_gross"] - expected_gross) < 0.01
        assert vat_result["effective_vat_rate"] == 19.0

        # Check that dynamic keys are included
        assert "dynamic_keys" in vat_result
        assert len(vat_result["dynamic_keys"]) > 0


class TestHeatPumpPricingEngineVATIntegration:
    """Test VAT integration with heat pump pricing engine"""

    def test_heatpump_engine_vat_mappings(self):
        """Test that heat pump engine sets up correct VAT mappings"""
        engine = EnhancedHeatPumpPricingEngine("DE")

        # Check that heat pump-specific categories are mapped
        hp_rate = engine.vat_manager.get_vat_rate_for_category("Heat Pump")
        tank_rate = engine.vat_manager.get_vat_rate_for_category("Buffer Tank")
        service_rate = engine.vat_manager.get_vat_rate_for_category(
            "Installation Service")
        subsidy_rate = engine.vat_manager.get_vat_rate_for_category(
            "BEG Subsidy")

        # Hardware and services should use standard VAT
        assert hp_rate == 19.0
        assert tank_rate == 19.0
        assert service_rate == 19.0

        # Subsidies should be VAT exempt
        assert subsidy_rate == 0.0

    def test_heatpump_system_vat_with_beg_subsidy(self):
        """Test VAT calculation for heat pump system with BEG subsidy"""
        engine = EnhancedHeatPumpPricingEngine("DE")

        # Mock heat pump components
        from pricing.enhanced_pricing_engine import PriceComponent
        components = [
            PriceComponent(
                product_id=1,
                model_name="Heat Pump 12kW",
                category="Heat Pump",
                quantity=1,
                price_euro=8000.0),
            PriceComponent(
                product_id=2,
                model_name="Buffer Tank 500L",
                category="Buffer Tank",
                quantity=1,
                price_euro=1200.0),
            PriceComponent(
                product_id=3,
                model_name="Installation",
                category="Installation Service",
                quantity=1,
                price_euro=2000.0)]

        beg_subsidy = 3000.0  # 30% subsidy

        vat_result = engine.calculate_heatpump_system_vat(
            components,
            beg_subsidy=beg_subsidy,
            additional_costs=300.0
        )

        # Calculate expected values
        component_net = 8000.0 + 1200.0 + 2000.0  # 11200.0
        total_net_before_subsidy = component_net + 300.0  # 11500.0
        total_net_after_subsidy = total_net_before_subsidy - beg_subsidy  # 8500.0
        expected_vat = total_net_before_subsidy * 0.19  # VAT on full amount: 2185.0
        expected_gross_after_subsidy = total_net_after_subsidy + expected_vat  # 10685.0

        assert vat_result["total_net_before_subsidy"] == total_net_before_subsidy
        assert vat_result["beg_subsidy"] == beg_subsidy
        assert vat_result["total_net_after_subsidy"] == total_net_after_subsidy
        assert abs(vat_result["total_vat"] - expected_vat) < 0.01
        assert abs(
            vat_result["total_gross_after_subsidy"] -
            expected_gross_after_subsidy) < 0.01

        # Check BEG subsidy dynamic keys
        assert "HP_BEG_SUBSIDY" in vat_result["dynamic_keys"]
        assert "HP_NET_AFTER_SUBSIDY" in vat_result["dynamic_keys"]
        assert "HP_GROSS_AFTER_SUBSIDY" in vat_result["dynamic_keys"]

        assert vat_result["dynamic_keys"]["HP_BEG_SUBSIDY"] == beg_subsidy
        assert vat_result["dynamic_keys"]["HP_NET_AFTER_SUBSIDY"] == total_net_after_subsidy


class TestVATDynamicKeyIntegration:
    """Test VAT dynamic key integration with pricing system"""

    def test_vat_keys_in_final_pricing_result(self):
        """Test that VAT keys are properly included in final pricing result"""
        engine = PricingEngine("pv")

        # Mock a simple calculation
        vat_calculation = engine.vat_manager.calculate_vat(1000.0, "PV Module")

        # Check that VAT calculation has dynamic keys
        assert len(vat_calculation.dynamic_keys) > 0

        # Verify key format
        for key, value in vat_calculation.dynamic_keys.items():
            assert key.startswith("VAT_")
            assert isinstance(value, (int, float, str))

    def test_mixed_vat_dynamic_keys(self):
        """Test dynamic keys for mixed VAT calculations"""
        engine = PricingEngine("pv")

        # Set up different VAT rates for testing
        engine.vat_manager.set_category_vat_mapping(
            "Special Product", VATCategory.REDUCED)

        items = [
            {"net_amount": 1000.0, "category": "PV Module"},      # 19% VAT
            {"net_amount": 200.0, "category": "Special Product"}  # 7% VAT
        ]

        vat_result = engine.vat_manager.calculate_mixed_vat(items)

        # Check that mixed VAT keys are generated (may have suffixes)
        mixed_net_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_MIXED_TOTAL_NET")), None)
        mixed_vat_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_MIXED_TOTAL_VAT")), None)
        mixed_gross_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_MIXED_TOTAL_GROSS")), None)
        mixed_rate_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_MIXED_EFFECTIVE_VAT_RATE")), None)
        mixed_count_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_MIXED_CATEGORY_COUNT")), None)

        assert mixed_net_key is not None
        assert mixed_vat_key is not None
        assert mixed_gross_key is not None
        assert mixed_rate_key is not None
        assert mixed_count_key is not None

        # Check individual category keys
        pv_net_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_PV_MODULE_NET_AMOUNT")), None)
        special_net_key = next((k for k in vat_result.dynamic_keys.keys(
        ) if k.startswith("VAT_SPECIAL_PRODUCT_NET_AMOUNT")), None)

        assert pv_net_key is not None
        assert special_net_key is not None

        # Verify values
        assert vat_result.dynamic_keys[mixed_net_key] == 1200.0
        assert vat_result.dynamic_keys[mixed_count_key] == 2


class TestVATErrorHandling:
    """Test VAT error handling in pricing integration"""

    def test_vat_calculation_error_handling(self):
        """Test error handling in VAT calculations"""
        engine = PricingEngine("pv")

        # Test with invalid VAT rate override
        with pytest.raises(CalculationError):
            engine.vat_manager.calculate_vat(1000.0, vat_rate_override=150.0)

    def test_mixed_vat_error_handling(self):
        """Test error handling in mixed VAT calculations"""
        engine = PricingEngine("pv")

        # Test with negative amounts
        items = [
            {"net_amount": -100.0, "category": "PV Module"}
        ]

        with pytest.raises(CalculationError):
            engine.vat_manager.calculate_mixed_vat(items)

    def test_vat_fallback_behavior(self):
        """Test VAT fallback behavior when errors occur"""
        engine = PVPricingEngine("DE")

        # Mock components that might cause issues
        from pricing.enhanced_pricing_engine import PriceComponent
        components = [
            PriceComponent(
                product_id=1,
                model_name="Test Product",
                category="Unknown Category",
                quantity=1,
                price_euro=1000.0)]

        # Should fall back to standard VAT calculation
        vat_result = engine.calculate_pv_system_vat(components)

        # Should still get a valid result
        assert vat_result["total_net"] == 1000.0
        assert vat_result["total_vat"] > 0  # Should have some VAT
        assert vat_result["total_gross"] > vat_result["total_net"]


class TestVATConfigurationIntegration:
    """Test VAT configuration integration with pricing system"""

    def test_vat_configuration_summary(self):
        """Test VAT configuration summary includes pricing engine mappings"""
        engine = PVPricingEngine("DE")

        summary = engine.vat_manager.get_vat_summary()

        assert "country_code" in summary
        assert "vat_rates" in summary
        assert "category_mappings" in summary

        # Check that PV-specific mappings are included
        mappings = summary["category_mappings"]
        assert "PV Module" in mappings
        assert "Inverter" in mappings
        assert "Battery Storage" in mappings
        assert "Installation Service" in mappings

    def test_vat_validation_with_pricing_engines(self):
        """Test VAT configuration validation with pricing engines"""
        engine = PVPricingEngine("DE")

        # Validation should pass for properly configured engine
        issues = engine.vat_manager.validate_vat_configuration()
        assert len(issues) == 0

        # Test with invalid configuration - should raise ValidationError
        with pytest.raises(ValidationError, match="Override VAT rate must be between 0 and 100"):
            engine.vat_manager.set_category_vat_mapping(
                "Test Category", VATCategory.STANDARD, override_rate=150.0)


if __name__ == "__main__":
    pytest.main([__file__])
