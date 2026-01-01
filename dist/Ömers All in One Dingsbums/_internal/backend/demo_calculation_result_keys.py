"""
Demo: Calculation Results Dynamic Keys

This demo shows how to use the Calculation Results Dynamic Keys service
to attach dynamic keys to calculation results, create versions, compare
results, track history, and export data.

Requirements: 14.7
Task: 225
"""

try:
    from backend.services.calculation_result_key_service import (
        CalculationResultKeyManager,
        CalculationType,
        get_calculation_result_manager
    )
except ImportError:
    from services.calculation_result_key_service import (
        CalculationResultKeyManager,
        CalculationType,
        get_calculation_result_manager
    )


def demo_basic_usage():
    """Demo: Basic usage of calculation result keys"""
    print("=" * 60)
    print("DEMO: Basic Calculation Result Keys")
    print("=" * 60)

    manager = get_calculation_result_manager()

    # Register a solar calculation result
    solar_data = {
        'system_size': 10.5,
        'module_count': 30,
        'annual_production': 12000,
        'self_consumption_rate': 0.35,
        'payback_period': 8.5,
        'total_cost': 15000,
        'savings_25_years': 45000,
        'co2_savings': 180000
    }

    result = manager.register_calculation_result(
        CalculationType.SOLAR,
        solar_data,
        project_id="PRJ_DEMO_001",
        user_id="USER_123"
    )

    print(f"\n Registered solar calculation result")
    print(f"  Key: {result.key}")
    print(f"  Type: {result.calculation_type.value}")
    print(f"  System Size: {result.get_value('system_size')} kWp")
    print(f"  Annual Production: {result.get_value('annual_production')} kWh")
    print(f"  Payback Period: {result.get_value('payback_period')} years")

    return result.key


def demo_versioning(result_key):
    """Demo: Result versioning"""
    print("\n" + "=" * 60)
    print("DEMO: Result Versioning")
    print("=" * 60)

    manager = get_calculation_result_manager()

    # Get original result
    result = manager.get_result_by_key(result_key)
    print(f"\n Original result (Version 1):")
    print(f"  System Size: {result.get_value('system_size')} kWp")

    # Update result - creates version 2
    updated_data = result.data.copy()
    updated_data['system_size'] = 12.0
    updated_data['module_count'] = 35
    updated_data['annual_production'] = 14000

    manager.update_result(
        result_key,
        updated_data,
        user_id="USER_123",
        change_summary="Increased system size to 12 kWp"
    )

    print(f"\n Updated result (Version 2):")
    print(f"  System Size: {updated_data['system_size']} kWp")
    print(f"  Change: Increased system size to 12 kWp")

    # Create another version
    updated_data2 = updated_data.copy()
    updated_data2['system_size'] = 15.0
    updated_data2['module_count'] = 45
    updated_data2['annual_production'] = 17500

    manager.create_version(
        result_key,
        updated_data2,
        user_id="USER_123",
        change_summary="Further increased to 15 kWp"
    )

    print(f"\n Created Version 3:")
    print(f"  System Size: {updated_data2['system_size']} kWp")

    # Get all versions
    versions = manager.get_versions(result_key)
    print(f"\n Total versions: {len(versions)}")
    for v in versions:
        print(f"  - Version {v.version_number}: "
              f"{v.data['system_size']} kWp "
              f"({v.change_summary or 'Initial'})")

    # Get latest version
    latest = manager.get_latest_version(result_key)
    print(f"\n Latest version: {latest.version_number}")
    print(f"  System Size: {latest.data['system_size']} kWp")


def demo_comparison():
    """Demo: Result comparison"""
    print("\n" + "=" * 60)
    print("DEMO: Result Comparison")
    print("=" * 60)

    manager = get_calculation_result_manager()

    # Create two different solar calculations
    data1 = {
        'system_size': 10.5,
        'annual_production': 12000,
        'total_cost': 15000,
        'payback_period': 8.5
    }

    data2 = {
        'system_size': 15.0,
        'annual_production': 17500,
        'total_cost': 21000,
        'payback_period': 7.8
    }

    result1 = manager.register_calculation_result(
        CalculationType.SOLAR,
        data1,
        project_id="PRJ_COMPARE_A"
    )

    result2 = manager.register_calculation_result(
        CalculationType.SOLAR,
        data2,
        project_id="PRJ_COMPARE_B"
    )

    print(f"\n Created two results for comparison:")
    print(f"  Result 1: {data1['system_size']} kWp system")
    print(f"  Result 2: {data2['system_size']} kWp system")

    # Compare results
    comparison = manager.compare_results(result1.key, result2.key)

    print(f"\n Comparison results:")
    print(f"  Similarity Score: {comparison.similarity_score:.2%}")
    print(f"  Differences found: {len(comparison.differences)}")

    for key, diff in comparison.differences.items():
        val1 = diff['value1']
        val2 = diff['value2']
        change = diff['change']

        if isinstance(change, (int, float)):
            print(f"  - {key}: {val1} → {val2} ({change:+.1f}%)")
        else:
            print(f"  - {key}: {val1} → {val2} ({change})")


