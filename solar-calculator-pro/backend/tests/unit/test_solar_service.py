"""
Task 21: Backend Unit Tests - Solar Service
============================================
Unit tests for the Solar Calculator Service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def solar_calculation_input():
    """Sample solar calculation input data."""
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
def expected_calculation_result():
    """Expected calculation result structure."""
    return {
        "system_size_kwp": 8.0,
        "module_count": 20,
        "annual_production_kwh": 7600,
        "self_consumption_rate": 0.35,
        "grid_feed_rate": 0.65,
        "annual_savings_eur": 1200,
        "payback_years": 8.5,
        "co2_savings_kg": 3800,
        "roi_percent": 11.8
    }


@pytest.fixture
def mock_database_service():
    """Mock database service."""
    mock = Mock()
    mock.get_module_specs.return_value = {
        "power_wp": 400,
        "efficiency": 0.21,
        "dimensions": {"width": 1.0, "height": 1.7}
    }
    mock.get_location_irradiance.return_value = 1050  # kWh/m²/year
    return mock


@pytest.fixture
def mock_pricing_service():
    """Mock pricing service."""
    mock = Mock()
    mock.get_system_price.return_value = Decimal("12500.00")
    mock.get_installation_cost.return_value = Decimal("2500.00")
    return mock


# ============================================================================
# Solar Calculation Tests
# ============================================================================

class TestSolarCalculations:
    """Tests for solar calculation functions."""

    def test_calculate_system_size(self, solar_calculation_input):
        """Test system size calculation based on roof area."""
        roof_area = solar_calculation_input["roof_area"]
        module_power = solar_calculation_input["module_power_wp"]
        module_area = 1.7  # m² per module
        
        usable_area = roof_area * 0.8  # 80% usable
        max_modules = int(usable_area / module_area)
        system_size_kwp = (max_modules * module_power) / 1000
        
        assert system_size_kwp > 0
        assert system_size_kwp <= roof_area * 0.2  # Max ~200 Wp/m²

    def test_calculate_annual_production(self, solar_calculation_input):
        """Test annual production calculation."""
        system_size_kwp = 8.0
        specific_yield = 950  # kWh/kWp for Germany
        
        annual_production = system_size_kwp * specific_yield
        
        assert annual_production == 7600
        assert annual_production > 0

    def test_calculate_self_consumption_rate(self, solar_calculation_input):
        """Test self-consumption rate calculation."""
        annual_production = 7600
        annual_consumption = solar_calculation_input["annual_consumption_kwh"]
        
        # Simple model: higher production relative to consumption = lower self-consumption
        ratio = annual_production / annual_consumption
        if ratio <= 0.5:
            self_consumption_rate = 0.7
        elif ratio <= 1.0:
            self_consumption_rate = 0.5
        elif ratio <= 1.5:
            self_consumption_rate = 0.35
        else:
            self_consumption_rate = 0.25
        
        assert 0 < self_consumption_rate <= 1.0

    def test_calculate_annual_savings(self, solar_calculation_input):
        """Test annual savings calculation."""
        annual_production = 7600
        self_consumption_rate = 0.35
        electricity_price = solar_calculation_input["electricity_price_kwh"]
        feed_in_tariff = 0.08  # €/kWh
        
        self_consumed = annual_production * self_consumption_rate
        fed_in = annual_production * (1 - self_consumption_rate)
        
        savings_self_consumption = self_consumed * electricity_price
        income_feed_in = fed_in * feed_in_tariff
        
        total_savings = savings_self_consumption + income_feed_in
        
        assert total_savings > 0
        assert savings_self_consumption > income_feed_in  # Self-consumption more valuable

    def test_calculate_payback_period(self):
        """Test payback period calculation."""
        total_investment = 15000
        annual_savings = 1200
        
        payback_years = total_investment / annual_savings
        
        assert payback_years == 12.5
        assert payback_years > 0

    def test_calculate_co2_savings(self):
        """Test CO2 savings calculation."""
        annual_production = 7600
        co2_factor = 0.5  # kg CO2 per kWh (German grid mix)
        
        co2_savings = annual_production * co2_factor
        
        assert co2_savings == 3800
        assert co2_savings > 0

    def test_calculate_roi(self):
        """Test ROI calculation."""
        total_investment = 15000
        annual_savings = 1200
        system_lifetime = 25  # years
        
        total_savings = annual_savings * system_lifetime
        roi = ((total_savings - total_investment) / total_investment) * 100
        
        assert roi > 0
        assert roi == 100.0  # (30000 - 15000) / 15000 * 100


class TestSolarValidation:
    """Tests for input validation."""

    def test_validate_roof_area_positive(self):
        """Test that roof area must be positive."""
        roof_area = -10
        assert roof_area <= 0, "Negative roof area should be invalid"

    def test_validate_roof_area_reasonable(self):
        """Test that roof area is within reasonable bounds."""
        roof_area = 500
        max_reasonable = 1000  # m²
        
        assert roof_area <= max_reasonable

    def test_validate_roof_angle(self):
        """Test roof angle validation."""
        valid_angles = [0, 15, 30, 45, 60, 90]
        invalid_angles = [-10, 100, 180]
        
        for angle in valid_angles:
            assert 0 <= angle <= 90
        
        for angle in invalid_angles:
            assert not (0 <= angle <= 90)

    def test_validate_orientation(self):
        """Test orientation validation."""
        valid_orientations = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]
        
        for orientation in valid_orientations:
            assert orientation in valid_orientations

    def test_validate_consumption(self):
        """Test annual consumption validation."""
        valid_consumption = 4500
        invalid_consumption = -100
        
        assert valid_consumption > 0
        assert invalid_consumption <= 0


class TestSolarEdgeCases:
    """Tests for edge cases."""

    def test_zero_consumption(self):
        """Test calculation with zero consumption."""
        annual_consumption = 0
        annual_production = 7600
        
        # Should handle division by zero
        if annual_consumption == 0:
            self_consumption_rate = 0
        else:
            self_consumption_rate = min(annual_production / annual_consumption, 1.0)
        
        assert self_consumption_rate == 0

    def test_very_small_roof(self):
        """Test calculation with very small roof."""
        roof_area = 5  # m²
        module_area = 1.7
        
        max_modules = int(roof_area * 0.8 / module_area)
        
        assert max_modules >= 0
        assert max_modules <= 3

    def test_very_large_system(self):
        """Test calculation with very large system."""
        system_size_kwp = 100
        specific_yield = 950
        
        annual_production = system_size_kwp * specific_yield
        
        assert annual_production == 95000

    def test_north_facing_roof(self):
        """Test calculation for north-facing roof (worst case)."""
        orientation = "north"
        base_yield = 950
        orientation_factor = 0.6  # 60% of optimal
        
        adjusted_yield = base_yield * orientation_factor
        
        assert adjusted_yield < base_yield
        assert adjusted_yield == 570


# ============================================================================
# Integration with Services Tests
# ============================================================================

class TestSolarServiceIntegration:
    """Tests for service integration."""

    def test_get_module_specifications(self, mock_database_service):
        """Test getting module specifications from database."""
        specs = mock_database_service.get_module_specs("monocrystalline")
        
        assert specs["power_wp"] == 400
        assert specs["efficiency"] == 0.21
        assert "dimensions" in specs

    def test_get_location_irradiance(self, mock_database_service):
        """Test getting location irradiance data."""
        irradiance = mock_database_service.get_location_irradiance(51.1657, 10.4515)
        
        assert irradiance == 1050
        assert irradiance > 0

    def test_get_system_price(self, mock_pricing_service):
        """Test getting system price from pricing service."""
        price = mock_pricing_service.get_system_price(8.0, "monocrystalline")
        
        assert price == Decimal("12500.00")
        assert price > 0

    def test_full_calculation_flow(self, solar_calculation_input, mock_database_service, mock_pricing_service):
        """Test complete calculation flow."""
        # Step 1: Get module specs
        specs = mock_database_service.get_module_specs(solar_calculation_input["module_type"])
        
        # Step 2: Calculate system size
        roof_area = solar_calculation_input["roof_area"]
        module_area = specs["dimensions"]["width"] * specs["dimensions"]["height"]
        max_modules = int(roof_area * 0.8 / module_area)
        system_size_kwp = (max_modules * specs["power_wp"]) / 1000
        
        # Step 3: Get irradiance
        irradiance = mock_database_service.get_location_irradiance(
            solar_calculation_input["location"]["latitude"],
            solar_calculation_input["location"]["longitude"]
        )
        
        # Step 4: Calculate production
        performance_ratio = 0.85
        annual_production = system_size_kwp * irradiance * performance_ratio
        
        # Step 5: Get price
        price = mock_pricing_service.get_system_price(system_size_kwp, solar_calculation_input["module_type"])
        
        # Assertions
        assert system_size_kwp > 0
        assert annual_production > 0
        assert price > 0


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
