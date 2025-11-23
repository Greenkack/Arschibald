"""
Battery Storage Service Demo

Demonstrates all features of the battery storage service including:
- Battery sizing calculations
- ROI analysis
- Discharge strategies
- Grid independence
- Lifecycle analysis
- Monitoring integration
"""

from services.battery_storage_service import (
    BatteryStorageService,
    BatterySizingRequest,
    DischargeStrategy
)


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_battery_sizing():
    """Demonstrate battery sizing calculations"""
    print_section("1. BATTERY SIZING CALCULATIONS")
    
    service = BatteryStorageService()
    
    # Example 1: Basic sizing
    print("Example 1: Basic Battery Sizing")
    print("-" * 40)
    request = BatterySizingRequest(
        daily_consumption_kwh=15.0,
        pv_system_size_kwp=10.0,
        annual_production_kwh=10000.0,
        self_consumption_rate=0.35,
        grid_feed_in_tariff=0.08,
        electricity_price=0.30
    )
    
    result = service.calculate_battery_sizing(request)
    print(f"Recommended Capacity: {result['recommended_capacity_kwh']:.2f} kWh")
    print(f"Selected Battery: {result['selected_battery']}")
    print(f"Battery Specs: {result['battery_specs']['capacity_kwh']} kWh")
    print(f"Performance:")
    print(f"  - Storable Energy/Day: {result['performance']['storable_energy_per_day_kwh']:.2f} kWh")
    print(f"  - New Self-Consumption: {result['performance']['new_self_consumption_rate_percent']:.1f}%")
    print(f"  - Improvement: +{result['performance']['improvement_percent']:.1f}%")
    print(f"  - Daily Cycles: {result['performance']['cycles_per_day']:.2f}")
    
    # Example 2: Sizing for backup
    print("\nExample 2: Sizing for 8 Hours Backup")
    print("-" * 40)
    request_backup = BatterySizingRequest(
        daily_consumption_kwh=15.0,
        pv_system_size_kwp=10.0,
        annual_production_kwh=10000.0,
        self_consumption_rate=0.35,
        grid_feed_in_tariff=0.08,
        electricity_price=0.30,
        backup_hours=8
    )
    
    result_backup = service.calculate_battery_sizing(request_backup)
    print(f"Recommended Capacity: {result_backup['recommended_capacity_kwh']:.2f} kWh")
    print(f"Backup Hours: {result_backup['sizing_rationale']['backup_hours']}")
    
    # Example 3: Sizing for self-sufficiency target
    print("\nExample 3: Sizing for 80% Self-Sufficiency")
    print("-" * 40)
    request_target = BatterySizingRequest(
        daily_consumption_kwh=15.0,
        pv_system_size_kwp=10.0,
        annual_production_kwh=10000.0,
        self_consumption_rate=0.35,
        grid_feed_in_tariff=0.08,
        electricity_price=0.30,
        target_self_sufficiency=0.8
    )
    
    result_target = service.calculate_battery_sizing(request_target)
    print(f"Recommended Capacity: {result_target['recommended_capacity_kwh']:.2f} kWh")
    print(f"Target Self-Sufficiency: {result_target['sizing_rationale']['target_self_sufficiency'] * 100:.0f}%")


def demo_roi_analysis():
    """Demonstrate ROI analysis"""
    print_section("2. ROI ANALYSIS")
    
    service = BatteryStorageService()
    battery_specs = service.default_battery_specs['medium']
    
    request = BatterySizingRequest(
        daily_consumption_kwh=15.0,
        pv_system_size_kwp=10.0,
        annual_production_kwh=10000.0,
        self_consumption_rate=0.35,
        grid_feed_in_tariff=0.08,
        electricity_price=0.30
    )
    
    result = service.calculate_battery_roi(battery_specs, request, analysis_years=20)
    
    print(f"Initial Investment: €{result['initial_investment']:,.2f}")
    print(f"Annual Savings (Year 1): €{result['annual_savings_year_1']:,.2f}")
    print(f"Lifetime Savings (20 years): €{result['lifetime_savings']:,.2f}")
    print(f"Simple Payback Period: {result['simple_payback_years']:.1f} years")
    print(f"Payback Year: {result['payback_year']}")
    print(f"Net Present Value: €{result['npv']:,.2f}")
    print(f"ROI: {result['roi_percent']:.1f}%")
    
    print("\nSavings Breakdown:")
    print(f"  - Grid Purchase Savings: €{result['savings_breakdown']['grid_purchase_savings']:,.2f}/year")
    print(f"  - Arbitrage Savings: €{result['savings_breakdown']['arbitrage_savings']:,.2f}/year")
    
    print("\nCash Flow Analysis (First 5 Years):")
    print("-" * 60)
    print(f"{'Year':<6} {'Annual Savings':<18} {'Cumulative':<18} {'Capacity':<12}")
    print("-" * 60)
    for cf in result['cash_flow_analysis'][:5]:
        print(f"{cf['year']:<6} €{cf['annual_savings']:>15,.2f} €{cf['cumulative_savings']:>15,.2f} {cf['capacity_remaining']:>10.1f}%")


