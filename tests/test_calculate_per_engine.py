"""Tests for Calculate Per Engine

Comprehensive tests for all calculate_per scenarios and feature integrations.
"""


import pytest

from pricing.calculate_per_engine import (
    CalculatePerEngine,
    CalculationContext,
    CalculationMethod,
    calculate_price_by_method,
    get_supported_calculation_methods,
    validate_calculation_method,
)
from pricing.pricing_errors import CalculationError


class TestCalculationMethod:
    """Test CalculationMethod enum and string conversion"""

    def test_from_string_standard_values(self):
        """Test conversion of standard string values"""
        assert CalculationMethod.from_string(
            "Stück") == CalculationMethod.PER_PIECE
        assert CalculationMethod.from_string(
            "Meter") == CalculationMethod.PER_METER
        assert CalculationMethod.from_string(
            "pauschal") == CalculationMethod.LUMP_SUM
        assert CalculationMethod.from_string(
            "kWp") == CalculationMethod.PER_KWP
        assert CalculationMethod.from_string(
            "m²") == CalculationMethod.PER_SQUARE_METER
        assert CalculationMethod.from_string(
            "Stunde") == CalculationMethod.PER_HOUR

    def test_from_string_case_insensitive(self):
        """Test case insensitive conversion"""
        assert CalculationMethod.from_string(
            "STÜCK") == CalculationMethod.PER_PIECE
        assert CalculationMethod.from_string(
            "meter") == CalculationMethod.PER_METER
        assert CalculationMethod.from_string(
            "PAUSCHAL") == CalculationMethod.LUMP_SUM
        assert CalculationMethod.from_string(
            "KWP") == CalculationMethod.PER_KWP

    def test_from_string_english_variants(self):
        """Test English variant conversions"""
        assert CalculationMethod.from_string(
            "piece") == CalculationMethod.PER_PIECE
        assert CalculationMethod.from_string(
            "unit") == CalculationMethod.PER_PIECE
        assert CalculationMethod.from_string(
            "lump_sum") == CalculationMethod.LUMP_SUM
        assert CalculationMethod.from_string(
            "flat") == CalculationMethod.LUMP_SUM
        assert CalculationMethod.from_string(
            "hour") == CalculationMethod.PER_HOUR

    def test_from_string_empty_or_invalid(self):
        """Test handling of empty or invalid strings"""
        assert CalculationMethod.from_string("") == CalculationMethod.PER_PIECE
        assert CalculationMethod.from_string(
            None) == CalculationMethod.PER_PIECE
        assert CalculationMethod.from_string(
            "invalid") == CalculationMethod.PER_PIECE


class TestCalculationContext:
    """Test CalculationContext data class"""

    def test_context_initialization(self):
        """Test basic context initialization"""
        context = CalculationContext(
            capacity_w=400.0,
            power_kw=8.0,
            technology="Monokristallin",
            category="Modul"
        )

        assert context.capacity_w == 400.0
        assert context.power_kw == 8.0
        assert context.technology == "Monokristallin"
        assert context.category == "Modul"

    def test_context_area_calculation(self):
        """Test automatic area calculation from dimensions"""
        context = CalculationContext(
            length_m=2.0,
            width_m=1.0
        )

        assert context.area_m2 == 2.0

    def test_context_system_capacity_calculation(self):
        """Test automatic system capacity calculation"""
        # From power_kw
        context1 = CalculationContext(power_kw=8.0)
        assert context1.system_capacity_kwp == 8.0

        # From capacity_w
        context2 = CalculationContext(capacity_w=400.0)
        assert context2.system_capacity_kwp == 0.4


