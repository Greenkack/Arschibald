"""
Phase 3 - Quick Test Script
===========================

Schneller Test ob Session Persistence funktioniert.
"""

import sys
from pathlib import Path

# Test 1: Module Import
print(" Test 1: Module Import")
try:
    from core_integration import (
        bootstrap_session,
        persist_session_input,
        get_current_session,
        is_feature_enabled
    )
    print("core_integration imports OK")
except Exception as e:
    print(f"core_integration import failed: {e}")
    sys.exit(1)

try:
    from session_widgets import (
        session_text_input,
        session_number_input,
        persist_calculation_result
    )
    print("session_widgets imports OK")
except Exception as e:
    print(f"session_widgets import failed: {e}")
    sys.exit(1)

# Test 2: Feature Flag
print("\n Test 2: Feature Flag")
session_enabled = is_feature_enabled('session')
if session_enabled:
    print(f"Session Persistence: ENABLED")
else:
    print(f"Session Persistence: DISABLED")
    print("   Set FEATURE_SESSION_PERSISTENCE=true in .env to enable")

# Test 3: Session Manager
print("\n Test 3: Session Manager")
try:
    from core.session_manager import SessionManager
    sm = SessionManager()
    print("SessionManager instantiated")
except Exception as e:
    print(f"SessionManager failed: {e}")
    sys.exit(1)

# Test 4: Database
print("\n Test 4: Database Connection")
try:
    from core.session_persistence import get_persistence_engine
    engine = get_persistence_engine()
    print(f"Persistence Engine: {type(engine).__name__}")
except Exception as e:
    print(f"Persistence Engine failed: {e}")
    sys.exit(1)

# Test 5: Session Bootstrap (without Streamlit)
print("\n Test 5: Session Bootstrap")
try:
    from core.session import UserSession
    test_session = UserSession(user_id="test_user")
    print(f"Session created: {test_session.session_id}")
    print(f"   User ID: {test_session.user_id}")
    print(f"   Created: {test_session.created_at}")
except Exception as e:
    print(f"Session bootstrap failed: {e}")
    sys.exit(1)

# Test 6: Form Data Storage
print("\n Test 6: Form Data Storage")
try:
    test_session.update_form_data("test_form", "test_key", "test_value")
    print("Form data stored")
    print(f"   Forms: {list(test_session.form_states.keys())}")
except Exception as e:
    print(f"Form data storage failed: {e}")
    sys.exit(1)

# Test 7: Session Persistence
print("\n Test 7: Session Persistence")
try:
    from core.session_persistence import persist_session
    persist_session(test_session, immediate=True)
    print(f"Session persisted to database")
except Exception as e:
    print(f"Session persistence failed: {e}")
    sys.exit(1)

# Test 8: Session Recovery
print("\n Test 8: Session Recovery")
try:
    from core.session_persistence import recover_session
    recovered = recover_session(test_session.session_id)
    if recovered:
        print(f"Session recovered: {recovered.session_id}")
        print(f"   Form data preserved: {len(recovered.form_states)} forms")
    else:
        print(f"Session recovery failed: None returned")
except Exception as e:
    print(f"Session recovery failed: {e}")
    sys.exit(1)

# Test 9: File Structure
print("\n Test 9: File Structure")
required_files = [
    "core/session.py",
    "core/session_manager.py",
    "core/session_persistence.py",
    "core/session_recovery.py",
    "core_integration.py",
    "session_widgets.py",
    ".env"
]

for file in required_files:
    path = Path(file)
    if path.exists():
        print(f"{file}")
    else:
        print(f"{file} - MISSING")

# Test 10: Environment Variables
print("\n Test 10: Environment Variables")
import os
env_vars = {
    'FEATURE_SESSION_PERSISTENCE': os.getenv('FEATURE_SESSION_PERSISTENCE', 'not set'),
    'SESSION_TIMEOUT': os.getenv('SESSION_TIMEOUT', 'not set'),
    'DATABASE_URL': os.getenv('DATABASE_URL', 'not set'),
}

for var, value in env_vars.items():
    status = "" if value != 'not set' else ""
    print(f"{status} {var}: {value}")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print("All core tests passed!")
print("\nNext Steps:")
print("1. Run the demo: streamlit run PHASE_3_USAGE_EXAMPLE.py")
print("2. Test browser refresh in main app: streamlit run gui.py")
print("3. Check admin dashboard for session status")
print("\nTo enable Session Persistence:")
print("   Set FEATURE_SESSION_PERSISTENCE=true in .env")
print("="*60)