def demo_discharge_strategies():
    """Demonstrate discharge strategies"""
    print_section("3. DISCHARGE STRATEGIES")
    
    service = BatteryStorageService()
    battery_specs = service.default_battery_specs['medium']
    
    # Sample hourly data (24 hours)
    hourly_production = [0, 0, 0, 0, 0, 0.5, 2, 4, 6, 8, 9, 10,
                         9, 8, 6, 4, 2, 0.5, 0, 0, 0, 0, 0, 0]
    hourly_consumption = [1, 1, 1, 1, 1, 2, 3, 2, 1.5, 1, 1, 1.5,
                          2, 1.5, 1, 1.5, 2, 3, 4, 3, 2, 1.5, 1, 1]
    
    strategies = [
        ('self_consumption', 'Self-Consumption'),
        ('peak_shaving', 'Peak Shaving'),
        ('time_of_use', 'Time-of-Use'),
        ('backup', 'Backup')
    ]
    
    for strategy_type, strategy_name in strategies:
        print(f"\n{strategy_name} Strategy")
        print("-" * 40)
        
        strategy = DischargeStrategy(
            strategy_type=strategy_type,
            peak_hours=[17, 18, 19, 20],
            min_soc=0.2,
            max_soc=1.0,
            priority='self_consumption'
        )
        
        result = service.calculate_discharge_strategy(
            strategy,
            battery_specs,
            hourly_production,
            hourly_consumption
        )
        
        perf = result['performance']
        print(f"Total Charged: {perf['total_charged_kwh']:.2f} kWh")
        print(f"Total Discharged: {perf['total_discharged_kwh']:.2f} kWh")
        print(f"Round-Trip Efficiency: {perf['round_trip_efficiency_percent']:.1f}%")
        print(f"Grid Import: {perf['grid_import_kwh']:.2f} kWh")
        print(f"Grid Export: {perf['grid_export_kwh']:.2f} kWh")
        print(f"Self-Consumption from Battery: {perf['self_consumption_from_battery_kwh']:.2f} kWh")
        print(f"Final SOC: {perf['final_soc_percent']:.1f}%")


def demo_grid_independence():
    """Demonstrate grid independence calculations"""
    print_section("4. GRID INDEPENDENCE")
    
    service = BatteryStorageService()
    battery_specs = service.default_battery_specs['medium']
    
    request = BatterySizingRequest(
        daily_consumption_kwh=15.0,
        pv_system_size_kwp=10.0,
        annual_production_kwh=10000.0,
        self_consumption_rate=0.35,
        grid_feed_in_tariff=0.08,
        electricity_price=0.30
    )
    
    # Monthly data
    monthly_production = [600, 700, 850, 950, 1100, 1150,
                          1200, 1150, 1000, 800, 650, 550]
    monthly_consumption = [450, 450, 450, 450, 450, 450,
                           450, 450, 450, 450, 450, 450]
    
    result = service.calculate_grid_independence(
        battery_specs,
        request,
        monthly_production,
        monthly_consumption
    )
    
    print("Annual Metrics:")
    print("-" * 40)
    metrics = result['annual_metrics']
    print(f"Self-Sufficiency: {metrics['self_sufficiency_percent']:.1f}%")
    print(f"Grid Dependency: {metrics['grid_dependency_percent']:.1f}%")
    print(f"Battery Contribution: {metrics['battery_contribution_percent']:.1f}%")
    print(f"Total Self-Consumption: {metrics['total_self_consumption_kwh']:,.2f} kWh")
    print(f"Total Grid Import: {metrics['total_grid_import_kwh']:,.2f} kWh")
    print(f"Total Battery Contribution: {metrics['total_battery_contribution_kwh']:,.2f} kWh")
    
    print("\nComparison:")
    print("-" * 40)
    comp = result['comparison']
    print(f"Without Battery: {comp['without_battery_self_sufficiency_percent']:.1f}%")
    print(f"With Battery: {comp['with_battery_self_sufficiency_percent']:.1f}%")
    print(f"Improvement: +{comp['improvement_percent']:.1f}%")
    
    print("\nMonthly Analysis (First 6 Months):")
    print("-" * 80)
    print(f"{'Month':<6} {'Production':<12} {'Consumption':<12} {'Battery':<12} {'Grid Import':<12} {'Self-Suff.':<12}")
    print("-" * 80)
    for month_data in result['monthly_analysis'][:6]:
        print(f"{month_data['month']:<6} "
              f"{month_data['production_kwh']:>10.0f} kWh "
              f"{month_data['consumption_kwh']:>10.0f} kWh "
              f"{month_data['battery_contribution_kwh']:>10.1f} kWh "
              f"{month_data['grid_import_kwh']:>10.1f} kWh "
              f"{month_data['self_sufficiency_percent']:>10.1f}%")


