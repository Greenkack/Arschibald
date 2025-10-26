"""Tests for Session Repository"""

import time
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .database import Base, DatabaseManager
from .session import UserSession
from .session_repository import SessionModel, SessionRepository, init_session_tables


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)

    db_manager = DatabaseManager()
    db_manager.engine = engine
    db_manager.SessionLocal = SessionLocal

    yield db_manager

    Base.metadata.drop_all(engine)


@pytest.fixture
def session_repo(test_db):
    """Create session repository with test database"""
    return SessionRepository(db_manager=test_db)


@pytest.fixture
def sample_session():
    """Create sample user session"""
    session = UserSession(user_id="test_user")
    session.add_navigation("home")
    session.add_navigation("dashboard", {"view": "overview"})

    form_state = session.get_form_state("test_form")
    form_state.data = {"field1": "value1"}
    session.mark_form_dirty("test_form")

    return session


class TestSessionModel:
    """Test SessionModel database model"""

    def test_create_session_model(self, test_db):
        """Test creating session model"""
        with test_db.session_scope() as db_session:
            session_model = SessionModel(
                session_id="test_session_123",
                user_id="user123",
                session_data='{"test": "data"}',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )

            db_session.add(session_model)
            db_session.flush()

            assert session_model.id is not None
            assert session_model.session_id == "test_session_123"
            assert session_model.user_id == "user123"

    def test_session_model_repr(self):
        """Test session model string representation"""
        session_model = SessionModel(
            session_id="test_123",
            user_id="user_456",
            session_data="{}"
        )

        repr_str = repr(session_model)
        assert "test_123" in repr_str
        assert "user_456" in repr_str


