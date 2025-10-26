"""Example Usage of Enhanced Session Management System"""

import time

from core.session import (
    UserSession,
    bootstrap_session,
    cleanup_expired_sessions,
    persist_input,
    recover_session,
    save_session,
)
from core.session_repository import SessionRepository, init_session_tables


def example_basic_session():
    """Example: Basic session creation and usage"""
    print("\n=== Basic Session Usage ===")

    # Create new session
    session = UserSession(user_id="user123")
    print(f"Created session: {session.session_id}")
    print(f"User ID: {session.user_id}")
    print(f"Current page: {session.current_page}")

    # Add navigation
    session.add_navigation("dashboard", {"view": "overview"})
    session.add_navigation("settings")

    print(f"Navigation history: {len(session.navigation_history)} entries")
    print(f"Page views: {session.page_views}")
    print(f"Interaction count: {session.interaction_count}")


def example_form_state_management():
    """Example: Form state management"""
    print("\n=== Form State Management ===")

    session = UserSession(user_id="user456")

    # Get or create form state
    form_state = session.get_form_state("contact_form")
    print(f"Form ID: {form_state.form_id}")

    # Update form data
    form_state.data = {
        "name": "John Doe",
        "email": "john@example.com",
        "message": "Hello!"
    }

    # Mark as dirty (unsaved changes)
    session.mark_form_dirty("contact_form")
    print(f"Dirty forms: {session.dirty_forms}")

    # Simulate save
    session.mark_form_clean("contact_form")
    print(f"Form saved at: {form_state.last_saved}")
    print(f"Dirty forms: {session.dirty_forms}")


def example_session_persistence():
    """Example: Session persistence to database"""
    print("\n=== Session Persistence ===")

    # Initialize database tables
    init_session_tables()

    # Create session
    session = UserSession(user_id="user789")
    session.add_navigation("home")
    session.add_navigation("profile", {"tab": "settings"})

    # Create repository
    repo = SessionRepository()

    # Save session
    repo.save_session(session)
    print(f"Session saved: {session.session_id}")

    # Retrieve session
    retrieved_data = repo.get_session(session.session_id)
    if retrieved_data:
        retrieved_session = UserSession.from_dict(retrieved_data)
        print(f"Session retrieved: {retrieved_session.session_id}")
        print(
            f"Navigation history: {len(retrieved_session.navigation_history)} entries")


def example_session_recovery():
    """Example: Session recovery after browser refresh"""
    print("\n=== Session Recovery ===")

    # Initialize database
    init_session_tables()

    # Create and save session
    original_session = UserSession(user_id="user_recovery")
    original_session.add_navigation("dashboard")

    form_state = original_session.get_form_state("important_form")
    form_state.data = {"field1": "important data"}
    original_session.mark_form_dirty("important_form")

    repo = SessionRepository()
    repo.save_session(original_session)
    print(f"Original session saved: {original_session.session_id}")

    # Simulate browser refresh - recover session
    recovered_session = recover_session(original_session.session_id)

    if recovered_session:
        print(f"Session recovered: {recovered_session.session_id}")
        print(
            f"Form data preserved: {
                recovered_session.form_states['important_form'].data}")
        print(f"Dirty forms: {recovered_session.dirty_forms}")
    else:
        print("Session recovery failed")


def example_bootstrap_session():
    """Example: Bootstrap session with automatic recovery"""
    print("\n=== Bootstrap Session ===")

    # Initialize database
    init_session_tables()

    # First visit - create new session
    session1 = bootstrap_session(
        user_id="bootstrap_user",
        restore_from_db=False)
    print(f"First visit - new session: {session1.session_id}")

    # Save session
    save_session(session1, immediate=True)

    # Simulate browser refresh - bootstrap will restore
    session2 = bootstrap_session(
        session_id=session1.session_id,
        restore_from_db=True
    )
    print(f"After refresh - restored session: {session2.session_id}")
    print(f"Same session: {session1.session_id == session2.session_id}")


def example_persist_input():
    """Example: Persist input with debouncing"""
    print("\n=== Persist Input ===")

    # Initialize database
    init_session_tables()

    # Bootstrap session
    session = bootstrap_session(user_id="input_user", restore_from_db=False)

    # Simulate rapid input changes (will be debounced)
    print("Simulating rapid input changes...")
    for i in range(5):
        persist_input(f"field_{i}", f"value_{i}")
        time.sleep(0.05)

    print("Inputs persisted (debounced to database)")

    # Wait for debounce to complete
    time.sleep(0.6)
    print("Database write completed")


def example_permissions_and_roles():
    """Example: Permissions and roles"""
    print("\n=== Permissions and Roles ===")

    session = UserSession(
        user_id="admin_user",
        roles={"admin", "editor"},
        permissions={"read", "write", "delete"}
    )

    # Check permissions
    print(f"Has 'read' permission: {session.has_permission('read')}")
    print(f"Has 'admin' role: {session.has_role('admin')}")
    print(f"Has 'user' role: {session.has_role('user')}")


