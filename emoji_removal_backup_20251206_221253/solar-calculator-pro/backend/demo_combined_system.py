"""
Demo script for Combined Heat Pump + PV System Integration.
Demonstrates system analysis, optimization, and monitoring capabilities.
"""

from services.combined_system_service import CombinedSystemService
from models.combined_system_schemas import (
    CombinedSystemRequest,
    ControlStrategy,
    TimeOfUseProfile,
    OptimizationRequest
)


def demo_basic_analysis():
    """Demonstrate basic combined system analysis"""
    print("=" * 80)
    print("DEMO 1: Basic Combined System Analysis")
    print("=" * 80)
    
    service = CombinedSystemService()
    
    request = CombinedSystemRequest(
        # PV System
        pv_system_size=10.0,
        pv_annual_production=10000.0,
        pv_module_count=30,
        pv_orientation="south",
        pv_tilt_angle=30.0,
        
        # Heat Pump
        hp_model="Viessmann Vitocal 200-S",
        hp_cop=4.2,
        hp_heating_capacity=8.0,
        hp_power_consumption=2.0,
        
        # Building
        annual_heating_demand=12000.0,
        building_insulation_quality="good",
        
        # Battery
        battery_capacity=10.0,
        battery_efficiency=0.95,
        
        # Tariff
        electricity_price=0.30,
        feed_in_tariff=0.08,
        
        # Control
        control_strategy=ControlStrategy.SELF_CONSUMPTION,
        
        # Location
        location="Berlin",
        latitude=52.52,
        longitude=13.40
    )
    
    result = service.analyze_combined_system(request)
    
    print("\n📊 SYSTEM CONFIGURATION")
    print(f"PV System: {result.system_configuration['pv_system_size_kwp']} kWp")
    print(f"Heat Pump: {result.system_configuration['heat_pump_model']}")
    print(f"Battery: {result.system_configuration['battery_capacity_kwh']} kWh")
    print(f"Control Strategy: {result.system_configuration['control_strategy']}")
    
    print("\n⚡ ANNUAL ENERGY FLOW")
    print(f"PV Production: {result.annual_energy_flow['total_pv_production']:,.0f} kWh")
    print(f"HP Consumption: {result.annual_energy_flow['total_hp_consumption']:,.0f} kWh")
    print(f"Self-Consumption: {result.annual_energy_flow['total_self_consumption']:,.0f} kWh")
    print(f"Grid Import: {result.annual_energy_flow['total_grid_import']:,.0f} kWh")
    print(f"Grid Export: {result.annual_energy_flow['total_grid_export']:,.0f} kWh")
    
    print("\n🔄 SYNERGY ANALYSIS")
    print(f"PV to HP Direct: {result.synergy_analysis.pv_to_hp_direct:,.0f} kWh")
    print(f"PV to HP via Battery: {result.synergy_analysis.pv_to_hp_via_battery:,.0f} kWh")
    print(f"Total PV for Heating: {result.synergy_analysis.total_pv_for_heating:,.0f} kWh")
    print(f"Heating Cost Reduction: €{result.synergy_analysis.heating_cost_reduction:,.2f}")
    print(f"Heating Cost Reduction: {result.synergy_analysis.heating_cost_reduction_percent:.1f}%")
    print(f"COP Improvement: +{result.synergy_analysis.cop_improvement:.2f}")
    print(f"Heating Grid Independence: {result.synergy_analysis.grid_independence_heating:.1f}%")
    
    print("\n💰 FINANCIAL ANALYSIS")
    print(f"Total Investment: €{result.financial_analysis.total_investment:,.2f}")
    print(f"  - PV System: €{result.financial_analysis.pv_system_cost:,.2f}")
    print(f"  - Heat Pump: €{result.financial_analysis.heat_pump_cost:,.2f}")
    print(f"  - Battery: €{result.financial_analysis.battery_cost:,.2f}")
    print(f"  - Installation: €{result.financial_analysis.installation_cost:,.2f}")
    print(f"\nAnnual Savings: €{result.financial_analysis.annual_savings:,.2f}")
    print(f"Payback Period: {result.financial_analysis.simple_payback_years:.1f} years")
    print(f"NPV (20 years): €{result.financial_analysis.npv_20_years:,.2f}")
    print(f"IRR: {result.financial_analysis.irr:.1f}%")
    print(f"LCOE: €{result.financial_analysis.lcoe:.3f}/kWh")
    
    print("\n📈 PERFORMANCE METRICS")
    print(f"Self-Consumption Rate: {result.self_consumption_rate * 100:.1f}%")
    print(f"Grid Independence Rate: {result.grid_independence_rate * 100:.1f}%")
    print(f"Renewable Energy Rate: {result.renewable_energy_rate * 100:.1f}%")
    
    print("\n🌱 ENVIRONMENTAL IMPACT")
    print(f"Annual CO2 Savings: {result.annual_co2_savings:,.0f} kg")
    print(f"Equivalent Trees Planted: {result.equivalent_trees_planted}")
    
    print("\n📋 CONTROL RECOMMENDATIONS")
    for i, rec in enumerate(result.control_recommendations, 1):
        print(f"{i}. {rec}")
    
    print("\n✅ Analysis Complete!\n")