class TestSessionRepository:
    """Test SessionRepository operations"""

    def test_save_new_session(self, session_repo, sample_session):
        """Test saving new session"""
        session_repo.save_session(sample_session)

        # Retrieve and verify
        retrieved = session_repo.get_session(sample_session.session_id)

        assert retrieved is not None
        assert retrieved['session_id'] == sample_session.session_id
        assert retrieved['user_id'] == sample_session.user_id

    def test_update_existing_session(self, session_repo, sample_session):
        """Test updating existing session"""
        # Save initial session
        session_repo.save_session(sample_session)

        # Modify session
        sample_session.add_navigation("settings")
        sample_session.version = 2

        # Update
        session_repo.save_session(sample_session)

        # Retrieve and verify
        retrieved = session_repo.get_session(sample_session.session_id)

        assert retrieved is not None
        assert retrieved['version'] == 2
        assert len(retrieved['navigation_history']) == 3

    def test_get_nonexistent_session(self, session_repo):
        """Test getting nonexistent session"""
        retrieved = session_repo.get_session("nonexistent_id")

        assert retrieved is None

    def test_get_session_by_user(self, session_repo):
        """Test getting session by user ID"""
        # Create multiple sessions for same user
        session1 = UserSession(user_id="user123")
        session2 = UserSession(user_id="user123")

        session_repo.save_session(session1)
        time.sleep(0.01)  # Ensure different timestamps
        session_repo.save_session(session2)

        # Get most recent session
        retrieved = session_repo.get_session_by_user("user123")

        assert retrieved is not None
        assert retrieved['session_id'] == session2.session_id

    def test_delete_session(self, session_repo, sample_session):
        """Test deleting session"""
        # Save session
        session_repo.save_session(sample_session)

        # Delete
        result = session_repo.delete_session(sample_session.session_id)

        assert result is True

        # Verify deletion
        retrieved = session_repo.get_session(sample_session.session_id)
        assert retrieved is None

    def test_delete_nonexistent_session(self, session_repo):
        """Test deleting nonexistent session"""
        result = session_repo.delete_session("nonexistent_id")

        assert result is False

    def test_cleanup_expired_sessions(self, session_repo, test_db):
        """Test cleaning up expired sessions"""
        # Create old session
        old_session = UserSession(user_id="old_user")
        session_repo.save_session(old_session)

        # Manually set old timestamp
        with test_db.session_scope() as db_session:
            session_model = db_session.query(SessionModel).filter(
                SessionModel.session_id == old_session.session_id
            ).first()
            session_model.last_activity = datetime.utcnow() - timedelta(hours=25)

        # Create recent session
        recent_session = UserSession(user_id="recent_user")
        session_repo.save_session(recent_session)

        # Cleanup
        count = session_repo.cleanup_expired_sessions(max_age_hours=24)

        assert count == 1

        # Verify old session deleted
        assert session_repo.get_session(old_session.session_id) is None

        # Verify recent session still exists
        assert session_repo.get_session(recent_session.session_id) is not None

    def test_get_active_session_count(self, session_repo):
        """Test getting active session count"""
        # Create active sessions
        for i in range(3):
            session = UserSession(user_id=f"user{i}")
            session_repo.save_session(session)

        count = session_repo.get_active_session_count(
            active_threshold_minutes=30)

        assert count == 3

    def test_get_all_sessions(self, session_repo):
        """Test getting all sessions with pagination"""
        # Create multiple sessions
        for i in range(5):
            session = UserSession(user_id=f"user{i}")
            session_repo.save_session(session)
            time.sleep(0.01)

        # Get first page
        sessions = session_repo.get_all_sessions(limit=3, offset=0)

        assert len(sessions) == 3

        # Get second page
        sessions = session_repo.get_all_sessions(limit=3, offset=3)

        assert len(sessions) == 2

    def test_get_all_sessions_by_user(self, session_repo):
        """Test getting all sessions filtered by user"""
        # Create sessions for different users
        for i in range(3):
            session = UserSession(user_id="target_user")
            session_repo.save_session(session)

        for i in range(2):
            session = UserSession(user_id="other_user")
            session_repo.save_session(session)

        # Get sessions for target user
        sessions = session_repo.get_all_sessions(user_id="target_user")

        assert len(sessions) == 3
        for session_data in sessions:
            assert session_data['user_id'] == "target_user"

    def test_update_last_activity(self, session_repo, sample_session):
        """Test updating last activity timestamp"""
        # Save session
        session_repo.save_session(sample_session)

        # Wait a bit
        time.sleep(0.1)

        # Update activity
        result = session_repo.update_last_activity(sample_session.session_id)

        assert result is True

        # Verify update
        retrieved = session_repo.get_session(sample_session.session_id)
        original_activity = datetime.fromisoformat(
            sample_session.last_activity.isoformat())
        retrieved_activity = datetime.fromisoformat(retrieved['last_activity'])

        assert retrieved_activity > original_activity

    def test_resolve_conflict_last_write_wins_local(self, session_repo):
        """Test conflict resolution: local session wins"""
        # Create and save initial session
        session = UserSession(user_id="user123")
        session.add_navigation("home")
        session_repo.save_session(session)

        # Create local version with later timestamp
        local_session = UserSession(
            session_id=session.session_id,
            user_id="user123")
        local_session.add_navigation("dashboard")
        local_session.updated_at = datetime.utcnow() + timedelta(seconds=1)

        # Resolve conflict
        resolved = session_repo.resolve_conflict(
            session.session_id,
            local_session,
            strategy='last_write_wins'
        )

        assert resolved.session_id == local_session.session_id
        assert len(resolved.navigation_history) == 1
        assert resolved.navigation_history[0].page == "dashboard"

    def test_resolve_conflict_last_write_wins_db(self, session_repo):
        """Test conflict resolution: database session wins"""
        # Create and save initial session with later timestamp
        session = UserSession(user_id="user123")
        session.add_navigation("home")
        session.updated_at = datetime.utcnow() + timedelta(seconds=2)
        session_repo.save_session(session)

        # Create local version with earlier timestamp
        local_session = UserSession(
            session_id=session.session_id,
            user_id="user123")
        local_session.add_navigation("dashboard")
        local_session.updated_at = datetime.utcnow()

        # Resolve conflict
        resolved = session_repo.resolve_conflict(
            session.session_id,
            local_session,
            strategy='last_write_wins'
        )

        assert resolved.session_id == session.session_id
        assert len(resolved.navigation_history) == 1
        assert resolved.navigation_history[0].page == "home"

    def test_resolve_conflict_merge(self, session_repo):
        """Test conflict resolution: merge strategy"""
        # Create and save initial session
        session = UserSession(user_id="user123")
        session.add_navigation("home")
        form1 = session.get_form_state("form1")
        form1.data = {"field1": "value1"}
        session_repo.save_session(session)

        # Create local version with different changes
        local_session = UserSession(
            session_id=session.session_id,
            user_id="user123")
        local_session.add_navigation("dashboard")
        form2 = local_session.get_form_state("form2")
        form2.data = {"field2": "value2"}

        # Resolve conflict with merge
        resolved = session_repo.resolve_conflict(
            session.session_id,
            local_session,
            strategy='merge'
        )

        # Verify merge
        assert len(resolved.navigation_history) == 2
        assert "form1" in resolved.form_states
        assert "form2" in resolved.form_states
        assert resolved.version > session.version

    def test_resolve_conflict_no_conflict(self, session_repo):
        """Test conflict resolution when no DB session exists"""
        local_session = UserSession(user_id="user123")
        local_session.add_navigation("home")

        # Resolve (should just save)
        resolved = session_repo.resolve_conflict(
            local_session.session_id,
            local_session,
            strategy='last_write_wins'
        )

        assert resolved.session_id == local_session.session_id

        # Verify saved
        retrieved = session_repo.get_session(local_session.session_id)
        assert retrieved is not None


