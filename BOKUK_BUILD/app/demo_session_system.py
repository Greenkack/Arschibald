"""
Demo: Session Management System

This script demonstrates the session management system without Streamlit.
For Streamlit integration, see the Quick Reference guide.
"""

import time

from core import (
    UserSession,
    bootstrap_session,
    get_current_session,
    get_session_manager,
    persist_input,
    save_form,
)
from core.session_persistence import get_persistence_engine


def demo_basic_session():
    """Demo: Basic session creation and management"""
    print("\n=== Demo: Basic Session ===")

    # Create new session
    session = UserSession(user_id="demo_user")
    print(f"Created session: {session.session_id}")
    print(f"User ID: {session.user_id}")
    print(f"Current page: {session.current_page}")


def demo_navigation():
    """Demo: Navigation and history"""
    print("\n=== Demo: Navigation ===")

    session = UserSession()

    # Navigate to pages
    print("Navigating to profile...")
    session.navigate_to("profile", {"user_id": "123"})
    print(f"Current page: {session.current_page}")
    print(f"Page params: {session.page_params}")

    print("\nNavigating to settings...")
    session.navigate_to("settings", {"tab": "privacy"})
    print(f"Current page: {session.current_page}")

    # View history
    print(f"\nNavigation history ({len(session.navigation_history)} entries):")
    for entry in session.navigation_history:
        print(f"  - {entry.page} with params {entry.params}")

    # Go back
    print("\nGoing back...")
    session.go_back()
    print(f"Current page: {session.current_page}")


def demo_form_management():
    """Demo: Form state management"""
    print("\n=== Demo: Form Management ===")

    session = UserSession()

    # Update form data
    print("Updating contact form...")
    session.update_form_data("contact_form", "name", "John Doe")
    session.update_form_data("contact_form", "email", "john@example.com")
    session.update_form_data("contact_form", "phone", "+1234567890")

    # Get form state
    form_state = session.get_form_state("contact_form")
    print(f"Form data: {form_state.data}")
    print(f"Is dirty: {form_state.is_dirty}")

    # Mark as saved
    print("\nMarking form as saved...")
    session.mark_form_saved("contact_form")
    print(f"Is dirty: {form_state.is_dirty}")
    print(f"Last saved: {form_state.last_saved}")


def demo_form_snapshots():
    """Demo: Form snapshots and undo/redo"""
    print("\n=== Demo: Form Snapshots ===")

    session = UserSession()

    # Initial data
    session.update_form_data("editor", "content", "Version 1")
    snapshot1 = session.create_form_snapshot("editor", "Initial version")
    print(f"Created snapshot 1: {snapshot1.snapshot_id}")

    # Modify
    session.update_form_data("editor", "content", "Version 2")
    snapshot2 = session.create_form_snapshot("editor", "Second version")
    print(f"Created snapshot 2: {snapshot2.snapshot_id}")

    # Modify again
    session.update_form_data("editor", "content", "Version 3")
    print(f"Current content: {session.get_form_state('editor').data['content']}")

    # Restore first snapshot
    print(f"\nRestoring snapshot 1...")
    session.restore_form_snapshot(snapshot1.snapshot_id)
    print(f"Current content: {session.get_form_state('editor').data['content']}")


def demo_permissions():
    """Demo: Permissions and roles"""
    print("\n=== Demo: Permissions & Roles ===")

    session = UserSession()

    # Add roles
    session.add_role("user")
    session.add_role("editor")
    print(f"Roles: {session.roles}")

    # Add permissions
    session.add_permission("read")
    session.add_permission("write")
    session.add_permission("edit")
    print(f"Permissions: {session.permissions}")

    # Check permissions
    print(f"\nHas 'write' permission: {session.has_permission('write')}")
    print(f"Has 'delete' permission: {session.has_permission('delete')}")
    print(f"Has 'editor' role: {session.has_role('editor')}")


def demo_cache_tracking():
    """Demo: Cache key tracking"""
    print("\n=== Demo: Cache Tracking ===")

    session = UserSession()

    # Add cache keys
    session.add_cache_key("user_data_123")
    session.add_cache_key("user_data_456")
    session.add_cache_key("profile_789")
    print(f"Cache keys: {session.cache_keys}")

    # Invalidate by pattern
    print("\nInvalidating 'user_data' keys...")
    invalidated = session.invalidate_cache_keys("user_data")
    print(f"Invalidated: {invalidated}")
    print(f"Remaining: {session.cache_keys}")


