"""Tests for VAT Manager

Tests VAT calculation system including different VAT rates,
category-specific handling, and net/gross price calculations.
"""


import pytest

from pricing.pricing_errors import CalculationError, ValidationError
from pricing.vat_manager import (
    VATCategory,
    VATManager,
    VATRate,
    get_vat_manager,
)


class TestVATRate:
    """Test VAT rate configuration"""

    def test_valid_vat_rate_creation(self):
        """Test creating valid VAT rate"""
        rate = VATRate(
            category=VATCategory.STANDARD,
            rate_percent=19.0,
            description="German standard VAT",
            country_code="DE"
        )

        assert rate.category == VATCategory.STANDARD
        assert rate.rate_percent == 19.0
        assert rate.description == "German standard VAT"
        assert rate.country_code == "DE"

    def test_invalid_vat_rate_negative(self):
        """Test that negative VAT rates are rejected"""
        with pytest.raises(ValidationError, match="VAT rate must be between 0 and 100"):
            VATRate(
                category=VATCategory.STANDARD,
                rate_percent=-5.0,
                description="Invalid negative rate"
            )

    def test_invalid_vat_rate_over_100(self):
        """Test that VAT rates over 100% are rejected"""
        with pytest.raises(ValidationError, match="VAT rate must be between 0 and 100"):
            VATRate(
                category=VATCategory.STANDARD,
                rate_percent=150.0,
                description="Invalid high rate"
            )

    def test_zero_category_validation(self):
        """Test that ZERO category must have 0% rate"""
        with pytest.raises(ValidationError, match="Zero VAT category must have 0% rate"):
            VATRate(
                category=VATCategory.ZERO,
                rate_percent=19.0,
                description="Invalid zero category"
            )

    def test_exempt_category_validation(self):
        """Test that EXEMPT category must have 0% rate"""
        with pytest.raises(ValidationError, match="Exempt VAT category must have 0% rate"):
            VATRate(
                category=VATCategory.EXEMPT,
                rate_percent=7.0,
                description="Invalid exempt category"
            )


class TestVATManager:
    """Test VAT manager functionality"""

    def test_initialization_germany(self):
        """Test VAT manager initialization for Germany"""
        manager = VATManager("DE")

        assert manager.country_code == "DE"
        assert VATCategory.STANDARD in manager.vat_rates
        assert manager.vat_rates[VATCategory.STANDARD].rate_percent == 19.0
        assert manager.vat_rates[VATCategory.REDUCED].rate_percent == 7.0
        assert manager.vat_rates[VATCategory.ZERO].rate_percent == 0.0
        assert manager.vat_rates[VATCategory.EXEMPT].rate_percent == 0.0

    def test_initialization_other_country(self):
        """Test VAT manager initialization for other countries"""
        manager = VATManager("FR")

        assert manager.country_code == "FR"
        assert manager.vat_rates[VATCategory.STANDARD].rate_percent == 20.0
        assert manager.vat_rates[VATCategory.REDUCED].rate_percent == 10.0

    def test_set_vat_rate(self):
        """Test setting custom VAT rate"""
        manager = VATManager("DE")

        manager.set_vat_rate(
            VATCategory.STANDARD,
            21.0,
            "Custom standard rate")

        assert manager.vat_rates[VATCategory.STANDARD].rate_percent == 21.0
        assert manager.vat_rates[VATCategory.STANDARD].description == "Custom standard rate"

    def test_set_invalid_vat_rate(self):
        """Test setting invalid VAT rate"""
        manager = VATManager("DE")

        with pytest.raises(ValidationError):
            manager.set_vat_rate(VATCategory.STANDARD, -5.0)

    def test_category_mapping(self):
        """Test product category to VAT mapping"""
        manager = VATManager("DE")

        manager.set_category_vat_mapping(
            "Special Product", VATCategory.REDUCED)

        assert "Special Product" in manager.category_mappings
        assert manager.category_mappings["Special Product"].vat_category == VATCategory.REDUCED

    def test_category_mapping_with_override(self):
        """Test category mapping with override rate"""
        manager = VATManager("DE")

        manager.set_category_vat_mapping(
            "Custom Product",
            VATCategory.STANDARD,
            override_rate=15.0)

        mapping = manager.category_mappings["Custom Product"]
        assert mapping.vat_category == VATCategory.STANDARD
        assert mapping.override_rate == 15.0

    def test_invalid_override_rate(self):
        """Test invalid override rate"""
        manager = VATManager("DE")

        with pytest.raises(ValidationError, match="Override VAT rate must be between 0 and 100"):
            manager.set_category_vat_mapping(
                "Product", VATCategory.STANDARD, override_rate=150.0)

    def test_get_vat_rate_for_category_default(self):
        """Test getting VAT rate for unmapped category"""
        manager = VATManager("DE")

        rate = manager.get_vat_rate_for_category("Unknown Category")

        assert rate == 19.0  # Default standard rate

    def test_get_vat_rate_for_category_mapped(self):
        """Test getting VAT rate for mapped category"""
        manager = VATManager("DE")

        rate = manager.get_vat_rate_for_category("PV Module")

        assert rate == 19.0  # Standard rate for PV modules

    def test_get_vat_rate_for_category_with_override(self):
        """Test getting VAT rate for category with override"""
        manager = VATManager("DE")
        manager.set_category_vat_mapping(
            "Special Product",
            VATCategory.STANDARD,
            override_rate=15.0)

        rate = manager.get_vat_rate_for_category("Special Product")

        assert rate == 15.0


