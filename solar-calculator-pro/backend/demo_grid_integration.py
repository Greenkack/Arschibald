"""
Grid Integration Demo
Demonstrates all grid integration features
"""

from services.grid_integration_service import GridIntegrationService
from models.grid_schemas import (
    FeedInTariffRequest, NetMeteringRequest, GridConnectionRequest,
    PowerQualityRequest, GridStabilityRequest, SmartGridRequest,
    GridIntegrationAnalysisRequest, GridConnectionType, MeteringType,
    PowerQualityStandard
)


def demo_feed_in_tariff():
    """Demo feed-in tariff calculations"""
    print("\n" + "="*80)
    print("FEED-IN TARIFF ANALYSIS")
    print("="*80)
    
    service = GridIntegrationService()
    
    request = FeedInTariffRequest(
        system_size_kwp=10.0,
        annual_production_kwh=12000,
        self_consumption_rate=0.3,
        feed_in_tariff_per_kwh=0.10,
        electricity_price_per_kwh=0.30,
        contract_duration_years=20,
        degradation_rate=0.005
    )
    
    result = service.calculate_feed_in_tariff(request)
    
    print(f"\nSystem Size: {request.system_size_kwp} kWp")
    print(f"Annual Production: {request.annual_production_kwh:,.0f} kWh")
    print(f"Self-consumption Rate: {request.self_consumption_rate * 100:.1f}%")
    print(f"\nANNUAL BENEFITS:")
    print(f"  Feed-in Energy: {result.annual_feed_in_kwh:,.2f} kWh")
    print(f"  Feed-in Revenue: {result.annual_feed_in_revenue:,.2f} €")
    print(f"  Self-consumption: {result.annual_self_consumption_kwh:,.2f} kWh")
    print(f"  Self-consumption Savings: {result.annual_self_consumption_savings:,.2f} €")
    print(f"  Total Annual Benefit: {result.total_annual_benefit:,.2f} €")
    print(f"\nLIFETIME BENEFITS (20 years with degradation):")
    print(f"  Feed-in Revenue: {result.lifetime_feed_in_revenue:,.2f} €")
    print(f"  Self-consumption Savings: {result.lifetime_self_consumption_savings:,.2f} €")
    print(f"  Total Lifetime Benefit: {result.total_lifetime_benefit:,.2f} €")
    print(f"\nFINANCIAL METRICS:")
    print(f"  Average Benefit per kWp: {result.average_benefit_per_kwp:,.2f} €/kWp")
    if result.payback_period_years:
        print(f"  Payback Period: {result.payback_period_years:.1f} years")


def demo_net_metering():
    """Demo net metering analysis"""
    print("\n" + "="*80)
    print("NET METERING ANALYSIS")
    print("="*80)
    
    service = GridIntegrationService()
    
    # Seasonal production pattern
    monthly_production = [800, 900, 1100, 1200, 1300, 1400, 
                          1400, 1300, 1100, 900, 800, 700]
    # Relatively constant consumption
    monthly_consumption = [1000, 950, 900, 850, 800, 750,
                           750, 800, 850, 900, 950, 1000]
    
    request = NetMeteringRequest(
        system_size_kwp=10.0,
        annual_production_kwh=sum(monthly_production),
        annual_consumption_kwh=sum(monthly_consumption),
        electricity_price_per_kwh=0.30,
        net_metering_credit_per_kwh=0.27,
        monthly_production=monthly_production,
        monthly_consumption=monthly_consumption,
        rollover_allowed=True,
        max_rollover_months=12
    )
    
    result = service.analyze_net_metering(request)
    
    print(f"\nSystem Size: {request.system_size_kwp} kWp")
    print(f"Annual Production: {request.annual_production_kwh:,.0f} kWh")
    print(f"Annual Consumption: {request.annual_consumption_kwh:,.0f} kWh")
    print(f"\nANNUAL SUMMARY:")
    print(f"  Net Export: {result.annual_net_export_kwh:,.2f} kWh")
    print(f"  Net Import: {result.annual_net_import_kwh:,.2f} kWh")
    print(f"  Credits Earned: {result.annual_credits_earned:,.2f} €")
    print(f"  Credits Used: {result.annual_credits_used:,.2f} €")
    print(f"  Net Savings: {result.annual_net_savings:,.2f} €")
    print(f"\nPERFORMANCE METRICS:")
    print(f"  Self-sufficiency Rate: {result.self_sufficiency_rate * 100:.1f}%")
    print(f"  Grid Independence: {result.grid_independence_rate * 100:.1f}%")
    print(f"  Optimal System Size: {result.optimal_system_size_kwp:.2f} kWp")
    
    print(f"\nMONTHLY ANALYSIS:")
    print(f"{'Month':<8} {'Prod':<10} {'Cons':<10} {'Net':<10} {'Credits':<12} {'Import':<10}")
    print("-" * 70)
    for month_data in result.monthly_analysis[:6]:  # Show first 6 months
        print(f"{month_data['month']:<8} "
              f"{month_data['production_kwh']:<10.0f} "
              f"{month_data['consumption_kwh']:<10.0f} "
              f"{month_data['net_energy_kwh']:<10.0f} "
              f"{month_data['cumulative_credits']:<12.2f} "
              f"{month_data['grid_import_kwh']:<10.0f}")


