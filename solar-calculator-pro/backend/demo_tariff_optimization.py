"""
Demo script for tariff optimization system
"""

from datetime import time, datetime, timedelta
from models.tariff_schemas import (
    TariffStructure, TariffType, TariffPeriod, HeatingSchedule,
    OptimizationRequest, DemandResponseEvent, RealTimeTariffData
)
from services.tariff_optimization_service import TariffOptimizationService


def demo_time_of_use_optimization():
    """Demonstrate time-of-use tariff optimization"""
    print("=" * 80)
    print("DEMO: Time-of-Use Tariff Optimization")
    print("=" * 80)
    
    # Create time-of-use tariff
    tariff = TariffStructure(
        tariff_id="tou_demo",
        name="Standard Time-of-Use",
        type=TariffType.TIME_OF_USE,
        base_rate=0.30,
        periods=[
            TariffPeriod(start_time=time(22, 0), end_time=time(6, 0), rate=0.18, name="night"),
            TariffPeriod(start_time=time(6, 0), end_time=time(9, 0), rate=0.35, name="morning-peak"),
            TariffPeriod(start_time=time(9, 0), end_time=time(17, 0), rate=0.28, name="day"),
            TariffPeriod(start_time=time(17, 0), end_time=time(22, 0), rate=0.38, name="evening-peak")
        ]
    )
    
    # Create typical heating schedule
    schedule = [
        HeatingSchedule(hour=h, target_temperature=21.0 if 6 <= h <= 22 else 19.0, flexible=True)
        for h in range(24)
    ]
    
    # Create optimization request
    request = OptimizationRequest(
        tariff_structure=tariff,
        heat_pump_cop=3.5,
        annual_heating_demand=12000,
        current_schedule=schedule,
        comfort_priority=0.7
    )
    
    # Optimize
    service = TariffOptimizationService()
    result = service.optimize_schedule(request)
    
    # Display results
    print(f"\n Optimization Results:")
    print(f"   Original Annual Cost: {result.original_cost:,.2f} EUR")
    print(f"   Optimized Annual Cost: {result.optimized_cost:,.2f} EUR")
    print(f"    Annual Savings: {result.savings:,.2f} EUR ({result.savings_percent:.1f}%)")
    print(f"    Peak Load Reduction: {result.peak_load_reduction:.2f} kW")
    print(f"    Comfort Score: {result.comfort_score * 100:.1f}%")
    
    print(f"\n Optimized Schedule (sample hours):")
    for hour in [0, 6, 12, 18, 22]:
        slot = result.optimized_schedule[hour]
        shifted = f" (shifted from hour {slot.shifted_from})" if slot.shifted_from else ""
        print(f"   Hour {hour:02d}: {slot.target_temperature:.1f}°C, "
              f"{slot.estimated_consumption:.2f} kWh @ {slot.tariff_rate:.2f} EUR/kWh{shifted}")


def demo_tariff_comparison():
    """Demonstrate tariff comparison"""
    print("\n" + "=" * 80)
    print("DEMO: Tariff Comparison")
    print("=" * 80)
    
    # Create different tariffs
    flat_rate = TariffStructure(
        tariff_id="flat",
        name="Flat Rate",
        type=TariffType.FLAT_RATE,
        base_rate=0.30,
        periods=[]
    )
    
    time_of_use = TariffStructure(
        tariff_id="tou",
        name="Time of Use",
        type=TariffType.TIME_OF_USE,
        base_rate=0.30,
        periods=[
            TariffPeriod(start_time=time(22, 0), end_time=time(6, 0), rate=0.18, name="off-peak"),
            TariffPeriod(start_time=time(6, 0), end_time=time(22, 0), rate=0.35, name="peak")
        ]
    )
    
    dynamic = TariffStructure(
        tariff_id="dynamic",
        name="Dynamic Pricing",
        type=TariffType.DYNAMIC,
        base_rate=0.28,
        periods=[
            TariffPeriod(start_time=time(0, 0), end_time=time(6, 0), rate=0.15, name="very-low"),
            TariffPeriod(start_time=time(6, 0), end_time=time(9, 0), rate=0.40, name="high"),
            TariffPeriod(start_time=time(9, 0), end_time=time(17, 0), rate=0.25, name="medium"),
            TariffPeriod(start_time=time(17, 0), end_time=time(21, 0), rate=0.42, name="very-high"),
            TariffPeriod(start_time=time(21, 0), end_time=time(24, 0), rate=0.20, name="low")
        ]
    )
    
    # Compare tariffs
    service = TariffOptimizationService()
    heating_profile = {hour: 1.2 for hour in range(24)}
    
    comparisons = service.compare_tariffs([flat_rate, time_of_use, dynamic], heating_profile)
    
    print(f"\n Tariff Comparison Results:")
    for i, comp in enumerate(comparisons, 1):
        print(f"\n{i}. {comp.tariff_name} ({comp.tariff_type.value})")
        print(f"   Annual Cost: {comp.annual_cost:,.2f} EUR")
        print(f"   Potential Savings: {comp.potential_savings:,.2f} EUR")
        print(f"   {' RECOMMENDED' if comp.recommended else '   Not recommended'}")
        print(f"   Pros: {', '.join(comp.pros)}")
        print(f"   Cons: {', '.join(comp.cons)}")


