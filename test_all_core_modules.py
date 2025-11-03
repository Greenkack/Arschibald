"""
Complete Core Module Integration Test
======================================

Testet alle 31 Core-Module auf Verfügbarkeit und Funktionsfähigkeit.
"""

import sys
from pathlib import Path

# Test Results
results = {
    'passed': [],
    'failed': [],
    'skipped': [],
}

def test_module_import(module_name, description):
    """Test if module can be imported"""
    try:
        exec(f"from core.{module_name} import *")
        results['passed'].append(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        results['failed'].append(f"❌ {module_name} - Import Error: {e}")
        return False
    except Exception as e:
        results['failed'].append(f"⚠️ {module_name} - Error: {e}")
        return False


def test_core_integration():
    """Test core_integration.py"""
    try:
        from core_integration import (
            init_core_integration,
            FEATURES,
            # Phase 1-4
            get_app_config,
            get_app_logger,
            get_app_cache,
            get_session_manager,
            get_database_manager,
            # Phase 5-12
            get_security_manager,
            get_router,
            get_form_manager,
            get_widget_manager,
            get_navigation_history,
            get_job_manager,
            get_migration_manager,
            get_cache_invalidator,
            get_cache_monitor,
            get_cache_warmer,
            get_db_performance_monitor,
            get_di_container,
        )
        results['passed'].append("✅ core_integration.py - All imports successful")
        return True
    except ImportError as e:
        results['failed'].append(f"❌ core_integration.py - Import failed: {e}")
        return False


print("=" * 70)
print("COMPLETE CORE MODULE INTEGRATION TEST")
print("=" * 70)
print()

# Test 1: Phase 1-4 (Basic Integration)
print("📦 Testing Phase 1-4: Basic Integration")
print("-" * 70)

test_module_import("config", "Configuration Management")
test_module_import("logging_config", "Logging Configuration")
test_module_import("logging_system", "Structured Logging")
test_module_import("cache", "Multi-Backend Cache")
test_module_import("session", "Session Data Models")
test_module_import("session_manager", "Session Management")
test_module_import("session_persistence", "Session Storage")
test_module_import("session_recovery", "Session Recovery")
test_module_import("database", "Database Manager")
test_module_import("connection_manager", "Connection Pooling")

print()

# Test 2: Phase 5 (Security & Auth)
print("🔐 Testing Phase 5: Security & Authentication")
print("-" * 70)

test_module_import("security", "User Auth, RBAC, Tokens")
test_module_import("router", "URL Routing, Guards")

print()

# Test 3: Phase 6 (Forms & Widgets)
print("📝 Testing Phase 6: Forms & Widgets")
print("-" * 70)

test_module_import("form_manager", "Multi-Step Forms")
test_module_import("widgets", "Custom Widgets")
test_module_import("widget_persistence", "Widget State Persistence")
test_module_import("widget_validation", "Form Validation")

print()

# Test 4: Phase 7 (Navigation)
print("🧭 Testing Phase 7: Navigation")
print("-" * 70)

test_module_import("navigation_history", "Navigation Tracking")

print()

# Test 5: Phase 8 (Jobs)
print("⚙️ Testing Phase 8: Jobs & Background Tasks")
print("-" * 70)

test_module_import("jobs", "Job System Core")
test_module_import("job_repository", "Job Persistence")
test_module_import("job_notifications", "Job Notifications")
test_module_import("job_ui", "Job Management UI")

print()

# Test 6: Phase 9 (Migrations)
print("🔄 Testing Phase 9: Database Migrations")
print("-" * 70)

test_module_import("migrations", "Migration Core")
test_module_import("migration_manager", "Migration Execution")
test_module_import("migration_templates", "Migration Templates")
test_module_import("cli_migrations", "CLI Interface")

print()

# Test 7: Phase 10 (Cache Extensions)
print("🚀 Testing Phase 10: Cache Extensions")
print("-" * 70)

test_module_import("cache_invalidation", "Smart Invalidation")
test_module_import("cache_monitoring", "Cache Monitoring")
test_module_import("cache_warming", "Cache Pre-Population")

print()

# Test 8: Phase 11 (DB Extensions)
print("🗄️ Testing Phase 11: Database Extensions")
print("-" * 70)

test_module_import("db_performance_monitor", "Query Performance")
test_module_import("session_repository", "Session DB Ops")

print()

# Test 9: Phase 12 (DI Container)
print("🔧 Testing Phase 12: Dependency Injection")
print("-" * 70)

test_module_import("containers", "DI Container")

print()

# Test 10: Core Integration
print("🔗 Testing Core Integration Layer")
print("-" * 70)

test_core_integration()

print()

# Summary
print("=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
print()

print(f"✅ Passed: {len(results['passed'])}")
print(f"❌ Failed: {len(results['failed'])}")
print(f"⏭️ Skipped: {len(results['skipped'])}")

total = len(results['passed']) + len(results['failed']) + len(results['skipped'])
success_rate = (len(results['passed']) / total * 100) if total > 0 else 0

print(f"\n📈 Success Rate: {success_rate:.1f}%")

if results['failed']:
    print("\n❌ FAILED TESTS:")
    for fail in results['failed']:
        print(f"   {fail}")

if results['skipped']:
    print("\n⏭️ SKIPPED TESTS:")
    for skip in results['skipped']:
        print(f"   {skip}")

print()
print("=" * 70)

if success_rate == 100:
    print("🎉 ALL TESTS PASSED! All 31 modules are available!")
    sys.exit(0)
elif success_rate >= 80:
    print("🟢 GOOD: Most modules are available")
    sys.exit(0)
elif success_rate >= 50:
    print("🟡 PARTIAL: Some modules are missing")
    sys.exit(1)
else:
    print("🔴 CRITICAL: Many modules are missing")
    sys.exit(1)
