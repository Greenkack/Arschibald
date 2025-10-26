"""Session Repository for Database Persistence"""

import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text

from .database import Base, DatabaseManager, get_db_manager

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SessionModel(Base):
    """Database model for user sessions"""
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    session_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<SessionModel(session_id='{
            self.session_id}', user_id='{
            self.user_id}')>"


class SessionRepository:
    """Repository for session persistence operations"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or get_db_manager()

    def save_session(self, session: 'UserSession') -> None:
        """
        Save or update session in database

        Args:
            session: UserSession instance to save
        """

        with self.db_manager.session_scope() as db_session:
            # Check if session exists
            existing = db_session.query(SessionModel).filter(
                SessionModel.session_id == session.session_id
            ).first()

            session_data_json = session.to_json()

            if existing:
                # Update existing session
                existing.session_data = session_data_json
                existing.updated_at = datetime.utcnow()
                existing.last_activity = session.last_activity
                existing.version = session.version
                existing.user_id = session.user_id

                logger.debug("Session updated", session_id=session.session_id)
            else:
                # Create new session
                new_session = SessionModel(
                    session_id=session.session_id,
                    user_id=session.user_id,
                    session_data=session_data_json,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    last_activity=session.last_activity,
                    version=session.version
                )
                db_session.add(new_session)

                logger.debug("Session created", session_id=session.session_id)

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        Get session data from database

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session data dictionary or None
        """
        with self.db_manager.session_scope() as db_session:
            session_model = db_session.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()

            if session_model:
                try:
                    session_data = json.loads(session_model.session_data)
                    logger.debug("Session retrieved", session_id=session_id)
                    return session_data
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to parse session data",
                        session_id=session_id,
                        error=str(e)
                    )
                    return None

            logger.debug("Session not found", session_id=session_id)
            return None

    def get_session_by_user(self, user_id: str) -> dict[str, Any] | None:
        """
        Get most recent session for a user

        Args:
            user_id: User ID

        Returns:
            Session data dictionary or None
        """
        with self.db_manager.session_scope() as db_session:
            session_model = db_session.query(SessionModel).filter(
                SessionModel.user_id == user_id
            ).order_by(SessionModel.last_activity.desc()).first()

            if session_model:
                try:
                    session_data = json.loads(session_model.session_data)
                    logger.debug("User session retrieved", user_id=user_id)
                    return session_data
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to parse session data",
                        user_id=user_id,
                        error=str(e)
                    )
                    return None

            logger.debug("User session not found", user_id=user_id)
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session from database

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False otherwise
        """
        with self.db_manager.session_scope() as db_session:
            session_model = db_session.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()

            if session_model:
                db_session.delete(session_model)
                logger.info("Session deleted", session_id=session_id)
                return True

            logger.debug(
                "Session not found for deletion",
                session_id=session_id)
            return False

    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired sessions

        Args:
            max_age_hours: Maximum session age in hours

        Returns:
            Number of sessions deleted
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        with self.db_manager.session_scope() as db_session:
            expired_sessions = db_session.query(SessionModel).filter(
                SessionModel.last_activity < cutoff_time
            ).all()

            count = len(expired_sessions)

            for session in expired_sessions:
                db_session.delete(session)

            logger.info(
                "Expired sessions cleaned up",
                count=count,
                max_age_hours=max_age_hours)
            return count

    def get_active_session_count(
            self, active_threshold_minutes: int = 30) -> int:
        """
        Get count of active sessions

        Args:
            active_threshold_minutes: Minutes to consider session active

        Returns:
            Number of active sessions
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=active_threshold_minutes)

        with self.db_manager.session_scope() as db_session:
            count = db_session.query(SessionModel).filter(
                SessionModel.last_activity >= cutoff_time
            ).count()

            return count

    def get_all_sessions(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: str = None
    ) -> list[dict[str, Any]]:
        """
        Get all sessions with pagination

        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            user_id: Optional user ID filter

        Returns:
            List of session data dictionaries
        """
        with self.db_manager.session_scope() as db_session:
            query = db_session.query(SessionModel)

            if user_id:
                query = query.filter(SessionModel.user_id == user_id)

            query = query.order_by(SessionModel.last_activity.desc())
            query = query.limit(limit).offset(offset)

            sessions = []
            for session_model in query.all():
                try:
                    session_data = json.loads(session_model.session_data)
                    sessions.append(session_data)
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to parse session data",
                        session_id=session_model.session_id,
                        error=str(e)
                    )

            return sessions

    def update_last_activity(self, session_id: str) -> bool:
        """
        Update last activity timestamp for session

        Args:
            session_id: Session ID

        Returns:
            True if updated, False otherwise
        """
        with self.db_manager.session_scope() as db_session:
            session_model = db_session.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()

            if session_model:
                session_model.last_activity = datetime.utcnow()
                session_model.updated_at = datetime.utcnow()
                logger.debug("Session activity updated", session_id=session_id)
                return True

            logger.debug(
                "Session not found for activity update",
                session_id=session_id)
            return False

    def resolve_conflict(
        self,
        session_id: str,
        local_session: 'UserSession',
        strategy: str = 'last_write_wins'
    ) -> 'UserSession':
        """
        Resolve session conflict using specified strategy

        Args:
            session_id: Session ID
            local_session: Local session instance
            strategy: Conflict resolution strategy ('last_write_wins', 'merge')

        Returns:
            Resolved UserSession
        """
        from .session import UserSession

        db_session_data = self.get_session(session_id)

        if not db_session_data:
            # No conflict, save local session
            self.save_session(local_session)
            return local_session

        db_session = UserSession.from_dict(db_session_data)

        if strategy == 'last_write_wins':
            # Use the session with the most recent update
            if local_session.updated_at > db_session.updated_at:
                self.save_session(local_session)
                logger.info(
                    "Conflict resolved: local session wins",
                    session_id=session_id
                )
                return local_session
            logger.info(
                "Conflict resolved: database session wins",
                session_id=session_id
            )
            return db_session

        if strategy == 'merge':
            # Merge sessions (simple merge strategy)
            merged = db_session

            # Merge form states
            for form_id, form_state in local_session.form_states.items():
                if form_id not in merged.form_states or form_state.updated_at > merged.form_states[
                        form_id].updated_at:
                    merged.form_states[form_id] = form_state

            # Merge navigation history
            merged.navigation_history.extend(local_session.navigation_history)
            merged.navigation_history = sorted(
                merged.navigation_history,
                key=lambda x: x.timestamp
            )[-merged.max_history_size:]

            # Merge page views
            for page, count in local_session.page_views.items():
                merged.page_views[page] = merged.page_views.get(
                    page, 0) + count

            # Use most recent metadata
            if local_session.updated_at > merged.updated_at:
                merged.current_page = local_session.current_page
                merged.page_params = local_session.page_params
                merged.last_activity = local_session.last_activity

            merged.updated_at = datetime.utcnow()
            merged.version += 1

            self.save_session(merged)
            logger.info(
                "Conflict resolved: sessions merged",
                session_id=session_id)
            return merged

        raise ValueError(f"Unknown conflict resolution strategy: {strategy}")


def init_session_tables():
    """Initialize session tables in database"""
    db_manager = get_db_manager()
    Base.metadata.create_all(
        bind=db_manager.engine, tables=[
            SessionModel.__table__])
    logger.info("Session tables initialized")