def demo_grid_connection():
    """Demo grid connection requirements"""
    print("\n" + "="*80)
    print("GRID CONNECTION REQUIREMENTS")
    print("="*80)
    
    service = GridIntegrationService()
    
    request = GridConnectionRequest(
        system_size_kwp=15.0,
        connection_type=GridConnectionType.THREE_PHASE,
        voltage_level=400,
        distance_to_grid_m=100,
        inverter_power_kw=15.0,
        location="Commercial Area",
        building_type="commercial"
    )
    
    result = service.calculate_grid_connection_requirements(request)
    
    print(f"\nSystem Size: {request.system_size_kwp} kWp")
    print(f"Connection Type: {request.connection_type.value}")
    print(f"Distance to Grid: {request.distance_to_grid_m} m")
    print(f"\nCONNECTION FEASIBILITY:")
    print(f"  Feasible: {' Yes' if result.connection_feasible else ' No'}")
    print(f"  Grid Capacity Sufficient: {' Yes' if result.grid_capacity_sufficient else ' No'}")
    print(f"\nTECHNICAL REQUIREMENTS:")
    print(f"  Required Cable Size: {result.required_cable_size_mm2} mm²")
    print(f"  Voltage Drop: {result.voltage_drop_percent:.2f}%")
    print(f"  Max Fault Current: {result.max_fault_current_a:.2f} A")
    print(f"  Recommended Type: {result.connection_type_recommended.value}")
    print(f"\nPROTECTION DEVICES:")
    for device in result.required_protection_devices:
        print(f"  • {device}")
    print(f"\nCOSTS AND TIMELINE:")
    print(f"  Estimated Connection Cost: {result.estimated_connection_cost:,.2f} €")
    print(f"  Estimated Approval Time: {result.estimated_approval_time_days} days")
    if result.additional_requirements:
        print(f"\nADDITIONAL REQUIREMENTS:")
        for req in result.additional_requirements:
            print(f"  • {req}")


def demo_power_quality():
    """Demo power quality analysis"""
    print("\n" + "="*80)
    print("POWER QUALITY ANALYSIS")
    print("="*80)
    
    service = GridIntegrationService()
    
    request = PowerQualityRequest(
        system_size_kwp=10.0,
        inverter_specs={
            "rated_power_kw": 10.0,
            "efficiency": 0.97,
            "power_factor": 0.99,
            "thd": 0.03
        },
        grid_voltage=400,
        grid_frequency=50.0,
        standard=PowerQualityStandard.VDE_AR_N_4105
    )
    
    result = service.analyze_power_quality(request)
    
    print(f"\nSystem Size: {request.system_size_kwp} kWp")
    print(f"Standard: {request.standard.value}")
    print(f"\nCOMPLIANCE STATUS: {' COMPLIANT' if result.compliant else ' NON-COMPLIANT'}")
    print(f"\nPOWER QUALITY METRICS:")
    print(f"  Voltage Regulation: {result.voltage_regulation_percent:.2f}%")
    print(f"  Frequency Deviation: ±{result.frequency_deviation_hz:.3f} Hz")
    print(f"  Power Factor: {result.power_factor:.3f}")
    print(f"  Total Harmonic Distortion: {result.total_harmonic_distortion_percent:.2f}%")
    print(f"  Flicker Severity: {result.flicker_severity:.4f}")
    print(f"  DC Injection: {result.dc_injection_ma:.2f} mA")
    print(f"\nINDIVIDUAL HARMONICS:")
    for harmonic, value in result.individual_harmonics.items():
        print(f"  {harmonic}: {value * 100:.2f}%")
    
    if result.compliance_issues:
        print(f"\nCOMPLIANCE ISSUES:")
        for issue in result.compliance_issues:
            print(f"   {issue}")
    
    if result.recommendations:
        print(f"\nRECOMMENDATIONS:")
        for rec in result.recommendations:
            print(f"  • {rec}")


