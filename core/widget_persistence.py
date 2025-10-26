"""Widget Auto-Persistence Engine

This module provides debounced persistence for widget states to prevent excessive
database writes while ensuring data integrity and conflict resolution.

Key Features:
- Debounced persistence to prevent excessive DB writes
- Widget state batching for efficient operations
- Conflict resolution for concurrent user scenarios
- State recovery with validation
"""

import json
import threading
from collections import defaultdict
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


class WidgetStateModel(Base):
    """Database model for widget states"""
    __tablename__ = 'widget_states'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, index=True)
    widget_key = Column(String(255), nullable=False, index=True)
    widget_value = Column(Text, nullable=True)
    widget_type = Column(String(50), nullable=True)
    # SQLite doesn't have boolean
    is_valid = Column(Integer, default=1, nullable=False)
    errors = Column(Text, nullable=True)  # JSON array
    warnings = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False)
    version = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<WidgetStateModel(session_id='{
            self.session_id}', key='{
            self.widget_key}')>"


class WidgetPersistenceEngine:
    """Debounced persistence engine for widget states"""

    def __init__(
        self,
        db_manager: DatabaseManager = None,
        debounce_ms: int = 500,
        batch_size: int = 10,
        batch_timeout_ms: int = 1000
    ):
        self.db_manager = db_manager or get_db_manager()
        self.debounce_ms = debounce_ms
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms

        # Pending saves: {session_id: {widget_key: (value, timer)}}
        self._pending_saves: dict[str, dict[str,
                                            tuple[Any, threading.Timer]]] = defaultdict(dict)

        # Batch queue: {session_id: [(widget_key, value, timestamp)]}
        self._batch_queue: dict[str, list[tuple[str,
                                                Any, datetime]]] = defaultdict(list)

        # Locks
        self._save_lock = threading.Lock()
        self._batch_lock = threading.Lock()

        # Batch timer
        self._batch_timer: threading.Timer | None = None

    def schedule_save(
        self,
        session_id: str,
        widget_key: str,
        widget_value: Any,
        widget_type: str = None,
        is_valid: bool = True,
        errors: list[str] = None,
        warnings: list[str] = None
    ) -> None:
        """
        Schedule debounced save for widget state

        Args:
            session_id: Session ID
            widget_key: Widget key
            widget_value: Widget value
            widget_type: Widget type (text, number, etc.)
            is_valid: Whether widget value is valid
            errors: Validation errors
            warnings: Validation warnings
        """
        with self._save_lock:
            # Cancel existing timer if any
            if widget_key in self._pending_saves[session_id]:
                _, timer = self._pending_saves[session_id][widget_key]
                timer.cancel()

            # Create save data
            save_data = {
                'session_id': session_id,
                'widget_key': widget_key,
                'widget_value': widget_value,
                'widget_type': widget_type,
                'is_valid': is_valid,
                'errors': errors or [],
                'warnings': warnings or []
            }

            # Schedule new save
            timer = threading.Timer(
                self.debounce_ms / 1000.0,
                lambda: self._execute_save(session_id, widget_key, save_data)
            )
            self._pending_saves[session_id][widget_key] = (save_data, timer)
            timer.start()

            logger.debug(
                "Widget save scheduled",
                session_id=session_id,
                widget_key=widget_key,
                debounce_ms=self.debounce_ms
            )

    def _execute_save(
            self,
            session_id: str,
            widget_key: str,
            save_data: dict) -> None:
        """Execute the actual save"""
        try:
            # Add to batch queue
            with self._batch_lock:
                self._batch_queue[session_id].append((
                    widget_key,
                    save_data,
                    datetime.now()
                ))

                # Check if batch is ready
                if len(self._batch_queue[session_id]) >= self.batch_size:
                    self._flush_batch(session_id)
                else:
                    # Schedule batch flush if not already scheduled
                    if self._batch_timer is None or not self._batch_timer.is_alive():
                        self._batch_timer = threading.Timer(
                            self.batch_timeout_ms / 1000.0,
                            lambda: self._flush_all_batches()
                        )
                        self._batch_timer.start()

            logger.debug(
                "Widget added to batch",
                session_id=session_id,
                widget_key=widget_key)
        except Exception as e:
            logger.error(
                "Widget save failed",
                session_id=session_id,
                widget_key=widget_key,
                error=str(e))
        finally:
            with self._save_lock:
                self._pending_saves[session_id].pop(widget_key, None)

    def _flush_batch(self, session_id: str) -> None:
        """Flush batch for specific session"""
        with self._batch_lock:
            batch = self._batch_queue.pop(session_id, [])

            if not batch:
                return

            try:
                self._save_batch(session_id, batch)
                logger.info(
                    "Widget batch saved",
                    session_id=session_id,
                    count=len(batch)
                )
            except Exception as e:
                logger.error(
                    "Widget batch save failed",
                    session_id=session_id,
                    count=len(batch),
                    error=str(e)
                )

    def _flush_all_batches(self) -> None:
        """Flush all pending batches"""
        with self._batch_lock:
            session_ids = list(self._batch_queue.keys())

        for session_id in session_ids:
            self._flush_batch(session_id)

    def _save_batch(self, session_id: str,
                    batch: list[tuple[str, dict, datetime]]) -> None:
        """Save batch of widget states to database"""
        with self.db_manager.session_scope() as db_session:
            for widget_key, save_data, timestamp in batch:
                # Check if widget state exists
                existing = db_session.query(WidgetStateModel).filter(
                    WidgetStateModel.session_id == session_id,
                    WidgetStateModel.widget_key == widget_key
                ).first()

                # Serialize value
                try:
                    value_json = json.dumps(
                        save_data['widget_value'], default=str)
                except (TypeError, ValueError):
                    value_json = str(save_data['widget_value'])

                # Serialize errors and warnings
                errors_json = json.dumps(save_data['errors'])
                warnings_json = json.dumps(save_data['warnings'])

                if existing:
                    # Update existing
                    existing.widget_value = value_json
                    existing.widget_type = save_data.get('widget_type')
                    existing.is_valid = 1 if save_data['is_valid'] else 0
                    existing.errors = errors_json
                    existing.warnings = warnings_json
                    existing.updated_at = datetime.utcnow()
                    existing.version += 1
                else:
                    # Create new
                    new_state = WidgetStateModel(
                        session_id=session_id,
                        widget_key=widget_key,
                        widget_value=value_json,
                        widget_type=save_data.get('widget_type'),
                        is_valid=1 if save_data['is_valid'] else 0,
                        errors=errors_json,
                        warnings=warnings_json,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        version=1
                    )
                    db_session.add(new_state)

    def flush(self, session_id: str = None, widget_key: str = None) -> None:
        """
        Immediately flush pending saves

        Args:
            session_id: Optional session ID to flush (all if None)
            widget_key: Optional widget key to flush (all if None)
        """
        if session_id and widget_key:
            # Flush specific widget
            with self._save_lock:
                if widget_key in self._pending_saves.get(session_id, {}):
                    save_data, timer = self._pending_saves[session_id][widget_key]
                    timer.cancel()
                    self._execute_save(session_id, widget_key, save_data)
        elif session_id:
            # Flush all widgets for session
            with self._save_lock:
                widgets = list(self._pending_saves.get(session_id, {}).keys())

            for widget_key in widgets:
                self.flush(session_id, widget_key)

            # Flush batch
            self._flush_batch(session_id)
        else:
            # Flush all
            with self._save_lock:
                session_ids = list(self._pending_saves.keys())

            for sid in session_ids:
                self.flush(sid)

            # Flush all batches
            self._flush_all_batches()

    def recover_widget_states(
        self,
        session_id: str,
        widget_keys: list[str] = None
    ) -> dict[str, Any]:
        """
        Recover widget states from database

        Args:
            session_id: Session ID
            widget_keys: Optional list of widget keys to recover (all if None)

        Returns:
            Dictionary of widget_key -> value
        """
        recovered = {}

        try:
            with self.db_manager.session_scope() as db_session:
                query = db_session.query(WidgetStateModel).filter(
                    WidgetStateModel.session_id == session_id
                )

                if widget_keys:
                    query = query.filter(
                        WidgetStateModel.widget_key.in_(widget_keys))

                for state in query.all():
                    try:
                        value = json.loads(state.widget_value)
                        recovered[state.widget_key] = {
                            'value': value,
                            'type': state.widget_type,
                            'is_valid': bool(state.is_valid),
                            'errors': json.loads(state.errors) if state.errors else [],
                            'warnings': json.loads(state.warnings) if state.warnings else [],
                            'updated_at': state.updated_at,
                            'version': state.version
                        }
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.error(
                            "Failed to parse widget state",
                            session_id=session_id,
                            widget_key=state.widget_key,
                            error=str(e)
                        )

            logger.info(
                "Widget states recovered",
                session_id=session_id,
                count=len(recovered)
            )
        except Exception as e:
            logger.error(
                "Widget state recovery failed",
                session_id=session_id,
                error=str(e)
            )

        return recovered

    def resolve_conflict(
        self,
        session_id: str,
        widget_key: str,
        local_value: Any,
        local_updated_at: datetime,
        strategy: str = 'last_write_wins'
    ) -> tuple[Any, bool]:
        """
        Resolve widget state conflict

        Args:
            session_id: Session ID
            widget_key: Widget key
            local_value: Local widget value
            local_updated_at: Local update timestamp
            strategy: Conflict resolution strategy

        Returns:
            Tuple of (resolved_value, was_conflict)
        """
        try:
            with self.db_manager.session_scope() as db_session:
                db_state = db_session.query(WidgetStateModel).filter(
                    WidgetStateModel.session_id == session_id,
                    WidgetStateModel.widget_key == widget_key
                ).first()

                if not db_state:
                    # No conflict, use local value
                    return local_value, False

                db_value = json.loads(db_state.widget_value)
                db_updated_at = db_state.updated_at

                if strategy == 'last_write_wins':
                    if local_updated_at > db_updated_at:
                        logger.info(
                            "Conflict resolved: local wins",
                            session_id=session_id,
                            widget_key=widget_key
                        )
                        return local_value, True
                    logger.info(
                        "Conflict resolved: database wins",
                        session_id=session_id,
                        widget_key=widget_key
                    )
                    return db_value, True

                if strategy == 'prefer_local':
                    return local_value, True

                if strategy == 'prefer_remote':
                    return db_value, True

                raise ValueError(
                    f"Unknown conflict resolution strategy: {strategy}")

        except Exception as e:
            logger.error(
                "Conflict resolution failed",
                session_id=session_id,
                widget_key=widget_key,
                error=str(e)
            )
            return local_value, False

    def cleanup_old_states(self, max_age_hours: int = 24) -> int:
        """
        Clean up old widget states

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of states deleted
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        try:
            with self.db_manager.session_scope() as db_session:
                old_states = db_session.query(WidgetStateModel).filter(
                    WidgetStateModel.updated_at < cutoff_time
                ).all()

                count = len(old_states)

                for state in old_states:
                    db_session.delete(state)

                logger.info(
                    "Old widget states cleaned up",
                    count=count,
                    max_age_hours=max_age_hours
                )
                return count
        except Exception as e:
            logger.error("Widget state cleanup failed", error=str(e))
            return 0

    def get_widget_count(self, session_id: str = None) -> int:
        """Get count of widget states"""
        try:
            with self.db_manager.session_scope() as db_session:
                query = db_session.query(WidgetStateModel)

                if session_id:
                    query = query.filter(
                        WidgetStateModel.session_id == session_id)

                return query.count()
        except Exception as e:
            logger.error("Widget count failed", error=str(e))
            return 0


# Global persistence engine
_persistence_engine: WidgetPersistenceEngine | None = None
_engine_lock = threading.Lock()


def get_persistence_engine() -> WidgetPersistenceEngine:
    """Get global widget persistence engine"""
    global _persistence_engine

    with _engine_lock:
        if _persistence_engine is None:
            _persistence_engine = WidgetPersistenceEngine()

    return _persistence_engine


def init_widget_persistence_tables():
    """Initialize widget persistence tables in database"""
    db_manager = get_db_manager()
    Base.metadata.create_all(
        bind=db_manager.engine, tables=[
            WidgetStateModel.__table__])
    logger.info("Widget persistence tables initialized")


# Convenience functions

def save_widget_state(
    session_id: str,
    widget_key: str,
    widget_value: Any,
    widget_type: str = None,
    is_valid: bool = True,
    errors: list[str] = None,
    warnings: list[str] = None
) -> None:
    """Schedule widget state save"""
    engine = get_persistence_engine()
    engine.schedule_save(
        session_id=session_id,
        widget_key=widget_key,
        widget_value=widget_value,
        widget_type=widget_type,
        is_valid=is_valid,
        errors=errors,
        warnings=warnings
    )


def flush_widget_states(
        session_id: str = None,
        widget_key: str = None) -> None:
    """Flush pending widget state saves"""
    engine = get_persistence_engine()
    engine.flush(session_id=session_id, widget_key=widget_key)


def recover_widget_states(
    session_id: str,
    widget_keys: list[str] = None
) -> dict[str, Any]:
    """Recover widget states from database"""
    engine = get_persistence_engine()
    return engine.recover_widget_states(
        session_id=session_id, widget_keys=widget_keys)


def cleanup_old_widget_states(max_age_hours: int = 24) -> int:
    """Clean up old widget states"""
    engine = get_persistence_engine()
    return engine.cleanup_old_states(max_age_hours=max_age_hours)