def demo_time_of_use_tariff():
    """Demonstrate analysis with time-of-use tariff"""
    print("=" * 80)
    print("DEMO 2: Time-of-Use Tariff Optimization")
    print("=" * 80)
    
    service = CombinedSystemService()
    
    # Define time-of-use tariff
    tariff = []
    for hour in range(24):
        if 17 <= hour <= 20:  # Peak hours
            price = 0.40
            is_peak = True
        elif 0 <= hour <= 5:  # Off-peak hours
            price = 0.20
            is_peak = False
        else:  # Standard hours
            price = 0.30
            is_peak = False
        
        tariff.append(TimeOfUseProfile(
            hour=hour,
            price_per_kwh=price,
            is_peak=is_peak
        ))
    
    request = CombinedSystemRequest(
        pv_system_size=10.0,
        pv_annual_production=10000.0,
        pv_module_count=30,
        pv_orientation="south",
        pv_tilt_angle=30.0,
        hp_model="Viessmann Vitocal 200-S",
        hp_cop=4.2,
        hp_heating_capacity=8.0,
        hp_power_consumption=2.0,
        annual_heating_demand=12000.0,
        building_insulation_quality="good",
        battery_capacity=10.0,
        battery_efficiency=0.95,
        electricity_price=0.30,  # Average price
        feed_in_tariff=0.08,
        time_of_use_tariff=tariff,
        control_strategy=ControlStrategy.COST_OPTIMIZATION,
        location="Berlin",
        latitude=52.52,
        longitude=13.40
    )
    
    result = service.analyze_combined_system(request)
    
    print("\n⏰ TIME-OF-USE TARIFF")
    print("Peak Hours (17-20): €0.40/kWh")
    print("Off-Peak Hours (0-5): €0.20/kWh")
    print("Standard Hours: €0.30/kWh")
    
    print("\n💰 FINANCIAL IMPACT")
    print(f"Annual Savings: €{result.financial_analysis.annual_savings:,.2f}")
    print(f"Payback Period: {result.financial_analysis.simple_payback_years:.1f} years")
    
    print("\n🎯 SMART CONTROL SCHEDULE (First 24 Hours)")
    print(f"{'Hour':<6} {'Mode':<12} {'Power':<8} {'Reason':<50}")
    print("-" * 80)
    for schedule in result.smart_control_schedule[:24]:
        print(f"{schedule.hour:02d}:00  {schedule.hp_operation_mode:<12} "
              f"{schedule.hp_power_level:.1f}      {schedule.reason}")
    
    print("\n✅ Time-of-Use Analysis Complete!\n")


