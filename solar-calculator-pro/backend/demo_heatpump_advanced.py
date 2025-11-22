"""
Demo script for Heat Pump Advanced Service

This script demonstrates all features of the Heat Pump Advanced Service.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.heatpump_advanced_service import (
    HeatPumpAdvancedService,
    HeatPumpType,
    HeatingSystem,
    TariffType
)


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def demo_air_source_calculation():
    """Demo air source heat pump calculation"""
    print_section("1. Air Source Heat Pump Calculation")
    
    service = HeatPumpAdvancedService()
    service.initialize()
    
    result = service.calculate_air_source_heat_pump(
        building_area_m2=150.0,
        insulation_quality="good",
        outdoor_temp_c=5.0,
        indoor_temp_c=20.0,
        heating_system=HeatingSystem.UNDERFLOOR
    )
    
    print(f"Heat Pump Type: {result['heat_pump_type']}")
    print(f"Heating Demand: {result['heating_demand_kw']:.2f} kW")
    print(f"COP: {result['cop']:.2f}")
    print(f"Power Consumption: {result['power_consumption_kw']:.2f} kW")
    print(f"Flow Temperature: {result['flow_temperature_c']:.1f}°C")
    print(f"Annual Consumption: {result['annual_consumption_kwh']:.0f} kWh")
    print(f"Annual Heating Hours: {result['annual_heating_hours']:.0f} hours")
    print(f"Efficiency: {result['efficiency_percent']:.1f}%")


def demo_cop_calculation():
    """Demo COP calculation"""
    print_section("2. COP (Coefficient of Performance) Calculation")
    
    service = HeatPumpAdvancedService()
    service.initialize()
    
    cop_result = service.calculate_cop(
        heat_pump_type=HeatPumpType.AIR_SOURCE,
        outdoor_temp_c=5.0,
        indoor_temp_c=20.0,
        flow_temp_c=40.0,
        return_temp_c=35.0
    )
    
    print(f"COP Heating: {cop_result.cop_heating:.2f}")
    print(f"COP Cooling: {cop_result.cop_cooling:.2f}")
    print(f"SCOP Seasonal: {cop_result.scop_seasonal:.2f}")
    print(f"Outdoor Temperature: {cop_result.outdoor_temp_c:.1f}°C")
    print(f"Indoor Temperature: {cop_result.indoor_temp_c:.1f}°C")
    print(f"Flow Temperature: {cop_result.flow_temp_c:.1f}°C")
    print(f"Efficiency: {cop_result.efficiency_percent:.1f}%")
    print(f"Power Consumption: {cop_result.power_consumption_kw:.2f} kW")
    print(f"Heating Output: {cop_result.heating_output_kw:.2f} kW")


def demo_dynamic_tariff():
    """Demo dynamic tariff optimization"""
    print_section("3. Dynamic Tariff Optimization")
    
    service = HeatPumpAdvancedService()
    service.initialize()
    
    # Create sample hourly tariffs
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
    
    print(f"Annual Cost: €{result.annual_cost_eur:.2f}")
    print(f"Cost Savings: {result.cost_savings_percent:.1f}%")
    print(f"Peak Avoidance Hours: {len(result.peak_avoidance_hours)} hours")
    print(f"Optimal Heating Hours: {len(result.optimal_heating_hours)} hours")
    print(f"Storage Utilization: {result.storage_utilization_percent:.1f}%")
    print(f"Grid Friendly Score: {result.grid_friendly_score:.1f}/100")
    
    print("\nOptimal Schedule (first 6 hours):")
    for schedule in result.optimal_schedule[:6]:
        print(f"  Hour {schedule['hour']:2d}: "
              f"Tariff €{schedule['tariff_eur_kwh']:.3f}/kWh, "
              f"Power {schedule['heating_power_kw']:.2f} kW, "
              f"{'OPTIMAL' if schedule['is_optimal'] else 'PEAK' if schedule['is_peak'] else 'NORMAL'}")


def demo_cost_comparison():
    """Demo heating cost comparison"""
    print_section("4. Heating Cost Comparison")
    
    service = HeatPumpAdvancedService()
    service.initialize()
    
    result = service.compare_heating_costs(
        annual_heating_demand_kwh=15000.0,
        heat_pump_cop=3.5,
        electricity_price_eur_kwh=0.30,
        gas_price_eur_kwh=0.08,
        oil_price_eur_l=1.20,
        heat_pump_investment_eur=15000.0
    )
    
    print(f"Heat Pump Annual Cost: €{result.heat_pump_annual_cost_eur:.2f}")
    print(f"Gas Annual Cost: €{result.gas_annual_cost_eur:.2f}")
    print(f"Oil Annual Cost: €{result.oil_annual_cost_eur:.2f}")
    print(f"Electric Annual Cost: €{result.electric_annual_cost_eur:.2f}")
    print(f"\nSavings vs Gas: €{result.savings_vs_gas_eur:.2f}/year")
    print(f"Savings vs Oil: €{result.savings_vs_oil_eur:.2f}/year")
    print(f"Savings vs Electric: €{result.savings_vs_electric_eur:.2f}/year")
    print(f"\nPayback Period: {result.payback_period_years:.1f} years")
    print(f"25-Year ROI: €{result.roi_25years_eur:.2f}")


def demo_seasonal_performance():
    """Demo seasonal performance analysis"""
    print_section("5. Seasonal Performance Analysis")
    
    service = HeatPumpAdvancedService()
    service.initialize()
    
    result = service.analyze_seasonal_performance(
        heat_pump_type=HeatPumpType.AIR_SOURCE,
        latitude=51.0,
        building_area_m2=150.0,
        insulation_quality="good",
        heating_system=HeatingSystem.UNDERFLOOR
    )
    
    print(f"Winter COP: {result.winter_cop:.2f}")
    print(f"Spring COP: {result.spring_cop:.2f}")
    print(f"Summer COP: {result.summer_cop:.2f}")
    print(f"Autumn COP: {result.autumn_cop:.2f}")
    print(f"Annual Average COP: {result.annual_average_cop:.2f}")
    print(f"Efficiency Variation: {result.efficiency_variation_percent:.1f}%")
    
    print("\nMonthly Performance:")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, month in enumerate(months):
        print(f"  {month}: COP {result.monthly_cop[i]:.2f}, "
              f"Consumption {result.monthly_consumption_kwh[i]:.0f} kWh, "
              f"Demand {result.monthly_heating_demand_kwh[i]:.0f} kWh")


def demo_pv_heatpump_optimization():
    """Demo PV + heat pump optimization"""
    print_section("6. PV + Heat Pump Optimization")
    
    service = HeatPumpAdvancedService()
    service.initialize()
    
    result = service.optimize_pv_heatpump_combination(
        pv_system_size_kwp=10.0,
        annual_pv_production_kwh=10000.0,
        heat_pump_capacity_kw=8.0,
        annual_hp_consumption_kwh=5000.0,
        annual_household_consumption_kwh=4000.0,
        electricity_price_eur_kwh=0.30,
        feed_in_tariff_eur_kwh=0.08
    )
    
    print(f"PV System Size: {result.pv_system_size_kwp:.1f} kWp")
    print(f"Heat Pump Capacity: {result.heat_pump_capacity_kw:.1f} kW")
    print(f"Annual PV Production: {result.annual_pv_production_kwh:.0f} kWh")
    print(f"Annual HP Consumption: {result.annual_hp_consumption_kwh:.0f} kWh")
    print(f"\nSelf-Consumption Rate: {result.self_consumption_rate_percent:.1f}%")
    print(f"Autarky Rate: {result.autarky_rate_percent:.1f}%")
    print(f"Grid Import: {result.grid_import_kwh:.0f} kWh")
    print(f"Grid Export: {result.grid_export_kwh:.0f} kWh")
    print(f"\nCombined Savings: €{result.combined_savings_eur:.2f}/year")
    print(f"Synergy Benefit: €{result.synergy_benefit_eur:.2f}/year")


def demo_smart_grid():
    """Demo smart grid integration"""
    print_section("7. Smart Grid Integration")
    
    service = HeatPumpAdvancedService()
    service.initialize()
    
    result = service.analyze_smart_grid_integration(
        heat_pump_capacity_kw=8.0,
        thermal_storage_capacity_kwh=50.0,
        annual_consumption_kwh=5000.0,
        grid_signal_response_time_min=15.0
    )
    
    print(f"Demand Response Potential: {result.demand_response_potential_kw:.1f} kW")
    print(f"Load Shifting Capacity: {result.load_shifting_capacity_kwh:.1f} kWh")
    print(f"Grid Stabilization Score: {result.grid_stabilization_score:.1f}/100")
    print(f"Peak Shaving Contribution: {result.peak_shaving_contribution_kw:.1f} kW")
    print(f"Renewable Integration Score: {result.renewable_integration_score:.1f}/100")
    print(f"Flexibility Value: €{result.flexibility_value_eur_year:.2f}/year")
    print(f"Grid Services Revenue: €{result.grid_services_revenue_eur_year:.2f}/year")


def demo_environmental_impact():
    """Demo environmental impact analysis"""
    print_section("8. Environmental Impact Analysis")
    
    service = HeatPumpAdvancedService()
    service.initialize()
    
    result = service.analyze_environmental_impact(
        annual_heating_demand_kwh=15000.0,
        heat_pump_cop=3.5,
        electricity_co2_g_kwh=400.0,
        gas_co2_g_kwh=200.0,
        oil_co2_g_kwh=266.0,
        renewable_energy_percent=30.0
    )
    
    print(f"Annual CO2 Savings: {result.annual_co2_savings_kg:.0f} kg")
    print(f"CO2 Savings vs Gas: {result.co2_savings_vs_gas_kg:.0f} kg")
    print(f"CO2 Savings vs Oil: {result.co2_savings_vs_oil_kg:.0f} kg")
    print(f"Renewable Energy: {result.renewable_energy_percent:.1f}%")
    print(f"Primary Energy Factor: {result.primary_energy_factor:.2f}")
    print(f"Environmental Score: {result.environmental_score:.1f}/100")
    print(f"Carbon Footprint Reduction: {result.carbon_footprint_reduction_percent:.1f}%")
    print(f"Equivalent Trees Planted: {result.equivalent_trees_planted} trees")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  HEAT PUMP ADVANCED SERVICE - DEMONSTRATION")
    print("=" * 80)
    
    try:
        demo_air_source_calculation()
        demo_cop_calculation()
        demo_dynamic_tariff()
        demo_cost_comparison()
        demo_seasonal_performance()
        demo_pv_heatpump_optimization()
        demo_smart_grid()
        demo_environmental_impact()
        
        print("\n" + "=" * 80)
        print("  ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
