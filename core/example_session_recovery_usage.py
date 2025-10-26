"""Example Usage of Session Recovery System"""


# Example 1: Basic Session Recovery After Browser Refresh
def example_basic_recovery():
    """
    Example: Recover session after browser refresh

    This is the most common use case - recovering a user's session
    when they refresh the browser.
    """
    from core.session_recovery import recover_session_after_refresh

    # In a Streamlit app, this would typically be called at the top of your main script
    # The session_id would come from query parameters or session_state

    session = recover_session_after_refresh(
        session_id=None,  # Will auto-detect from query params or session_state
        validate_forms=True  # Validate form data during recovery
    )

    if session:
        print(f"Session recovered: {session.session_id}")
        print(f"Current page: {session.current_page}")
        print(f"User ID: {session.user_id}")
    else:
        print("No session to recover, new session created")


# Example 2: Recovery with Specific Session ID
def example_recovery_with_session_id():
    """
    Example: Recover session with a specific session ID

    Use this when you have a session ID from a URL parameter or cookie.
    """
    from core.session_recovery import recover_session_after_refresh

    # Session ID from URL parameter or cookie
    session_id = "550e8400-e29b-41d4-a716-446655440000"

    session = recover_session_after_refresh(
        session_id=session_id,
        validate_forms=True
    )

    if session:
        print(f"Session {session_id} recovered successfully")
        print(f"Form states: {len(session.form_states)}")
        print(f"Navigation history: {len(session.navigation_history)} entries")
    else:
        print(f"Session {session_id} not found")


# Example 3: Recovery with Form Validation
def example_recovery_with_validation():
    """
    Example: Recover session and validate form data

    This ensures that recovered form data is still valid according
    to the current validation rules.
    """
    from core.session_recovery import get_recovery_status, recover_session_after_refresh

    # Recover session with validation
    session = recover_session_after_refresh(
        session_id="550e8400-e29b-41d4-a716-446655440000",
        validate_forms=True
    )

    # Check recovery status
    status = get_recovery_status()

    if status['has_errors']:
        print("Form validation errors detected during recovery:")
        for form_id, errors in status['validation_errors'].items():
            print(f"  Form '{form_id}':")
            for error in errors:
                print(f"    - {error}")
    else:
        print("All forms recovered successfully with valid data")


# Example 4: Recovery Without Validation
def example_recovery_without_validation():
    """
    Example: Recover session without validating form data

    Use this when you want to recover the session quickly without
    validation overhead, or when validation rules have changed.
    """
    from core.session_recovery import recover_session_after_refresh

    session = recover_session_after_refresh(
        session_id="550e8400-e29b-41d4-a716-446655440000",
        validate_forms=False  # Skip validation
    )

    if session:
        print("Session recovered without validation")
        print(f"Forms: {list(session.form_states.keys())}")


# Example 5: Ensuring Session Persistence
def example_ensure_persistence():
    """
    Example: Ensure session ID is persisted for recovery

    Call this function on every page to ensure the session can be
    recovered after a browser refresh.
    """
    from core.session_recovery import ensure_session_persistence

    # This should be called at the top of every Streamlit page
    ensure_session_persistence()

    print("Session ID persisted in query parameters and session_state")


# Example 6: Streamlit App Integration
def example_streamlit_integration():
    """
    Example: Complete Streamlit app with session recovery

    This shows how to integrate session recovery into a Streamlit app.
    """
    import streamlit as st

    from core.session_recovery import (
        ensure_session_persistence,
        get_recovery_status,
        recover_session_after_refresh,
    )

    # At the top of your Streamlit app
    st.title("My Streamlit App with Session Recovery")

    # Ensure session persistence
    ensure_session_persistence()

    # Recover session if needed
    session = recover_session_after_refresh(validate_forms=True)

    # Check for recovery errors
    status = get_recovery_status()
    if status['has_errors']:
        st.warning("Some form data could not be validated:")
        for form_id, errors in status['validation_errors'].items():
            with st.expander(f"Form: {form_id}"):
                for error in errors:
                    st.error(error)

    # Display session info
    st.sidebar.write(f"Session ID: {session.session_id}")
    st.sidebar.write(f"Current Page: {session.current_page}")
    st.sidebar.write(f"Interaction Count: {session.interaction_count}")

    # Your app content here
    st.write("Welcome back! Your session has been restored.")


# Example 7: Recovery with Navigation State
def example_recovery_with_navigation():
    """
    Example: Recover session with navigation state

    This shows how navigation history and parameters are preserved.
    """
    from core.session_recovery import recover_session_after_refresh

    session = recover_session_after_refresh(
        session_id="550e8400-e29b-41d4-a716-446655440000"
    )

    if session:
        print(f"Current page: {session.current_page}")
        print(f"Page parameters: {session.page_params}")
        print(
            f"\nNavigation history ({len(session.navigation_history)} entries):")

        for i, entry in enumerate(session.navigation_history[-5:], 1):
            print(f"  {i}. {entry.page} - {entry.timestamp}")
            if entry.params:
                print(f"     Params: {entry.params}")


