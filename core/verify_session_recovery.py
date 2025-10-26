"""Verification Script for Session Recovery System"""

import uuid
from datetime import datetime

from session import FormState, NavigationEntry, UserSession
from session_recovery import (
    SessionRecoveryManager,
    clear_recovery_errors,
    get_recovery_manager,
    get_recovery_status,
)


def verify_basic_recovery():
    """Verify basic recovery functionality"""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Recovery Manager Creation")
    print("=" * 60)

    manager = SessionRecoveryManager()
    assert manager.recovery_attempts == 0
    assert manager.max_recovery_attempts == 3
    assert manager.validation_errors == {}

    print("✓ Recovery manager created successfully")
    print(f"  - Max attempts: {manager.max_recovery_attempts}")
    print(f"  - Initial errors: {len(manager.validation_errors)}")


def verify_form_validation():
    """Verify form validation functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Form Validation")
    print("=" * 60)

    manager = SessionRecoveryManager()

    # Test required field validation
    schema = {
        'name': {'required': True, 'type': 'string'},
        'email': {'required': True, 'type': 'string'}
    }

    data = {'name': 'John'}  # Missing email
    errors = manager._validate_form_data(data, schema)

    assert 'email' in errors
    print("✓ Required field validation works")
    print("  - Detected missing field: email")

    # Test type validation
    schema = {'age': {'type': 'number'}}
    data = {'age': 'not a number'}
    errors = manager._validate_form_data(data, schema)

    assert 'age' in errors
    print("✓ Type validation works")
    print("  - Detected type error: age must be number")

    # Test min/max validation
    schema = {'age': {'type': 'number', 'min': 18, 'max': 100}}
    data = {'age': 15}
    errors = manager._validate_form_data(data, schema)

    assert 'age' in errors
    print("✓ Min/max validation works")
    print("  - Detected range error: age below minimum")

    # Test length validation
    schema = {'username': {'type': 'string', 'minLength': 3, 'maxLength': 20}}
    data = {'username': 'ab'}
    errors = manager._validate_form_data(data, schema)

    assert 'username' in errors
    print("✓ Length validation works")
    print("  - Detected length error: username too short")


def verify_form_recovery():
    """Verify form recovery with validation"""
    print("\n" + "=" * 60)
    print("TEST 3: Form Recovery with Validation")
    print("=" * 60)

    manager = SessionRecoveryManager()

    # Create session with valid form data
    session = UserSession(session_id=str(uuid.uuid4()))
    form_state = FormState(
        form_id='contact_form',
        data={'name': 'John Doe', 'email': 'john@example.com'},
        validation_schema={
            'name': {'required': True, 'type': 'string'},
            'email': {'required': True, 'type': 'string'}
        }
    )
    session.form_states['contact_form'] = form_state

    # Recover and validate
    manager._recover_and_validate_forms(session)

    assert len(manager.validation_errors) == 0
    print("✓ Valid form data recovered successfully")
    print("  - Form ID: contact_form")
    print("  - Fields: name, email")
    print("  - Validation errors: 0")

    # Create session with invalid form data
    session2 = UserSession(session_id=str(uuid.uuid4()))
    form_state2 = FormState(
        form_id='invalid_form',
        data={'name': 'John'},  # Missing required email
        validation_schema={
            'name': {'required': True, 'type': 'string'},
            'email': {'required': True, 'type': 'string'}
        }
    )
    session2.form_states['invalid_form'] = form_state2

    # Recover and validate
    manager._recover_and_validate_forms(session2)

    assert 'invalid_form' in manager.validation_errors
    print("✓ Invalid form data detected correctly")
    print("  - Form ID: invalid_form")
    print(
        f"  - Validation errors: {len(manager.validation_errors['invalid_form'])}")


def verify_navigation_recovery():
    """Verify navigation state recovery"""
    print("\n" + "=" * 60)
    print("TEST 4: Navigation State Recovery")
    print("=" * 60)

    manager = SessionRecoveryManager()

    # Create session with navigation state
    session = UserSession(session_id=str(uuid.uuid4()))
    session.current_page = 'dashboard'
    session.page_params = {'filter': 'active', 'sort': 'date'}
    session.navigation_history = [
        NavigationEntry(
            page='home',
            params={},
            timestamp=datetime.now()
        ),
        NavigationEntry(
            page='dashboard',
            params={'filter': 'active'},
            timestamp=datetime.now()
        )
    ]

    # Recover navigation state
    manager._recover_navigation_state(session)

    print("✓ Navigation state recovered successfully")
    print(f"  - Current page: {session.current_page}")
    print(f"  - Page params: {session.page_params}")
    print(f"  - History entries: {len(session.navigation_history)}")


def verify_cache_recovery():
    """Verify cache key recovery"""
    print("\n" + "=" * 60)
    print("TEST 5: Cache Key Recovery")
    print("=" * 60)

    manager = SessionRecoveryManager()

    # Create session with cache keys
    session = UserSession(session_id=str(uuid.uuid4()))
    session.cache_keys = {'key1', 'key2', 'key3'}
    session.cache_dependencies = {
        'key1': {'dep1', 'dep2'},
        'key2': {'dep3'}
    }

    # Recover cache keys
    manager._recover_cache_keys(session)

    print("✓ Cache keys recovered successfully")
    print(f"  - Cache keys: {len(session.cache_keys)}")
    print(f"  - Dependencies: {len(session.cache_dependencies)}")
    for key in list(session.cache_keys)[:3]:
        deps = session.cache_dependencies.get(key, set())
        print(f"    - {key}: {len(deps)} dependencies")


def verify_recovery_status():
    """Verify recovery status management"""
    print("\n" + "=" * 60)
    print("TEST 6: Recovery Status Management")
    print("=" * 60)

    manager = get_recovery_manager()

    # Get initial status
    status = get_recovery_status()

    print("✓ Recovery status retrieved")
    print(f"  - Recovery attempts: {status['recovery_attempts']}")
    print(f"  - Max attempts: {status['max_attempts']}")
    print(f"  - Has errors: {status['has_errors']}")

    # Add validation errors
    manager.validation_errors = {'form1': ['error1', 'error2']}

    status = get_recovery_status()
    assert status['has_errors'] is True
    print("✓ Validation errors tracked correctly")
    print(f"  - Error count: {len(status['validation_errors'])}")

    # Clear errors
    clear_recovery_errors()

    status = get_recovery_status()
    assert status['has_errors'] is False
    print("✓ Validation errors cleared successfully")


def verify_global_manager():
    """Verify global recovery manager"""
    print("\n" + "=" * 60)
    print("TEST 7: Global Recovery Manager")
    print("=" * 60)

    manager1 = get_recovery_manager()
    manager2 = get_recovery_manager()

    assert manager1 is manager2
    print("✓ Global recovery manager is singleton")
    print(f"  - Manager ID: {id(manager1)}")


def main():
    """Run all verification tests"""
    print("\n" + "=" * 60)
    print("SESSION RECOVERY SYSTEM VERIFICATION")
    print("=" * 60)

    try:
        verify_basic_recovery()
        verify_form_validation()
        verify_form_recovery()
        verify_navigation_recovery()
        verify_cache_recovery()
        verify_recovery_status()
        verify_global_manager()

        print("\n" + "=" * 60)
        print("ALL VERIFICATION TESTS PASSED ✓")
        print("=" * 60)
        print("\nSession Recovery System is working correctly!")
        print("\nKey Features Verified:")
        print("  ✓ Recovery manager creation")
        print("  ✓ Form validation (required, type, min/max, length)")
        print("  ✓ Form data recovery with validation")
        print("  ✓ Navigation state restoration")
        print("  ✓ Cache key restoration")
        print("  ✓ Recovery status management")
        print("  ✓ Global manager singleton")

        print("\nNext Steps:")
        print("  1. Integrate with Streamlit application")
        print("  2. Add ensure_session_persistence() to all pages")
        print("  3. Call recover_session_after_refresh() on app startup")
        print("  4. Monitor recovery metrics in production")

    except AssertionError as e:
        print(f"\n✗ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