class TestVATCalculation:
    """Test VAT calculation functionality"""

    def test_basic_vat_calculation(self):
        """Test basic VAT calculation"""
        manager = VATManager("DE")

        result = manager.calculate_vat(1000.0, "PV Module")

        assert result.net_amount == 1000.0
        assert result.vat_rate_percent == 19.0
        assert result.vat_amount == 190.0
        assert result.gross_amount == 1190.0
        assert result.vat_category == VATCategory.STANDARD

    def test_vat_calculation_with_override(self):
        """Test VAT calculation with rate override"""
        manager = VATManager("DE")

        result = manager.calculate_vat(1000.0, vat_rate_override=21.0)

        assert result.net_amount == 1000.0
        assert result.vat_rate_percent == 21.0
        assert result.vat_amount == 210.0
        assert result.gross_amount == 1210.0

    def test_vat_calculation_reduced_rate(self):
        """Test VAT calculation with reduced rate"""
        manager = VATManager("DE")
        manager.set_category_vat_mapping("Books", VATCategory.REDUCED)

        result = manager.calculate_vat(100.0, "Books")

        assert result.net_amount == 100.0
        assert result.vat_rate_percent == 7.0
        # Allow for floating point precision
        assert abs(result.vat_amount - 7.0) < 0.01
        assert abs(result.gross_amount - 107.0) < 0.01
        assert result.vat_category == VATCategory.REDUCED

    def test_vat_calculation_zero_rate(self):
        """Test VAT calculation with zero rate"""
        manager = VATManager("DE")
        manager.set_category_vat_mapping("Export", VATCategory.ZERO)

        result = manager.calculate_vat(1000.0, "Export")

        assert result.net_amount == 1000.0
        assert result.vat_rate_percent == 0.0
        assert result.vat_amount == 0.0
        assert result.gross_amount == 1000.0
        assert result.vat_category == VATCategory.ZERO

    def test_vat_calculation_negative_amount(self):
        """Test VAT calculation with negative amount"""
        manager = VATManager("DE")

        with pytest.raises(CalculationError, match="VAT calculation failed"):
            manager.calculate_vat(-100.0)

    def test_vat_calculation_invalid_override(self):
        """Test VAT calculation with invalid override rate"""
        manager = VATManager("DE")

        with pytest.raises(CalculationError, match="VAT calculation failed"):
            manager.calculate_vat(1000.0, vat_rate_override=150.0)

    def test_vat_calculation_dynamic_keys(self):
        """Test that VAT calculation generates dynamic keys"""
        manager = VATManager("DE")

        result = manager.calculate_vat(1000.0, "PV Module")

        assert "VAT_PV_MODULE_NET_AMOUNT" in result.dynamic_keys
        assert "VAT_PV_MODULE_VAT_RATE" in result.dynamic_keys
        assert "VAT_PV_MODULE_VAT_AMOUNT" in result.dynamic_keys
        assert "VAT_PV_MODULE_GROSS_AMOUNT" in result.dynamic_keys
        assert result.dynamic_keys["VAT_PV_MODULE_NET_AMOUNT"] == 1000.0
        assert result.dynamic_keys["VAT_PV_MODULE_VAT_AMOUNT"] == 190.0


