"""Session Manager with Recovery and State Management"""

import uuid
from typing import Any

try:
    import streamlit as st

    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

from .session import UserSession
from .session_persistence import (
    get_persistence_engine,
    persist_session,
    recover_session,
)

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SessionManager:
    """
    Session manager for Streamlit applications.

    Provides comprehensive session management including:
    - Session initialization and recovery
    - Automatic persistence with debouncing
    - Browser refresh recovery
    - Form data recovery
    - Navigation state restoration
    """

    def __init__(self):
        self.persistence_engine = get_persistence_engine()

    def bootstrap_session(
        self, session_id: str | None = None, user_id: str | None = None
    ) -> UserSession:
        """
        Initialize or recover user session.

        This function handles:
        1. Session recovery from database if session_id exists
        2. Creation of new session if recovery fails
        3. Integration with Streamlit session_state
        4. Automatic persistence setup

        Args:
            session_id: Optional session ID to recover
            user_id: Optional user ID for new sessions

        Returns:
            UserSession: Initialized or recovered session
        """
        if not STREAMLIT_AVAILABLE:
            # Create standalone session for non-Streamlit usage
            if session_id:
                session = self.persistence_engine.recover_session(session_id)
                if session:
                    logger.info(
                        "Session recovered (standalone)",
                        session_id=session_id,
                    )
                    return session

            # Create new session
            session = UserSession(user_id=user_id)
            logger.info(
                "New session created (standalone)",
                session_id=session.session_id,
            )
            return session

        # Streamlit-specific session management
        # Check if session already exists in session_state
        if "user_session" in st.session_state:
            session = st.session_state.user_session
            logger.debug(
                "Session loaded from session_state",
                session_id=session.session_id,
            )
            return session

        # Try to recover session from database
        if session_id:
            session = self.persistence_engine.recover_session(session_id)
            if session:
                # Store in session_state
                st.session_state.user_session = session
                st.session_state.session_id = session.session_id

                # Restore navigation state
                if session.current_page:
                    st.session_state.current_page = session.current_page
                if session.page_params:
                    st.session_state.page_params = session.page_params

                # Restore form states
                for form_id, form_state in session.form_states.items():
                    for key, value in form_state.data.items():
                        widget_key = f"{form_id}_{key}"
                        st.session_state[widget_key] = value

                logger.info(
                    "Session recovered and restored",
                    session_id=session_id,
                    forms_restored=len(session.form_states),
                )
                return session

        # Create new session
        session = UserSession(user_id=user_id)

        # Store in session_state
        st.session_state.user_session = session
        st.session_state.session_id = session.session_id
        st.session_state.current_page = session.current_page
        st.session_state.page_params = session.page_params

        # Persist new session
        self.persistence_engine.persist_session(session, immediate=True)

        logger.info(
            "New session created and persisted",
            session_id=session.session_id,
            user_id=user_id,
        )

        return session

    def get_current_session(self) -> UserSession | None:
        """
        Get current session from Streamlit session_state.

        Returns:
            UserSession if available, None otherwise
        """
        if not STREAMLIT_AVAILABLE:
            return None

        return st.session_state.get("user_session")

    def persist_input(
        self,
        key: str,
        value: Any,
        form_id: str | None = None,
        immediate: bool = False,
    ) -> None:
        """
        Persist input to session_state and database with debouncing.

        This function implements the "controlled widgets" pattern:
        1. Immediately update session_state
        2. Update UserSession form state
        3. Debounce write to database

        Args:
            key: Widget key
            value: Widget value
            form_id: Optional form ID for grouping
            immediate: If True, write to DB immediately
        """
        if not STREAMLIT_AVAILABLE:
            logger.warning("persist_input called without Streamlit")
            return

        # Update session_state immediately
        st.session_state[key] = value

        # Get current session
        session = self.get_current_session()
        if not session:
            logger.warning(
                "No active session for persist_input",
                key=key,
            )
            return

        # Update form state if form_id provided
        if form_id:
            session.update_form_data(form_id, key, value)
        else:
            # Store in default form
            session.update_form_data("_default", key, value)

        # Persist to database with debouncing
        self.persistence_engine.persist_session(session, immediate=immediate)

        logger.debug(
            "Input persisted",
            key=key,
            form_id=form_id,
            immediate=immediate,
        )

    def save_form(
        self, form_id: str, data: dict[str, Any], immediate: bool = True
    ) -> None:
        """
        Save complete form data with transaction.

        Args:
            form_id: Form identifier
            data: Form data dictionary
            immediate: If True, write immediately (default for forms)
        """
        session = self.get_current_session()
        if not session:
            logger.warning("No active session for save_form")
            return

        # Update form state
        form_state = session.get_form_state(form_id)
        form_state.data.update(data)

        # Create snapshot before save
        session.create_form_snapshot(
            form_id, description=f"Save at {form_state.updated_at}"
        )

        # Mark as saved
        session.mark_form_saved(form_id)

        # Persist immediately for explicit saves
        self.persistence_engine.persist_session(session, immediate=immediate)

        logger.info(
            "Form saved",
            form_id=form_id,
            fields=len(data),
        )

    def restore_form_state(self, form_id: str) -> dict[str, Any]:
        """
        Restore form state from session.

        Args:
            form_id: Form identifier

        Returns:
            Form data dictionary
        """
        session = self.get_current_session()
        if not session:
            return {}

        form_state = session.get_form_state(form_id)

        # Restore to session_state
        if STREAMLIT_AVAILABLE:
            for key, value in form_state.data.items():
                widget_key = f"{form_id}_{key}"
                st.session_state[widget_key] = value

        logger.debug(
            "Form state restored",
            form_id=form_id,
            fields=len(form_state.data),
        )

        return form_state.data

    def navigate_to(
        self, page: str, params: dict[str, Any] | None = None
    ) -> None:
        """
        Navigate to page with parameter preservation.

        Args:
            page: Target page name
            params: Optional page parameters
        """
        session = self.get_current_session()
        if not session:
            logger.warning("No active session for navigation")
            return

        # Update session navigation
        session.navigate_to(page, params)

        # Update session_state
        if STREAMLIT_AVAILABLE:
            st.session_state.current_page = page
            st.session_state.page_params = params or {}

        # Persist navigation state
        self.persistence_engine.persist_session(session, immediate=False)

        logger.info(
            "Navigation",
            page=page,
            params=params,
        )

    def go_back(self) -> bool:
        """
        Navigate back in history.

        Returns:
            True if navigation successful, False otherwise
        """
        session = self.get_current_session()
        if not session:
            return False

        success = session.go_back()

        if success and STREAMLIT_AVAILABLE:
            st.session_state.current_page = session.current_page
            st.session_state.page_params = session.page_params

            # Persist navigation state
            self.persistence_engine.persist_session(
                session, immediate=False
            )

        return success

    def invalidate_cache(self, pattern: str | None = None) -> None:
        """
        Invalidate cache keys.

        Args:
            pattern: Optional pattern to match keys
        """
        session = self.get_current_session()
        if not session:
            return

        invalidated = session.invalidate_cache_keys(pattern)

        logger.info(
            "Cache invalidated",
            pattern=pattern,
            count=len(invalidated),
        )

    def cleanup_session(self) -> None:
        """Clean up current session"""
        if not STREAMLIT_AVAILABLE:
            return

        session = self.get_current_session()
        if session:
            # Flush any pending writes
            self.persistence_engine.flush_all()

            # Clear from session_state
            if "user_session" in st.session_state:
                del st.session_state.user_session

            logger.info(
                "Session cleaned up",
                session_id=session.session_id,
            )


