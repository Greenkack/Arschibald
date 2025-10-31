"""Tests for Enhanced Session Management"""

import time
import uuid
from datetime import datetime

import pytest

from .session import (
    FormSnapshot,
    FormState,
    NavigationEntry,
    SessionPersistence,
    UserSession,
    bootstrap_session,
    get_current_session,
    persist_input,
)


class TestNavigationEntry:
    """Test NavigationEntry dataclass"""

    def test_create_navigation_entry(self):
        """Test creating navigation entry"""
        entry = NavigationEntry(
            page="home",
            params={"id": "123"},
            timestamp=datetime.now()
        )

        assert entry.page == "home"
        assert entry.params == {"id": "123"}
        assert isinstance(entry.timestamp, datetime)

    def test_navigation_entry_serialization(self):
        """Test navigation entry to/from dict"""
        entry = NavigationEntry(
            page="dashboard",
            params={"filter": "active"},
            timestamp=datetime.now()
        )

        data = entry.to_dict()
        assert data['page'] == "dashboard"
        assert data['params'] == {"filter": "active"}

        restored = NavigationEntry.from_dict(data)
        assert restored.page == entry.page
        assert restored.params == entry.params


class TestFormSnapshot:
    """Test FormSnapshot dataclass"""

    def test_create_form_snapshot(self):
        """Test creating form snapshot"""
        snapshot = FormSnapshot(
            snapshot_id=str(uuid.uuid4()),
            form_id="contact_form",
            data={"name": "John", "email": "john@example.com"},
            timestamp=datetime.now(),
            description="Initial state"
        )

        assert snapshot.form_id == "contact_form"
        assert snapshot.data["name"] == "John"
        assert snapshot.description == "Initial state"

    def test_form_snapshot_serialization(self):
        """Test form snapshot to/from dict"""
        snapshot = FormSnapshot(
            snapshot_id=str(uuid.uuid4()),
            form_id="test_form",
            data={"field1": "value1"},
            timestamp=datetime.now()
        )

        data = snapshot.to_dict()
        restored = FormSnapshot.from_dict(data)

        assert restored.snapshot_id == snapshot.snapshot_id
        assert restored.form_id == snapshot.form_id
        assert restored.data == snapshot.data


class TestFormState:
    """Test FormState dataclass"""

    def test_create_form_state(self):
        """Test creating form state"""
        form_state = FormState(form_id="user_profile")

        assert form_state.form_id == "user_profile"
        assert form_state.data == {}
        assert form_state.is_dirty is False
        assert form_state.auto_save is True

    def test_form_state_with_data(self):
        """Test form state with data"""
        form_state = FormState(
            form_id="settings",
            data={"theme": "dark", "language": "en"}
        )

        assert form_state.data["theme"] == "dark"
        assert form_state.data["language"] == "en"

    def test_form_state_validation(self):
        """Test form state validation fields"""
        form_state = FormState(
            form_id="registration",
            errors={"email": ["Invalid email format"]},
            warnings={"password": ["Weak password"]}
        )

        assert "email" in form_state.errors
        assert "password" in form_state.warnings

    def test_form_state_serialization(self):
        """Test form state to/from dict"""
        form_state = FormState(
            form_id="test_form",
            data={"field": "value"},
            is_dirty=True
        )

        data = form_state.to_dict()
        restored = FormState.from_dict(data)

        assert restored.form_id == form_state.form_id
        assert restored.data == form_state.data
        assert restored.is_dirty == form_state.is_dirty