def demo_demand_response():
    """Demonstrate demand response event processing"""
    print("\n" + "=" * 80)
    print("DEMO: Demand Response Event")
    print("=" * 80)
    
    # Create demand response event
    event = DemandResponseEvent(
        event_id="dr_20240115_001",
        start_time=datetime.now() + timedelta(hours=2),
        end_time=datetime.now() + timedelta(hours=4),
        incentive_rate=0.75,  # 75 cents per kWh reduced
        required_reduction=3.0  # 3 kW reduction needed
    )
    
    # Create current schedule
    schedule = [
        HeatingSchedule(hour=h, target_temperature=21.0, flexible=True)
        for h in range(24)
    ]
    
    # Process event
    service = TariffOptimizationService()
    result = service.process_demand_response(event, schedule)
    
    print(f"\n Demand Response Event Analysis:")
    print(f"   Event ID: {event.event_id}")
    print(f"   Duration: {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}")
    print(f"   Required Reduction: {event.required_reduction} kW")
    print(f"   Incentive Rate: {event.incentive_rate:.2f} EUR/kWh")
    
    print(f"\n Participation Analysis:")
    print(f"   Can Participate: {' Yes' if result['can_participate'] else ' No'}")
    print(f"   Current Load: {result['current_load']:.2f} kW")
    print(f"   Reduction Achieved: {result['reduction_achieved']:.2f} kW")
    print(f"    Incentive Earnings: {result['incentive_earnings']:.2f} EUR")
    print(f"   Recommendation: {result['recommendation'].upper()}")


def demo_real_time_monitoring():
    """Demonstrate real-time tariff monitoring"""
    print("\n" + "=" * 80)
    print("DEMO: Real-Time Tariff Monitoring")
    print("=" * 80)
    
    # Create real-time tariff data
    tariff_data = RealTimeTariffData(
        timestamp=datetime.now(),
        current_rate=0.22,
        forecast_next_hour=0.28,
        forecast_next_4_hours=[0.28, 0.32, 0.35, 0.30],
        forecast_next_24_hours=[
            0.22, 0.20, 0.18, 0.18, 0.20, 0.25,  # 0-5
            0.35, 0.38, 0.40, 0.32, 0.28, 0.26,  # 6-11
            0.28, 0.30, 0.32, 0.34, 0.36, 0.42,  # 12-17
            0.45, 0.40, 0.35, 0.28, 0.24, 0.22   # 18-23
        ],
        grid_load_level="medium"
    )
    
    # Create schedule
    schedule = [
        HeatingSchedule(hour=h, target_temperature=21.0, flexible=True)
        for h in range(24)
    ]
    
    # Monitor
    service = TariffOptimizationService()
    result = service.monitor_real_time_tariff(tariff_data, schedule)
    
    print(f"\n Real-Time Tariff Analysis:")
    print(f"   Current Rate: {result['current_rate']:.2f} EUR/kWh")
    print(f"   Average Forecast: {result['average_forecast']:.2f} EUR/kWh")
    print(f"   Grid Load Level: {result['grid_load_level'].upper()}")
    print(f"   Is Favorable: {' Yes' if result['is_favorable'] else ' No'}")
    
    print(f"\n Recommendation:")
    print(f"   {result['recommendation']}")
    print(f"   Action: {result['action'].upper()}")
    print(f"    Savings Opportunity: {result['savings_opportunity']:.2f} EUR per 10 kWh")
    
    print(f"\n Optimal Hours (Next 24h):")
    optimal_hours = result['optimal_hours_next_24h']
    print(f"   Best times to heat: {', '.join(f'{h:02d}:00' for h in optimal_hours[:5])}")


def main():
    """Run all demos"""
    print("\n HEAT PUMP DYNAMIC TARIFF OPTIMIZATION SYSTEM")
    print("=" * 80)
    
    demo_time_of_use_optimization()
    demo_tariff_comparison()
    demo_demand_response()
    demo_real_time_monitoring()
    
    print("\n" + "=" * 80)
    print(" All demos completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
