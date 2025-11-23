"""
Demo: Heat Pump Environmental Analysis

This demo showcases the comprehensive environmental analysis features
for heat pump systems including:
- CO2 savings calculations
- Environmental impact analysis
- Renewable energy percentage tracking
- Carbon footprint tracking over lifetime
- Sustainability reporting
- Environmental certifications
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.heatpump_advanced_service import (
    HeatPumpAdvancedService,
    HeatPumpType,
    HeatingSystem
)


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def demo_environmental_analysis():
    """Demonstrate environmental analysis features"""
    print_section("HEAT PUMP ENVIRONMENTAL ANALYSIS DEMO")
    
    # Initialize service
    service = HeatPumpAdvancedService()
    service.initialize()
    
    # Example system parameters
    annual_heating_demand_kwh = 15000.0
    heat_pump_cop = 4.2
    building_area_m2 = 150.0
    
    print("\nSystem Parameters:")
    print(f"  Annual Heating Demand: {annual_heating_demand_kwh:,.0f} kWh")
    print(f"  Heat Pump COP: {heat_pump_cop}")
    print(f"  Building Area: {building_area_m2} m²")
    
    # Scenario 1: Standard grid electricity
    print_section("Scenario 1: Standard Grid Electricity (40% renewable)")
    
    impact1 = service.analyze_environmental_impact(
        annual_heating_demand_kwh=annual_heating_demand_kwh,
        heat_pump_cop=heat_pump_cop,
        electricity_co2_g_kwh=400.0,
        gas_co2_g_kwh=200.0,
        oil_co2_g_kwh=266.0,
        renewable_energy_percent=40.0,
        lifetime_years=25,
        building_area_m2=building_area_m2,
        heat_pump_type=HeatPumpType.AIR_SOURCE
    )
    
    print(f"\n📊 Environmental Metrics:")
    print(f"  Annual CO2 Savings: {impact1.annual_co2_savings_kg:,.0f} kg ({impact1.annual_co2_savings_kg/1000:.2f} tons)")
    print(f"  Lifetime CO2 Savings (25y): {impact1.lifetime_co2_savings_kg:,.0f} kg ({impact1.lifetime_co2_savings_kg/1000:.2f} tons)")
    print(f"  Carbon Footprint Reduction: {impact1.carbon_footprint_reduction_percent:.1f}%")
    print(f"  Equivalent Trees Planted: {impact1.equivalent_trees_planted:,}")
    
    print(f"\n🌱 Sustainability:")
    print(f"  Sustainability Rating: {impact1.sustainability_rating}")
    print(f"  Environmental Score: {impact1.environmental_score:.1f}/100")
    print(f"  Air Quality Score: {impact1.air_quality_improvement_score:.1f}/100")
    
    print(f"\n♻️ Renewable Energy:")
    print(f"  Grid Renewable %: {impact1.renewable_energy_percent:.1f}%")
    print(f"  Renewable Contribution: {impact1.renewable_energy_contribution_kwh:,.0f} kWh/year")
    print(f"  Fossil Fuel Replacement: {impact1.fossil_fuel_replacement_percent:.1f}%")
    
    print(f"\n🏆 Environmental Certifications:")
    for cert in impact1.environmental_certifications:
        print(f"  ✓ {cert}")
    
    print(f"\n💧 Additional Benefits:")
    print(f"  Water Conservation: {impact1.water_conservation_liters_year:,.0f} liters/year")
    print(f"  Noise Reduction: {impact1.noise_pollution_reduction_db:.1f} dB")
    print(f"  Primary Energy Factor: {impact1.primary_energy_factor:.2f}")
    
    # Show carbon footprint tracking (first 5 years)
    print(f"\n📈 Carbon Footprint Tracking (First 5 Years):")
    print(f"  {'Year':<6} {'HP Emissions':<15} {'Gas Emissions':<15} {'Annual Savings':<15} {'Cumulative':<15}")
    print(f"  {'-'*6} {'-'*15} {'-'*15} {'-'*15} {'-'*15}")
    for year_data in impact1.carbon_footprint_tracking[:5]:
        print(f"  {year_data['year']:<6} "
              f"{year_data['hp_emissions_kg']:>12,.0f} kg "
              f"{year_data['gas_emissions_kg']:>12,.0f} kg "
              f"{year_data['annual_savings_kg']:>12,.0f} kg "
              f"{year_data['cumulative_savings_kg']:>12,.0f} kg")
    
    # Scenario 2: Green electricity tariff
    print_section("Scenario 2: Green Electricity Tariff (100% renewable)")
    
    impact2 = service.analyze_environmental_impact(
        annual_heating_demand_kwh=annual_heating_demand_kwh,
        heat_pump_cop=heat_pump_cop,
        electricity_co2_g_kwh=400.0,
        gas_co2_g_kwh=200.0,
        oil_co2_g_kwh=266.0,
        renewable_energy_percent=100.0,
        lifetime_years=25,
        building_area_m2=building_area_m2,
        heat_pump_type=HeatPumpType.AIR_SOURCE
    )
    
    print(f"\n📊 Environmental Metrics:")
    print(f"  Annual CO2 Savings: {impact2.annual_co2_savings_kg:,.0f} kg ({impact2.annual_co2_savings_kg/1000:.2f} tons)")
    print(f"  Lifetime CO2 Savings (25y): {impact2.lifetime_co2_savings_kg:,.0f} kg ({impact2.lifetime_co2_savings_kg/1000:.2f} tons)")
    print(f"  Carbon Footprint Reduction: {impact2.carbon_footprint_reduction_percent:.1f}%")
    print(f"  Equivalent Trees Planted: {impact2.equivalent_trees_planted:,}")
    
    print(f"\n🌱 Sustainability:")
    print(f"  Sustainability Rating: {impact2.sustainability_rating}")
    print(f"  Environmental Score: {impact2.environmental_score:.1f}/100")
    
    print(f"\n💡 Improvement vs. Standard Grid:")
    improvement_co2 = impact2.annual_co2_savings_kg - impact1.annual_co2_savings_kg
    improvement_score = impact2.environmental_score - impact1.environmental_score
    print(f"  Additional CO2 Savings: {improvement_co2:,.0f} kg/year")
    print(f"  Environmental Score Increase: +{improvement_score:.1f} points")
    print(f"  Rating Improvement: {impact1.sustainability_rating} → {impact2.sustainability_rating}")
    
    # Scenario 3: Ground source heat pump
    print_section("Scenario 3: Ground Source Heat Pump (Higher Efficiency)")
    
    impact3 = service.analyze_environmental_impact(
        annual_heating_demand_kwh=annual_heating_demand_kwh,
        heat_pump_cop=4.8,  # Higher COP for ground source
        electricity_co2_g_kwh=400.0,
        gas_co2_g_kwh=200.0,
        oil_co2_g_kwh=266.0,
        renewable_energy_percent=40.0,
        lifetime_years=25,
        building_area_m2=building_area_m2,
        heat_pump_type=HeatPumpType.GROUND_SOURCE
    )
    
    print(f"\n📊 Environmental Metrics:")
    print(f"  Annual CO2 Savings: {impact3.annual_co2_savings_kg:,.0f} kg ({impact3.annual_co2_savings_kg/1000:.2f} tons)")
    print(f"  Lifetime CO2 Savings (25y): {impact3.lifetime_co2_savings_kg:,.0f} kg ({impact3.lifetime_co2_savings_kg/1000:.2f} tons)")
    print(f"  Sustainability Rating: {impact3.sustainability_rating}")
    print(f"  Environmental Score: {impact3.environmental_score:.1f}/100")
    print(f"  Noise Reduction: {impact3.noise_pollution_reduction_db:.1f} dB (quieter than air source)")
    
    print(f"\n🏆 Additional Certifications:")
    ground_source_certs = [cert for cert in impact3.environmental_certifications 
                          if cert not in impact1.environmental_certifications]
    for cert in ground_source_certs:
        print(f"  ✓ {cert}")
    
    # Generate sustainability report
    print_section("Comprehensive Sustainability Report")
    
    system_details = {
        "heat_pump_type": "Air Source Heat Pump",
        "capacity_kw": 10.0,
        "cop": heat_pump_cop,
        "heating_system": "Underfloor Heating",
        "installation_year": 2024,
        "building_type": "Residential",
        "building_area_m2": building_area_m2
    }
    
    report = service.generate_sustainability_report(impact1, system_details)
    
    print(f"\n📋 Executive Summary:")
    summary = report["executive_summary"]
    print(f"  Sustainability Rating: {summary['sustainability_rating']}")
    print(f"  Environmental Score: {summary['environmental_score']}/100")
    print(f"  Annual CO2 Savings: {summary['annual_co2_savings_tons']} tons")
    print(f"  Lifetime CO2 Savings: {summary['lifetime_co2_savings_tons']} tons")
    print(f"  Equivalent Trees: {summary['equivalent_trees']:,}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    # Comparison table
    print_section("Scenario Comparison")
    
    print(f"\n{'Metric':<40} {'Standard Grid':<20} {'Green Tariff':<20} {'Ground Source':<20}")
    print(f"{'-'*40} {'-'*20} {'-'*20} {'-'*20}")
    print(f"{'Annual CO2 Savings (tons)':<40} {impact1.annual_co2_savings_kg/1000:>18.2f}  {impact2.annual_co2_savings_kg/1000:>18.2f}  {impact3.annual_co2_savings_kg/1000:>18.2f}")
    print(f"{'Lifetime CO2 Savings (tons)':<40} {impact1.lifetime_co2_savings_kg/1000:>18.2f}  {impact2.lifetime_co2_savings_kg/1000:>18.2f}  {impact3.lifetime_co2_savings_kg/1000:>18.2f}")
    print(f"{'Sustainability Rating':<40} {impact1.sustainability_rating:>20}  {impact2.sustainability_rating:>20}  {impact3.sustainability_rating:>20}")
    print(f"{'Environmental Score':<40} {impact1.environmental_score:>18.1f}  {impact2.environmental_score:>18.1f}  {impact3.environmental_score:>18.1f}")
    print(f"{'Carbon Reduction %':<40} {impact1.carbon_footprint_reduction_percent:>18.1f}  {impact2.carbon_footprint_reduction_percent:>18.1f}  {impact3.carbon_footprint_reduction_percent:>18.1f}")
    print(f"{'Equivalent Trees':<40} {impact1.equivalent_trees_planted:>20,}  {impact2.equivalent_trees_planted:>20,}  {impact3.equivalent_trees_planted:>20,}")
    
    print("\n" + "=" * 80)
    print("  Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    demo_environmental_analysis()