def demo_grid_stability():
    """Demo grid stability calculations"""
    print("\n" + "="*80)
    print("GRID STABILITY ANALYSIS")
    print("="*80)
    
    service = GridIntegrationService()
    
    request = GridStabilityRequest(
        system_size_kwp=10.0,
        grid_short_circuit_power_mva=50.0,
        grid_impedance_ohm=0.1,
        inverter_response_time_ms=50,
        enable_reactive_power_support=True,
        enable_voltage_regulation=True
    )
    
    result = service.calculate_grid_stability(request)
    
    print(f"\nSystem Size: {request.system_size_kwp} kWp")
    print(f"Grid Short Circuit Power: {request.grid_short_circuit_power_mva} MVA")
    print(f"\nSTABILITY METRICS:")
    print(f"  Overall Stability Index: {result.stability_index:.3f} (0=unstable, 1=very stable)")
    print(f"  Short Circuit Ratio: {result.short_circuit_ratio:.2f}")
    print(f"  Voltage Stability Margin: {result.voltage_stability_margin:.3f}")
    print(f"  Frequency Stability Margin: {result.frequency_stability_margin:.3f}")
    print(f"  Reactive Power Capability: {result.reactive_power_capability_kvar:.2f} kVAR")
    print(f"\nGRID SUPPORT SERVICES:")
    for service_name in result.grid_support_services:
        print(f"   {service_name}")
    
    if result.stability_concerns:
        print(f"\nSTABILITY CONCERNS:")
        for concern in result.stability_concerns:
            print(f"   {concern}")
    
    print(f"\nRECOMMENDED SETTINGS:")
    for setting, value in result.recommended_settings.items():
        print(f"  {setting}: {value}")


def demo_smart_grid():
    """Demo smart grid integration"""
    print("\n" + "="*80)
    print("SMART GRID INTEGRATION")
    print("="*80)
    
    service = GridIntegrationService()
    
    request = SmartGridRequest(
        system_size_kwp=10.0,
        battery_capacity_kwh=10.0,
        enable_demand_response=True,
        enable_frequency_regulation=True,
        enable_voltage_support=True,
        time_of_use_tariff={
            "peak": 0.40,
            "off_peak": 0.15,
            "shoulder": 0.25
        }
    )
    
    result = service.analyze_smart_grid_integration(request)
    
    print(f"\nSystem Size: {request.system_size_kwp} kWp")
    print(f"Battery Capacity: {request.battery_capacity_kwh} kWh")
    print(f"\nSMART GRID READINESS: {' READY' if result.smart_grid_ready else ' NOT READY'}")
    print(f"\nAVAILABLE SERVICES:")
    for service_name in result.available_services:
        print(f"   {service_name}")
    print(f"\nREVENUE STREAMS:")
    total_revenue = 0
    for stream, revenue in result.potential_revenue_streams.items():
        print(f"  {stream}: {revenue:,.2f} €/year")
        total_revenue += revenue
    print(f"  {'' * 40}")
    print(f"  Total Annual Revenue: {result.annual_grid_services_revenue:,.2f} €/year")
    print(f"\nCAPABILITIES:")
    print(f"  Demand Response Capacity: {result.demand_response_capacity_kw:.2f} kW")
    print(f"  Frequency Regulation: {' Yes' if result.frequency_regulation_capability else ' No'}")
    print(f"  Voltage Support: {' Yes' if result.voltage_support_capability else ' No'}")
    print(f"\nFINANCIAL ANALYSIS:")
    print(f"  Integration Cost: {result.integration_cost:,.2f} €")
    if result.payback_period_years:
        print(f"  Payback Period: {result.payback_period_years:.1f} years")
    
    if result.recommended_upgrades:
        print(f"\nRECOMMENDED UPGRADES:")
        for upgrade in result.recommended_upgrades:
            print(f"  • {upgrade}")


