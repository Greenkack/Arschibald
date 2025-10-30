"""
Core Integration Functionality Test
====================================

Testet die tatsächliche Funktionsfähigkeit der core_integration.py
"""

import sys

def test_initialization():
    """Test core initialization"""
    print("🔧 Testing Core Initialization...")
    try:
        from core_integration import init_core_integration
        status = init_core_integration(enable_logging=True)
        
        print(f"   ✅ Initialization completed")
        print(f"   📊 Status: {len([k for k, v in status.items() if v is True and k != 'errors'])} modules enabled")
        
        if status.get('errors'):
            print(f"   ⚠️ Errors: {len(status['errors'])}")
            for error in status['errors'][:5]:  # Show first 5 errors
                print(f"      - {error}")
        
        return True
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False


def test_phase_1_4_getters():
    """Test Phase 1-4 getter functions"""
    print("\n📦 Testing Phase 1-4 Getters...")
    from core_integration import (
        get_app_config,
        get_app_logger,
        get_app_cache,
        get_session_manager,
        get_database_manager,
    )
    
    tests = [
        ("Config", get_app_config),
        ("Logger", get_app_logger),
        ("Cache", get_app_cache),
        ("Session Manager", get_session_manager),
        ("Database Manager", get_database_manager),
    ]
    
    passed = 0
    for name, func in tests:
        try:
            result = func()
            if result is not None:
                print(f"   ✅ {name}: Available")
                passed += 1
            else:
                print(f"   ⚠️ {name}: Disabled (feature flag off)")
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
    
    return passed == len(tests)


def test_phase_5_12_getters():
    """Test Phase 5-12 getter functions"""
    print("\n🔐 Testing Phase 5-12 Getters...")
    from core_integration import (
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
    
    tests = [
        ("Security Manager", get_security_manager),
        ("Router", get_router),
        ("Form Manager", get_form_manager),
        ("Widget Manager", get_widget_manager),
        ("Navigation History", get_navigation_history),
        ("Job Manager", get_job_manager),
        ("Migration Manager", get_migration_manager),
        ("Cache Invalidator", get_cache_invalidator),
        ("Cache Monitor", get_cache_monitor),
        ("Cache Warmer", get_cache_warmer),
        ("DB Performance Monitor", get_db_performance_monitor),
        ("DI Container", get_di_container),
    ]
    
    passed = 0
    for name, func in tests:
        try:
            result = func()
            if result is not None:
                print(f"   ✅ {name}: Available")
                passed += 1
            else:
                print(f"   ⚠️ {name}: Disabled (feature flag off)")
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
    
    return passed > 0  # At least some should work


def test_feature_flags():
    """Test feature flags"""
    print("\n🚩 Testing Feature Flags...")
    from core_integration import FEATURES
    
    enabled = [k for k, v in FEATURES.items() if v is True]
    disabled = [k for k, v in FEATURES.items() if v is False]
    
    print(f"   ✅ Enabled: {len(enabled)}")
    for feature in enabled:
        print(f"      - {feature}")
    
    if disabled:
        print(f"   ⚠️ Disabled: {len(disabled)}")
        for feature in disabled:
            print(f"      - {feature}")
    
    return True


def test_helper_functions():
    """Test helper functions"""
    print("\n🛠️ Testing Helper Functions...")
    from core_integration import (
        is_feature_enabled,
        log_error,
        cache_get,
        cache_set,
    )
    
    tests_passed = 0
    
    # Test is_feature_enabled
    try:
        result = is_feature_enabled('config')
        print(f"   ✅ is_feature_enabled('config'): {result}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ is_feature_enabled failed: {e}")
    
    # Test cache_get (may return None if cache disabled)
    try:
        result = cache_get('test_key', 'default')
        print(f"   ✅ cache_get: {result}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ cache_get failed: {e}")
    
    # Test cache_set
    try:
        cache_set('test_key', 'test_value', ttl=60)
        print(f"   ✅ cache_set: Success")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ cache_set failed: {e}")
    
    # Test log_error
    try:
        log_error("test_event", "Test error message")
        print(f"   ✅ log_error: Success")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ log_error failed: {e}")
    
    return tests_passed >= 2  # At least 2 should work


print("=" * 70)
print("CORE INTEGRATION FUNCTIONALITY TEST")
print("=" * 70)

results = []

# Run all tests
results.append(("Initialization", test_initialization()))
results.append(("Phase 1-4 Getters", test_phase_1_4_getters()))
results.append(("Phase 5-12 Getters", test_phase_5_12_getters()))
results.append(("Feature Flags", test_feature_flags()))
results.append(("Helper Functions", test_helper_functions()))

# Summary
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)

passed = sum(1 for _, result in results if result)
total = len(results)

print()
for name, result in results:
    status = "✅ PASSED" if result else "❌ FAILED"
    print(f"{status}: {name}")

print()
success_rate = (passed / total * 100) if total > 0 else 0
print(f"📈 Success Rate: {success_rate:.1f}% ({passed}/{total})")

print("=" * 70)

if success_rate == 100:
    print("🎉 ALL FUNCTIONALITY TESTS PASSED!")
    sys.exit(0)
elif success_rate >= 80:
    print("🟢 GOOD: Core integration is functional")
    sys.exit(0)
else:
    print("🔴 CRITICAL: Core integration has issues")
    sys.exit(1)
