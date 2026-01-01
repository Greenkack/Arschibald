"""
Verification Script for Calculation Results Dynamic Keys

This script verifies that all features of Task 225 are implemented correctly.

Requirements: 14.7
Task: 225
"""

import sys


def verify_imports():
    """Verify all required imports work"""
    print("=" * 60)
    print("VERIFICATION: Imports")
    print("=" * 60)

    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from services.calculation_result_key_service import (
            CalculationResultKeyManager,
            CalculationType,
            CalculationResult,
            CalculationResultVersion,
            CalculationComparison,
            get_calculation_result_manager
        )
        print(" All imports successful")
        return True
    except ImportError as e:
        print(f" Import failed: {e}")
        return False


def verify_dynamic_keys():
    """Verify dynamic key attachment to calculation results"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Dynamic Keys for Calculation Results")
    print("=" * 60)

    try:
        from services.calculation_result_key_service import (
            get_calculation_result_manager,
            CalculationType
        )

        manager = get_calculation_result_manager()

        # Test key creation
        key = manager.create_result_key(
            CalculationType.SOLAR,
            project_id="PRJ_TEST"
        )

        assert key is not None, "Key should not be None"
        assert "SOL_" in key, "Key should have SOL prefix"
        assert "PRJ_TEST" in key, "Key should include project ID"

        print(" Dynamic key generation works")

        # Test result registration
        data = {'system_size': 10.5, 'annual_production': 12000}
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            data
        )

        assert result.key is not None, "Result should have key"
        assert result.data == data, "Result data should match"

        print(" Result registration with dynamic key works")

        return True
    except Exception as e:
        print(f" Dynamic keys verification failed: {e}")
        return False


def verify_versioning():
    """Verify result versioning with keys"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Result Versioning")
    print("=" * 60)

    try:
        from services.calculation_result_key_service import (
            get_calculation_result_manager,
            CalculationType
        )

        manager = get_calculation_result_manager()

        # Register result
        data = {'system_size': 10.5}
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            data
        )

        # Check initial version
        versions = manager.get_versions(result.key)
        assert len(versions) == 1, "Should have 1 initial version"
        assert versions[0].version_number == 1, "First version should be 1"

        print(" Initial version creation works")

        # Create new version
        updated_data = {'system_size': 12.0}
        version = manager.create_version(
            result.key,
            updated_data,
            change_summary="Increased size"
        )

        assert version.version_number == 2, "Second version should be 2"
        assert version.change_summary == "Increased size"

        print(" Version creation works")

        # Get versions
        all_versions = manager.get_versions(result.key)
        assert len(all_versions) == 2, "Should have 2 versions"

        print(" Get versions works")

        # Get specific version
        v2 = manager.get_version(result.key, 2)
        assert v2 is not None, "Version 2 should exist"
        assert v2.data['system_size'] == 12.0

        print(" Get specific version works")

        # Get latest version
        latest = manager.get_latest_version(result.key)
        assert latest.version_number == 2, "Latest should be version 2"

        print(" Get latest version works")

        return True
    except Exception as e:
        print(f" Versioning verification failed: {e}")
        return False


def verify_comparison():
    """Verify key-based result comparison"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Result Comparison")
    print("=" * 60)

    try:
        from services.calculation_result_key_service import (
            get_calculation_result_manager,
            CalculationType
        )

        manager = get_calculation_result_manager()

        # Create two results
        data1 = {'system_size': 10.5, 'annual_production': 12000}
        data2 = {'system_size': 12.0, 'annual_production': 14000}

        result1 = manager.register_calculation_result(
            CalculationType.SOLAR,
            data1
        )
        result2 = manager.register_calculation_result(
            CalculationType.SOLAR,
            data2
        )

        # Compare
        comparison = manager.compare_results(result1.key, result2.key)

        assert comparison is not None, "Comparison should not be None"
        assert comparison.result_key_1 == result1.key
        assert comparison.result_key_2 == result2.key
        assert len(comparison.differences) > 0, "Should have differences"
        assert 'system_size' in comparison.differences

        print(" Result comparison works")

        # Check similarity score
        assert 0.0 <= comparison.similarity_score <= 1.0

        print(" Similarity score calculation works")

        # Check change calculation
        size_diff = comparison.differences['system_size']
        assert 'change' in size_diff
        assert size_diff['value1'] == 10.5
        assert size_diff['value2'] == 12.0

        print(" Change calculation works")

        return True
    except Exception as e:
        print(f" Comparison verification failed: {e}")
        return False


def verify_history():
    """Verify result history with keys"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Result History")
    print("=" * 60)

    try:
        from services.calculation_result_key_service import (
            get_calculation_result_manager,
            CalculationType
        )

        manager = get_calculation_result_manager()

        # Register some results
        for i in range(3):
            manager.register_calculation_result(
                CalculationType.SOLAR,
                {'system_size': 10.0 + i}
            )

        # Get history
        history = manager.get_result_history()
        assert len(history) > 0, "History should not be empty"

        print(" Get history works")

        # Filter by type
        solar_history = manager.get_result_history(
            calculation_type=CalculationType.SOLAR
        )
        assert len(solar_history) > 0, "Solar history should not be empty"

        print(" Filter history by type works")

        # Limit results
        limited = manager.get_result_history(limit=2)
        assert len(limited) <= 2, "Should respect limit"

        print(" History limit works")

        return True
    except Exception as e:
        print(f" History verification failed: {e}")
        return False


