"""Tests for Session Manager"""

import pytest

from core.session import UserSession
from core.session_manager import SessionManager


@pytest.fixture
def session_manager():
    """Create test session manager"""
    return SessionManager()


class TestSessionManager:
    """Test SessionManager (without Streamlit)"""

    def test_bootstrap_new_session(self, session_manager):
        """Test bootstrapping new session"""
        session = session_manager.bootstrap_session(user_id="test_user")

        assert session is not None
        assert session.user_id == "test_user"
        assert session.current_page == "home"

    def test_bootstrap_recover_session(self, session_manager):
        """Test recovering existing session"""
        # Create and persist session
        session1 = session_manager.bootstrap_session(user_id="test_user")
        session1.navigate_to("profile")
        session_manager.persistence_engine.persist_session(
            session1, immediate=True
        )

        # Bootstrap with same session_id
        session2 = session_manager.bootstrap_session(
            session_id=session1.session_id
        )

        assert session2 is not None
        assert session2.session_id == session1.session_id
        assert session2.current_page == "profile"

    def test_navigate_to(self, session_manager):
        """Test navigation"""
        session = session_manager.bootstrap_session()

        # Store session for testing
        session_manager._test_session = session

        # Mock get_current_session
        original_get = session_manager.get_current_session
        session_manager.get_current_session = lambda: session

        session_manager.navigate_to("settings", {"tab": "profile"})

        assert session.current_page == "settings"
        assert session.page_params["tab"] == "profile"

        # Restore
        session_manager.get_current_session = original_get

    def test_go_back(self, session_manager):
        """Test navigation back"""
        session = session_manager.bootstrap_session()

        # Mock get_current_session
        session_manager.get_current_session = lambda: session

        # Navigate
        session_manager.navigate_to("page1")
        session_manager.navigate_to("page2")

        # Go back
        success = session_manager.go_back()
        assert success
        assert session.current_page == "page1"

    def test_save_form(self, session_manager):
        """Test saving form"""
        session = session_manager.bootstrap_session()
        session_manager.get_current_session = lambda: session

        form_data = {"name": "John", "email": "john@example.com"}
        session_manager.save_form("contact_form", form_data)

        form_state = session.get_form_state("contact_form")
        assert form_state.data["name"] == "John"
        assert form_state.data["email"] == "john@example.com"
        assert not form_state.is_dirty

    def test_restore_form_state(self, session_manager):
        """Test restoring form state"""
        session = session_manager.bootstrap_session()
        session_manager.get_current_session = lambda: session

        # Save form
        form_data = {"field1": "value1", "field2": "value2"}
        session_manager.save_form("test_form", form_data)

        # Restore
        restored_data = session_manager.restore_form_state("test_form")
        assert restored_data["field1"] == "value1"
        assert restored_data["field2"] == "value2"

    def test_invalidate_cache(self, session_manager):
        """Test cache invalidation"""
        session = session_manager.bootstrap_session()
        session_manager.get_current_session = lambda: session

        # Add cache keys
        session.add_cache_key("user_data_123")
        session.add_cache_key("user_data_456")
        session.add_cache_key("profile_789")

        # Invalidate by pattern
        session_manager.invalidate_cache("user_data")

        assert "profile_789" in session.cache_keys
        assert "user_data_123" not in session.cache_keys

    def test_cleanup_session(self, session_manager):
        """Test session cleanup"""
        session = session_manager.bootstrap_session()

        # This should flush pending writes
        session_manager.cleanup_session()

        # Verify no errors
        assert True


class TestSessionManagerFunctions:
    """Test module-level functions"""

    def test_bootstrap_session_function(self):
        """Test bootstrap_session function"""
        from core.session_manager import bootstrap_session

        session = bootstrap_session(user_id="func_test")
        assert session is not None
        assert session.user_id == "func_test"

    def test_get_current_session_function(self):
        """Test get_current_session function"""
        from core.session_manager import get_current_session

        # Without Streamlit, should return None
        session = get_current_session()
        assert session is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