class TestMixedVATCalculation:
    """Test mixed VAT calculations for multiple items"""

    def test_mixed_vat_empty_items(self):
        """Test mixed VAT calculation with empty items"""
        manager = VATManager("DE")

        result = manager.calculate_mixed_vat([])

        assert result.net_amount == 0.0
        assert result.vat_amount == 0.0
        assert result.gross_amount == 0.0

    def test_mixed_vat_single_category(self):
        """Test mixed VAT calculation with single category"""
        manager = VATManager("DE")

        items = [
            {"net_amount": 1000.0, "category": "PV Module"},
            {"net_amount": 500.0, "category": "PV Module"}
        ]

        result = manager.calculate_mixed_vat(items)

        assert result.net_amount == 1500.0
        assert result.vat_amount == 285.0  # 1500 * 0.19
        assert result.gross_amount == 1785.0
        assert result.vat_rate_percent == 19.0

    def test_mixed_vat_multiple_categories(self):
        """Test mixed VAT calculation with multiple categories"""
        manager = VATManager("DE")
        manager.set_category_vat_mapping("Books", VATCategory.REDUCED)

        items = [
            {"net_amount": 1000.0, "category": "PV Module"},  # 19% VAT
            {"net_amount": 100.0, "category": "Books"}        # 7% VAT
        ]

        result = manager.calculate_mixed_vat(items)

        assert result.net_amount == 1100.0
        assert result.vat_amount == 197.0  # 1000*0.19 + 100*0.07
        assert result.gross_amount == 1297.0

        # Check effective rate
        expected_effective_rate = (197.0 / 1100.0) * 100.0
        assert abs(result.vat_rate_percent - expected_effective_rate) < 0.01

    def test_mixed_vat_category_breakdown(self):
        """Test mixed VAT calculation category breakdown"""
        manager = VATManager("DE")
        manager.set_category_vat_mapping("Service", VATCategory.REDUCED)

        items = [
            {"net_amount": 1000.0, "category": "PV Module"},
            {"net_amount": 500.0, "category": "PV Module"},
            {"net_amount": 200.0, "category": "Service"}
        ]

        result = manager.calculate_mixed_vat(items)

        breakdown = result.breakdown["category_breakdowns"]

        # Check PV Module breakdown
        assert "PV Module" in breakdown
        assert breakdown["PV Module"]["net_amount"] == 1500.0
        assert breakdown["PV Module"]["vat_amount"] == 285.0
        assert breakdown["PV Module"]["vat_rate"] == 19.0
        assert len(breakdown["PV Module"]["items"]) == 2

        # Check Service breakdown
        assert "Service" in breakdown
        assert breakdown["Service"]["net_amount"] == 200.0
        assert abs(breakdown["Service"]["vat_amount"] -
                   14.0) < 0.01  # Allow for floating point precision
        assert breakdown["Service"]["vat_rate"] == 7.0
        assert len(breakdown["Service"]["items"]) == 1

    def test_mixed_vat_negative_amount(self):
        """Test mixed VAT calculation with negative amount"""
        manager = VATManager("DE")

        items = [
            {"net_amount": -100.0, "category": "PV Module"}
        ]

        with pytest.raises(CalculationError, match="Mixed VAT calculation failed"):
            manager.calculate_mixed_vat(items)


