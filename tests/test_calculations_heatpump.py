"""
Unit Tests für calculations_heatpump.py
Angepasst an echte Funktionssignaturen
"""

import pytest
from calculations_heatpump import (
    calculate_domestic_hot_water_demand,
    calculate_heat_load_with_climate_zone,
    calculate_required_flow_temperature,
    check_radiator_compatibility,
    calculate_co2_costs_fossil_heating,
    calculate_green_fuel_premium,
    calculate_beg_subsidy,
    calculate_npv_20_years,
    compare_heating_systems_20_years,
    calculate_pv_self_consumption_heatpump
)


class TestDomesticHotWaterDemand:
    """Tests für calculate_domestic_hot_water_demand(living_area_m2, persons)"""
    
    def test_standard_household(self):
        result = calculate_domestic_hot_water_demand(150, 4)
        assert isinstance(result, (int, float))
        assert result > 0
    
    def test_large_household(self):
        result = calculate_domestic_hot_water_demand(200, 6)
        assert result > calculate_domestic_hot_water_demand(200, 4)


class TestHeatLoadWithClimateZone:
    """Tests für calculate_heat_load_with_climate_zone(...)"""
    
    def test_cold_zone(self):
        result = calculate_heat_load_with_climate_zone("Einfamilienhaus", 150, "Kalt", "Gut", 4)
        assert isinstance(result, dict)
        assert "heating_load_kw" in result
        assert result["heating_load_kw"] > 0
    
    def test_climate_comparison(self):
        cold = calculate_heat_load_with_climate_zone("Einfamilienhaus", 150, "Kalt", "Gut", 4)
        mild = calculate_heat_load_with_climate_zone("Einfamilienhaus", 150, "Mild", "Gut", 4)
        assert cold["heating_load_kw"] > mild["heating_load_kw"]


class TestRequiredFlowTemperature:
    """Tests für calculate_required_flow_temperature(...)"""
    
    def test_standard_radiator(self):
        result = calculate_required_flow_temperature(10, 10, 20, 1.3)
        assert isinstance(result, float)
        assert result > 20
    
    def test_large_area_lower_temp(self):
        small_area = calculate_required_flow_temperature(8, 10, 20, 1.3)
        large_area = calculate_required_flow_temperature(8, 20, 20, 1.3)
        assert large_area < small_area


class TestRadiatorCompatibility:
    """Tests für check_radiator_compatibility(...)"""
    
    def test_optimal(self):
        result = check_radiator_compatibility(50, 70)
        assert result["recommendation"] == "Optimal"
        assert result["compatible"] == True
    
    def test_borderline(self):
        result = check_radiator_compatibility(60, 70)
        assert result["recommendation"] == "Grenzwertig"
    
    def test_upgrade_needed(self):
        result = check_radiator_compatibility(70, 70)
        assert result["recommendation"] == "Upgrade nötig"
        assert result["upgrade_cost_estimate_eur"] > 0


class TestCO2CostsFossilHeating:
    """Tests für calculate_co2_costs_fossil_heating(...)"""
    
    def test_oil_heating(self):
        result = calculate_co2_costs_fossil_heating("Heizöl", 20000, 80, 0)
        assert isinstance(result, dict)
        assert "co2_emissions_tons" in result
        assert result["co2_emissions_tons"] > 0
    
    def test_gas_lower_emissions(self):
        oil = calculate_co2_costs_fossil_heating("Heizöl", 15000, 80, 0)
        gas = calculate_co2_costs_fossil_heating("Erdgas", 15000, 80, 0)
        assert gas["co2_emissions_tons"] < oil["co2_emissions_tons"]


class TestGreenFuelPremium:
    """Tests für calculate_green_fuel_premium(...)"""
    
    def test_oil_premium(self):
        result = calculate_green_fuel_premium("Heizöl", 20000, 0.15)
        assert isinstance(result, float)
        assert result > 0
    
    def test_gas_premium(self):
        result = calculate_green_fuel_premium("Erdgas", 15000, 0.30)
        assert result > 0


class TestBEGSubsidy:
    """Tests für calculate_beg_subsidy(...)"""
    
    def test_base_subsidy(self):
        result = calculate_beg_subsidy(30000, False, False)
        assert result["base_subsidy_percent"] == 35
        assert result["subsidy_amount_eur"] == pytest.approx(10500, abs=1)
    
    def test_with_bonus(self):
        result = calculate_beg_subsidy(30000, True, False)
        assert result["total_subsidy_percent"] == 45
        assert result["subsidy_amount_eur"] == pytest.approx(13500, abs=1)
    
    def test_max_subsidy(self):
        result = calculate_beg_subsidy(30000, True, True)
        assert result["total_subsidy_percent"] == 50


class TestNPV20Years:
    """Tests für calculate_npv_20_years(...)"""
    
    def test_simple_calc(self):
        result = calculate_npv_20_years(20000, 2000, 2.0, 3.0, 0)
        assert isinstance(result, dict)
        assert "npv_eur" in result
    
    def test_cost_comparison(self):
        low = calculate_npv_20_years(20000, 1500, 2.0, 3.0, 0)
        high = calculate_npv_20_years(20000, 2500, 2.0, 3.0, 0)
        assert low["npv_eur"] > high["npv_eur"]


class TestCompareHeatingSystems20Years:
    """Tests für compare_heating_systems_20_years(...)"""
    
    def test_heatpump_vs_oil(self):
        building = {"annual_heat_demand_kwh": 15000}
        heatpump = {
            "investment_cost_eur": 25000,
            "jaz": 3.5,
            "electricity_price_kwh": 0.32
        }
        result = compare_heating_systems_20_years(building, heatpump, "Heizöl")
        
        assert "heatpump" in result
        assert "fossil_heating" in result
        assert "comparison" in result


class TestPVSelfConsumptionHeatpump:
    """Tests für calculate_pv_self_consumption_heatpump(...)"""
    
    def test_without_pv(self):
        result = calculate_pv_self_consumption_heatpump(4000, 0, 1000, 30, 0.30, 0.08)
        assert result["heatpump_from_pv_kwh"] == 0
    
    def test_with_pv(self):
        result = calculate_pv_self_consumption_heatpump(4000, 5, 1000, 30, 0.30, 0.08)
        assert result["heatpump_from_pv_kwh"] > 0
        assert result["cost_savings_eur"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