def demo_history():
    """Demo: Result history tracking"""
    print("\n" + "=" * 60)
    print("DEMO: Result History")
    print("=" * 60)

    manager = get_calculation_result_manager()

    # Get history
    history = manager.get_result_history(limit=10)

    print(f"\n Recent history (last 10 entries):")
    for i, entry in enumerate(history, 1):
        action = entry.get('action', 'unknown')
        calc_type = entry.get('calculation_type', 'N/A')
        timestamp = entry.get('timestamp', 'N/A')

        print(f"  {i}. {action.upper()} - {calc_type} - {timestamp[:19]}")

    # Filter by type
    solar_history = manager.get_result_history(
        calculation_type=CalculationType.SOLAR,
        limit=5
    )

    print(f"\n Solar calculation history (last 5):")
    for i, entry in enumerate(solar_history, 1):
        action = entry.get('action', 'unknown')
        timestamp = entry.get('timestamp', 'N/A')
        print(f"  {i}. {action.upper()} - {timestamp[:19]}")


def demo_export():
    """Demo: Result export"""
    print("\n" + "=" * 60)
    print("DEMO: Result Export")
    print("=" * 60)

    manager = get_calculation_result_manager()

    # Create a result
    data = {
        'system_size': 10.5,
        'module_count': 30,
        'annual_production': 12000,
        'total_cost': 15000.50,
        'payback_period': 8.5
    }

    result = manager.register_calculation_result(
        CalculationType.SOLAR,
        data,
        project_id="PRJ_EXPORT_001"
    )

    # Create a version
    updated_data = data.copy()
    updated_data['system_size'] = 12.0
    manager.create_version(result.key, updated_data)

    print(f"\n Created result with 2 versions")

    # Export as dictionary
    exported_dict = manager.export_result(
        result.key,
        format='dict',
        include_versions=True,
        apply_german_formatting=False
    )

    print(f"\n Exported as dictionary:")
    print(f"  Key: {exported_dict['key']}")
    print(f"  Type: {exported_dict['calculation_type']}")
    print(f"  Versions: {len(exported_dict['versions'])}")

    # Export with German formatting
    exported_german = manager.export_result(
        result.key,
        format='dict',
        apply_german_formatting=True
    )

    print(f"\n Exported with German formatting:")
    print(f"  System Size: {exported_german['data']['system_size']}")
    print(f"  Total Cost: {exported_german['data']['total_cost']}")

    # Export as JSON
    exported_json = manager.export_result(
        result.key,
        format='json',
        include_versions=False
    )

    print(f"\n Exported as JSON (first 200 chars):")
    print(f"  {exported_json[:200]}...")


def demo_statistics():
    """Demo: Statistics"""
    print("\n" + "=" * 60)
    print("DEMO: Statistics")
    print("=" * 60)

    manager = get_calculation_result_manager()

    stats = manager.get_statistics()

    print(f"\n System Statistics:")
    print(f"  Total Results: {stats['total_results']}")
    print(f"  Total Versions: {stats['total_versions']}")
    print(f"  Total Comparisons: {stats['total_comparisons']}")
    print(f"  Average Versions per Result: "
          f"{stats['average_versions_per_result']:.2f}")
    print(f"  History Entries: {stats['history_entries']}")

    print(f"\n Results by Type:")
    for calc_type, count in stats['results_by_type'].items():
        print(f"  - {calc_type}: {count}")


def demo_advanced_usage():
    """Demo: Advanced usage scenarios"""
    print("\n" + "=" * 60)
    print("DEMO: Advanced Usage")
    print("=" * 60)

    manager = get_calculation_result_manager()

    # Scenario: Track optimization iterations
    print(f"\n Scenario: Optimization Iterations")

    base_data = {
        'system_size': 10.0,
        'annual_production': 11500,
        'total_cost': 14000,
        'payback_period': 9.2
    }

    result = manager.register_calculation_result(
        CalculationType.SOLAR,
        base_data,
        project_id="PRJ_OPTIMIZE_001"
    )

    print(f"  Initial: {base_data['system_size']} kWp, "
          f"Payback: {base_data['payback_period']} years")

    # Optimization iterations
    optimizations = [
        (10.5, 12000, 15000, 8.9, "Increased modules"),
        (11.0, 12600, 15500, 8.7, "Added east-facing array"),
        (12.0, 13800, 16500, 8.5, "Optimized tilt angle")
    ]

    for size, prod, cost, payback, summary in optimizations:
        opt_data = {
            'system_size': size,
            'annual_production': prod,
            'total_cost': cost,
            'payback_period': payback
        }
        manager.update_result(
            result.key,
            opt_data,
            change_summary=summary
        )
        print(f"  {summary}: {size} kWp, Payback: {payback} years")

    versions = manager.get_versions(result.key)
    print(f"\n  Total optimization iterations: {len(versions)}")

    # Compare first and last
    first_version = versions[0]
    last_version = versions[-1]

    improvement = (
        (first_version.data['payback_period'] -
         last_version.data['payback_period']) /
        first_version.data['payback_period'] * 100
    )

    print(f"  Payback period improvement: {improvement:.1f}%")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("CALCULATION RESULTS DYNAMIC KEYS - COMPREHENSIVE DEMO")
    print("=" * 60)

    # Run demos
    result_key = demo_basic_usage()
    demo_versioning(result_key)
    demo_comparison()
    demo_history()
    demo_export()
    demo_statistics()
    demo_advanced_usage()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nAll calculation result key features demonstrated successfully!")
    print("\nKey Features:")
    print("   Dynamic key generation for all calculation results")
    print("   Result versioning with change tracking")
    print("   Key-based result comparison")
    print("   Result history tracking")
    print("   Result export with German formatting")
    print("   Comprehensive statistics")
    print("\n")


if __name__ == '__main__':
    main()