class TestCalculatePerEngine:
    """Test main CalculatePerEngine functionality"""

    @pytest.fixture
    def engine(self):
        """Create engine instance for testing"""
        return CalculatePerEngine()

    def test_per_piece_calculation(self, engine):
        """Test per piece calculation method"""
        result = engine.calculate_price(
            base_price=180.0,
            quantity=20,
            calculate_per="Stück"
        )

        assert result.calculation_method == CalculationMethod.PER_PIECE
        assert result.unit_price == 180.0
        assert result.total_price == 3600.0
        assert result.quantity == 20
        assert result.calculation_factor == 1.0

    def test_per_meter_calculation(self, engine):
        """Test per meter calculation method"""
        result = engine.calculate_price(
            base_price=8.50,
            quantity=50.0,
            calculate_per="Meter"
        )

        assert result.calculation_method == CalculationMethod.PER_METER
        assert result.unit_price == 8.50
        assert result.total_price == 425.0
        assert result.quantity == 50.0
        assert "50.0m × 8.50/m = 425.00" in result.calculation_notes[0]

    def test_lump_sum_calculation(self, engine):
        """Test lump sum calculation method"""
        result = engine.calculate_price(
            base_price=2500.0,
            quantity=3,  # Should be ignored
            calculate_per="pauschal"
        )

        assert result.calculation_method == CalculationMethod.LUMP_SUM
        assert result.unit_price == 2500.0
        assert result.total_price == 2500.0  # Quantity ignored
        assert result.quantity == 3
        assert result.calculation_factor == 0.0
        # Should warn about ignored quantity
        assert len(result.validation_warnings) > 0

    def test_per_kwp_calculation_with_context(self, engine):
        """Test per kWp calculation with system capacity context"""
        context = CalculationContext(
            system_capacity_kwp=10.0,
            category="Modul"
        )

        result = engine.calculate_price(
            base_price=50.0,
            quantity=25,  # 25 modules
            calculate_per="kWp",
            context=context
        )

        assert result.calculation_method == CalculationMethod.PER_KWP
        assert result.unit_price == 50.0
        assert result.total_price == 500.0  # 10 kWp × 50.0/kWp
        assert result.calculation_factor == 0.4  # 10 kWp / 25 modules

    def test_per_kwp_calculation_with_component_capacity(self, engine):
        """Test per kWp calculation using component capacity"""
        context = CalculationContext(
            capacity_w=400.0,  # 400W per module
            category="Modul"
        )

        result = engine.calculate_price(
            base_price=50.0,
            quantity=25,  # 25 modules = 10 kWp
            calculate_per="kWp",
            context=context
        )

        assert result.calculation_method == CalculationMethod.PER_KWP
        assert result.total_price == 500.0  # 10 kWp × 50.0/kWp

    def test_per_kwp_fallback_to_per_piece(self, engine):
        """Test per kWp fallback when no capacity information available"""
        result = engine.calculate_price(
            base_price=50.0,
            quantity=25,
            calculate_per="kWp"
        )

        # Should fallback to per piece calculation
        assert result.total_price == 1250.0  # 25 × 50.0
        assert len(result.validation_warnings) > 0
        assert "No kWp capacity found" in result.validation_warnings[0]

    def test_per_square_meter_calculation(self, engine):
        """Test per square meter calculation"""
        context = CalculationContext(
            area_m2=50.0
        )

        result = engine.calculate_price(
            base_price=25.0,
            quantity=10,
            calculate_per="m²",
            context=context
        )

        assert result.calculation_method == CalculationMethod.PER_SQUARE_METER
        assert result.total_price == 1250.0  # 50 m² × 25.0/m²

    def test_per_hour_calculation(self, engine):
        """Test per hour calculation"""
        context = CalculationContext(
            labor_hours=8.0
        )

        result = engine.calculate_price(
            base_price=75.0,
            quantity=1,
            calculate_per="Stunde",
            context=context
        )

        assert result.calculation_method == CalculationMethod.PER_HOUR
        assert result.total_price == 600.0  # 8h × 75.0/h

    def test_unknown_method_fallback(self, engine):
        """Test fallback for unknown calculation methods"""
        result = engine.calculate_price(
            base_price=100.0,
            quantity=5,
            calculate_per="unknown_method"
        )

        # Should fallback to per piece
        assert result.total_price == 500.0
        assert len(result.validation_warnings) > 0
        assert "Unknown method" in result.validation_warnings[0]


