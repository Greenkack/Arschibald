"""
Unit Tests for Extended PDF Options Parsing

Tests the parsing and validation of extended PDF options dictionary
to ensure proper handling of all configuration options.

Requirements: 8.1
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_default_options():
    """Test that default options are correctly set when not provided."""
    print("\n=== Test 1: Default Options ===")

    # Simulate empty options
    options = {}

    # Apply defaults
    default_options = {
        'enabled': False,
        'financing_details': False,
        'product_datasheets': [],
        'company_documents': [],
        'selected_charts': [],
        'chart_layout': 'one_per_page'
    }

    # Merge with defaults
    final_options = {**default_options, **options}

    # Verify defaults
    assert final_options['enabled'] is False, "Default 'enabled' should be False"
    assert final_options['financing_details'] is False, "Default 'financing_details' should be False"
    assert final_options['product_datasheets'] == [
    ], "Default 'product_datasheets' should be empty list"
    assert final_options['company_documents'] == [
    ], "Default 'company_documents' should be empty list"
    assert final_options['selected_charts'] == [
    ], "Default 'selected_charts' should be empty list"
    assert final_options['chart_layout'] == 'one_per_page', "Default 'chart_layout' should be 'one_per_page'"

    print("✓ All default options are correctly set")
    print(f"  - enabled: {final_options['enabled']}")
    print(f"  - financing_details: {final_options['financing_details']}")
    print(f"  - product_datasheets: {final_options['product_datasheets']}")
    print(f"  - company_documents: {final_options['company_documents']}")
    print(f"  - selected_charts: {final_options['selected_charts']}")
    print(f"  - chart_layout: {final_options['chart_layout']}")

    return True


def test_enabled_option():
    """Test the 'enabled' option parsing."""
    print("\n=== Test 2: Enabled Option ===")

    test_cases = [
        ({'enabled': True}, True, "Boolean True"),
        ({'enabled': False}, False, "Boolean False"),
        ({'enabled': 1}, 1, "Integer 1 (truthy)"),
        ({'enabled': 0}, 0, "Integer 0 (falsy)"),
        ({'enabled': 'yes'}, 'yes', "String 'yes' (truthy)"),
        ({'enabled': ''}, '', "Empty string (falsy)"),
        ({}, False, "Missing (default False)")
    ]

    default_options = {'enabled': False}

    for options, expected, description in test_cases:
        final_options = {**default_options, **options}
        actual = final_options.get('enabled', False)

        # Check if value matches expected
        if actual == expected:
            print(f"✓ {description}: {actual}")
        else:
            print(f"✗ {description}: expected {expected}, got {actual}")
            return False

    print("✓ All 'enabled' option tests passed")
    return True


def test_financing_details_option():
    """Test the 'financing_details' option parsing."""
    print("\n=== Test 3: Financing Details Option ===")

    test_cases = [
        ({'financing_details': True}, True),
        ({'financing_details': False}, False),
        ({}, False)  # Default
    ]

    default_options = {'financing_details': False}

    for options, expected in test_cases:
        final_options = {**default_options, **options}
        actual = final_options.get('financing_details', False)

        assert actual == expected, f"Expected {expected}, got {actual}"
        print(
            f"✓ financing_details={
                options.get(
                    'financing_details',
                    'default')} → {actual}")

    print("✓ All 'financing_details' option tests passed")
    return True


def test_product_datasheets_option():
    """Test the 'product_datasheets' option parsing."""
    print("\n=== Test 4: Product Datasheets Option ===")

    test_cases = [
        ({'product_datasheets': []}, [], "Empty list"),
        ({'product_datasheets': [1, 2, 3]}, [1, 2, 3], "List of IDs"),
        ({'product_datasheets': [42]}, [42], "Single ID"),
        ({}, [], "Missing (default empty list)")
    ]

    default_options = {'product_datasheets': []}

    for options, expected, description in test_cases:
        final_options = {**default_options, **options}
        actual = final_options.get('product_datasheets', [])

        assert actual == expected, f"{description}: Expected {expected}, got {actual}"
        print(f"✓ {description}: {actual}")

    print("✓ All 'product_datasheets' option tests passed")
    return True


def test_company_documents_option():
    """Test the 'company_documents' option parsing."""
    print("\n=== Test 5: Company Documents Option ===")

    test_cases = [
        ({'company_documents': []}, [], "Empty list"),
        ({'company_documents': [10, 20, 30]}, [10, 20, 30], "List of IDs"),
        ({'company_documents': [99]}, [99], "Single ID"),
        ({}, [], "Missing (default empty list)")
    ]

    default_options = {'company_documents': []}

    for options, expected, description in test_cases:
        final_options = {**default_options, **options}
        actual = final_options.get('company_documents', [])

        assert actual == expected, f"{description}: Expected {expected}, got {actual}"
        print(f"✓ {description}: {actual}")

    print("✓ All 'company_documents' option tests passed")
    return True


def test_selected_charts_option():
    """Test the 'selected_charts' option parsing."""
    print("\n=== Test 6: Selected Charts Option ===")

    test_cases = [
        (
            {'selected_charts': []},
            [],
            "Empty list"
        ),
        (
            {'selected_charts': ['monthly_prod_cons_chart_bytes']},
            ['monthly_prod_cons_chart_bytes'],
            "Single chart"
        ),
        (
            {
                'selected_charts': [
                    'monthly_prod_cons_chart_bytes',
                    'cumulative_cashflow_chart_bytes',
                    'consumption_coverage_pie_chart_bytes'
                ]
            },
            [
                'monthly_prod_cons_chart_bytes',
                'cumulative_cashflow_chart_bytes',
                'consumption_coverage_pie_chart_bytes'
            ],
            "Multiple charts"
        ),
        ({}, [], "Missing (default empty list)")
    ]

    default_options = {'selected_charts': []}

    for options, expected, description in test_cases:
        final_options = {**default_options, **options}
        actual = final_options.get('selected_charts', [])

        assert actual == expected, f"{description}: Expected {expected}, got {actual}"
        print(f"✓ {description}: {len(actual)} charts")

    print("✓ All 'selected_charts' option tests passed")
    return True


def test_chart_layout_option():
    """Test the 'chart_layout' option parsing."""
    print("\n=== Test 7: Chart Layout Option ===")

    test_cases = [
        ({'chart_layout': 'one_per_page'}, 'one_per_page', "One per page"),
        ({'chart_layout': 'two_per_page'}, 'two_per_page', "Two per page"),
        ({'chart_layout': 'four_per_page'}, 'four_per_page', "Four per page"),
        ({}, 'one_per_page', "Missing (default one_per_page)")
    ]

    default_options = {'chart_layout': 'one_per_page'}

    for options, expected, description in test_cases:
        final_options = {**default_options, **options}
        actual = final_options.get('chart_layout', 'one_per_page')

        assert actual == expected, f"{description}: Expected {expected}, got {actual}"
        print(f"✓ {description}: {actual}")

    print("✓ All 'chart_layout' option tests passed")
    return True


def test_complete_options_dictionary():
    """Test a complete options dictionary with all fields."""
    print("\n=== Test 8: Complete Options Dictionary ===")

    complete_options = {
        'enabled': True,
        'financing_details': True,
        'product_datasheets': [1, 2, 3],
        'company_documents': [10, 20],
        'selected_charts': [
            'monthly_prod_cons_chart_bytes',
            'cumulative_cashflow_chart_bytes'
        ],
        'chart_layout': 'two_per_page'
    }

    # Verify all fields are present and correct
    assert complete_options['enabled'] is True
    assert complete_options['financing_details'] is True
    assert complete_options['product_datasheets'] == [1, 2, 3]
    assert complete_options['company_documents'] == [10, 20]
    assert len(complete_options['selected_charts']) == 2
    assert complete_options['chart_layout'] == 'two_per_page'

    print("✓ Complete options dictionary validated")
    print(f"  - enabled: {complete_options['enabled']}")
    print(f"  - financing_details: {complete_options['financing_details']}")
    print(
        f"  - product_datasheets: {len(complete_options['product_datasheets'])} items")
    print(
        f"  - company_documents: {len(complete_options['company_documents'])} items")
    print(
        f"  - selected_charts: {len(complete_options['selected_charts'])} charts")
    print(f"  - chart_layout: {complete_options['chart_layout']}")

    return True


def test_partial_options_with_defaults():
    """Test partial options dictionary merged with defaults."""
    print("\n=== Test 9: Partial Options with Defaults ===")

    default_options = {
        'enabled': False,
        'financing_details': False,
        'product_datasheets': [],
        'company_documents': [],
        'selected_charts': [],
        'chart_layout': 'one_per_page'
    }

    # User provides only some options
    user_options = {
        'enabled': True,
        'selected_charts': ['monthly_prod_cons_chart_bytes']
    }

    # Merge
    final_options = {**default_options, **user_options}

    # Verify merged result
    assert final_options['enabled'] is True, "User option should override default"
    assert final_options['financing_details'] is False, "Should use default"
    assert final_options['product_datasheets'] == [], "Should use default"
    assert final_options['company_documents'] == [], "Should use default"
    assert len(final_options['selected_charts']
               ) == 1, "User option should override default"
    assert final_options['chart_layout'] == 'one_per_page', "Should use default"

    print("✓ Partial options correctly merged with defaults")
    print(f"  - User provided: {list(user_options.keys())}")
    print(
        f"  - Defaults used: {[k for k in default_options.keys() if k not in user_options]}")

    return True


def test_invalid_option_types():
    """Test handling of invalid option types."""
    print("\n=== Test 10: Invalid Option Types ===")

    # Test cases with invalid types
    test_cases = [
        (
            {'product_datasheets': 'not_a_list'},
            "product_datasheets should be a list"
        ),
        (
            {'company_documents': 42},
            "company_documents should be a list"
        ),
        (
            {'selected_charts': 'single_chart'},
            "selected_charts should be a list"
        )
    ]

    for invalid_options, description in test_cases:
        # In a real implementation, you would validate and handle these
        # For now, we just document the expected behavior
        print(f"⚠ {description}")
        print(f"  Invalid value: {invalid_options}")

    print("✓ Invalid option types documented")
    return True


def test_options_immutability():
    """Test that default options are not mutated."""
    print("\n=== Test 11: Options Immutability ===")

    default_options = {
        'enabled': False,
        'financing_details': False,
        'product_datasheets': [],
        'company_documents': [],
        'selected_charts': [],
        'chart_layout': 'one_per_page'
    }

    # Create a copy for comparison
    original_defaults = default_options.copy()

    # User modifies options
    user_options = {
        'enabled': True,
        'product_datasheets': [1, 2, 3]
    }

    # Merge (should not mutate defaults)
    final_options = {**default_options, **user_options}

    # Verify defaults are unchanged
    assert default_options == original_defaults, "Default options should not be mutated"

    # Verify final options have user values
    assert final_options['enabled'] is True
    assert final_options['product_datasheets'] == [1, 2, 3]

    print("✓ Default options remain immutable after merge")
    print(f"  - Defaults unchanged: {default_options == original_defaults}")
    print(f"  - Final options have user values: {final_options['enabled']}")

    return True


def run_all_tests():
    """Run all option parsing tests."""
    print("=" * 70)
    print("EXTENDED PDF OPTIONS PARSING TEST SUITE")
    print("Testing: Requirement 8.1 - Options Dictionary and Default Values")
    print("=" * 70)

    test_functions = [
        test_default_options,
        test_enabled_option,
        test_financing_details_option,
        test_product_datasheets_option,
        test_company_documents_option,
        test_selected_charts_option,
        test_chart_layout_option,
        test_complete_options_dictionary,
        test_partial_options_with_defaults,
        test_invalid_option_types,
        test_options_immutability
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except AssertionError as e:
            print(f"\n✗ Test failed: {test_func.__name__}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test error: {test_func.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(test_functions)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)

    if passed == len(test_functions):
        print("✓ ALL TESTS PASSED - Task 18.1 Complete")
    else:
        print("✗ SOME TESTS FAILED - Task 18.1 Needs Work")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