# Example 8: Recovery with Cache Keys
def example_recovery_with_cache():
    """
    Example: Recover session with cache keys

    This shows how cache keys are preserved for performance optimization.
    """
    from core.session_recovery import recover_session_after_refresh

    session = recover_session_after_refresh(
        session_id="550e8400-e29b-41d4-a716-446655440000"
    )

    if session:
        print(f"Cache keys recovered: {len(session.cache_keys)}")
        print(f"Cache dependencies: {len(session.cache_dependencies)}")

        # Cache keys can be used to restore cached data
        for key in list(session.cache_keys)[:5]:
            print(f"  - {key}")
            if key in session.cache_dependencies:
                deps = session.cache_dependencies[key]
                print(f"    Dependencies: {deps}")


# Example 9: Error Handling
def example_error_handling():
    """
    Example: Handle recovery errors gracefully

    This shows how to handle various recovery error scenarios.
    """
    from core.session_recovery import (
        SessionRecoveryError,
        clear_recovery_errors,
        get_recovery_status,
        recover_session_after_refresh,
    )

    try:
        session = recover_session_after_refresh(
            session_id="invalid-session-id",
            validate_forms=True
        )

        if session:
            # Check for validation errors
            status = get_recovery_status()
            if status['has_errors']:
                print("Recovery completed with validation errors:")
                for form_id, errors in status['validation_errors'].items():
                    print(f"  {form_id}: {errors}")

                # Clear errors after handling
                clear_recovery_errors()
        else:
            print("Session not found, new session created")

    except SessionRecoveryError as e:
        print(f"Recovery failed: {e}")
        # Fall back to creating a new session
        from core.session import bootstrap_session
        session = bootstrap_session()


# Example 10: Custom Recovery Manager
def example_custom_recovery_manager():
    """
    Example: Use custom recovery manager for advanced scenarios

    This shows how to use the SessionRecoveryManager directly
    for more control over the recovery process.
    """
    from core.session_recovery import SessionRecoveryManager

    # Create custom recovery manager
    manager = SessionRecoveryManager()
    manager.max_recovery_attempts = 5  # Increase retry attempts

    # Perform recovery
    session = manager.recover_complete_session(
        session_id="550e8400-e29b-41d4-a716-446655440000",
        validate_forms=True
    )

    # Get detailed status
    status = manager.get_recovery_status()
    print(f"Recovery attempts: {status['recovery_attempts']}")
    print(f"Max attempts: {status['max_attempts']}")
    print(f"Has errors: {status['has_errors']}")


# Example 11: Recovery in Production
def example_production_recovery():
    """
    Example: Production-ready recovery with logging and monitoring

    This shows best practices for production deployments.
    """
    import logging

    from core.session_recovery import (
        SessionRecoveryError,
        get_recovery_status,
        recover_session_after_refresh,
    )

    logger = logging.getLogger(__name__)

    try:
        # Attempt recovery
        session = recover_session_after_refresh(validate_forms=True)

        if session:
            logger.info(
                "Session recovered",
                extra={
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'page': session.current_page
                }
            )

            # Check for validation errors
            status = get_recovery_status()
            if status['has_errors']:
                logger.warning(
                    "Form validation errors during recovery",
                    extra={
                        'session_id': session.session_id,
                        'error_count': len(status['validation_errors'])
                    }
                )
        else:
            logger.info("New session created")

    except SessionRecoveryError as e:
        logger.error(
            "Session recovery failed",
            extra={'error': str(e)},
            exc_info=True
        )
        # Create fallback session
        from core.session import bootstrap_session
        session = bootstrap_session()


if __name__ == '__main__':
    print("Session Recovery System - Example Usage\n")
    print("=" * 60)

    print("\n1. Basic Recovery:")
    print("-" * 60)
    example_basic_recovery()

    print("\n2. Recovery with Session ID:")
    print("-" * 60)
    example_recovery_with_session_id()

    print("\n3. Recovery with Validation:")
    print("-" * 60)
    example_recovery_with_validation()

    print("\n4. Recovery without Validation:")
    print("-" * 60)
    example_recovery_without_validation()

    print("\n5. Ensure Persistence:")
    print("-" * 60)
    example_ensure_persistence()

    print("\n7. Recovery with Navigation:")
    print("-" * 60)
    example_recovery_with_navigation()

    print("\n8. Recovery with Cache:")
    print("-" * 60)
    example_recovery_with_cache()

    print("\n9. Error Handling:")
    print("-" * 60)
    example_error_handling()

    print("\n10. Custom Recovery Manager:")
    print("-" * 60)
    example_custom_recovery_manager()