def verify_export():
    """Verify result export with keys"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Result Export")
    print("=" * 60)

    try:
        from services.calculation_result_key_service import (
            get_calculation_result_manager,
            CalculationType
        )
        import json

        manager = get_calculation_result_manager()

        # Register result
        data = {'system_size': 10.5, 'annual_production': 12000}
        result = manager.register_calculation_result(
            CalculationType.SOLAR,
            data
        )

        # Export as JSON
        json_export = manager.export_result(result.key, format='json')
        assert isinstance(json_export, str), "JSON export should be string"
        json_data = json.loads(json_export)
        assert json_data['key'] == result.key

        print(" Export as JSON works")

        # Export as dict
        dict_export = manager.export_result(result.key, format='dict')
        assert isinstance(dict_export, dict), "Dict export should be dict"
        assert dict_export['key'] == result.key

        print(" Export as dict works")

        # Export with versions
        manager.create_version(result.key, {'system_size': 12.0})
        versioned_export = manager.export_result(
            result.key,
            format='dict',
            include_versions=True
        )
        assert 'versions' in versioned_export
        assert len(versioned_export['versions']) == 2

        print(" Export with versions works")

        # Export with German formatting
        german_export = manager.export_result(
            result.key,
            format='dict',
            apply_german_formatting=True
        )
        # Check that numbers are formatted
        system_size = german_export['data']['system_size']
        assert isinstance(system_size, str), "Should be formatted string"

        print(" Export with German formatting works")

        return True
    except Exception as e:
        print(f" Export verification failed: {e}")
        return False


def verify_all_features():
    """Verify all task requirements"""
    print("\n" + "=" * 60)
    print("VERIFICATION: All Task 225 Requirements")
    print("=" * 60)

    requirements = [
        ("Attach dynamic keys to all calculation results", verify_dynamic_keys),
        ("Create result versioning with keys", verify_versioning),
        ("Implement key-based result comparison", verify_comparison),
        ("Build result history with keys", verify_history),
        ("Create result export with keys", verify_export)
    ]

    results = []
    for name, verify_func in requirements:
        try:
            success = verify_func()
            results.append((name, success))
        except Exception as e:
            print(f" {name} failed with exception: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, success in results:
        status = " PASS" if success else " FAIL"
        print(f"{status}: {name}")
        if not success:
            all_passed = False

    return all_passed


def main():
    """Run all verifications"""
    print("\n" + "=" * 60)
    print("CALCULATION RESULTS DYNAMIC KEYS - VERIFICATION")
    print("Task 225 - Requirements 14.7")
    print("=" * 60)

    # Check imports first
    if not verify_imports():
        print("\n Import verification failed. Cannot continue.")
        sys.exit(1)

    # Run all feature verifications
    all_passed = verify_all_features()

    print("\n" + "=" * 60)
    if all_passed:
        print(" ALL VERIFICATIONS PASSED")
        print("=" * 60)
        print("\nTask 225 is complete and all features are working correctly!")
        sys.exit(0)
    else:
        print(" SOME VERIFICATIONS FAILED")
        print("=" * 60)
        print("\nPlease review the failures above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