def demo_lifecycle_analysis():
    """Demonstrate lifecycle analysis"""
    print_section("5. LIFECYCLE ANALYSIS")
    
    service = BatteryStorageService()
    battery_specs = service.default_battery_specs['medium']
    
    result = service.calculate_lifecycle_analysis(
        battery_specs,
        daily_cycles=1.0,
        analysis_years=20
    )
    
    print("Lifecycle Parameters:")
    print("-" * 40)
    params = result['lifecycle_parameters']
    print(f"Daily Cycles: {params['daily_cycles']}")
    print(f"Cycles per Year: {params['cycles_per_year']:.0f}")
    print(f"Total Cycles (20 years): {params['total_cycles']:,}")
    print(f"Warranty Cycles: {params['warranty_cycles']:,}")
    print(f"Warranty Years: {params['warranty_years']}")
    
    print("\nCost Analysis:")
    print("-" * 40)
    costs = result['cost_analysis']
    print(f"Initial Cost: €{costs['initial_cost']:,.2f}")
    print(f"Replacement Costs: €{costs['replacement_costs']:,.2f}")
    print(f"Maintenance Costs: €{costs['maintenance_costs']:,.2f}")
    print(f"Total Cost of Ownership: €{costs['total_cost_of_ownership']:,.2f}")
    print(f"Cost per Year: €{costs['cost_per_year']:,.2f}")
    
    print("\nReplacement Schedule:")
    print("-" * 40)
    if result['replacement_schedule']:
        for replacement in result['replacement_schedule']:
            print(f"Year {replacement['year']}: €{replacement['replacement_cost']:,.2f} "
                  f"(after {replacement['cycles_completed']:,} cycles)")
    else:
        print("No replacements needed within analysis period")
    
    print("\nCapacity Timeline (Every 5 Years):")
    print("-" * 60)
    print(f"{'Year':<6} {'Capacity':<15} {'Capacity %':<15} {'Cycles':<15}")
    print("-" * 60)
    for timeline in result['capacity_timeline'][::5]:
        print(f"{timeline['year']:<6} "
              f"{timeline['capacity_kwh']:>13.2f} kWh "
              f"{timeline['capacity_percent']:>13.1f}% "
              f"{timeline['cycles_completed']:>13,}")
    
    print("\nEnd of Life:")
    print("-" * 40)
    eol = result['end_of_life']
    print(f"Final Capacity: {eol['final_capacity_percent']:.1f}%")
    print(f"Total Cycles: {eol['total_cycles_completed']:,}")
    print(f"Years of Service: {eol['years_of_service']}")


def demo_monitoring_integration():
    """Demonstrate monitoring integration"""
    print_section("6. MONITORING INTEGRATION")
    
    service = BatteryStorageService()
    battery_specs = service.default_battery_specs['medium']
    
    result = service.get_monitoring_integration_config(
        battery_specs,
        monitoring_system='generic'
    )
    
    print("Configuration:")
    print("-" * 40)
    config = result['configuration']
    print(f"API Endpoint: {config['api_endpoint']}")
    print(f"Protocol: {config['protocol']}")
    print(f"Authentication: {config['authentication']}")
    print(f"Data Format: {config['data_format']}")
    
    print("\nReal-Time Data Points:")
    print("-" * 40)
    for dp in result['data_points']['real_time']:
        print(f"  - {dp['name']}: {dp['unit']} (every {dp['update_interval_seconds']}s)")
    
    print("\nHistorical Data Points:")
    print("-" * 40)
    for dp in result['data_points']['historical']:
        print(f"  - {dp['name']}: {dp['unit']} ({dp['aggregation']})")
    
    print("\nAlert Thresholds:")
    print("-" * 40)
    print("Critical:")
    for alert in result['alert_thresholds']['critical']:
        print(f"  - {alert['parameter']} {alert['condition']} {alert['value']}: {alert['message']}")
    
    print("\nWarning:")
    for alert in result['alert_thresholds']['warning'][:3]:
        print(f"  - {alert['parameter']} {alert['condition']} {alert['value']}: {alert['message']}")
    
    print("\nRecommended Polling Intervals:")
    print("-" * 40)
    for key, value in result['recommended_polling_intervals'].items():
        print(f"  - {key}: {value}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  BATTERY STORAGE SERVICE - COMPREHENSIVE DEMO")
    print("=" * 80)
    
    try:
        demo_battery_sizing()
        demo_roi_analysis()
        demo_discharge_strategies()
        demo_grid_independence()
        demo_lifecycle_analysis()
        demo_monitoring_integration()
        
        print("\n" + "=" * 80)
        print("  DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