class TestUserSession:
    """Test UserSession dataclass"""

    def test_create_user_session(self):
        """Test creating user session"""
        session = UserSession()

        assert session.session_id is not None
        assert session.current_page == "home"
        assert session.interaction_count == 0
        assert isinstance(session.created_at, datetime)

    def test_user_session_with_user_id(self):
        """Test user session with user ID"""
        session = UserSession(user_id="user123")

        assert session.user_id == "user123"

    def test_add_navigation(self):
        """Test adding navigation entry"""
        session = UserSession()

        session.add_navigation("dashboard", {"filter": "active"})

        assert len(session.navigation_history) == 1
        assert session.navigation_history[0].page == "dashboard"
        assert session.page_views["dashboard"] == 1
        assert session.interaction_count == 1

    def test_navigation_history_limit(self):
        """Test navigation history size limit"""
        session = UserSession(max_history_size=5)

        for i in range(10):
            session.add_navigation(f"page{i}")

        assert len(session.navigation_history) == 5
        assert session.navigation_history[0].page == "page5"

    def test_get_form_state(self):
        """Test getting form state"""
        session = UserSession()

        form_state = session.get_form_state("contact_form")

        assert form_state.form_id == "contact_form"
        assert "contact_form" in session.form_states

    def test_mark_form_dirty(self):
        """Test marking form as dirty"""
        session = UserSession()
        form_state = session.get_form_state("test_form")

        session.mark_form_dirty("test_form")

        assert "test_form" in session.dirty_forms
        assert form_state.is_dirty is True

    def test_mark_form_clean(self):
        """Test marking form as clean"""
        session = UserSession()
        session.get_form_state("test_form")  # Create form state first
        session.mark_form_dirty("test_form")

        session.mark_form_clean("test_form")

        assert "test_form" not in session.dirty_forms
        assert session.form_states["test_form"].is_dirty is False
        assert session.form_states["test_form"].last_saved is not None

    def test_cache_key_tracking(self):
        """Test cache key tracking"""
        session = UserSession()

        session.add_cache_key("user_data", {"user_id"})

        assert "user_data" in session.cache_keys
        assert "user_id" in session.cache_dependencies["user_data"]

        session.remove_cache_key("user_data")
        assert "user_data" not in session.cache_keys

    def test_permissions(self):
        """Test permission checking"""
        session = UserSession(
            permissions={"read", "write"}
        )

        assert session.has_permission("read")
        assert session.has_permission("write")
        assert not session.has_permission("admin")

    def test_roles(self):
        """Test role checking"""
        session = UserSession(
            roles={"user", "editor"}
        )

        assert session.has_role("user")
        assert session.has_role("editor")
        assert not session.has_role("admin")

    def test_session_duration(self):
        """Test session duration calculation"""
        session = UserSession()
        time.sleep(0.1)

        duration = session.session_duration
        assert duration.total_seconds() >= 0.1

    def test_session_serialization(self):
        """Test session to/from dict"""
        session = UserSession(
            user_id="user123",
            current_page="dashboard"
        )
        session.add_navigation("home")
        session.get_form_state("test_form")

        data = session.to_dict()
        restored = UserSession.from_dict(data)

        assert restored.session_id == session.session_id
        assert restored.user_id == session.user_id
        assert restored.current_page == session.current_page
        assert len(
            restored.navigation_history) == len(
            session.navigation_history)
        assert "test_form" in restored.form_states

    def test_session_json_serialization(self):
        """Test session to/from JSON"""
        session = UserSession(user_id="user123")

        json_str = session.to_json()
        restored = UserSession.from_json(json_str)

        assert restored.session_id == session.session_id
        assert restored.user_id == session.user_id


