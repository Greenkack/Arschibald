"""Session Recovery System for Browser Refresh Scenarios"""

from typing import Any, Optional

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SessionRecoveryError(Exception):
    """Base exception for session recovery errors"""


class FormValidationError(SessionRecoveryError):
    """Exception raised when form validation fails during recovery"""


class NavigationRecoveryError(SessionRecoveryError):
    """Exception raised when navigation state recovery fails"""


class CacheRecoveryError(SessionRecoveryError):
    """Exception raised when cache key recovery fails"""


class SessionRecoveryManager:
    """
    Manages complete session state restoration after browser refresh

    This class handles:
    - Session state restoration from database
    - Form data recovery with validation
    - Navigation state restoration with parameter preservation
    - Cache key restoration for performance optimization
    """

    def __init__(self):
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        self.validation_errors = {}

    def recover_complete_session(
        self,
        session_id: str = None,
        user_id: str = None,
        validate_forms: bool = True
    ) -> Optional['UserSession']:
        """
        Recover complete session state after browser refresh

        Args:
            session_id: Optional session ID to recover
            user_id: Optional user ID for recovery
            validate_forms: If True, validate form data during recovery

        Returns:
            Recovered UserSession or None if recovery fails

        Raises:
            SessionRecoveryError: If recovery fails after max attempts
        """
        from .session import bootstrap_session
        from .session_repository import SessionRepository

        # Try to get session ID from Streamlit query params or session_state
        if not session_id and STREAMLIT_AVAILABLE and st:
            # Check query parameters first
            try:
                query_params = st.query_params
                if 'session_id' in query_params:
                    session_id = query_params['session_id']
            except Exception as e:
                logger.debug("Could not read query params", error=str(e))

            # Check session_state
            if not session_id and hasattr(st, 'session_state'):
                session_id = st.session_state.get('_session_id')

        # If no session ID, try to recover by user_id
        if not session_id and user_id:
            try:
                repo = SessionRepository()
                session_data = repo.get_session_by_user(user_id)
                if session_data:
                    session_id = session_data.get('session_id')
            except Exception as e:
                logger.warning(
                    "Failed to recover session by user_id",
                    error=str(e))

        # If still no session ID, create new session
        if not session_id:
            logger.info("No session ID found, creating new session")
            return bootstrap_session(user_id=user_id)

        # Attempt recovery with retry logic
        for attempt in range(self.max_recovery_attempts):
            try:
                self.recovery_attempts = attempt + 1

                # Recover session from database
                session = self._recover_from_database(session_id)

                if not session:
                    logger.warning(
                        "Session not found in database",
                        session_id=session_id,
                        attempt=attempt + 1
                    )
                    if attempt == self.max_recovery_attempts - 1:
                        # Last attempt failed, create new session
                        return bootstrap_session(
                            session_id=session_id, user_id=user_id)
                    continue

                # Recover form data with validation
                if validate_forms:
                    self._recover_and_validate_forms(session)

                # Recover navigation state
                self._recover_navigation_state(session)

                # Recover cache keys
                self._recover_cache_keys(session)

                # Store recovered session in session_state
                if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
                    st.session_state.user_session = session
                    st.session_state._session_id = session.session_id

                logger.info(
                    "Session recovered successfully",
                    session_id=session_id,
                    attempt=attempt + 1
                )

                return session

            except Exception as e:
                logger.error(
                    "Session recovery attempt failed",
                    session_id=session_id,
                    attempt=attempt + 1,
                    error=str(e)
                )

                if attempt == self.max_recovery_attempts - 1:
                    raise SessionRecoveryError(
                        f"Failed to recover session after {
                            self.max_recovery_attempts} attempts: {
                            str(e)}")

        return None

    def _recover_from_database(
            self, session_id: str) -> Optional['UserSession']:
        """
        Recover session from database

        Args:
            session_id: Session ID to recover

        Returns:
            UserSession instance or None
        """
        from .session import UserSession
        from .session_repository import SessionRepository

        try:
            repo = SessionRepository()
            session_data = repo.get_session(session_id)

            if not session_data:
                return None

            session = UserSession.from_dict(session_data)
            logger.debug(
                "Session data recovered from database",
                session_id=session_id)

            return session

        except Exception as e:
            logger.error(
                "Failed to recover session from database",
                session_id=session_id,
                error=str(e)
            )
            raise SessionRecoveryError(f"Database recovery failed: {str(e)}")

    def _recover_and_validate_forms(self, session: 'UserSession') -> None:
        """
        Recover and validate form data

        Args:
            session: UserSession instance

        Raises:
            FormValidationError: If form validation fails
        """
        self.validation_errors = {}

        for form_id, form_state in session.form_states.items():
            try:
                # Validate form data if schema is available
                if form_state.validation_schema:
                    errors = self._validate_form_data(
                        form_state.data,
                        form_state.validation_schema
                    )

                    if errors:
                        self.validation_errors[form_id] = errors
                        form_state.errors = errors
                        logger.warning(
                            "Form validation errors during recovery",
                            form_id=form_id,
                            errors=errors
                        )

                # Restore form to session_state if Streamlit is available
                if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
                    for key, value in form_state.data.items():
                        st.session_state[f"{form_id}_{key}"] = value

                logger.debug("Form data recovered", form_id=form_id)

            except Exception as e:
                error_msg = f"Failed to recover form {form_id}: {str(e)}"
                self.validation_errors[form_id] = [error_msg]
                logger.error(
                    "Form recovery failed",
                    form_id=form_id,
                    error=str(e))

        if self.validation_errors:
            logger.warning(
                "Form validation errors detected during recovery",
                error_count=len(self.validation_errors)
            )

    def _validate_form_data(
        self,
        data: dict[str, Any],
        schema: dict[str, Any]
    ) -> dict[str, list[str]]:
        """
        Validate form data against schema

        Args:
            data: Form data to validate
            schema: Validation schema

        Returns:
            Dictionary of field errors
        """
        errors = {}

        for field, rules in schema.items():
            value = data.get(field)
            field_errors = []

            # Required field validation
            if rules.get('required') and not value:
                field_errors.append(f"{field} is required")

            # Type validation
            if value and 'type' in rules:
                expected_type = rules['type']
                if expected_type == 'string' and not isinstance(value, str):
                    field_errors.append(f"{field} must be a string")
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    field_errors.append(f"{field} must be a number")
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    field_errors.append(f"{field} must be a boolean")

            # Min/max validation for numbers
            if value and isinstance(value, (int, float)):
                if 'min' in rules and value < rules['min']:
                    field_errors.append(
                        f"{field} must be at least {
                            rules['min']}")
                if 'max' in rules and value > rules['max']:
                    field_errors.append(
                        f"{field} must be at most {
                            rules['max']}")

            # Length validation for strings
            if value and isinstance(value, str):
                if 'minLength' in rules and len(value) < rules['minLength']:
                    field_errors.append(
                        f"{field} must be at least {
                            rules['minLength']} characters")
                if 'maxLength' in rules and len(value) > rules['maxLength']:
                    field_errors.append(
                        f"{field} must be at most {
                            rules['maxLength']} characters")

            if field_errors:
                errors[field] = field_errors

        return errors

    def _recover_navigation_state(self, session: 'UserSession') -> None:
        """
        Recover navigation state with parameter preservation

        Args:
            session: UserSession instance

        Raises:
            NavigationRecoveryError: If navigation recovery fails
        """
        try:
            # Restore current page and params to session_state
            if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
                st.session_state.current_page = session.current_page
                st.session_state.page_params = session.page_params

                # Restore navigation history
                st.session_state.navigation_history = session.navigation_history

                # Update query params if available
                try:
                    if session.page_params:
                        st.query_params.update(session.page_params)
                except Exception as e:
                    logger.debug("Could not update query params", error=str(e))

            logger.debug(
                "Navigation state recovered",
                current_page=session.current_page,
                params_count=len(session.page_params)
            )

        except Exception as e:
            logger.error("Navigation state recovery failed", error=str(e))
            raise NavigationRecoveryError(
                f"Failed to recover navigation state: {str(e)}")

    def _recover_cache_keys(self, session: 'UserSession') -> None:
        """
        Recover cache keys for performance optimization

        Args:
            session: UserSession instance

        Raises:
            CacheRecoveryError: If cache recovery fails
        """
        try:
            # Restore cache keys to session_state
            if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
                st.session_state.cache_keys = session.cache_keys
                st.session_state.cache_dependencies = session.cache_dependencies

            logger.debug(
                "Cache keys recovered",
                cache_key_count=len(session.cache_keys),
                dependency_count=len(session.cache_dependencies)
            )

        except Exception as e:
            logger.error("Cache key recovery failed", error=str(e))
            raise CacheRecoveryError(f"Failed to recover cache keys: {str(e)}")

    def get_recovery_status(self) -> dict[str, Any]:
        """
        Get recovery status information

        Returns:
            Dictionary with recovery status
        """
        return {
            'recovery_attempts': self.recovery_attempts,
            'max_attempts': self.max_recovery_attempts,
            'validation_errors': self.validation_errors,
            'has_errors': len(self.validation_errors) > 0
        }

    def clear_validation_errors(self) -> None:
        """Clear validation errors"""
        self.validation_errors = {}