class TestSessionIntegration:
    """Integration tests for session repository"""

    def test_complete_session_persistence_cycle(self, session_repo):
        """Test complete persistence cycle"""
        # Create session
        session = UserSession(user_id="test_user")
        session.add_navigation("home")
        session.add_navigation("dashboard", {"view": "overview"})

        # Add form state
        form_state = session.get_form_state("profile_form")
        form_state.data = {"name": "John Doe", "email": "john@example.com"}
        session.mark_form_dirty("profile_form")

        # Save
        session_repo.save_session(session)

        # Retrieve
        retrieved_data = session_repo.get_session(session.session_id)
        retrieved_session = UserSession.from_dict(retrieved_data)

        # Verify
        assert retrieved_session.session_id == session.session_id
        assert retrieved_session.user_id == session.user_id
        assert len(retrieved_session.navigation_history) == 2
        assert "profile_form" in retrieved_session.form_states
        assert retrieved_session.form_states["profile_form"].data["name"] == "John Doe"
        assert "profile_form" in retrieved_session.dirty_forms

    def test_session_update_and_recovery(self, session_repo):
        """Test session update and recovery"""
        # Create and save initial session
        session = UserSession(user_id="user123")
        session.add_navigation("home")
        session_repo.save_session(session)

        # Simulate browser refresh - recover session
        recovered_data = session_repo.get_session(session.session_id)
        recovered_session = UserSession.from_dict(recovered_data)

        # Make changes
        recovered_session.add_navigation("settings")
        recovered_session.version += 1

        # Save changes
        session_repo.save_session(recovered_session)

        # Verify changes persisted
        final_data = session_repo.get_session(session.session_id)
        final_session = UserSession.from_dict(final_data)

        assert len(final_session.navigation_history) == 2
        assert final_session.version == 2


class TestInitSessionTables:
    """Test session table initialization"""

    def test_init_session_tables(self, test_db):
        """Test initializing session tables"""

        # Should not raise errors
        init_session_tables()

        # Verify table exists
        with test_db.session_scope() as db_session:
            result = db_session.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'")
            tables = result.fetchall()
            assert len(tables) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