class TestNetFromGrossCalculation:
    """Test net from gross calculation"""

    def test_calculate_net_from_gross_standard(self):
        """Test calculating net from gross with standard VAT"""
        manager = VATManager("DE")

        result = manager.calculate_net_from_gross(1190.0, 19.0)

        assert abs(result["net_amount"] - 1000.0) < 0.01
        assert abs(result["vat_amount"] - 190.0) < 0.01
        assert result["gross_amount"] == 1190.0
        assert result["vat_rate_percent"] == 19.0

    def test_calculate_net_from_gross_reduced(self):
        """Test calculating net from gross with reduced VAT"""
        manager = VATManager("DE")

        result = manager.calculate_net_from_gross(107.0, 7.0)

        assert abs(result["net_amount"] - 100.0) < 0.01
        assert abs(result["vat_amount"] - 7.0) < 0.01
        assert result["gross_amount"] == 107.0
        assert result["vat_rate_percent"] == 7.0

    def test_calculate_net_from_gross_zero_vat(self):
        """Test calculating net from gross with zero VAT"""
        manager = VATManager("DE")

        result = manager.calculate_net_from_gross(1000.0, 0.0)

        assert result["net_amount"] == 1000.0
        assert result["vat_amount"] == 0.0
        assert result["gross_amount"] == 1000.0
        assert result["vat_rate_percent"] == 0.0

    def test_calculate_net_from_gross_negative_amount(self):
        """Test calculating net from gross with negative amount"""
        manager = VATManager("DE")

        with pytest.raises(CalculationError, match="Net from gross calculation failed"):
            manager.calculate_net_from_gross(-100.0, 19.0)

    def test_calculate_net_from_gross_invalid_rate(self):
        """Test calculating net from gross with invalid VAT rate"""
        manager = VATManager("DE")

        with pytest.raises(CalculationError, match="Net from gross calculation failed"):
            manager.calculate_net_from_gross(1190.0, 150.0)


class TestVATSummaryAndValidation:
    """Test VAT summary and validation functionality"""

    def test_get_vat_summary(self):
        """Test getting VAT configuration summary"""
        manager = VATManager("DE")
        manager.set_category_vat_mapping(
            "Custom Product",
            VATCategory.REDUCED,
            override_rate=5.0)

        summary = manager.get_vat_summary()

        assert summary["country_code"] == "DE"
        assert "vat_rates" in summary
        assert "category_mappings" in summary

        # Check VAT rates
        assert "standard" in summary["vat_rates"]
        assert summary["vat_rates"]["standard"]["rate_percent"] == 19.0

        # Check category mappings
        assert "Custom Product" in summary["category_mappings"]
        assert summary["category_mappings"]["Custom Product"]["vat_category"] == "reduced"
        assert summary["category_mappings"]["Custom Product"]["override_rate"] == 5.0

    def test_validate_vat_configuration_valid(self):
        """Test validation of valid VAT configuration"""
        manager = VATManager("DE")

        issues = manager.validate_vat_configuration()

        assert len(issues) == 0

    def test_validate_vat_configuration_invalid_rate(self):
        """Test validation with invalid VAT rate"""
        manager = VATManager("DE")

        # Manually set invalid rate to test validation
        manager.vat_rates[VATCategory.STANDARD].rate_percent = 150.0

        issues = manager.validate_vat_configuration()

        assert len(issues) > 0
        assert any(
            "Invalid VAT rate for standard" in issue for issue in issues)

    def test_validate_vat_configuration_invalid_override(self):
        """Test validation with invalid override rate"""
        manager = VATManager("DE")
        manager.set_category_vat_mapping("Test", VATCategory.STANDARD)

        # Manually set invalid override to test validation
        manager.category_mappings["Test"].override_rate = -5.0

        issues = manager.validate_vat_configuration()

        assert len(issues) > 0
        assert any(
            "Invalid override rate for category 'Test'" in issue for issue in issues)