def demo_comparison_scenarios():
    """Demonstrate comparison with alternative scenarios"""
    print("=" * 80)
    print("DEMO 3: Comparison with Alternative Scenarios")
    print("=" * 80)
    
    service = CombinedSystemService()
    
    request = CombinedSystemRequest(
        pv_system_size=10.0,
        pv_annual_production=10000.0,
        pv_module_count=30,
        pv_orientation="south",
        pv_tilt_angle=30.0,
        hp_model="Viessmann Vitocal 200-S",
        hp_cop=4.2,
        hp_heating_capacity=8.0,
        hp_power_consumption=2.0,
        annual_heating_demand=12000.0,
        building_insulation_quality="good",
        battery_capacity=10.0,
        electricity_price=0.30,
        feed_in_tariff=0.08,
        control_strategy=ControlStrategy.BALANCED,
        location="Berlin",
        latitude=52.52,
        longitude=13.40
    )
    
    result = service.analyze_combined_system(request)
    
    print("\n📊 SCENARIO COMPARISON")
    print("\n1️⃣  PV ONLY (No Heat Pump)")
    print(f"   Investment: €{result.comparison_pv_only['investment']:,.2f}")
    print(f"   Annual Savings: €{result.comparison_pv_only['annual_savings']:,.2f}")
    print(f"   Payback: {result.comparison_pv_only['payback_years']:.1f} years")
    
    print("\n2️⃣  HEAT PUMP ONLY (No PV)")
    print(f"   Investment: €{result.comparison_hp_only['investment']:,.2f}")
    print(f"   Annual Savings: €{result.comparison_hp_only['annual_savings']:,.2f}")
    print(f"   Payback: {result.comparison_hp_only['payback_years']:.1f} years")
    
    print("\n3️⃣  COMBINED SYSTEM (PV + Heat Pump)")
    print(f"   Investment: €{result.financial_analysis.total_investment:,.2f}")
    print(f"   Annual Savings: €{result.financial_analysis.annual_savings:,.2f}")
    print(f"   Payback: {result.financial_analysis.simple_payback_years:.1f} years")
    
    print("\n4️⃣  CONVENTIONAL (No PV, No HP)")
    print(f"   Annual Cost: €{result.comparison_conventional['annual_cost']:,.2f}")
    
    print("\n🎁 SYNERGY BENEFIT")
    print(f"Additional benefit from combination: €{result.synergy_benefit:,.2f}/year")
    print(f"This is the extra savings you get by combining PV and HP")
    print(f"compared to installing them separately!")
    
    print("\n✅ Comparison Complete!\n")


def demo_monitoring():
    """Demonstrate system monitoring"""
    print("=" * 80)
    print("DEMO 4: Real-Time System Monitoring")
    print("=" * 80)
    
    service = CombinedSystemService()
    
    # Get monitoring data (simulated)
    monitoring = service.get_monitoring_data(system_id=1)
    
    print(f"\n📅 Timestamp: {monitoring.timestamp}")
    
    print("\n☀️ PV SYSTEM")
    print(f"Current Power: {monitoring.pv_current_power:.2f} kW")
    print(f"Daily Production: {monitoring.pv_daily_production:.1f} kWh")
    print(f"Monthly Production: {monitoring.pv_monthly_production:.1f} kWh")
    print(f"Annual Production: {monitoring.pv_annual_production:.1f} kWh")
    
    print("\n🔥 HEAT PUMP")
    print(f"Status: {monitoring.hp_status.upper()}")
    print(f"Current Power: {monitoring.hp_current_power:.2f} kW")
    print(f"Current COP: {monitoring.hp_current_cop:.1f}")
    print(f"Daily Consumption: {monitoring.hp_daily_consumption:.1f} kWh")
    print(f"Supply Temperature: {monitoring.hp_supply_temperature:.1f}°C")
    print(f"Return Temperature: {monitoring.hp_return_temperature:.1f}°C")
    
    print("\n🔋 BATTERY")
    print(f"State of Charge: {monitoring.battery_soc:.1f}%")
    print(f"Power: {monitoring.battery_power:+.2f} kW {'(charging)' if monitoring.battery_power > 0 else '(discharging)'}")
    
    print("\n🔌 GRID")
    print(f"Power: {monitoring.grid_power:+.2f} kW {'(importing)' if monitoring.grid_power > 0 else '(exporting)'}")
    print(f"Daily Import: {monitoring.grid_daily_import:.1f} kWh")
    print(f"Daily Export: {monitoring.grid_daily_export:.1f} kWh")
    
    print("\n📊 PERFORMANCE")
    print(f"Self-Consumption Rate Today: {monitoring.self_consumption_rate_today * 100:.1f}%")
    print(f"Grid Independence Rate Today: {monitoring.grid_independence_rate_today * 100:.1f}%")
    print(f"Cost Savings Today: €{monitoring.cost_savings_today:.2f}")
    
    print("\n✅ Monitoring Data Retrieved!\n")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("COMBINED HEAT PUMP + PV SYSTEM INTEGRATION - DEMO")
    print("=" * 80 + "\n")
    
    try:
        demo_basic_analysis()
        input("Press Enter to continue to next demo...")
        
        demo_time_of_use_tariff()
        input("Press Enter to continue to next demo...")
        
        demo_comparison_scenarios()
        input("Press Enter to continue to next demo...")
        
        demo_monitoring()
        
        print("=" * 80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
