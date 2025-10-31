"""Tests for Session Persistence Engine"""

import time
from datetime import datetime, timedelta

import pytest

from core.database import DatabaseManager
from core.session import UserSession
from core.session_persistence import (
    DebouncedWriter,
    SessionModel,
    SessionPersistenceEngine,
)


@pytest.fixture
def db_manager():
    """Create test database manager"""
    db = DatabaseManager()
    db.engine.execute("DROP TABLE IF EXISTS user_sessions")
    SessionModel.__table__.create(db.engine, checkfirst=True)
    yield db
    db.engine.execute("DROP TABLE IF EXISTS user_sessions")


@pytest.fixture
def persistence_engine(db_manager):
    """Create test persistence engine"""
    return SessionPersistenceEngine(
        db_manager=db_manager, debounce_delay=0.1, session_timeout=3600
    )


class TestDebouncedWriter:
    """Test DebouncedWriter"""

    def test_schedule_write(self):
        """Test scheduling writes"""
        writer = DebouncedWriter(delay_seconds=0.1)
        results = []

        def write_fn(value):
            results.append(value)

        writer.schedule_write("key1", write_fn, "value1")
        time.sleep(0.2)

        assert len(results) == 1
        assert results[0] == "value1"

    def test_debouncing(self):
        """Test that rapid writes are debounced"""
        writer = DebouncedWriter(delay_seconds=0.2)
        results = []

        def write_fn(value):
            results.append(value)

        # Schedule multiple writes rapidly
        writer.schedule_write("key1", write_fn, "value1")
        time.sleep(0.05)
        writer.schedule_write("key1", write_fn, "value2")
        time.sleep(0.05)
        writer.schedule_write("key1", write_fn, "value3")

        # Wait for debounce
        time.sleep(0.3)

        # Should only execute last write
        assert len(results) == 1
        assert results[0] == "value3"

    def test_flush(self):
        """Test immediate flush"""
        writer = DebouncedWriter(delay_seconds=1.0)
        results = []

        def write_fn(value):
            results.append(value)

        writer.schedule_write("key1", write_fn, "value1")
        writer.flush("key1")

        # Should execute immediately
        assert len(results) == 1
        assert results[0] == "value1"

    def test_flush_all(self):
        """Test flushing all pending writes"""
        writer = DebouncedWriter(delay_seconds=1.0)
        results = []

        def write_fn(value):
            results.append(value)

        writer.schedule_write("key1", write_fn, "value1")
        writer.schedule_write("key2", write_fn, "value2")
        writer.flush()

        assert len(results) == 2
        assert "value1" in results
        assert "value2" in results

    def test_cancel(self):
        """Test canceling pending write"""
        writer = DebouncedWriter(delay_seconds=0.1)
        results = []

        def write_fn(value):
            results.append(value)

        writer.schedule_write("key1", write_fn, "value1")
        writer.cancel("key1")
        time.sleep(0.2)

        # Should not execute
        assert len(results) == 0


