"""Session Persistence Engine with Debounced Database Writes"""

import threading
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session as DBSession

from .database import Base, DatabaseManager, get_db_manager
from .session import UserSession

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SessionModel(Base):
    """Database model for session persistence"""

    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    session_data = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    last_activity = Column(DateTime, nullable=False, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<SessionModel(session_id={self.session_id})>"


class DebouncedWriter:
    """
    Debounced writer to prevent excessive database writes.

    Batches write operations and executes them after a delay period
    to reduce database load while ensuring data persistence.
    """

    def __init__(self, delay_seconds: float = 2.0):
        """
        Initialize debounced writer.

        Args:
            delay_seconds: Delay before executing write (default: 2.0)
        """
        self.delay_seconds = delay_seconds
        self._pending_writes: dict[str, tuple[Callable, tuple, dict]] = {}
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def schedule_write(
        self,
        key: str,
        write_fn: Callable,
        *args,
        **kwargs,
    ) -> None:
        """
        Schedule a write operation with debouncing.

        Args:
            key: Unique key for the write operation
            write_fn: Function to execute for writing
            *args: Positional arguments for write_fn
            **kwargs: Keyword arguments for write_fn
        """
        with self._lock:
            # Cancel existing timer for this key
            if key in self._timers:
                self._timers[key].cancel()

            # Store pending write
            self._pending_writes[key] = (write_fn, args, kwargs)

            # Schedule new timer
            timer = threading.Timer(
                self.delay_seconds, self._execute_write, args=(key,)
            )
            self._timers[key] = timer
            timer.start()

            logger.debug(
                "Write scheduled",
                key=key,
                delay=self.delay_seconds,
            )

    def _execute_write(self, key: str) -> None:
        """Execute pending write"""
        with self._lock:
            if key not in self._pending_writes:
                return

            write_fn, args, kwargs = self._pending_writes.pop(key)
            self._timers.pop(key, None)

        try:
            write_fn(*args, **kwargs)
            logger.debug("Write executed", key=key)
        except Exception as e:
            logger.error(
                "Write failed",
                key=key,
                error=str(e),
                exc_info=True,
            )

    def flush(self, key: str | None = None) -> None:
        """
        Immediately execute pending writes.

        Args:
            key: Specific key to flush, or None to flush all
        """
        with self._lock:
            if key:
                # Flush specific key
                if key in self._timers:
                    self._timers[key].cancel()
                    self._execute_write(key)
            else:
                # Flush all pending writes
                keys = list(self._pending_writes.keys())
                for k in keys:
                    if k in self._timers:
                        self._timers[k].cancel()
                    self._execute_write(k)

    def cancel(self, key: str) -> None:
        """Cancel pending write"""
        with self._lock:
            if key in self._timers:
                self._timers[key].cancel()
                self._timers.pop(key)
            self._pending_writes.pop(key, None)


class SessionPersistenceEngine:
    """
    Session persistence engine with debounced database writes.

    Provides automatic session persistence with:
    - Debounced writes to reduce database load
    - Session recovery from database
    - Conflict resolution using last-write-wins
    - Automatic cleanup of expired sessions
    """

    def __init__(
        self,
        db_manager: DatabaseManager | None = None,
        debounce_delay: float = 2.0,
        session_timeout: int = 86400,
    ):
        """
        Initialize persistence engine.

        Args:
            db_manager: Database manager instance
            debounce_delay: Delay for debounced writes in seconds
            session_timeout: Session timeout in seconds (default: 24h)
        """
        self.db_manager = db_manager or get_db_manager()
        self.debounce_delay = debounce_delay
        self.session_timeout = session_timeout
        self.writer = DebouncedWriter(delay_seconds=debounce_delay)

        # Ensure table exists
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Ensure session table exists"""
        try:
            SessionModel.__table__.create(
                self.db_manager.engine, checkfirst=True
            )
        except Exception as e:
            logger.warning("Failed to create session table", error=str(e))

    def persist_session(
        self, session: UserSession, immediate: bool = False
    ) -> None:
        """
        Persist session to database with debouncing.

        Args:
            session: UserSession to persist
            immediate: If True, write immediately without debouncing
        """
        if immediate:
            self._write_session(session)
        else:
            self.writer.schedule_write(
                f"session_{session.session_id}",
                self._write_session,
                session,
            )

    def _write_session(self, session: UserSession) -> None:
        """Write session to database"""
        try:
            with self.db_manager.session_scope() as db_session:
                # Check if session exists
                existing = (
                    db_session.query(SessionModel)
                    .filter(SessionModel.session_id == session.session_id)
                    .first()
                )

                # Calculate expiration
                expires_at = datetime.now() + timedelta(
                    seconds=self.session_timeout
                )

                if existing:
                    # Update existing session
                    existing.session_data = session.to_json()
                    existing.updated_at = datetime.now()
                    existing.last_activity = session.metrics.last_activity
                    existing.expires_at = expires_at
                    existing.user_id = session.user_id
                else:
                    # Create new session
                    new_session = SessionModel(
                        session_id=session.session_id,
                        user_id=session.user_id,
                        session_data=session.to_json(),
                        created_at=session.created_at,
                        updated_at=datetime.now(),
                        last_activity=session.metrics.last_activity,
                        expires_at=expires_at,
                    )
                    db_session.add(new_session)

                # Update session's last_persisted timestamp
                session.last_persisted = datetime.now()

                logger.info(
                    "Session persisted",
                    session_id=session.session_id,
                    user_id=session.user_id,
                )

        except Exception as e:
            logger.error(
                "Failed to persist session",
                session_id=session.session_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def recover_session(self, session_id: str) -> UserSession | None:
        """
        Recover session from database.

        Args:
            session_id: Session ID to recover

        Returns:
            UserSession if found, None otherwise
        """
        try:
            with self.db_manager.session_scope() as db_session:
                session_model = (
                    db_session.query(SessionModel)
                    .filter(SessionModel.session_id == session_id)
                    .first()
                )

                if not session_model:
                    logger.info(
                        "Session not found",
                        session_id=session_id,
                    )
                    return None

                # Check if session expired
                if (
                    session_model.expires_at
                    and session_model.expires_at < datetime.now()
                ):
                    logger.info(
                        "Session expired",
                        session_id=session_id,
                        expired_at=session_model.expires_at,
                    )
                    # Delete expired session
                    db_session.delete(session_model)
                    return None

                # Deserialize session
                session = UserSession.from_json(session_model.session_data)

                logger.info(
                    "Session recovered",
                    session_id=session_id,
                    user_id=session.user_id,
                )

                return session

        except Exception as e:
            logger.error(
                "Failed to recover session",
                session_id=session_id,
                error=str(e),
                exc_info=True,
            )
            return None

    def recover_user_sessions(self, user_id: str) -> list[UserSession]:
        """
        Recover all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            List of UserSession objects
        """
        try:
            with self.db_manager.session_scope() as db_session:
                session_models = (
                    db_session.query(SessionModel)
                    .filter(SessionModel.user_id == user_id)
                    .filter(
                        (SessionModel.expires_at.is_(None))
                        | (SessionModel.expires_at > datetime.now())
                    )
                    .all()
                )

                sessions = []
                for model in session_models:
                    try:
                        session = UserSession.from_json(model.session_data)
                        sessions.append(session)
                    except Exception as e:
                        logger.warning(
                            "Failed to deserialize session",
                            session_id=model.session_id,
                            error=str(e),
                        )

                logger.info(
                    "User sessions recovered",
                    user_id=user_id,
                    count=len(sessions),
                )

                return sessions

        except Exception as e:
            logger.error(
                "Failed to recover user sessions",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            return []

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session from database.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            # Cancel any pending writes
            self.writer.cancel(f"session_{session_id}")

            with self.db_manager.session_scope() as db_session:
                result = (
                    db_session.query(SessionModel)
                    .filter(SessionModel.session_id == session_id)
                    .delete()
                )

                logger.info(
                    "Session deleted",
                    session_id=session_id,
                    deleted=result > 0,
                )

                return result > 0

        except Exception as e:
            logger.error(
                "Failed to delete session",
                session_id=session_id,
                error=str(e),
                exc_info=True,
            )
            return False

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from database.

        Returns:
            Number of sessions deleted
        """
        try:
            with self.db_manager.session_scope() as db_session:
                result = (
                    db_session.query(SessionModel)
                    .filter(SessionModel.expires_at < datetime.now())
                    .delete()
                )

                logger.info(
                    "Expired sessions cleaned up",
                    count=result,
                )

                return result

        except Exception as e:
            logger.error(
                "Failed to cleanup expired sessions",
                error=str(e),
                exc_info=True,
            )
            return 0

    def cleanup_inactive_sessions(self, inactive_days: int = 7) -> int:
        """
        Clean up inactive sessions.

        Args:
            inactive_days: Days of inactivity before cleanup

        Returns:
            Number of sessions deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=inactive_days)

            with self.db_manager.session_scope() as db_session:
                result = (
                    db_session.query(SessionModel)
                    .filter(SessionModel.last_activity < cutoff_date)
                    .delete()
                )

                logger.info(
                    "Inactive sessions cleaned up",
                    count=result,
                    inactive_days=inactive_days,
                )

                return result

        except Exception as e:
            logger.error(
                "Failed to cleanup inactive sessions",
                error=str(e),
                exc_info=True,
            )
            return 0

    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        try:
            with self.db_manager.session_scope() as db_session:
                count = (
                    db_session.query(SessionModel)
                    .filter(
                        (SessionModel.expires_at.is_(None))
                        | (SessionModel.expires_at > datetime.now())
                    )
                    .count()
                )
                return count
        except Exception as e:
            logger.error(
                "Failed to get session count",
                error=str(e),
            )
            return 0

    def flush_all(self) -> None:
        """Flush all pending writes immediately"""
        self.writer.flush()


# Global persistence engine instance
_persistence_engine: SessionPersistenceEngine | None = None


def get_persistence_engine() -> SessionPersistenceEngine:
    """Get global persistence engine instance"""
    global _persistence_engine
    if _persistence_engine is None:
        _persistence_engine = SessionPersistenceEngine()
    return _persistence_engine


def persist_session(
    session: UserSession, immediate: bool = False
) -> None:
    """
    Persist session to database.

    Args:
        session: UserSession to persist
        immediate: If True, write immediately without debouncing
    """
    engine = get_persistence_engine()
    engine.persist_session(session, immediate=immediate)


def recover_session(session_id: str) -> UserSession | None:
    """
    Recover session from database.

    Args:
        session_id: Session ID to recover

    Returns:
        UserSession if found, None otherwise
    """
    engine = get_persistence_engine()
    return engine.recover_session(session_id)
