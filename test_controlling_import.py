"""Test script to check controlling imports"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("CONTROLLING SYSTEM IMPORT TEST")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Project root: {project_root}")
print()

# Track test results
test_results = {}

# Test 1: Import admin_controlling_settings_ui
print("Test 1: Admin Controlling Settings UI")
print("-" * 60)
try:
    from admin_controlling_settings_ui import render_admin_controlling_settings
    print(" admin_controlling_settings_ui imported successfully")
    test_results['admin_ui'] = True
except ImportError as e:
    print(f" Failed to import admin_controlling_settings_ui: {e}")
    test_results['admin_ui'] = False
print()

# Test 2: Import controlling package
print("Test 2: Controlling Package")
print("-" * 60)
try:
    import controlling
    print(" controlling package imported successfully")
    
    # Check key exports
    key_exports = [
        'EmployeeManager', 'PositionManager', 'CriterionManager',
        'PerformanceDataManager', 'AnalyticsEngine', 'ReportGenerator',
        'ChartGenerator', 'NotificationManager'
    ]
    available = [name for name in key_exports if hasattr(controlling, name)]
    print(f"   Key exports: {len(available)}/{len(key_exports)} available")
    if available:
        print(f"   Available: {', '.join(available)}")
    test_results['package'] = True
except ImportError as e:
    print(f" Failed to import controlling: {e}")
    test_results['package'] = False
print()

# Test 3: Import controlling_ui
print("Test 3: Controlling UI")
print("-" * 60)
try:
    from controlling_ui import render_controlling_page
    print(" controlling_ui imported successfully")
    test_results['controlling_ui'] = True
except ImportError as e:
    print(f" Failed to import controlling_ui: {e}")
    test_results['controlling_ui'] = False
print()

# Test 4: Import core managers
print("Test 4: Core Managers")
print("-" * 60)
try:
    from controlling.managers import (
        EmployeeManager,
        PositionManager,
        CriterionManager,
        PerformanceDataManager
    )
    print(" Core managers imported successfully")
    test_results['managers'] = True
except ImportError as e:
    print(f" Failed to import core managers: {e}")
    test_results['managers'] = False
print()

# Test 5: Import database models
print("Test 5: Database Models")
print("-" * 60)
try:
    from controlling.models import (
        Employee,
        Position,
        Criterion,
        PerformanceData,
        Report
    )
    print(" Database models imported successfully")
    test_results['models'] = True
except ImportError as e:
    print(f" Failed to import models: {e}")
    test_results['models'] = False
print()

# Test 6: Check database
print("Test 6: Database Connection")
print("-" * 60)
try:
    from controlling.database import SessionLocal, check_controlling_db
    print(" controlling database imported successfully")
    
    # Try to create a session
    db = SessionLocal()
    print(" Database session created successfully")
    db.close()
    
    # Check if tables exist
    if check_controlling_db():
        print(" Database tables verified")
        test_results['database'] = True
    else:
        print("  Database tables may not be initialized")
        print("   Run: python controlling/database.py")
        test_results['database'] = False
except Exception as e:
    print(f" Failed to access controlling database: {e}")
    test_results['database'] = False
print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
tests_passed = sum(test_results.values())
total_tests = len(test_results)
print(f"Tests passed: {tests_passed}/{total_tests}")
print()

if tests_passed == total_tests:
    print(" All tests passed! Controlling system is ready.")
elif tests_passed >= total_tests - 1:
    print("  Most tests passed. Check warnings above.")
else:
    print(" Multiple tests failed. Check errors above.")

print()
print("Test results:")
for test_name, passed in test_results.items():
    status = " PASS" if passed else " FAIL"
    print(f"  {test_name:20s}: {status}")

print()
print("=" * 60)
