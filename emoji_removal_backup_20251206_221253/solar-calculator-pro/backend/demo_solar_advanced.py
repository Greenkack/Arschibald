"""
Demo script for Solar Calculator Advanced Service

This script demonstrates all features of the advanced solar calculator service.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.solar_calculator_advanced_service import get_advanced_solar_service


def demo_standard_calculation():
    """Demo: Standard calculation variant"""
    print("\n" + "="*80)
    print("DEMO 1: Standard Calculation")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    result = service.calculate_standard(
        roof_area_m2=50.0,
        latitude=51.5,
        longitude=10.0,
        orientation=0.0,  # South
        tilt=30.0,
        module_power_w=400.0,
        annual_consumption_kwh=4000.0
    )
    
    print(f"\nSystem Size: {result['system_size_kwp']:.2f} kWp")
    print(f"Module Count: {result['module_count']}")
    print(f"Annual Production: {result['annual_production_kwh']:.0f} kWh")
    print(f"Annual Self-Consumption: {result['annual_self_consumption_kwh']:.0f} kWh")
    print(f"Self-Consumption Rate: {result['self_consumption_rate_percent']:.1f}%")
    print(f"Specific Yield: {result['specific_yield_kwh_kwp']:.0f} kWh/kWp")


def demo_premium_calculation():
    """Demo: Premium calculation with shading and battery"""
    print("\n" + "="*80)
    print("DEMO 2: Premium Calculation (with Shading & Battery)")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    result = service.calculate_premium(
        roof_area_m2=50.0,
        latitude=51.5,
        longitude=10.0,
        orientation=0.0,
        tilt=30.0,
        module_power_w=400.0,
        annual_consumption_kwh=4000.0,
        include_shading_analysis=True,
        include_battery=True,
        battery_capacity_kwh=None  # Auto-optimize
    )
    
    print(f"\nSystem Size: {result['system_size_kwp']:.2f} kWp")
    print(f"Annual Production: {result['annual_production_kwh']:.0f} kWh")
    
    if result['shading_analysis']:
        shading = result['shading_analysis']
        print(f"\nShading Analysis:")
        print(f"  Level: {shading.overall_shading_level.value}")
        print(f"  Annual Loss: {shading.annual_shading_loss_percent:.1f}%")
        print(f"  Recommendations:")
        for rec in shading.recommendations[:3]:
            print(f"    - {rec}")
    
    if result['battery_analysis']:
        battery = result['battery_analysis']
        print(f"\nBattery Analysis:")
        print(f"  Optimal Capacity: {battery.optimal_capacity_kwh:.1f} kWh")
        print(f"  Annual Cycles: {battery.annual_cycles:.0f}")
        print(f"  Self-Consumption Increase: {battery.self_consumption_increase_percent:.1f}%")
        print(f"  ROI: {battery.roi_years:.1f} years")


def demo_module_placement():
    """Demo: Module placement optimization"""
    print("\n" + "="*80)
    print("DEMO 3: Module Placement Optimization")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    placements = service.optimize_module_placement(
        roof_area_m2=50.0,
        roof_length_m=10.0,
        roof_width_m=5.0,
        module_length_m=1.7,
        module_width_m=1.0,
        orientation=0.0,
        tilt=30.0,
        obstacles=[
            {
                "x": 5.0,
                "y": 5.0,
                "width": 1.0,
                "length": 1.0,
                "height_m": 2.0,
                "type": "chimney"
            }
        ]
    )
    
    print(f"\nOptimized Placement: {len(placements)} modules")
    print(f"\nFirst 5 module positions:")
    for i, placement in enumerate(placements[:5], 1):
        print(f"  {i}. Row {placement.row}, Col {placement.column}: "
              f"({placement.x_position:.2f}m, {placement.y_position:.2f}m) "
              f"- Shading: {placement.shading_factor*100:.1f}%")


def demo_shading_analysis():
    """Demo: Detailed shading analysis"""
    print("\n" + "="*80)
    print("DEMO 4: Shading Analysis")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    shading_result = service.analyze_shading(
        latitude=51.5,
        longitude=10.0,
        orientation=0.0,
        tilt=30.0,
        roof_area_m2=50.0,
        obstacles=[
            {
                "height_m": 10.0,
                "distance_m": 15.0,
                "azimuth_deg": 180.0,  # South
                "width_m": 5.0,
                "type": "building"
            }
        ]
    )
    
    print(f"\nShading Level: {shading_result.overall_shading_level.value.upper()}")
    print(f"Annual Loss: {shading_result.annual_shading_loss_percent:.1f}%")
    print(f"\nMonthly Shading Factors:")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for month, factor in zip(months, shading_result.monthly_shading_factors):
        print(f"  {month}: {factor*100:.1f}%")
    
    print(f"\nRecommendations:")
    for rec in shading_result.recommendations:
        print(f"  - {rec}")


def demo_production_forecast():
    """Demo: Energy production forecasting"""
    print("\n" + "="*80)
    print("DEMO 5: Energy Production Forecast (25 years)")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    forecast = service.forecast_energy_production(
        system_size_kwp=10.0,
        latitude=51.5,
        longitude=10.0,
        orientation=0.0,
        tilt=30.0,
        years=25,
        degradation_rate_percent=0.5
    )
    
    print(f"\nYear 1 Production: {forecast['first_year_production_kwh']:.0f} kWh")
    print(f"Year 25 Production: {forecast['last_year_production_kwh']:.0f} kWh")
    print(f"Total 25-Year Production: {forecast['total_production_kwh']:.0f} kWh")
    print(f"Average Annual: {forecast['average_annual_kwh']:.0f} kWh")
    print(f"Degradation Rate: {forecast['degradation_rate_percent']}% per year")
    
    print(f"\nProduction by Year (first 10 years):")
    for year, production in enumerate(forecast['annual_forecast_kwh'][:10], 1):
        print(f"  Year {year:2d}: {production:,.0f} kWh")


def demo_battery_analysis():
    """Demo: Battery storage analysis"""
    print("\n" + "="*80)
    print("DEMO 6: Battery Storage Analysis")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    battery_analysis = service.analyze_battery_storage(
        annual_production_kwh=12000.0,
        annual_consumption_kwh=4000.0,
        battery_capacity_kwh=10.0,
        battery_efficiency_percent=90.0,
        depth_of_discharge_percent=90.0
    )
    
    print(f"\nBattery Configuration:")
    print(f"  Actual Capacity: {battery_analysis.actual_capacity_kwh} kWh")
    print(f"  Optimal Capacity: {battery_analysis.optimal_capacity_kwh:.1f} kWh")
    print(f"  Efficiency: {battery_analysis.efficiency_percent}%")
    print(f"  Depth of Discharge: {battery_analysis.depth_of_discharge_percent}%")
    
    print(f"\nPerformance:")
    print(f"  Daily Cycles: {battery_analysis.daily_cycles:.2f}")
    print(f"  Annual Cycles: {battery_analysis.annual_cycles:.0f}")
    print(f"  Expected Lifetime: {battery_analysis.expected_lifetime_years:.1f} years")
    
    print(f"\nBenefits:")
    print(f"  Self-Consumption Increase: {battery_analysis.self_consumption_increase_percent:.1f}%")
    print(f"  Autarky Increase: {battery_analysis.autarky_increase_percent:.1f}%")
    
    print(f"\nFinancial:")
    print(f"  ROI: {battery_analysis.roi_years:.1f} years")
    print(f"  Cost-Benefit Ratio: {battery_analysis.cost_benefit_ratio:.2f}")


def demo_grid_feed_in():
    """Demo: Grid feed-in analysis"""
    print("\n" + "="*80)
    print("DEMO 7: Grid Feed-In Analysis")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    grid_analysis = service.analyze_grid_feed_in(
        annual_production_kwh=12000.0,
        annual_consumption_kwh=4000.0,
        annual_self_consumption_kwh=3000.0,
        system_size_kwp=10.0,
        feed_in_tariff_eur_kwh=0.082,
        grid_connection_capacity_kw=7.0
    )
    
    print(f"\nFeed-In Summary:")
    print(f"  Annual Feed-In: {grid_analysis.annual_feed_in_kwh:,.0f} kWh")
    print(f"  Feed-In Tariff: €{grid_analysis.feed_in_tariff_eur_kwh:.3f}/kWh")
    print(f"  Annual Revenue: €{grid_analysis.annual_feed_in_revenue_eur:,.2f}")
    
    print(f"\nGrid Connection:")
    print(f"  Connection Capacity: {grid_analysis.grid_connection_capacity_kw:.1f} kW")
    print(f"  Peak Feed-In Power: {grid_analysis.peak_feed_in_power_kw:.1f} kW")
    print(f"  Curtailment Losses: {grid_analysis.curtailment_losses_kwh:.0f} kWh")
    print(f"  Grid Stability Score: {grid_analysis.grid_stability_score:.0f}/100")
    
    print(f"\nMonthly Feed-In (kWh):")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for month, feed_in in zip(months, grid_analysis.monthly_feed_in_kwh):
        print(f"  {month}: {feed_in:,.0f}")


def demo_roi_npv():
    """Demo: ROI and NPV analysis"""
    print("\n" + "="*80)
    print("DEMO 8: ROI and NPV Analysis")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    roi_analysis = service.calculate_roi_npv(
        initial_investment_eur=15000.0,
        annual_production_kwh=12000.0,
        annual_self_consumption_kwh=3000.0,
        annual_feed_in_kwh=9000.0,
        electricity_price_eur_kwh=0.30,
        feed_in_tariff_eur_kwh=0.082,
        electricity_price_increase_percent=3.0,
        discount_rate_percent=4.0,
        years=25,
        degradation_rate_percent=0.5,
        maintenance_cost_annual_eur=200.0
    )
    
    print(f"\nInvestment:")
    print(f"  Initial Investment: €{roi_analysis.initial_investment_eur:,.2f}")
    
    print(f"\nAnnual (Year 1):")
    print(f"  Savings: €{roi_analysis.annual_savings_eur:,.2f}")
    print(f"  Revenue: €{roi_analysis.annual_revenue_eur:,.2f}")
    print(f"  Total Benefit: €{roi_analysis.annual_savings_eur + roi_analysis.annual_revenue_eur:,.2f}")
    
    print(f"\nFinancial Metrics:")
    print(f"  Payback Period: {roi_analysis.payback_period_years:.1f} years")
    print(f"  Break-Even Year: {roi_analysis.break_even_year}")
    print(f"  Net Present Value: €{roi_analysis.net_present_value_eur:,.2f}")
    print(f"  Internal Rate of Return: {roi_analysis.internal_rate_of_return_percent:.2f}%")
    print(f"  Profitability Index: {roi_analysis.profitability_index:.2f}")
    
    print(f"\nCumulative Cash Flow (selected years):")
    years_to_show = [1, 5, 10, 15, 20, 25]
    for year in years_to_show:
        if year <= len(roi_analysis.cumulative_cash_flow_25years):
            cash_flow = roi_analysis.cumulative_cash_flow_25years[year-1]
            print(f"  Year {year:2d}: €{cash_flow:,.2f}")


def demo_custom_calculation():
    """Demo: Custom calculation with advanced parameters"""
    print("\n" + "="*80)
    print("DEMO 9: Custom Calculation")
    print("="*80)
    
    service = get_advanced_solar_service()
    
    result = service.calculate_custom({
        "roof_area_m2": 50.0,
        "latitude": 51.5,
        "longitude": 10.0,
        "orientation": 0.0,
        "tilt": 30.0,
        "module_power_w": 400.0,
        "annual_consumption_kwh": 4000.0,
        "system_efficiency": 0.87,
        "degradation_rate_percent": 0.4,
        "temperature_coefficient": -0.35,
        "module_area_m2": 1.7,
        "utilization_factor": 0.90
    })
    
    print(f"\nSystem Configuration:")
    print(f"  System Size: {result['system_size_kwp']:.2f} kWp")
    print(f"  Module Count: {result['module_count']}")
    print(f"  Annual Production: {result['annual_production_kwh']:.0f} kWh")
    
    print(f"\nCustom Parameters:")
    params = result['custom_parameters']
    print(f"  System Efficiency: {params['system_efficiency']*100:.1f}%")
    print(f"  Degradation Rate: {params['degradation_rate_percent']}% per year")
    print(f"  Temperature Coefficient: {params['temperature_coefficient']}%/°C")
    print(f"  Temperature Loss: {params['temperature_loss_percent']:.1f}%")
    
    print(f"\n25-Year Production Forecast (selected years):")
    years_to_show = [1, 5, 10, 15, 20, 25]
    for year in years_to_show:
        if year <= len(result['production_25years']):
            production = result['production_25years'][year-1]
            print(f"  Year {year:2d}: {production:,.0f} kWh")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("SOLAR CALCULATOR ADVANCED SERVICE - COMPREHENSIVE DEMO")
    print("="*80)
    
    try:
        demo_standard_calculation()
        demo_premium_calculation()
        demo_module_placement()
        demo_shading_analysis()
        demo_production_forecast()
        demo_battery_analysis()
        demo_grid_feed_in()
        demo_roi_npv()
        demo_custom_calculation()
        
        print("\n" + "="*80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