def demo_session_metrics():
    """Demo: Session metrics"""
    print("\n=== Demo: Session Metrics ===")

    session = UserSession()

    # Simulate activity
    session.navigate_to("home")
    session.navigate_to("profile")
    session.navigate_to("settings")
    session.update_form_data("form1", "field", "value")

    # View metrics
    print(f"Page views: {session.metrics.page_views}")
    print(f"Interaction count: {session.metrics.interaction_count}")
    print(f"Session duration: {session.metrics.session_duration}")
    print(f"Last activity: {session.metrics.last_activity}")


def demo_persistence():
    """Demo: Session persistence"""
    print("\n=== Demo: Session Persistence ===")

    engine = get_persistence_engine()

    # Create and persist session
    session = UserSession(user_id="persist_demo")
    session.navigate_to("profile", {"id": "123"})
    session.update_form_data("form1", "field1", "value1")

    print(f"Created session: {session.session_id}")
    print("Persisting session...")
    engine.persist_session(session, immediate=True)

    # Recover session
    print("\nRecovering session...")
    recovered = engine.recover_session(session.session_id)

    if recovered:
        print(f"Recovered session: {recovered.session_id}")
        print(f"Current page: {recovered.current_page}")
        print(f"Page params: {recovered.page_params}")
        print(f"Form data: {recovered.form_states['form1'].data}")
    else:
        print("Failed to recover session")

    # Cleanup
    print("\nCleaning up...")
    engine.delete_session(session.session_id)


def demo_debounced_persistence():
    """Demo: Debounced persistence"""
    print("\n=== Demo: Debounced Persistence ===")

    engine = get_persistence_engine()
    session = UserSession(user_id="debounce_demo")

    print("Scheduling multiple rapid updates...")
    for i in range(5):
        session.update_form_data("form1", f"field{i}", f"value{i}")
        engine.persist_session(session, immediate=False)
        print(f"  Update {i+1} scheduled")
        time.sleep(0.1)

    print("\nWaiting for debounce...")
    time.sleep(2.5)

    # Verify persistence
    recovered = engine.recover_session(session.session_id)
    if recovered:
        print(f"Session persisted with {len(recovered.form_states['form1'].data)} fields")
    else:
        print("Session not yet persisted")

    # Cleanup
    engine.delete_session(session.session_id)


def demo_session_cleanup():
    """Demo: Session cleanup"""
    print("\n=== Demo: Session Cleanup ===")

    engine = get_persistence_engine()

    # Create test sessions
    print("Creating test sessions...")
    for i in range(3):
        session = UserSession(user_id=f"cleanup_user_{i}")
        engine.persist_session(session, immediate=True)

    # Get count
    count = engine.get_session_count()
    print(f"Active sessions: {count}")

    # Cleanup (this won't delete anything as sessions are fresh)
    print("\nRunning cleanup...")
    expired_count = engine.cleanup_expired_sessions()
    print(f"Cleaned up {expired_count} expired sessions")

    # Final count
    count = engine.get_session_count()
    print(f"Active sessions after cleanup: {count}")


def demo_serialization():
    """Demo: Session serialization"""
    print("\n=== Demo: Session Serialization ===")

    session = UserSession(user_id="serialize_demo")
    session.navigate_to("profile")
    session.update_form_data("form1", "field", "value")
    session.add_role("admin")

    # Serialize to JSON
    print("Serializing to JSON...")
    json_str = session.to_json()
    print(f"JSON length: {len(json_str)} characters")

    # Deserialize
    print("\nDeserializing from JSON...")
    restored = UserSession.from_json(json_str)
    print(f"Restored session: {restored.session_id}")
    print(f"Current page: {restored.current_page}")
    print(f"Roles: {restored.roles}")


def demo_bootstrap():
    """Demo: Bootstrap session"""
    print("\n=== Demo: Bootstrap Session ===")

    # Bootstrap new session
    print("Bootstrapping new session...")
    session1 = bootstrap_session(user_id="bootstrap_demo")
    print(f"Session ID: {session1.session_id}")

    # Persist
    engine = get_persistence_engine()
    engine.persist_session(session1, immediate=True)

    # Bootstrap with recovery
    print("\nBootstrapping with recovery...")
    session2 = bootstrap_session(session_id=session1.session_id)
    print(f"Recovered session: {session2.session_id}")
    print(f"Same session: {session1.session_id == session2.session_id}")

    # Cleanup
    engine.delete_session(session1.session_id)


def main():
    """Run all demos"""
    print("=" * 60)
    print("Session Management System Demo")
    print("=" * 60)

    demos = [
        demo_basic_session,
        demo_navigation,
        demo_form_management,
        demo_form_snapshots,
        demo_permissions,
        demo_cache_tracking,
        demo_session_metrics,
        demo_persistence,
        demo_debounced_persistence,
        demo_session_cleanup,
        demo_serialization,
        demo_bootstrap,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\nError in {demo.__name__}: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