# Global recovery manager instance
_recovery_manager: SessionRecoveryManager | None = None


def get_recovery_manager() -> SessionRecoveryManager:
    """Get global session recovery manager"""
    global _recovery_manager
    if _recovery_manager is None:
        _recovery_manager = SessionRecoveryManager()
    return _recovery_manager


def recover_session_after_refresh(
    session_id: str = None,
    user_id: str = None,
    validate_forms: bool = True
) -> Optional['UserSession']:
    """
    Recover session after browser refresh

    This is the main entry point for session recovery.

    Args:
        session_id: Optional session ID to recover
        user_id: Optional user ID for recovery
        validate_forms: If True, validate form data during recovery

    Returns:
        Recovered UserSession or None
    """
    manager = get_recovery_manager()
    return manager.recover_complete_session(
        session_id=session_id,
        user_id=user_id,
        validate_forms=validate_forms
    )


def get_recovery_status() -> dict[str, Any]:
    """
    Get current recovery status

    Returns:
        Dictionary with recovery status information
    """
    manager = get_recovery_manager()
    return manager.get_recovery_status()


def clear_recovery_errors() -> None:
    """Clear recovery validation errors"""
    manager = get_recovery_manager()
    manager.clear_validation_errors()


def ensure_session_persistence() -> None:
    """
    Ensure session ID is persisted for recovery

    This function should be called on every page to ensure
    the session ID is available for recovery after refresh.
    """
    if not STREAMLIT_AVAILABLE or not st or not hasattr(st, 'session_state'):
        return

    # Get or create session
    from .session import get_current_session
    session = get_current_session()

    # Store session ID in session_state
    st.session_state._session_id = session.session_id

    # Update query params with session ID
    try:
        current_params = dict(st.query_params)
        if 'session_id' not in current_params:
            st.query_params['session_id'] = session.session_id
    except Exception as e:
        logger.debug(
            "Could not update query params with session_id",
            error=str(e))