class TestFeatureAdjustments:
    """Test feature-based pricing adjustments"""

    @pytest.fixture
    def engine(self):
        return CalculatePerEngine()

    def test_technology_adjustment_modul(self, engine):
        """Test technology-based adjustments for modules"""
        context = CalculationContext(
            technology="HJT",
            category="Modul"
        )

        result = engine.calculate_price(
            base_price=180.0,
            quantity=1,
            calculate_per="Stück",
            context=context
        )

        # Should have HJT premium adjustment
        assert result.total_price > 180.0
        assert "technology_HJT" in result.price_adjustments
        assert result.price_adjustments["technology_HJT"] == 50.0

    def test_feature_adjustment_bifacial(self, engine):
        """Test feature-based adjustments for bifacial modules"""
        context = CalculationContext(
            feature="Bifazial",
            category="Modul"
        )

        result = engine.calculate_price(
            base_price=180.0,
            quantity=1,
            calculate_per="Stück",
            context=context
        )

        # Should have bifacial premium
        assert result.total_price == 230.0  # 180 + 50
        assert "feature_Bifazial" in result.price_adjustments

    def test_design_adjustment_all_black(self, engine):
        """Test design-based adjustments for all-black modules"""
        context = CalculationContext(
            design="All-Black",
            category="Modul"
        )

        result = engine.calculate_price(
            base_price=180.0,
            quantity=1,
            calculate_per="Stück",
            context=context
        )

        # Should have all-black premium
        assert result.total_price == 205.0  # 180 + 25
        assert "design_All-Black" in result.price_adjustments

    def test_upgrade_adjustment_premium(self, engine):
        """Test upgrade-based adjustments"""
        context = CalculationContext(
            upgrade="Premium",
            category="Modul"
        )

        result = engine.calculate_price(
            base_price=180.0,
            quantity=1,
            calculate_per="Stück",
            context=context
        )

        # Should have premium upgrade adjustment
        assert result.total_price == 280.0  # 180 + 100
        assert "upgrade_Premium" in result.price_adjustments

    def test_efficiency_adjustment_high_efficiency(self, engine):
        """Test efficiency-based adjustments for high-efficiency modules"""
        context = CalculationContext(
            efficiency_percent=22.5,
            category="Modul"
        )

        result = engine.calculate_price(
            base_price=180.0,
            quantity=1,
            calculate_per="Stück",
            context=context
        )

        # Should have high efficiency premium
        assert result.total_price == 230.0  # 180 + 50
        assert "efficiency_22.5%" in result.price_adjustments

    def test_multiple_adjustments_combined(self, engine):
        """Test multiple feature adjustments combined"""
        context = CalculationContext(
            technology="HJT",
            feature="Bifazial",
            design="All-Black",
            efficiency_percent=22.5,
            category="Modul"
        )

        result = engine.calculate_price(
            base_price=180.0,
            quantity=1,
            calculate_per="Stück",
            context=context
        )

        # Should have all adjustments: 50 + 50 + 25 + 50 = 175
        assert result.total_price == 355.0  # 180 + 175
        assert len(result.price_adjustments) == 4

    def test_no_adjustments_for_unknown_category(self, engine):
        """Test that no adjustments are applied for unknown categories"""
        context = CalculationContext(
            technology="HJT",
            feature="Bifazial",
            category="Unknown"
        )

        result = engine.calculate_price(
            base_price=180.0,
            quantity=1,
            calculate_per="Stück",
            context=context
        )

        # Should have no adjustments
        assert result.total_price == 180.0
        assert len(result.price_adjustments) == 0


class TestValidation:
    """Test input validation and error handling"""

    @pytest.fixture
    def engine(self):
        return CalculatePerEngine()

    def test_negative_base_price_validation(self, engine):
        """Test validation of negative base price"""
        with pytest.raises(CalculationError, match="Base price cannot be negative"):
            engine.calculate_price(-100.0, 1, "Stück")

    def test_negative_quantity_validation(self, engine):
        """Test validation of negative quantity"""
        with pytest.raises(CalculationError, match="Quantity cannot be negative"):
            engine.calculate_price(100.0, -1, "Stück")

    def test_empty_calculate_per_validation(self, engine):
        """Test validation of empty calculate_per"""
        with pytest.raises(CalculationError, match="Calculation method.*cannot be empty"):
            engine.calculate_price(100.0, 1, "")

    def test_very_high_price_warning(self, engine):
        """Test warning for very high prices"""
        result = engine.calculate_price(
            base_price=200000.0,  # Very high unit price
            quantity=1,
            calculate_per="Stück"
        )

        assert len(result.validation_warnings) > 0
        assert "Very high unit price" in result.validation_warnings[0]

    def test_very_long_cable_warning(self, engine):
        """Test warning for very long cable lengths"""
        result = engine.calculate_price(
            base_price=8.50,
            quantity=1500.0,  # Very long cable
            calculate_per="Meter"
        )

        assert len(result.validation_warnings) > 0
        assert "Very long cable length" in result.validation_warnings[0]


