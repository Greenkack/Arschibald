"""
Verification Script for Task 2: Enhanced Session Management & State Persistence

This script verifies that all components of Task 2 are properly implemented.
"""

import sys
import time


def verify_imports():
    """Verify all required imports"""
    print("=" * 60)
    print("1. Verifying Imports")
    print("=" * 60)

    try:
        from core import (
            FormSnapshot,
            FormState,
            NavigationEntry,
            SessionMetrics,
            UserPreferences,
            UserSession,
            bootstrap_session,
            get_current_session,
            get_session_manager,
            persist_input,
            save_form,
        )

        print("✅ All core session imports successful")

        from core.session_persistence import (
            DebouncedWriter,
            SessionModel,
            SessionPersistenceEngine,
            get_persistence_engine,
            persist_session,
            recover_session,
        )

        print("✅ All persistence imports successful")

        from core.session_manager import SessionManager

        print("✅ SessionManager import successful")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def verify_user_session():
    """Verify UserSession functionality"""
    print("\n" + "=" * 60)
    print("2. Verifying UserSession")
    print("=" * 60)

    from core import UserSession

    try:
        # Create session
        session = UserSession(user_id="test_user")
        print(f"✅ Created session: {session.session_id}")

        # Navigation
        session.navigate_to("profile", {"id": "123"})
        assert session.current_page == "profile"
        print("✅ Navigation works")

        # Form management
        session.update_form_data("form1", "field1", "value1")
        form_state = session.get_form_state("form1")
        assert form_state.data["field1"] == "value1"
        print("✅ Form management works")

        # Snapshots
        snapshot = session.create_form_snapshot("form1", "Test")
        assert len(session.form_snapshots["form1"]) == 1
        print("✅ Form snapshots work")

        # Permissions
        session.add_role("admin")
        session.add_permission("write")
        assert session.has_role("admin")
        assert session.has_permission("write")
        print("✅ Permissions work")

        # Cache tracking
        session.add_cache_key("cache1")
        assert "cache1" in session.cache_keys
        print("✅ Cache tracking works")

        # Serialization
        json_str = session.to_json()
        restored = UserSession.from_json(json_str)
        assert restored.session_id == session.session_id
        print("✅ Serialization works")

        return True
    except Exception as e:
        print(f"❌ UserSession verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_debounced_writer():
    """Verify DebouncedWriter functionality"""
    print("\n" + "=" * 60)
    print("3. Verifying DebouncedWriter")
    print("=" * 60)

    from core.session_persistence import DebouncedWriter

    try:
        writer = DebouncedWriter(delay_seconds=0.1)
        results = []

        def write_fn(value):
            results.append(value)

        # Test debouncing
        writer.schedule_write("key1", write_fn, "value1")
        time.sleep(0.05)
        writer.schedule_write("key1", write_fn, "value2")
        time.sleep(0.15)

        assert len(results) == 1
        assert results[0] == "value2"
        print("✅ Debouncing works")

        # Test flush
        results.clear()
        writer.schedule_write("key2", write_fn, "value3")
        writer.flush("key2")
        assert len(results) == 1
        print("✅ Flush works")

        return True
    except Exception as e:
        print(f"❌ DebouncedWriter verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_session_manager():
    """Verify SessionManager functionality"""
    print("\n" + "=" * 60)
    print("4. Verifying SessionManager")
    print("=" * 60)

    from core import bootstrap_session, get_session_manager

    try:
        # Bootstrap session
        session = bootstrap_session(user_id="verify_user")
        print(f"✅ Bootstrapped session: {session.session_id}")

        # Get manager
        manager = get_session_manager()
        print("✅ Got session manager")

        # Test navigation (without Streamlit)
        manager.get_current_session = lambda: session
        manager.navigate_to("test_page", {"param": "value"})
        assert session.current_page == "test_page"
        print("✅ Navigation via manager works")

        # Test form save
        manager.save_form("test_form", {"field": "value"})
        form_state = session.get_form_state("test_form")
        assert form_state.data["field"] == "value"
        print("✅ Form save via manager works")

        return True
    except Exception as e:
        print(f"❌ SessionManager verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_api_functions():
    """Verify module-level API functions"""
    print("\n" + "=" * 60)
    print("5. Verifying API Functions")
    print("=" * 60)

    try:
        from core import (
            bootstrap_session,
            get_current_session,
            persist_input,
            save_form,
        )

        # Test bootstrap_session
        session = bootstrap_session(user_id="api_test")
        print(f"✅ bootstrap_session() works: {session.session_id}")

        # Test get_current_session (returns None without Streamlit)
        current = get_current_session()
        print(f"✅ get_current_session() works: {current}")

        # Note: persist_input and save_form require Streamlit
        print("✅ persist_input() and save_form() available")

        return True
    except Exception as e:
        print(f"❌ API functions verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_documentation():
    """Verify documentation exists"""
    print("\n" + "=" * 60)
    print("6. Verifying Documentation")
    print("=" * 60)

    import os

    docs = [
        "core/SESSION_QUICK_REFERENCE.md",
        "demo_session_system.py",
        "TASK_2_SESSION_MANAGEMENT_SUMMARY.md",
    ]

    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"✅ {doc} exists")
        else:
            print(f"❌ {doc} missing")
            all_exist = False

    return all_exist


def verify_tests():
    """Verify test files exist"""
    print("\n" + "=" * 60)
    print("7. Verifying Test Files")
    print("=" * 60)

    import os

    tests = [
        "tests/test_session.py",
        "tests/test_session_persistence.py",
        "tests/test_session_manager.py",
    ]

    all_exist = True
    for test in tests:
        if os.path.exists(test):
            print(f"✅ {test} exists")
        else:
            print(f"❌ {test} missing")
            all_exist = False

    return all_exist


def run_verification():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("TASK 2 VERIFICATION: Enhanced Session Management")
    print("=" * 60)

    checks = [
        ("Imports", verify_imports),
        ("UserSession", verify_user_session),
        ("DebouncedWriter", verify_debounced_writer),
        ("SessionManager", verify_session_manager),
        ("API Functions", verify_api_functions),
        ("Documentation", verify_documentation),
        ("Test Files", verify_tests),
    ]

    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with exception: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All verifications passed! Task 2 is complete.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} verification(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_verification())