def example_cache_tracking():
    """Example: Cache key tracking"""
    print("\n=== Cache Tracking ===")

    session = UserSession(user_id="cache_user")

    # Track cache keys with dependencies
    session.add_cache_key("user_data", {"user_id"})
    session.add_cache_key("user_posts", {"user_id", "posts"})
    session.add_cache_key("user_profile", {"user_id", "profile"})

    print(f"Tracked cache keys: {session.cache_keys}")
    print(f"Cache dependencies: {session.cache_dependencies}")

    # Remove cache key
    session.remove_cache_key("user_posts")
    print(f"After removal: {session.cache_keys}")


def example_session_metrics():
    """Example: Session metrics tracking"""
    print("\n=== Session Metrics ===")

    session = UserSession(user_id="metrics_user")

    # Simulate user activity
    session.add_navigation("home")
    session.add_navigation("products")
    session.add_navigation("cart")
    session.add_navigation("home")
    session.add_navigation("checkout")

    print(f"Total interactions: {session.interaction_count}")
    print(f"Page views: {session.page_views}")
    print(f"Session duration: {session.session_duration}")
    print(f"Last activity: {session.last_activity}")


def example_cleanup_expired_sessions():
    """Example: Cleanup expired sessions"""
    print("\n=== Cleanup Expired Sessions ===")

    # Initialize database
    init_session_tables()

    # Create some sessions
    repo = SessionRepository()
    for i in range(3):
        session = UserSession(user_id=f"user_{i}")
        repo.save_session(session)

    print("Created 3 sessions")

    # Cleanup sessions older than 24 hours
    count = cleanup_expired_sessions(max_age_hours=24)
    print(f"Cleaned up {count} expired sessions")


def example_conflict_resolution():
    """Example: Session conflict resolution"""
    print("\n=== Conflict Resolution ===")

    # Initialize database
    init_session_tables()
    repo = SessionRepository()

    # Create and save initial session
    session = UserSession(user_id="conflict_user")
    session.add_navigation("home")
    repo.save_session(session)
    print(f"Initial session saved: {session.session_id}")

    # Simulate concurrent modification
    local_session = UserSession(
        session_id=session.session_id,
        user_id="conflict_user")
    local_session.add_navigation("dashboard")

    # Resolve conflict (last write wins)
    resolved = repo.resolve_conflict(
        session.session_id,
        local_session,
        strategy='last_write_wins'
    )
    print(f"Conflict resolved: {resolved.session_id}")
    print(f"Navigation history: {len(resolved.navigation_history)} entries")


def example_session_serialization():
    """Example: Session serialization"""
    print("\n=== Session Serialization ===")

    # Create session with data
    session = UserSession(user_id="serialize_user")
    session.add_navigation("home")
    session.add_navigation("settings", {"tab": "profile"})

    form_state = session.get_form_state("test_form")
    form_state.data = {"field": "value"}

    # Serialize to dict
    session_dict = session.to_dict()
    print(f"Serialized to dict: {len(session_dict)} keys")

    # Serialize to JSON
    session_json = session.to_json()
    print(f"Serialized to JSON: {len(session_json)} characters")

    # Deserialize
    restored = UserSession.from_json(session_json)
    print(f"Restored session: {restored.session_id}")
    print(f"Data preserved: {restored.form_states['test_form'].data}")


def example_complete_workflow():
    """Example: Complete session workflow"""
    print("\n=== Complete Session Workflow ===")

    # Initialize database
    init_session_tables()

    # 1. User visits site - bootstrap session
    print("1. User visits site")
    session = bootstrap_session(user_id="workflow_user", restore_from_db=False)
    print(f"   Session created: {session.session_id}")

    # 2. User navigates
    print("2. User navigates to dashboard")
    session.add_navigation("dashboard", {"view": "overview"})
    persist_input("current_page", "dashboard")

    # 3. User fills form
    print("3. User fills contact form")
    form_state = session.get_form_state("contact_form")
    form_state.data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "message": "Hello!"
    }
    session.mark_form_dirty("contact_form")
    persist_input("contact_form_name", "Jane Smith")

    # 4. Save session
    print("4. Session auto-saved to database")
    save_session(session, immediate=True)

    # 5. Browser refresh - recover session
    print("5. Browser refresh - recovering session")
    recovered = recover_session(session.session_id)

    if recovered:
        print(f"   Session recovered: {recovered.session_id}")
        print(
            f"   Form data preserved: {
                recovered.form_states['contact_form'].data}")
        print(
            f"   Navigation preserved: {len(recovered.navigation_history)} entries")

    # 6. User continues work
    print("6. User continues work")
    recovered.add_navigation("settings")
    recovered.mark_form_clean("contact_form")

    # 7. Final save
    print("7. Final session save")
    save_session(recovered, immediate=True)

    print("\nWorkflow complete!")


if __name__ == "__main__":
    print("Enhanced Session Management System - Examples")
    print("=" * 60)

    # Run examples
    example_basic_session()
    example_form_state_management()
    example_session_persistence()
    example_session_recovery()
    example_bootstrap_session()
    example_persist_input()
    example_permissions_and_roles()
    example_cache_tracking()
    example_session_metrics()
    example_cleanup_expired_sessions()
    example_conflict_resolution()
    example_session_serialization()
    example_complete_workflow()

    print("\n" + "=" * 60)
    print("All examples completed!")