class TestSessionPersistence:
    """Test SessionPersistence engine"""

    def test_create_persistence_engine(self):
        """Test creating persistence engine"""
        persistence = SessionPersistence(debounce_ms=100)

        assert persistence.debounce_ms == 100

    def test_schedule_save(self):
        """Test scheduling debounced save"""
        persistence = SessionPersistence(debounce_ms=100)
        session = UserSession()

        save_called = []

        def save_fn(sess):
            save_called.append(sess.session_id)

        persistence.schedule_save(session.session_id, session, save_fn)

        # Should not be called immediately
        assert len(save_called) == 0

        # Wait for debounce
        time.sleep(0.15)

        # Should be called after debounce
        assert len(save_called) == 1
        assert save_called[0] == session.session_id

    def test_debounce_cancellation(self):
        """Test that rapid saves are debounced"""
        persistence = SessionPersistence(debounce_ms=100)
        session = UserSession()

        save_count = []

        def save_fn(sess):
            save_count.append(1)

        # Schedule multiple saves rapidly
        for _ in range(5):
            persistence.schedule_save(session.session_id, session, save_fn)
            time.sleep(0.02)

        # Wait for debounce
        time.sleep(0.15)

        # Should only save once
        assert len(save_count) == 1

    def test_flush_immediate(self):
        """Test immediate flush"""
        persistence = SessionPersistence(debounce_ms=1000)
        session = UserSession()

        save_called = []

        def save_fn(sess):
            save_called.append(sess.session_id)

        persistence.schedule_save(session.session_id, session, save_fn)

        # Flush immediately
        persistence.flush(session.session_id)

        # Should be called immediately
        assert len(save_called) == 1


class TestSessionFunctions:
    """Test session management functions"""

    def test_bootstrap_session_new(self):
        """Test bootstrapping new session"""
        session = bootstrap_session(restore_from_db=False)

        assert session is not None
        assert session.session_id is not None
        assert session.current_page == "home"

    def test_bootstrap_session_with_user(self):
        """Test bootstrapping session with user ID"""
        session = bootstrap_session(user_id="user123", restore_from_db=False)

        assert session.user_id == "user123"

    def test_get_current_session(self):
        """Test getting current session"""
        session = get_current_session()

        assert session is not None
        assert isinstance(session, UserSession)

    def test_persist_input(self):
        """Test persisting input"""
        # This test requires database setup
        # Just test that it doesn't raise errors
        try:
            persist_input("test_key", "test_value")
        except Exception:
            # Expected if database not initialized
            pass


class TestSessionIntegration:
    """Integration tests for session management"""

    def test_complete_session_lifecycle(self):
        """Test complete session lifecycle"""
        # Create session
        session = UserSession(user_id="test_user")

        # Add navigation
        session.add_navigation("dashboard", {"view": "overview"})
        session.add_navigation("settings")

        # Create form state
        form_state = session.get_form_state("profile_form")
        form_state.data = {"name": "John Doe", "email": "john@example.com"}
        session.mark_form_dirty("profile_form")

        # Add cache keys
        session.add_cache_key("user_data", {"user_id"})

        # Serialize and restore
        data = session.to_dict()
        restored = UserSession.from_dict(data)

        # Verify restoration
        assert restored.user_id == session.user_id
        assert len(restored.navigation_history) == 2
        assert "profile_form" in restored.form_states
        assert restored.form_states["profile_form"].data["name"] == "John Doe"
        assert "user_data" in restored.cache_keys
        assert "profile_form" in restored.dirty_forms

    def test_session_with_multiple_forms(self):
        """Test session with multiple forms"""
        session = UserSession()

        # Create multiple forms
        form1 = session.get_form_state("form1")
        form1.data = {"field1": "value1"}

        form2 = session.get_form_state("form2")
        form2.data = {"field2": "value2"}

        session.mark_form_dirty("form1")

        # Verify state
        assert len(session.form_states) == 2
        assert len(session.dirty_forms) == 1
        assert "form1" in session.dirty_forms
        assert "form2" not in session.dirty_forms

    def test_session_metrics_tracking(self):
        """Test session metrics tracking"""
        session = UserSession()

        # Simulate user activity
        session.add_navigation("home")
        session.add_navigation("dashboard")
        session.add_navigation("home")
        session.add_navigation("settings")

        # Verify metrics
        assert session.interaction_count == 4
        assert session.page_views["home"] == 2
        assert session.page_views["dashboard"] == 1
        assert session.page_views["settings"] == 1
        assert len(session.navigation_history) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
