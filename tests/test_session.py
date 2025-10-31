"""Tests for Session Management System"""

import json
import time
import uuid
from datetime import datetime, timedelta

import pytest

from core.session import (
    FormSnapshot,
    FormState,
    NavigationEntry,
    SessionMetrics,
    UserPreferences,
    UserSession,
)


class TestNavigationEntry:
    """Test NavigationEntry"""

    def test_create_navigation_entry(self):
        """Test creating navigation entry"""
        entry = NavigationEntry(
            page="home",
            params={"id": "123"},
            timestamp=datetime.now(),
            scroll_position=100,
        )

        assert entry.page == "home"
        assert entry.params == {"id": "123"}
        assert entry.scroll_position == 100

    def test_navigation_entry_serialization(self):
        """Test navigation entry serialization"""
        entry = NavigationEntry(
            page="profile",
            params={"user_id": "456"},
            timestamp=datetime.now(),
        )

        # Serialize
        data = entry.to_dict()
        assert data["page"] == "profile"
        assert data["params"] == {"user_id": "456"}

        # Deserialize
        restored = NavigationEntry.from_dict(data)
        assert restored.page == entry.page
        assert restored.params == entry.params


class TestFormSnapshot:
    """Test FormSnapshot"""

    def test_create_form_snapshot(self):
        """Test creating form snapshot"""
        snapshot = FormSnapshot(
            snapshot_id=str(uuid.uuid4()),
            form_id="user_form",
            data={"name": "John", "email": "john@example.com"},
            timestamp=datetime.now(),
            description="Initial save",
        )

        assert snapshot.form_id == "user_form"
        assert snapshot.data["name"] == "John"
        assert snapshot.description == "Initial save"

    def test_form_snapshot_serialization(self):
        """Test form snapshot serialization"""
        snapshot = FormSnapshot(
            snapshot_id=str(uuid.uuid4()),
            form_id="test_form",
            data={"field1": "value1"},
            timestamp=datetime.now(),
        )

        # Serialize
        data = snapshot.to_dict()
        assert data["form_id"] == "test_form"

        # Deserialize
        restored = FormSnapshot.from_dict(data)
        assert restored.form_id == snapshot.form_id
        assert restored.data == snapshot.data


class TestFormState:
    """Test FormState"""

    def test_create_form_state(self):
        """Test creating form state"""
        form_state = FormState(
            form_id="contact_form",
            data={"name": "Alice", "message": "Hello"},
        )

        assert form_state.form_id == "contact_form"
        assert form_state.data["name"] == "Alice"
        assert not form_state.is_dirty
        assert form_state.version == 1

    def test_form_state_serialization(self):
        """Test form state serialization"""
        form_state = FormState(
            form_id="test_form",
            data={"field": "value"},
            is_dirty=True,
        )

        # Serialize
        data = form_state.to_dict()
        assert data["form_id"] == "test_form"
        assert data["is_dirty"] is True

        # Deserialize
        restored = FormState.from_dict(data)
        assert restored.form_id == form_state.form_id
        assert restored.is_dirty == form_state.is_dirty


class TestUserPreferences:
    """Test UserPreferences"""

    def test_default_preferences(self):
        """Test default preferences"""
        prefs = UserPreferences()

        assert prefs.theme == "auto"
        assert prefs.language == "en"
        assert prefs.timezone == "UTC"
        assert prefs.auto_save is True

    def test_preferences_serialization(self):
        """Test preferences serialization"""
        prefs = UserPreferences(
            theme="dark", language="de", auto_save_interval=60
        )

        # Serialize
        data = prefs.to_dict()
        assert data["theme"] == "dark"
        assert data["language"] == "de"

        # Deserialize
        restored = UserPreferences.from_dict(data)
        assert restored.theme == prefs.theme
        assert restored.language == prefs.language


class TestSessionMetrics:
    """Test SessionMetrics"""

    def test_record_page_view(self):
        """Test recording page views"""
        metrics = SessionMetrics()

        metrics.record_page_view("home")
        metrics.record_page_view("profile")
        metrics.record_page_view("home")

        assert metrics.page_views["home"] == 2
        assert metrics.page_views["profile"] == 1

    def test_record_interaction(self):
        """Test recording interactions"""
        metrics = SessionMetrics()

        metrics.record_interaction()
        metrics.record_interaction()

        assert metrics.interaction_count == 2

    def test_session_duration(self):
        """Test session duration calculation"""
        metrics = SessionMetrics()
        time.sleep(0.1)

        duration = metrics.session_duration
        assert duration.total_seconds() >= 0.1

    def test_metrics_serialization(self):
        """Test metrics serialization"""
        metrics = SessionMetrics()
        metrics.record_page_view("test")
        metrics.record_interaction()

        # Serialize
        data = metrics.to_dict()
        assert data["page_views"]["test"] == 1
        assert data["interaction_count"] == 1

        # Deserialize
        restored = SessionMetrics.from_dict(data)
        assert restored.page_views == metrics.page_views
        assert restored.interaction_count == metrics.interaction_count


