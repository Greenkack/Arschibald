"""
Tests for Heat Pump Advanced Service

Tests all heat pump calculation types, COP calculations, dynamic tariff optimization,
heating cost comparison, seasonal performance analysis, PV + heat pump optimization,
smart grid integration, and environmental impact analysis.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.heatpump_advanced_service import (
    HeatPumpAdvancedService,
    HeatPumpType,
    HeatingSystem,
    TariffType
)


@pytest.fixture
def service():
    """Create and initialize service"""
    svc = HeatPumpAdvancedService()
    svc.initialize()
    return svc


class TestHeatPumpCalculations:
    """Test heat pump calculation types"""
    
    def test_air_source_calculation(self, service):
        """Test air source heat pump calculation"""
        result = service.calculate_air_source_heat_pump(
            building_area_m2=150.0,
            insulation_quality="good",
            outdoor_temp_c=5.0,
            indoor_temp_c=20.0,
            heating_system=HeatingSystem.UNDERFLOOR
        )
        
        assert result["heat_pump_type"] == HeatPumpType.AIR_SOURCE
        assert result["heating_demand_kw"] > 0
        assert 2.0 <= result["cop"] <= 5.0
        assert result["annual_consumption_kwh"] > 0
        assert result["efficiency_percent"] > 0
    
    def test_ground_source_calculation(self, service):
        """Test ground source heat pump calculation"""
        result = service.calculate_ground_source_heat_pump(
            building_area_m2=150.0,
            insulation_quality="good",
            ground_temp_c=10.0,
            indoor_temp_c=20.0,
            heating_system=HeatingSystem.UNDERFLOOR,
            collector_type="horizontal"
        )
        
        assert result["heat_pump_type"] == HeatPumpType.GROUND_SOURCE
        assert result["cop"] > result.get("cop", 0)  # Ground source should have higher COP
        assert result["collector_area_m2"] > 0
        assert result["ground_temperature_c"] == 10.0
    
    def test_water_source_calculation(self, service):
        """Test water source heat pump calculation"""
        result = service.calculate_water_source_heat_pump(
            building_area_m2=150.0,
            insulation_quality="good",
            water_temp_c=12.0,
            indoor_temp_c=20.0,
            heating_system=HeatingSystem.UNDERFLOOR
        )
        
        assert result["heat_pump_type"] == HeatPumpType.WATER_SOURCE
        assert result["cop"] >= 3.0
        assert result["water_temperature_c"] == 12.0


class TestCOPCalculations:
    """Test COP calculations"""
    
    def test_cop_calculation(self, service):
        """Test COP calculation"""
        cop_result = service.calculate_cop(
            heat_pump_type=HeatPumpType.AIR_SOURCE,
            outdoor_temp_c=5.0,
            indoor_temp_c=20.0,
            flow_temp_c=40.0,
            return_temp_c=35.0
        )
        
        assert cop_result.cop_heating > 0
        assert cop_result.cop_cooling > 0
        assert cop_result.scop_seasonal > 0
        assert 0 < cop_result.efficiency_percent <= 100
        assert cop_result.power_consumption_kw > 0
        assert cop_result.heating_output_kw > 0
    
    def test_cop_temperature_dependency(self, service):
        """Test that COP decreases with lower outdoor temperature"""
        cop_warm = service.calculate_cop(
            heat_pump_type=HeatPumpType.AIR_SOURCE,
            outdoor_temp_c=10.0,
            indoor_temp_c=20.0,
            flow_temp_c=40.0,
            return_temp_c=35.0
        )
        
        cop_cold = service.calculate_cop(
            heat_pump_type=HeatPumpType.AIR_SOURCE,
            outdoor_temp_c=-5.0,
            indoor_temp_c=20.0,
            flow_temp_c=40.0,
            return_temp_c=35.0
        )
        
        assert cop_warm.cop_heating > cop_cold.cop_heating


class TestDynamicTariffOptimization:
    """Test dynamic tariff optimization"""
    
    def test_tariff_optimization(self, service):
        """Test dynamic tariff optimization"""
        # Create sample hourly tariffs (higher during peak hours)
        hourly_tariffs = [0.20] * 24
        for hour in [17, 18, 19, 20]:  # Peak hours
            hourly_tariffs[hour] = 0.35
        for hour in [2, 3, 4, 5]:  # Off-peak hours
            hourly_tariffs[hour] = 0.15
        
        result = service.optimize_dynamic_tariff(
            annual_heating_demand_kwh=15000.0,
            tariff_type=TariffType.TIME_OF_USE,
            hourly_tariffs_eur_kwh=hourly_tariffs,
            thermal_storage_capacity_kwh=50.0
        )
        
        assert len(result.optimal_schedule) == 24
        assert result.annual_cost_eur > 0
        assert result.cost_savings_percent >= 0
        assert len(result.peak_avoidance_hours) > 0
        assert len(result.optimal_heating_hours) > 0
        assert 0 <= result.grid_friendly_score <= 100
    
    def test_storage_impact(self, service):
        """Test that thermal storage improves optimization"""
        hourly_tariffs = [0.20] * 24
        
        result_no_storage = service.optimize_dynamic_tariff(
            annual_heating_demand_kwh=15000.0,
            tariff_type=TariffType.TIME_OF_USE,
            hourly_tariffs_eur_kwh=hourly_tariffs,
            thermal_storage_capacity_kwh=0.0
        )
        
        result_with_storage = service.optimize_dynamic_tariff(
            annual_heating_demand_kwh=15000.0,
            tariff_type=TariffType.TIME_OF_USE,
            hourly_tariffs_eur_kwh=hourly_tariffs,
            thermal_storage_capacity_kwh=100.0
        )
        
        assert result_with_storage.storage_utilization_percent > result_no_storage.storage_utilization_percent


class TestHeatingCostComparison:
    """Test heating cost comparison"""
    
    def test_cost_comparison(self, service):
        """Test heating cost comparison"""
        result = service.compare_heating_costs(
            annual_heating_demand_kwh=15000.0,
            heat_pump_cop=3.5,
            electricity_price_eur_kwh=0.30,
            gas_price_eur_kwh=0.08,
            oil_price_eur_l=1.20,
            heat_pump_investment_eur=15000.0
        )
        
        assert result.heat_pump_annual_cost_eur > 0
        assert result.gas_annual_cost_eur > 0
        assert result.oil_annual_cost_eur > 0
        assert result.electric_annual_cost_eur > 0
        assert result.payback_period_years > 0
    
    def test_heat_pump_savings(self, service):
        """Test that heat pump saves money vs electric heating"""
        result = service.compare_heating_costs(
            annual_heating_demand_kwh=15000.0,
            heat_pump_cop=3.5,
            electricity_price_eur_kwh=0.30,
            gas_price_eur_kwh=0.08,
            oil_price_eur_l=1.20,
            heat_pump_investment_eur=15000.0
        )
        
        # Heat pump should be cheaper than electric heating
        assert result.heat_pump_annual_cost_eur < result.electric_annual_cost_eur
        assert result.savings_vs_electric_eur > 0


class TestSeasonalPerformance:
    """Test seasonal performance analysis"""
    
    def test_seasonal_analysis(self, service):
        """Test seasonal performance analysis"""
        result = service.analyze_seasonal_performance(
            heat_pump_type=HeatPumpType.AIR_SOURCE,
            latitude=51.0,
            building_area_m2=150.0,
            insulation_quality="good",
            heating_system=HeatingSystem.UNDERFLOOR
        )
        
        assert result.winter_cop > 0
        assert result.spring_cop > 0
        assert result.summer_cop > 0
        assert result.autumn_cop > 0
        assert result.annual_average_cop > 0
        assert len(result.monthly_cop) == 12
        assert len(result.monthly_consumption_kwh) == 12
        assert len(result.monthly_heating_demand_kwh) == 12
    
    def test_seasonal_variation(self, service):
        """Test that winter COP is lower than summer COP"""
        result = service.analyze_seasonal_performance(
            heat_pump_type=HeatPumpType.AIR_SOURCE,
            latitude=51.0,
            building_area_m2=150.0,
            insulation_quality="good",
            heating_system=HeatingSystem.UNDERFLOOR
        )
        
        # Winter should have lower COP than summer for air source
        assert result.winter_cop < result.summer_cop


class TestPVHeatPumpOptimization:
    """Test PV + heat pump optimization"""
    
    def test_pv_hp_optimization(self, service):
        """Test PV + heat pump optimization"""
        result = service.optimize_pv_heatpump_combination(
            pv_system_size_kwp=10.0,
            annual_pv_production_kwh=10000.0,
            heat_pump_capacity_kw=8.0,
            annual_hp_consumption_kwh=5000.0,
            annual_household_consumption_kwh=4000.0,
            electricity_price_eur_kwh=0.30,
            feed_in_tariff_eur_kwh=0.08
        )
        
        assert result.pv_system_size_kwp == 10.0
        assert result.heat_pump_capacity_kw == 8.0
        assert 0 <= result.self_consumption_rate_percent <= 100
        assert 0 <= result.autarky_rate_percent <= 100
        assert result.combined_savings_eur > 0
        assert len(result.optimal_operation_schedule) == 24
    
    def test_synergy_benefit(self, service):
        """Test that PV + HP combination provides synergy benefit"""
        result = service.optimize_pv_heatpump_combination(
            pv_system_size_kwp=10.0,
            annual_pv_production_kwh=10000.0,
            heat_pump_capacity_kw=8.0,
            annual_hp_consumption_kwh=5000.0,
            annual_household_consumption_kwh=4000.0,
            electricity_price_eur_kwh=0.30,
            feed_in_tariff_eur_kwh=0.08
        )
        
        # Synergy benefit should be positive (load shifting increases self-consumption)
        assert result.synergy_benefit_eur >= 0


class TestSmartGridIntegration:
    """Test smart grid integration"""
    
    def test_grid_integration(self, service):
        """Test smart grid integration analysis"""
        result = service.analyze_smart_grid_integration(
            heat_pump_capacity_kw=8.0,
            thermal_storage_capacity_kwh=50.0,
            annual_consumption_kwh=5000.0,
            grid_signal_response_time_min=15.0
        )
        
        assert result.demand_response_potential_kw > 0
        assert result.load_shifting_capacity_kwh > 0
        assert 0 <= result.grid_stabilization_score <= 100
        assert result.peak_shaving_contribution_kw > 0
        assert 0 <= result.renewable_integration_score <= 100
        assert result.flexibility_value_eur_year >= 0
        assert result.grid_services_revenue_eur_year >= 0
    
    def test_storage_improves_flexibility(self, service):
        """Test that thermal storage improves grid flexibility"""
        result_small_storage = service.analyze_smart_grid_integration(
            heat_pump_capacity_kw=8.0,
            thermal_storage_capacity_kwh=20.0,
            annual_consumption_kwh=5000.0
        )
        
        result_large_storage = service.analyze_smart_grid_integration(
            heat_pump_capacity_kw=8.0,
            thermal_storage_capacity_kwh=100.0,
            annual_consumption_kwh=5000.0
        )
        
        assert result_large_storage.load_shifting_capacity_kwh > result_small_storage.load_shifting_capacity_kwh
        assert result_large_storage.flexibility_value_eur_year > result_small_storage.flexibility_value_eur_year


class TestEnvironmentalImpact:
    """Test environmental impact analysis"""
    
    def test_environmental_analysis(self, service):
        """Test environmental impact analysis"""
        result = service.analyze_environmental_impact(
            annual_heating_demand_kwh=15000.0,
            heat_pump_cop=3.5,
            electricity_co2_g_kwh=400.0,
            gas_co2_g_kwh=200.0,
            oil_co2_g_kwh=266.0,
            renewable_energy_percent=30.0
        )
        
        assert result.annual_co2_savings_kg > 0
        assert result.co2_savings_vs_gas_kg > 0
        assert result.co2_savings_vs_oil_kg > 0
        assert 0 <= result.renewable_energy_percent <= 100
        assert result.primary_energy_factor > 0
        assert 0 <= result.environmental_score <= 100
        assert result.equivalent_trees_planted >= 0
    
    def test_renewable_energy_impact(self, service):
        """Test that renewable energy improves environmental score"""
        result_low_renewable = service.analyze_environmental_impact(
            annual_heating_demand_kwh=15000.0,
            heat_pump_cop=3.5,
            renewable_energy_percent=10.0
        )
        
        result_high_renewable = service.analyze_environmental_impact(
            annual_heating_demand_kwh=15000.0,
            heat_pump_cop=3.5,
            renewable_energy_percent=80.0
        )
        
        assert result_high_renewable.environmental_score > result_low_renewable.environmental_score
        assert result_high_renewable.annual_co2_savings_kg > result_low_renewable.annual_co2_savings_kg


class TestServiceHealth:
    """Test service health and initialization"""
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service.is_initialized
        assert service.service_name == "heatpump_advanced"
    
    def test_health_check(self, service):
        """Test health check"""
        health = service.health_check()
        assert health.status.value == "healthy"
        assert "cop_cache_size" in health.details
        assert "tariff_cache_size" in health.details


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
