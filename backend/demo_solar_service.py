"""
Demo script for Solar Calculator Service

This script demonstrates the basic usage of the Solar Calculator Service.
"""

import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.solar_service import get_solar_service
from backend.models.solar_schemas import SolarCalculationRequest, RoofOrientation


def main():
    print("=" * 70)
    print("Solar Calculator Service Demo")
    print("=" * 70)
    print()
    
    # Get service instance
    print("1. Initializing Solar Calculator Service...")
    service = get_solar_service()
    print(f"   [OK] Service initialized: {service.service_name}")
    print()
    
    # Check health
    print("2. Checking service health...")
    health = service.health_check()
    print(f"   [OK] Status: {health.status.value}")
    print(f"   [OK] Message: {health.message}")
    print()
    
    # Create a sample calculation request
    print("3. Creating calculation request...")
    request = SolarCalculationRequest(
        customer_name="Demo Customer",
        latitude=48.1351,  # Munich coordinates
        longitude=11.5820,
        roof_area_m2=50.0,
        roof_orientation=RoofOrientation.SOUTH,
        roof_inclination_deg=30.0,
        module_quantity=20,
        module_capacity_w=350.0,
        annual_consumption_kwh_yr=4000.0,
        electricity_price_kwh=0.30,
        include_storage=False
    )
    print(f"   [OK] Request created for {request.module_quantity} modules")
    print(f"   [OK] Location: {request.latitude}, {request.longitude}")
    print()
    
    # Perform calculation
    print("4. Performing solar system calculation...")
    try:
        result = service.calculate_solar_system(request)
        print(f"   [OK] Calculation completed in {result.calculation_duration_ms:.2f}ms")
        print()
        
        # Display results
        print("=" * 70)
        print("CALCULATION RESULTS")
        print("=" * 70)
        print()
        
        print("System Sizing:")
        print(f"  • System Size: {result.system_sizing.system_size_kwp:.2f} kWp")
        print(f"  • Module Count: {result.system_sizing.module_count}")
        print(f"  • Specific Yield: {result.system_sizing.specific_yield_kwh_kwp:.0f} kWh/kWp")
        print()
        
        print("Energy Production:")
        print(f"  • Annual Production: {result.energy_production.annual_production_kwh:.0f} kWh")
        print(f"  • Data Source: {result.energy_production.pvgis_source}")
        print(f"  • PVGIS Used: {'Yes' if result.energy_production.pvgis_data_used else 'No'}")
        print()
        
        print("Self-Consumption:")
        print(f"  • Annual Self-Consumption: {result.self_consumption.annual_self_consumption_kwh:.0f} kWh")
        print(f"  • Self-Consumption Rate: {result.self_consumption.self_consumption_rate_percent:.1f}%")
        print(f"  • Autarky Degree: {result.self_consumption.autarky_degree_percent:.1f}%")
        print(f"  • Grid Feed-in: {result.self_consumption.annual_grid_feed_in_kwh:.0f} kWh")
        print()
        
        print("Economic Analysis:")
        print(f"  • Investment Cost (net): €{result.economic_analysis.total_investment_cost_net:.2f}")
        print(f"  • Investment Cost (gross): €{result.economic_analysis.total_investment_cost_gross:.2f}")
        print(f"  • Annual Savings (Year 1): €{result.economic_analysis.annual_savings_year1:.2f}")
        print(f"  • Payback Period: {result.economic_analysis.payback_period_years:.1f} years")
        print(f"  • Total Savings (20 years): €{result.economic_analysis.total_savings_20years:.2f}")
        print()
        
        print("Environmental Impact:")
        print(f"  • Annual CO2 Savings: {result.environmental_impact.annual_co2_savings_kg:.0f} kg")
        print(f"  • Equivalent Trees: {result.environmental_impact.equivalent_trees}")
        print(f"  • Equivalent Car km: {result.environmental_impact.equivalent_car_km:.0f} km")
        print()
        
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  [WARN] {warning}")
            print()
        
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  [ERROR] {error}")
            print()
        
    except Exception as e:
        print(f"   [ERROR] Calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test caching
    print("=" * 70)
    print("TESTING CACHE")
    print("=" * 70)
    print()
    
    print("5. Testing cache functionality...")
    stats_before = service.get_cache_stats()
    print(f"   [OK] Cache entries before: {stats_before['total_entries']}")
    
    # Second calculation with same parameters (should be cached)
    print("   [INFO] Performing identical calculation...")
    result2 = service.calculate_solar_system(request)
    print(f"   [OK] Second calculation completed in {result2.calculation_duration_ms:.2f}ms")
    
    stats_after = service.get_cache_stats()
    print(f"   [OK] Cache entries after: {stats_after['total_entries']}")
    print()
    
    # Clear cache
    print("6. Clearing cache...")
    count = service.clear_cache()
    print(f"   [OK] Cleared {count} cache entries")
    print()
    
    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