class TestUserSession:
    """Test UserSession"""

    def test_create_session(self):
        """Test creating new session"""
        session = UserSession(user_id="user123")

        assert session.session_id is not None
        assert session.user_id == "user123"
        assert session.current_page == "home"
        assert len(session.navigation_history) == 0

    def test_navigate_to(self):
        """Test navigation"""
        session = UserSession()

        session.navigate_to("profile", {"user_id": "123"})

        assert session.current_page == "profile"
        assert session.page_params["user_id"] == "123"
        assert len(session.navigation_history) == 1
        assert session.navigation_history[0].page == "home"

    def test_go_back(self):
        """Test navigation back"""
        session = UserSession()

        session.navigate_to("page1")
        session.navigate_to("page2")
        session.navigate_to("page3")

        assert session.current_page == "page3"

        success = session.go_back()
        assert success
        assert session.current_page == "page2"

        success = session.go_back()
        assert success
        assert session.current_page == "page1"

    def test_form_state_management(self):
        """Test form state management"""
        session = UserSession()

        # Update form data
        session.update_form_data("contact_form", "name", "John")
        session.update_form_data("contact_form", "email", "john@example.com")

        form_state = session.get_form_state("contact_form")
        assert form_state.data["name"] == "John"
        assert form_state.data["email"] == "john@example.com"
        assert form_state.is_dirty
        assert "contact_form" in session.dirty_forms

    def test_mark_form_saved(self):
        """Test marking form as saved"""
        session = UserSession()

        session.update_form_data("test_form", "field", "value")
        assert "test_form" in session.dirty_forms

        session.mark_form_saved("test_form")
        assert "test_form" not in session.dirty_forms

        form_state = session.get_form_state("test_form")
        assert not form_state.is_dirty
        assert form_state.last_saved is not None

    def test_form_snapshots(self):
        """Test form snapshot creation and restoration"""
        session = UserSession()

        # Create initial form data
        session.update_form_data("form1", "field1", "value1")
        snapshot1 = session.create_form_snapshot("form1", "First save")

        # Modify form
        session.update_form_data("form1", "field1", "value2")
        snapshot2 = session.create_form_snapshot("form1", "Second save")

        # Verify snapshots
        assert len(session.form_snapshots["form1"]) == 2
        assert snapshot1.data["field1"] == "value1"
        assert snapshot2.data["field1"] == "value2"

        # Restore first snapshot
        success = session.restore_form_snapshot(snapshot1.snapshot_id)
        assert success

        form_state = session.get_form_state("form1")
        assert form_state.data["field1"] == "value1"

    def test_cache_key_tracking(self):
        """Test cache key tracking"""
        session = UserSession()

        session.add_cache_key("user_data_123")
        session.add_cache_key("profile_456", {"user_data_123"})

        assert "user_data_123" in session.cache_keys
        assert "profile_456" in session.cache_keys
        assert session.cache_dependencies["profile_456"] == {"user_data_123"}

    def test_cache_invalidation(self):
        """Test cache invalidation"""
        session = UserSession()

        session.add_cache_key("user_data_123")
        session.add_cache_key("user_data_456")
        session.add_cache_key("profile_789")

        # Invalidate by pattern
        invalidated = session.invalidate_cache_keys("user_data")
        assert len(invalidated) == 2
        assert "profile_789" in session.cache_keys

        # Invalidate all
        invalidated = session.invalidate_cache_keys()
        assert len(session.cache_keys) == 0

    def test_permissions(self):
        """Test permission management"""
        session = UserSession()

        session.add_permission("read")
        session.add_permission("write")

        assert session.has_permission("read")
        assert session.has_permission("write")
        assert not session.has_permission("delete")

        session.remove_permission("write")
        assert not session.has_permission("write")

    def test_roles(self):
        """Test role management"""
        session = UserSession()

        session.add_role("user")
        session.add_role("admin")

        assert session.has_role("user")
        assert session.has_role("admin")
        assert not session.has_role("superadmin")

        session.remove_role("admin")
        assert not session.has_role("admin")

    def test_session_serialization(self):
        """Test complete session serialization"""
        session = UserSession(user_id="test_user")

        # Add some data
        session.navigate_to("profile", {"id": "123"})
        session.update_form_data("form1", "field1", "value1")
        session.add_role("user")
        session.add_permission("read")
        session.add_cache_key("cache1")

        # Serialize to dict
        data = session.to_dict()
        assert data["user_id"] == "test_user"
        assert data["current_page"] == "profile"
        assert "form1" in data["form_states"]
        assert "user" in data["roles"]
        assert "read" in data["permissions"]

        # Deserialize
        restored = UserSession.from_dict(data)
        assert restored.session_id == session.session_id
        assert restored.user_id == session.user_id
        assert restored.current_page == session.current_page
        assert restored.has_role("user")
        assert restored.has_permission("read")

    def test_session_json_serialization(self):
        """Test JSON serialization"""
        session = UserSession(user_id="json_test")
        session.navigate_to("test_page")

        # Serialize to JSON
        json_str = session.to_json()
        assert isinstance(json_str, str)

        # Deserialize from JSON
        restored = UserSession.from_json(json_str)
        assert restored.session_id == session.session_id
        assert restored.current_page == session.current_page

    def test_metrics_tracking(self):
        """Test metrics tracking"""
        session = UserSession()

        # Navigate and interact
        session.navigate_to("page1")
        session.navigate_to("page2")
        session.update_form_data("form1", "field", "value")

        # Check metrics
        assert session.metrics.page_views["page1"] == 1
        assert session.metrics.page_views["page2"] == 1
        assert session.metrics.interaction_count == 1

    def test_snapshot_limit(self):
        """Test snapshot limit enforcement"""
        session = UserSession()

        # Create more than 50 snapshots
        for i in range(60):
            session.update_form_data("form1", "field", f"value{i}")
            session.create_form_snapshot("form1", f"Snapshot {i}")

        # Should only keep last 50
        assert len(session.form_snapshots["form1"]) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