def demo_comprehensive_analysis():
    """Demo comprehensive grid integration analysis"""
    print("\n" + "="*80)
    print("COMPREHENSIVE GRID INTEGRATION ANALYSIS")
    print("="*80)
    
    service = GridIntegrationService()
    
    request = GridIntegrationAnalysisRequest(
        system_size_kwp=10.0,
        annual_production_kwh=12000,
        annual_consumption_kwh=10000,
        location="Berlin, Germany",
        connection_type=GridConnectionType.THREE_PHASE,
        metering_type=MeteringType.NET_METERING,
        feed_in_tariff_per_kwh=0.10,
        electricity_price_per_kwh=0.30,
        grid_voltage=400,
        distance_to_grid_m=50,
        battery_capacity_kwh=10.0,
        enable_smart_grid=True
    )
    
    result = service.comprehensive_grid_analysis(request)
    
    print(f"\nSystem Size: {request.system_size_kwp} kWp")
    print(f"Location: {request.location}")
    print(f"Metering Type: {request.metering_type.value}")
    print(f"\n{'='*80}")
    print("OVERALL ASSESSMENT")
    print(f"{'='*80}")
    print(f"Compliance Status: {result.compliance_status}")
    print(f"Feasibility Score: {result.overall_feasibility_score}/100")
    print(f"\nTOTAL BENEFITS:")
    print(f"  Annual Benefit: {result.total_annual_benefit:,.2f} €/year")
    print(f"  Lifetime Benefit (20 years): {result.total_lifetime_benefit:,.2f} €")
    print(f"\nRECOMMENDED CONFIGURATION:")
    for key, value in result.recommended_configuration.items():
        print(f"  {key}: {value}")
    
    print(f"\n{'='*80}")
    print("DETAILED ANALYSIS SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n1. FEED-IN TARIFF:")
    print(f"   Annual Revenue: {result.feed_in_analysis.annual_feed_in_revenue:,.2f} €")
    print(f"   Self-consumption Savings: {result.feed_in_analysis.annual_self_consumption_savings:,.2f} €")
    
    if result.net_metering_analysis:
        print(f"\n2. NET METERING:")
        print(f"   Self-sufficiency: {result.net_metering_analysis.self_sufficiency_rate * 100:.1f}%")
        print(f"   Grid Independence: {result.net_metering_analysis.grid_independence_rate * 100:.1f}%")
    
    print(f"\n3. GRID CONNECTION:")
    print(f"   Feasible: {' Yes' if result.connection_requirements.connection_feasible else ' No'}")
    print(f"   Cable Size: {result.connection_requirements.required_cable_size_mm2} mm²")
    print(f"   Estimated Cost: {result.connection_requirements.estimated_connection_cost:,.2f} €")
    
    print(f"\n4. POWER QUALITY:")
    print(f"   Compliant: {' Yes' if result.power_quality.compliant else ' No'}")
    print(f"   Power Factor: {result.power_quality.power_factor:.3f}")
    print(f"   THD: {result.power_quality.total_harmonic_distortion_percent:.2f}%")
    
    print(f"\n5. GRID STABILITY:")
    print(f"   Stability Index: {result.grid_stability.stability_index:.3f}")
    print(f"   SCR: {result.grid_stability.short_circuit_ratio:.2f}")
    
    if result.smart_grid_potential:
        print(f"\n6. SMART GRID:")
        print(f"   Ready: {' Yes' if result.smart_grid_potential.smart_grid_ready else ' No'}")
        print(f"   Annual Revenue: {result.smart_grid_potential.annual_grid_services_revenue:,.2f} €")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("SOLAR GRID INTEGRATION - COMPREHENSIVE DEMO")
    print("="*80)
    print("\nThis demo showcases all grid integration features:")
    print("1. Feed-in Tariff Analysis")
    print("2. Net Metering Analysis")
    print("3. Grid Connection Requirements")
    print("4. Power Quality Analysis")
    print("5. Grid Stability Calculations")
    print("6. Smart Grid Integration")
    print("7. Comprehensive Analysis")
    
    try:
        demo_feed_in_tariff()
        demo_net_metering()
        demo_grid_connection()
        demo_power_quality()
        demo_grid_stability()
        demo_smart_grid()
        demo_comprehensive_analysis()
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nAll grid integration features demonstrated successfully!")
        print("See documentation for more details:")
        print("  - docs/GRID_INTEGRATION_GUIDE.md")
        print("  - docs/GRID_INTEGRATION_QUICK_REFERENCE.md")
        
    except Exception as e:
        print(f"\n Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