class TestGlobalVATManager:
    """Test global VAT manager instance"""

    def test_get_vat_manager_singleton(self):
        """Test that get_vat_manager returns singleton instance"""
        manager1 = get_vat_manager("DE")
        manager2 = get_vat_manager("DE")

        assert manager1 is manager2

    def test_get_vat_manager_different_country(self):
        """Test that different country codes create new instances"""
        manager_de = get_vat_manager("DE")
        manager_fr = get_vat_manager("FR")

        assert manager_de is not manager_fr
        assert manager_de.country_code == "DE"
        assert manager_fr.country_code == "FR"


class TestVATIntegrationScenarios:
    """Test real-world VAT calculation scenarios"""

    def test_pv_system_vat_calculation(self):
        """Test VAT calculation for complete PV system"""
        manager = VATManager("DE")

        # PV system components
        items = [
            {"net_amount": 3600.0,
             "category": "PV Module"},
            # 20 modules @ 180€
            {"net_amount": 800.0, "category": "Inverter"},        # 1 inverter
            {"net_amount": 3500.0, "category": "Battery Storage"},  # 1 battery
            {"net_amount": 500.0, "category": "Mounting System"},  # Mounting
            {"net_amount": 200.0, "category": "Cables"},          # Cables
            {"net_amount": 1000.0, "category": "Installation Service"}  # Installation
        ]

        result = manager.calculate_mixed_vat(items)

        expected_net = 9600.0
        expected_vat = 1824.0  # 19% of 9600
        expected_gross = 11424.0

        assert result.net_amount == expected_net
        assert result.vat_amount == expected_vat
        assert result.gross_amount == expected_gross
        assert result.vat_rate_percent == 19.0

    def test_mixed_system_with_subsidies(self):
        """Test VAT calculation with subsidized components"""
        manager = VATManager("DE")

        # Set subsidy category to zero VAT
        manager.set_category_vat_mapping("Subsidy", VATCategory.ZERO)

        items = [
            {"net_amount": 5000.0, "category": "Heat Pump"},  # 19% VAT
            # This should fail due to negative amount
            {"net_amount": -1000.0, "category": "Subsidy"}
        ]

        with pytest.raises(CalculationError, match="Mixed VAT calculation failed"):
            manager.calculate_mixed_vat(items)

    def test_export_system_zero_vat(self):
        """Test VAT calculation for export (zero VAT)"""
        manager = VATManager("DE")
        manager.set_category_vat_mapping("Export System", VATCategory.ZERO)

        result = manager.calculate_vat(10000.0, "Export System")

        assert result.net_amount == 10000.0
        assert result.vat_amount == 0.0
        assert result.gross_amount == 10000.0
        assert result.vat_category == VATCategory.ZERO

    def test_b2b_vs_b2c_pricing(self):
        """Test different VAT handling for B2B vs B2C"""
        manager = VATManager("DE")

        # B2C calculation (with VAT)
        b2c_result = manager.calculate_vat(1000.0, "PV Module")

        # B2B calculation (VAT exempt)
        manager.set_category_vat_mapping("B2B Product", VATCategory.EXEMPT)
        b2b_result = manager.calculate_vat(1000.0, "B2B Product")

        assert b2c_result.gross_amount == 1190.0
        assert b2b_result.gross_amount == 1000.0
        assert b2c_result.vat_amount == 190.0
        assert b2b_result.vat_amount == 0.0


if __name__ == "__main__":
    pytest.main([__file__])