# Global session manager instance
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def bootstrap_session(
    session_id: str | None = None, user_id: str | None = None
) -> UserSession:
    """
    Initialize or recover user session.

    This is the main entry point for session management.
    Call this at the start of your Streamlit app.

    Args:
        session_id: Optional session ID to recover
        user_id: Optional user ID for new sessions

    Returns:
        UserSession: Initialized or recovered session

    Example:
        ```python
        import streamlit as st
        from core.session_manager import bootstrap_session

        # At the start of your app
        session = bootstrap_session()

        # Access session data
        st.write(f"Current page: {session.current_page}")
        ```
    """
    manager = get_session_manager()
    return manager.bootstrap_session(session_id, user_id)


def persist_input(
    key: str,
    value: Any,
    form_id: str | None = None,
    immediate: bool = False,
) -> None:
    """
    Persist input to session_state and database.

    Args:
        key: Widget key
        value: Widget value
        form_id: Optional form ID for grouping
        immediate: If True, write to DB immediately

    Example:
        ```python
        import streamlit as st
        from core.session_manager import persist_input

        # In your widget callback
        def on_text_change():
            persist_input("username", st.session_state.username)

        st.text_input("Username", key="username", on_change=on_text_change)
        ```
    """
    manager = get_session_manager()
    manager.persist_input(key, value, form_id, immediate)


def save_form(
    form_id: str, data: dict[str, Any], immediate: bool = True
) -> None:
    """
    Save complete form data.

    Args:
        form_id: Form identifier
        data: Form data dictionary
        immediate: If True, write immediately

    Example:
        ```python
        from core.session_manager import save_form

        # Save form data
        form_data = {
            "name": st.session_state.name,
            "email": st.session_state.email,
        }
        save_form("user_profile", form_data)
        ```
    """
    manager = get_session_manager()
    manager.save_form(form_id, data, immediate)


def get_current_session() -> UserSession | None:
    """
    Get current session.

    Returns:
        UserSession if available, None otherwise
    """
    manager = get_session_manager()
    return manager.get_current_session()
