"""
Verification Script for Dropdown and Selection Dynamic Keys

This script verifies that the dropdown key service is working correctly.

Requirements: 14.7
Task: 224
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.dropdown_key_service import (
    DropdownKeyManager,
    DropdownType,
    get_dropdown_manager
)


def verify_basic_functionality():
    """Verify basic dropdown functionality"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Basic Dropdown Functionality")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Create dropdown
    options = [
        {"value": "mono", "label": "Monocrystalline"},
        {"value": "poly", "label": "Polycrystalline"},
        {"value": "thin", "label": "Thin Film"}
    ]

    dropdown = manager.register_dropdown(
        "module_type",
        DropdownType.SINGLE_SELECT,
        "Module Type",
        options
    )

    print(f"✓ Created dropdown: {dropdown.label}")
    print(f"  Key: {dropdown.key}")
    print(f"  Options: {len(dropdown.get_options())}")

    # Verify options
    for option in dropdown.get_options():
        print(f"  - {option.label} (key: {option.key[:20]}...)")

    assert len(dropdown.get_options()) == 3
    print("\n✓ Basic functionality verified")


def verify_selection_history():
    """Verify selection history tracking"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Selection History")
    print("=" * 60)

    manager = DropdownKeyManager()

    options = [
        {"value": "opt1", "label": "Option 1"},
        {"value": "opt2", "label": "Option 2"}
    ]

    dropdown = manager.register_dropdown(
        "test_dropdown",
        DropdownType.SINGLE_SELECT,
        "Test",
        options
    )

    # Record selections
    option = dropdown.get_options()[0]
    manager.record_selection(
        dropdown.key,
        option.key,
        user_id="user123"
    )

    # Get history
    history = manager.get_selection_history()
    assert len(history) >= 1

    print(f"✓ Recorded {len(history)} selection(s)")
    print(f"  Latest: {history[0].option_label} by {history[0].user_id}")
    print("\n✓ Selection history verified")


def verify_cascading_dropdown():
    """Verify cascading dropdown functionality"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Cascading Dropdown")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register cascading relationship
    parent_key, child_key = manager.register_cascading_dropdown(
        "country",
        "state"
    )

    print(f"✓ Created cascading relationship")
    print(f"  Parent key: {parent_key[:30]}...")
    print(f"  Child key: {child_key[:30]}...")

    # Verify relationship
    children = manager.get_cascading_children(parent_key)
    assert child_key in children

    print(f"  Children: {len(children)}")
    print("\n✓ Cascading dropdown verified")


def verify_statistics():
    """Verify statistics functionality"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Statistics")
    print("=" * 60)

    manager = DropdownKeyManager()

    # Register multiple dropdowns
    for i in range(3):
        options = [
            {"value": f"opt{j}", "label": f"Option {j}"}
            for j in range(2)
        ]
        manager.register_dropdown(
            f"dropdown_{i}",
            DropdownType.SINGLE_SELECT,
            f"Dropdown {i}",
            options
        )

    stats = manager.get_statistics()

    print(f"✓ Statistics:")
    print(f"  Total Dropdowns: {stats['total_dropdowns']}")
    print(f"  Total Options: {stats['total_options']}")
    print(f"  Avg Options/Dropdown: "
          f"{stats['average_options_per_dropdown']:.2f}")

    assert stats['total_dropdowns'] >= 3
    assert stats['total_options'] >= 6

    print("\n✓ Statistics verified")


def verify_global_manager():
    """Verify global manager singleton"""
    print("\n" + "=" * 60)
    print("VERIFICATION: Global Manager")
    print("=" * 60)

    manager1 = get_dropdown_manager()
    manager2 = get_dropdown_manager()

    assert manager1 is manager2

    print("✓ Global manager is singleton")
    print(f"  Manager ID: {id(manager1)}")
    print("\n✓ Global manager verified")


def main():
    """Run all verifications"""
    print("\n" + "=" * 60)
    print("DROPDOWN DYNAMIC KEYS - VERIFICATION")
    print("=" * 60)

    verifications = [
        verify_basic_functionality,
        verify_selection_history,
        verify_cascading_dropdown,
        verify_statistics,
        verify_global_manager
    ]

    passed = 0
    failed = 0

    for verify_func in verifications:
        try:
            verify_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {verify_func.__name__}")
            print(f"   Error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(verifications)}")
    print(f"Failed: {failed}/{len(verifications)}")

    if failed == 0:
        print("\n✓ ALL VERIFICATIONS PASSED")
        return 0
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