class TestBackwardCompatibility:
    """Test backward compatibility functions"""

    def test_calculate_price_by_method_basic(self):
        """Test legacy calculate_price_by_method function"""
        result = calculate_price_by_method(180.0, 20, "Stück")
        assert result == 3600.0

    def test_calculate_price_by_method_with_specs(self):
        """Test legacy function with product specs"""
        product_specs = {
            'capacity_w': 400.0,
            'technology': 'HJT',
            'category': 'Modul'
        }

        result = calculate_price_by_method(180.0, 25, "kWp", product_specs)
        # 25 modules × 400W = 10kWp, 10kWp × 180.0 = 1800.0, + HJT adjustment
        # (50.0) = 1850.0
        assert result == 1850.0

    def test_get_supported_calculation_methods(self):
        """Test getting supported calculation methods"""
        methods = get_supported_calculation_methods()

        assert "Stück" in methods
        assert "Meter" in methods
        assert "pauschal" in methods
        assert "kWp" in methods
        assert "m²" in methods
        assert "Stunde" in methods

    def test_validate_calculation_method(self):
        """Test calculation method validation"""
        assert validate_calculation_method("Stück")
        assert validate_calculation_method("Meter")
        assert validate_calculation_method(
            "invalid")  # Falls back to per piece
        assert validate_calculation_method("")  # Falls back to per piece


class TestRealWorldScenarios:
    """Test real-world calculation scenarios"""

    @pytest.fixture
    def engine(self):
        return CalculatePerEngine()

    def test_pv_module_scenario(self, engine):
        """Test realistic PV module calculation"""
        context = CalculationContext(
            capacity_w=400.0,
            technology="Monokristallin",
            feature="Halbzellen",
            design="All-Black",
            efficiency_percent=20.5,
            category="Modul",
            brand="SolarTech"
        )

        result = engine.calculate_price(
            base_price=180.0,
            quantity=25,  # 25 modules for 10kWp system
            calculate_per="Stück",
            context=context
        )

        # Base: 25 × 180 = 4500
        # Adjustments: Halbzellen (20) + All-Black (25) + High efficiency (25) = 70 per module
        # Total adjustments: 70 × 25 = 1750
        # Final: 4500 + 1750 = 6250
        assert result.total_price == 6250.0
        assert len(result.price_adjustments) == 3

    def test_cable_installation_scenario(self, engine):
        """Test cable installation calculation"""
        result = engine.calculate_price(
            base_price=8.50,
            quantity=75.0,  # 75 meters of cable
            calculate_per="Meter"
        )

        assert result.total_price == 637.50  # 75m × 8.50/m
        assert result.calculation_method == CalculationMethod.PER_METER

    def test_installation_service_scenario(self, engine):
        """Test installation service lump sum calculation"""
        context = CalculationContext(
            labor_hours=16.0,
            category="Dienstleistung"
        )

        result = engine.calculate_price(
            base_price=2500.0,
            quantity=1,
            calculate_per="pauschal",
            context=context
        )

        assert result.total_price == 2500.0  # Lump sum regardless of labor hours
        assert result.calculation_method == CalculationMethod.LUMP_SUM

    def test_inverter_per_kwp_scenario(self, engine):
        """Test inverter pricing per kWp"""
        context = CalculationContext(
            power_kw=8.0,
            technology="String",
            feature="WiFi",
            category="Wechselrichter"
        )

        result = engine.calculate_price(
            base_price=150.0,  # 150€ per kWp
            quantity=1,  # 1 inverter
            calculate_per="kWp",
            context=context
        )

        # 8kWp × 150€/kWp = 1200€ + WiFi feature (25€) = 1225€
        assert result.total_price == 1225.0
        assert "feature_WiFi" in result.price_adjustments


if __name__ == "__main__":
    pytest.main([__file__])