class TestSessionPersistenceEngine:
    """Test SessionPersistenceEngine"""

    def test_persist_session_immediate(self, persistence_engine):
        """Test immediate session persistence"""
        session = UserSession(user_id="test_user")
        session.navigate_to("profile")

        persistence_engine.persist_session(session, immediate=True)

        # Verify in database
        recovered = persistence_engine.recover_session(session.session_id)
        assert recovered is not None
        assert recovered.user_id == "test_user"
        assert recovered.current_page == "profile"

    def test_persist_session_debounced(self, persistence_engine):
        """Test debounced session persistence"""
        session = UserSession(user_id="test_user")

        persistence_engine.persist_session(session, immediate=False)

        # Should not be in database yet
        time.sleep(0.05)
        recovered = persistence_engine.recover_session(session.session_id)
        assert recovered is None

        # Wait for debounce
        time.sleep(0.15)
        recovered = persistence_engine.recover_session(session.session_id)
        assert recovered is not None

    def test_update_existing_session(self, persistence_engine):
        """Test updating existing session"""
        session = UserSession(user_id="test_user")

        # Initial persist
        persistence_engine.persist_session(session, immediate=True)

        # Update session
        session.navigate_to("settings")
        persistence_engine.persist_session(session, immediate=True)

        # Verify update
        recovered = persistence_engine.recover_session(session.session_id)
        assert recovered.current_page == "settings"

    def test_recover_nonexistent_session(self, persistence_engine):
        """Test recovering non-existent session"""
        recovered = persistence_engine.recover_session("nonexistent")
        assert recovered is None

    def test_recover_expired_session(self, persistence_engine):
        """Test recovering expired session"""
        # Create engine with very short timeout
        short_timeout_engine = SessionPersistenceEngine(
            db_manager=persistence_engine.db_manager,
            debounce_delay=0.1,
            session_timeout=1,
        )

        session = UserSession(user_id="test_user")
        short_timeout_engine.persist_session(session, immediate=True)

        # Wait for expiration
        time.sleep(2)

        # Should return None for expired session
        recovered = short_timeout_engine.recover_session(session.session_id)
        assert recovered is None

    def test_recover_user_sessions(self, persistence_engine):
        """Test recovering all sessions for a user"""
        # Create multiple sessions for same user
        session1 = UserSession(user_id="user123")
        session2 = UserSession(user_id="user123")
        session3 = UserSession(user_id="user456")

        persistence_engine.persist_session(session1, immediate=True)
        persistence_engine.persist_session(session2, immediate=True)
        persistence_engine.persist_session(session3, immediate=True)

        # Recover sessions for user123
        sessions = persistence_engine.recover_user_sessions("user123")
        assert len(sessions) == 2

        session_ids = {s.session_id for s in sessions}
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids

    def test_delete_session(self, persistence_engine):
        """Test deleting session"""
        session = UserSession(user_id="test_user")
        persistence_engine.persist_session(session, immediate=True)

        # Delete session
        success = persistence_engine.delete_session(session.session_id)
        assert success

        # Verify deletion
        recovered = persistence_engine.recover_session(session.session_id)
        assert recovered is None

    def test_cleanup_expired_sessions(self, persistence_engine):
        """Test cleaning up expired sessions"""
        # Create engine with short timeout
        short_timeout_engine = SessionPersistenceEngine(
            db_manager=persistence_engine.db_manager,
            debounce_delay=0.1,
            session_timeout=1,
        )

        # Create sessions
        session1 = UserSession(user_id="user1")
        session2 = UserSession(user_id="user2")

        short_timeout_engine.persist_session(session1, immediate=True)
        short_timeout_engine.persist_session(session2, immediate=True)

        # Wait for expiration
        time.sleep(2)

        # Cleanup
        count = short_timeout_engine.cleanup_expired_sessions()
        assert count == 2

    def test_cleanup_inactive_sessions(self, persistence_engine):
        """Test cleaning up inactive sessions"""
        session = UserSession(user_id="test_user")
        persistence_engine.persist_session(session, immediate=True)

        # Manually update last_activity to old date
        with persistence_engine.db_manager.session_scope() as db_session:
            session_model = (
                db_session.query(SessionModel)
                .filter(SessionModel.session_id == session.session_id)
                .first()
            )
            session_model.last_activity = datetime.now() - timedelta(days=10)

        # Cleanup sessions inactive for 7 days
        count = persistence_engine.cleanup_inactive_sessions(inactive_days=7)
        assert count == 1

    def test_get_session_count(self, persistence_engine):
        """Test getting session count"""
        # Create sessions
        session1 = UserSession(user_id="user1")
        session2 = UserSession(user_id="user2")

        persistence_engine.persist_session(session1, immediate=True)
        persistence_engine.persist_session(session2, immediate=True)

        count = persistence_engine.get_session_count()
        assert count == 2

    def test_flush_all(self, persistence_engine):
        """Test flushing all pending writes"""
        session1 = UserSession(user_id="user1")
        session2 = UserSession(user_id="user2")

        # Schedule debounced writes
        persistence_engine.persist_session(session1, immediate=False)
        persistence_engine.persist_session(session2, immediate=False)

        # Flush immediately
        persistence_engine.flush_all()

        # Verify both are persisted
        recovered1 = persistence_engine.recover_session(session1.session_id)
        recovered2 = persistence_engine.recover_session(session2.session_id)

        assert recovered1 is not None
        assert recovered2 is not None

    def test_session_data_integrity(self, persistence_engine):
        """Test that all session data is preserved"""
        session = UserSession(user_id="test_user")

        # Add comprehensive data
        session.navigate_to("profile", {"id": "123"})
        session.update_form_data("form1", "field1", "value1")
        session.add_role("admin")
        session.add_permission("write")
        session.add_cache_key("cache1")
        session.create_form_snapshot("form1", "Test snapshot")

        # Persist and recover
        persistence_engine.persist_session(session, immediate=True)
        recovered = persistence_engine.recover_session(session.session_id)

        # Verify all data
        assert recovered.current_page == "profile"
        assert recovered.page_params["id"] == "123"
        assert "form1" in recovered.form_states
        assert recovered.form_states["form1"].data["field1"] == "value1"
        assert recovered.has_role("admin")
        assert recovered.has_permission("write")
        assert "cache1" in recovered.cache_keys
        assert len(recovered.form_snapshots["form1"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
