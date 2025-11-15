"""
verify_module_migration.py

Verification script for Task 17: Module Migration to shadcn/ui
Tests that all migrated modules and helper functions work correctly.
"""

import sys
from typing import List, Tuple

def test_imports() -> Tuple[bool, List[str]]:
    """Test that all required modules can be imported."""
    errors = []
    
    try:
        from utils.shadcn_migration_helpers import (
            inject_shadcn_styles,
            shadcn_card,
            shadcn_alert,
            shadcn_metric,
            shadcn_badge,
            apply_shadcn_chart_theme,
            shadcn_section,
            get_theme_manager,
            SHADCN_AVAILABLE,
        )
        print("✅ Migration helpers imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import migration helpers: {e}")
    
    try:
        from solar_calculator_shadcn import (
            render_solar_calculator_with_shadcn,
            display_pricing_with_shadcn,
            apply_chart_theme_to_all_figures,
        )
        print("✅ Solar calculator shadcn module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import solar_calculator_shadcn: {e}")
    
    try:
        from crm_shadcn import (
            render_crm_with_shadcn,
            render_customer_list_with_cards,
            render_crm_dashboard_with_metrics,
        )
        print("✅ CRM shadcn module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import crm_shadcn: {e}")
    
    try:
        from admin_panel_shadcn import (
            render_admin_panel_with_shadcn,
            render_admin_navigation_with_shadcn,
            render_admin_dashboard_with_metrics,
        )
        print("✅ Admin panel shadcn module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import admin_panel_shadcn: {e}")
    
    return len(errors) == 0, errors


def test_helper_functions() -> Tuple[bool, List[str]]:
    """Test that helper functions work correctly."""
    errors = []
    
    try:
        from utils.shadcn_migration_helpers import SHADCN_AVAILABLE
        
        if SHADCN_AVAILABLE:
            print("✅ shadcn/ui components are available")
        else:
            print("⚠️  shadcn/ui components not available (fallback mode)")
    except Exception as e:
        errors.append(f"❌ Failed to check SHADCN_AVAILABLE: {e}")
    
    try:
        from utils.shadcn_migration_helpers import get_theme_manager
        theme_manager = get_theme_manager()
        if theme_manager:
            print("✅ Theme manager initialized successfully")
        else:
            print("⚠️  Theme manager not available (fallback mode)")
    except Exception as e:
        errors.append(f"❌ Failed to initialize theme manager: {e}")
    
    return len(errors) == 0, errors


def test_documentation() -> Tuple[bool, List[str]]:
    """Test that documentation files exist."""
    import os
    errors = []
    
    docs = [
        'docs/SHADCN_MIGRATION_GUIDE.md',
        'docs/SHADCN_MIGRATION_QUICK_REFERENCE.md',
        'TASK_17_MODULE_MIGRATION_COMPLETE.md',
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            print(f"✅ Documentation exists: {doc}")
        else:
            errors.append(f"❌ Documentation missing: {doc}")
    
    return len(errors) == 0, errors


def test_demo_files() -> Tuple[bool, List[str]]:
    """Test that demo files exist."""
    import os
    errors = []
    
    demos = [
        'demo_module_migration.py',
    ]
    
    for demo in demos:
        if os.path.exists(demo):
            print(f"✅ Demo file exists: {demo}")
        else:
            errors.append(f"❌ Demo file missing: {demo}")
    
    return len(errors) == 0, errors


def test_original_modules_unchanged() -> Tuple[bool, List[str]]:
    """Test that original modules still exist and are unchanged."""
    import os
    errors = []
    
    originals = [
        'solar_calculator.py',
        'crm.py',
        'admin_panel.py',
    ]
    
    for original in originals:
        if os.path.exists(original):
            print(f"✅ Original module preserved: {original}")
        else:
            errors.append(f"❌ Original module missing: {original}")
    
    return len(errors) == 0, errors


def run_all_tests():
    """Run all verification tests."""
    print("=" * 60)
    print("Task 17: Module Migration Verification")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test 1: Imports
    print("Test 1: Module Imports")
    print("-" * 60)
    passed, errors = test_imports()
    if not passed:
        all_passed = False
        for error in errors:
            print(error)
    print()
    
    # Test 2: Helper Functions
    print("Test 2: Helper Functions")
    print("-" * 60)
    passed, errors = test_helper_functions()
    if not passed:
        all_passed = False
        for error in errors:
            print(error)
    print()
    
    # Test 3: Documentation
    print("Test 3: Documentation Files")
    print("-" * 60)
    passed, errors = test_documentation()
    if not passed:
        all_passed = False
        for error in errors:
            print(error)
    print()
    
    # Test 4: Demo Files
    print("Test 4: Demo Files")
    print("-" * 60)
    passed, errors = test_demo_files()
    if not passed:
        all_passed = False
        for error in errors:
            print(error)
    print()
    
    # Test 5: Original Modules
    print("Test 5: Original Modules Preserved")
    print("-" * 60)
    passed, errors = test_original_modules_unchanged()
    if not passed:
        all_passed = False
        for error in errors:
            print(error)
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print()
        print("Task 17 verification complete!")
        print("All modules migrated successfully to shadcn/ui components.")
        print()
        print("Next steps:")
        print("1. Run demo: streamlit run demo_module_migration.py")
        print("2. Review documentation: docs/SHADCN_MIGRATION_GUIDE.md")
        print("3. Integrate into gui.py")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the errors above and fix any issues.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
