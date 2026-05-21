"""
Heat Pump Sizing Service - Demo

This demo shows how to use the Heat Pump Sizing Service for comprehensive
heat pump sizing calculations.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.heatpump_sizing_service import (
    HeatPumpSizingService,
    BuildingType,
    InsulationStandard,
    ClimateZone
)


def demo_complete_sizing_workflow():
    """Demonstrate complete sizing workflow"""
    print("=" * 80)
    print("HEAT PUMP SIZING SERVICE - COMPLETE WORKFLOW DEMO")
    print("=" * 80)
    
    # Initialize service
    service = HeatPumpSizingService()
    service.initialize()
    print(" Service initialized\n")
    
    # Building parameters
    building_area_m2 = 150.0
    building_volume_m3 = 375.0
    building_type = BuildingType.SINGLE_FAMILY
    insulation_standard = InsulationStandard.ENEV_2009
    climate_zone = ClimateZone.ZONE_2
    
    print(f"Building Parameters:")
    print(f"  Area: {building_area_m2} m²")
    print(f"  Volume: {building_volume_m3} m³")
    print(f"  Type: {building_type.value}")
    print(f"  Insulation: {insulation_standard.value}")
    print(f"  Climate Zone: {climate_zone.value}")
    print()
    
    # Step 1: Calculate Heat Load
    print("-" * 80)
    print("STEP 1: HEAT LOAD CALCULATION (DIN EN 12831)")
    print("-" * 80)
    
    heat_load = service.calculate_heat_load(
        building_area_m2=building_area_m2,
        building_volume_m3=building_volume_m3,
        building_type=building_type,
        insulation_standard=insulation_standard,
        climate_zone=climate_zone
    )
    
    print(f"Design Heat Load: {heat_load.design_heat_load_kw:.2f} kW")
    print(f"  - Transmission Loss: {heat_load.transmission_heat_loss_kw:.2f} kW")
    print(f"  - Ventilation Loss: {heat_load.ventilation_heat_loss_kw:.2f} kW")
    print(f"  - Heat Gains: {heat_load.heat_gain_kw:.2f} kW")
    print(f"  - Safety Margin: {heat_load.safety_margin_kw:.2f} kW")
    print(f"Total Heat Load: {heat_load.total_heat_load_kw:.2f} kW")
    print(f"Specific Heat Load: {heat_load.specific_heat_load_w_m2:.1f} W/m²")
    print(f"Design Temperatures: {heat_load.design_outdoor_temp_c}°C → {heat_load.design_indoor_temp_c}°C")
    print()
    
    # Step 2: Analyze Insulation
    print("-" * 80)
    print("STEP 2: INSULATION ANALYSIS")
    print("-" * 80)
    
    insulation = service.analyze_insulation(
        building_area_m2=building_area_m2,
        insulation_standard=insulation_standard,
        climate_zone=climate_zone
    )
    
    print(f"U-Values:")
    print(f"  - Walls: {insulation.u_value_walls_w_m2k:.2f} W/m²K")
    print(f"  - Roof: {insulation.u_value_roof_w_m2k:.2f} W/m²K")
    print(f"  - Floor: {insulation.u_value_floor_w_m2k:.2f} W/m²K")
    print(f"  - Windows: {insulation.u_value_windows_w_m2k:.2f} W/m²K")
    print(f"Average U-Value: {insulation.average_u_value_w_m2k:.2f} W/m²K")
    print(f"Insulation Quality Score: {insulation.insulation_quality_score:.1f}/100")
    print(f"Improvement Potential: {insulation.improvement_potential_percent:.1f}%")
    print(f"Annual Heat Loss: {insulation.annual_heat_loss_kwh:.0f} kWh")
    
    if insulation.recommended_improvements:
        print("\nRecommended Improvements:")
        for i, rec in enumerate(insulation.recommended_improvements, 1):
            print(f"  {i}. {rec}")
    print()
    
    # Step 3: Climate-Based Sizing
    print("-" * 80)
    print("STEP 3: CLIMATE-BASED SIZING")
    print("-" * 80)
    
    # Test both bivalent and monovalent
    for bivalent in [True, False]:
        operation_mode = "Bivalent" if bivalent else "Monovalent"
        print(f"\n{operation_mode} Operation:")
        
        sizing = service.calculate_climate_sizing(
            design_heat_load_kw=heat_load.total_heat_load_kw,
            climate_zone=climate_zone,
            bivalent_operation=bivalent
        )
        
        print(f"  Recommended Capacity: {sizing.recommended_capacity_kw:.2f} kW")
        print(f"  Sizing Factor: {sizing.sizing_factor:.2f}")
        print(f"  Bivalent Point: {sizing.bivalent_point_c}°C")
        print(f"  Design Outdoor Temp: {sizing.design_outdoor_temp_c}°C")
        print(f"  Average Winter Temp: {sizing.average_winter_temp_c:.1f}°C")
        print(f"  Heating Degree Days: {sizing.heating_degree_days:.0f}")
    
    # Use bivalent for remaining calculations
    sizing = service.calculate_climate_sizing(
        design_heat_load_kw=heat_load.total_heat_load_kw,
        climate_zone=climate_zone,
        bivalent_operation=True
    )
    print()
    
    # Step 4: Backup Heating Analysis
    print("-" * 80)
    print("STEP 4: BACKUP HEATING ANALYSIS")
    print("-" * 80)
    
    backup = service.calculate_backup_heating(
        design_heat_load_kw=heat_load.total_heat_load_kw,
        heat_pump_capacity_kw=sizing.recommended_capacity_kw,
        climate_zone=climate_zone,
        bivalent_point_c=sizing.bivalent_point_c,
        backup_type="electric"
    )
    
    if backup.backup_required:
        print(f" Backup Heating Required")
        print(f"  Type: {backup.backup_type}")
        print(f"  Capacity: {backup.backup_capacity_kw:.2f} kW")
        print(f"  Activation Temperature: {backup.backup_activation_temp_c}°C")
        print(f"  Annual Backup Hours: {backup.annual_backup_hours:.0f} hours")
        print(f"  Annual Backup Energy: {backup.annual_backup_energy_kwh:.0f} kWh")
        print(f"  Annual Backup Cost: {backup.backup_cost_eur_year:.2f} EUR")
        print(f"  Backup Percentage: {backup.backup_percentage:.1f}% of total heating")
    else:
        print(" No Backup Heating Required (Monovalent Operation)")
    print()
    
    # Step 5: Sizing Warnings
    print("-" * 80)
    print("STEP 5: SIZING VALIDATION & WARNINGS")
    print("-" * 80)
    
    # Test with optimal size
    warnings_optimal = service.analyze_sizing_warnings(
        design_heat_load_kw=heat_load.total_heat_load_kw,
        heat_pump_capacity_kw=sizing.recommended_capacity_kw,
        climate_zone=climate_zone,
        bivalent_operation=True
    )
    
    print(f"Optimal Sizing Analysis:")
    print(f"  Heat Pump Capacity: {sizing.recommended_capacity_kw:.2f} kW")
    print(f"  Optimal Range: {warnings_optimal.optimal_size_range_kw[0]:.1f} - {warnings_optimal.optimal_size_range_kw[1]:.1f} kW")
    print(f"  Oversized: {warnings_optimal.is_oversized}")
    print(f"  Undersized: {warnings_optimal.is_undersized}")
    
    if warnings_optimal.warnings:
        print("\n  Warnings:")
        for warning in warnings_optimal.warnings:
            print(f"     {warning}")
    
    if warnings_optimal.recommendations:
        print("\n  Recommendations:")
        for rec in warnings_optimal.recommendations:
            print(f"    → {rec}")
    
    # Test with oversized unit
    print(f"\nOversized Example (12 kW):")
    warnings_over = service.analyze_sizing_warnings(
        design_heat_load_kw=heat_load.total_heat_load_kw,
        heat_pump_capacity_kw=12.0,
        climate_zone=climate_zone,
        bivalent_operation=True
    )
    print(f"  Oversizing: {warnings_over.oversizing_percent:.1f}%")
    print(f"  Efficiency Impact: {warnings_over.efficiency_impact_percent:.1f}%")
    if warnings_over.warnings:
        for warning in warnings_over.warnings[:2]:  # Show first 2 warnings
            print(f"     {warning}")
    
    # Test with undersized unit
    print(f"\nUndersized Example (5 kW):")
    warnings_under = service.analyze_sizing_warnings(
        design_heat_load_kw=heat_load.total_heat_load_kw,
        heat_pump_capacity_kw=5.0,
        climate_zone=climate_zone,
        bivalent_operation=True
    )
    print(f"  Undersizing: {warnings_under.undersizing_percent:.1f}%")
    print(f"  Efficiency Impact: {warnings_under.efficiency_impact_percent:.1f}%")
    if warnings_under.warnings:
        for warning in warnings_under.warnings[:2]:  # Show first 2 warnings
            print(f"     {warning}")
    print()
    
    # Step 6: Seasonal Performance Prediction
    print("-" * 80)
    print("STEP 6: SEASONAL PERFORMANCE PREDICTION")
    print("-" * 80)
    
    seasonal = service.predict_seasonal_performance(
        heat_pump_capacity_kw=sizing.recommended_capacity_kw,
        climate_zone=climate_zone,
        heat_pump_type="air_source",
        flow_temperature_c=35.0
    )
    
    print(f"Seasonal Performance (Air Source, 35°C Flow Temperature):")
    print(f"\n  Winter:")
    print(f"    Capacity: {seasonal.winter_capacity_kw:.2f} kW")
    print(f"    COP: {seasonal.winter_cop:.2f}")
    
    print(f"\n  Spring:")
    print(f"    Capacity: {seasonal.spring_capacity_kw:.2f} kW")
    print(f"    COP: {seasonal.spring_cop:.2f}")
    
    print(f"\n  Summer:")
    print(f"    Capacity: {seasonal.summer_capacity_kw:.2f} kW")
    print(f"    COP: {seasonal.summer_cop:.2f}")
    
    print(f"\n  Autumn:")
    print(f"    Capacity: {seasonal.autumn_capacity_kw:.2f} kW")
    print(f"    COP: {seasonal.autumn_cop:.2f}")
    
    print(f"\n  Annual SCOP: {seasonal.annual_scop:.2f}")
    print(f"  Capacity Degradation: {seasonal.capacity_degradation_percent:.1f}%")
    
    print(f"\n  Monthly Performance:")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, month_data in enumerate(seasonal.monthly_performance):
        print(f"    {months[i]}: {month_data['capacity_kw']:.1f} kW, COP {month_data['cop']:.2f}, {month_data['outdoor_temp_c']:+.0f}°C")
    
    print()
    print("=" * 80)
    print("SIZING SUMMARY")
    print("=" * 80)
    print(f"Building: {building_area_m2} m², {insulation_standard.value}, {climate_zone.value}")
    print(f"Heat Load: {heat_load.total_heat_load_kw:.2f} kW ({heat_load.specific_heat_load_w_m2:.1f} W/m²)")
    print(f"Recommended Heat Pump: {sizing.recommended_capacity_kw:.2f} kW (bivalent)")
    print(f"Backup Heating: {backup.backup_capacity_kw:.2f} kW ({backup.backup_percentage:.1f}% of total)")
    print(f"Annual SCOP: {seasonal.annual_scop:.2f}")
    print(f"Insulation Quality: {insulation.insulation_quality_score:.0f}/100")
    print("=" * 80)


def demo_comparison_scenarios():
    """Compare different scenarios"""
    print("\n\n")
    print("=" * 80)
    print("SCENARIO COMPARISON DEMO")
    print("=" * 80)
    
    service = HeatPumpSizingService()
    service.initialize()
    
    scenarios = [
        ("Old Building", InsulationStandard.OLD_BUILDING),
        ("Standard (1990s)", InsulationStandard.STANDARD),
        ("EnEV 2009", InsulationStandard.ENEV_2009),
        ("KfW 55", InsulationStandard.KFW_55),
        ("Passive House", InsulationStandard.PASSIVE_HOUSE),
    ]
    
    print(f"\nComparing 150 m² single-family house in different insulation standards:")
    print(f"Climate Zone: {ClimateZone.ZONE_2.value}\n")
    
    print(f"{'Standard':<20} {'Heat Load':<12} {'HP Size':<12} {'Specific':<12} {'Quality':<10}")
    print("-" * 70)
    
    for name, standard in scenarios:
        heat_load = service.calculate_heat_load(
            building_area_m2=150.0,
            building_volume_m3=375.0,
            building_type=BuildingType.SINGLE_FAMILY,
            insulation_standard=standard,
            climate_zone=ClimateZone.ZONE_2
        )
        
        sizing = service.calculate_climate_sizing(
            design_heat_load_kw=heat_load.total_heat_load_kw,
            climate_zone=ClimateZone.ZONE_2,
            bivalent_operation=True
        )
        
        insulation = service.analyze_insulation(
            building_area_m2=150.0,
            insulation_standard=standard,
            climate_zone=ClimateZone.ZONE_2
        )
        
        print(f"{name:<20} {heat_load.total_heat_load_kw:>6.2f} kW    {sizing.recommended_capacity_kw:>6.2f} kW    {heat_load.specific_heat_load_w_m2:>6.1f} W/m²   {insulation.insulation_quality_score:>5.0f}/100")
    
    print("\nKey Insights:")
    print("  • Better insulation dramatically reduces heat load and HP size needed")
    print("  • Passive house needs ~70% less heating capacity than old building")
    print("  • Improving insulation is often more cost-effective than larger HP")


if __name__ == "__main__":
    # Run complete workflow demo
    demo_complete_sizing_workflow()
    
    # Run comparison demo
    demo_comparison_scenarios()
    
    print("\n Demo completed successfully!")
