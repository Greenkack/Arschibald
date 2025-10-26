"""Enhanced Session Management & State Persistence"""

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

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


@dataclass
class NavigationEntry:
    """Single navigation history entry"""
    page: str
    params: dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'page': self.page,
            'params': self.params,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'NavigationEntry':
        """Create from dictionary"""
        return cls(
            page=data['page'],
            params=data['params'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


@dataclass
class FormSnapshot:
    """Form state snapshot for undo/redo"""
    snapshot_id: str
    form_id: str
    data: dict[str, Any]
    timestamp: datetime
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'snapshot_id': self.snapshot_id,
            'form_id': self.form_id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FormSnapshot':
        """Create from dictionary"""
        return cls(
            snapshot_id=data['snapshot_id'],
            form_id=data['form_id'],
            data=data['data'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            description=data.get('description', '')
        )


@dataclass
class FormState:
    """Enhanced form state with validation and history"""
    form_id: str
    data: dict[str, Any] = field(default_factory=dict)

    # Validation
    errors: dict[str, list[str]] = field(default_factory=dict)
    warnings: dict[str, list[str]] = field(default_factory=dict)
    validation_schema: dict[str, Any] | None = None

    # History for undo/redo
    snapshots: list[FormSnapshot] = field(default_factory=list)
    current_snapshot_index: int = -1
    max_snapshots: int = 50

    # Persistence
    is_dirty: bool = False
    last_saved: datetime | None = None
    auto_save: bool = True
    save_debounce_ms: int = 500

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'form_id': self.form_id,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings,
            'validation_schema': self.validation_schema,
            'snapshots': [
                s.to_dict() for s in self.snapshots],
            'current_snapshot_index': self.current_snapshot_index,
            'max_snapshots': self.max_snapshots,
            'is_dirty': self.is_dirty,
            'last_saved': self.last_saved.isoformat() if self.last_saved else None,
            'auto_save': self.auto_save,
            'save_debounce_ms': self.save_debounce_ms,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FormState':
        """Create from dictionary"""
        snapshots = [FormSnapshot.from_dict(s)
                     for s in data.get('snapshots', [])]
        last_saved = datetime.fromisoformat(
            data['last_saved']) if data.get('last_saved') else None

        return cls(
            form_id=data['form_id'],
            data=data.get('data', {}),
            errors=data.get('errors', {}),
            warnings=data.get('warnings', {}),
            validation_schema=data.get('validation_schema'),
            snapshots=snapshots,
            current_snapshot_index=data.get('current_snapshot_index', -1),
            max_snapshots=data.get('max_snapshots', 50),
            is_dirty=data.get('is_dirty', False),
            last_saved=last_saved,
            auto_save=data.get('auto_save', True),
            save_debounce_ms=data.get('save_debounce_ms', 500),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            version=data.get('version', 1)
        )


@dataclass
class UserSession:
    """Enhanced user session with complete state management"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None

    # Navigation
    current_page: str = "home"
    page_params: dict[str, Any] = field(default_factory=dict)
    navigation_history: list[NavigationEntry] = field(default_factory=list)
    max_history_size: int = 100

    # Forms
    form_states: dict[str, FormState] = field(default_factory=dict)
    dirty_forms: set[str] = field(default_factory=set)
    form_snapshots: dict[str, list[FormSnapshot]] = field(default_factory=dict)

    # Cache tracking
    cache_keys: set[str] = field(default_factory=set)
    cache_dependencies: dict[str, set[str]] = field(default_factory=dict)

    # Permissions & Roles
    roles: set[str] = field(default_factory=set)
    permissions: set[str] = field(default_factory=set)

    # Preferences
    theme: str = "auto"
    language: str = "en"
    timezone: str = "UTC"
    preferences: dict[str, Any] = field(default_factory=dict)

    # Metrics
    page_views: dict[str, int] = field(default_factory=dict)
    interaction_count: int = 0
    session_start: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1

    @property
    def session_duration(self) -> timedelta:
        """Calculate session duration"""
        return datetime.now() - self.session_start

    def add_navigation(self, page: str, params: dict[str, Any] = None) -> None:
        """Add navigation entry to history"""
        entry = NavigationEntry(
            page=page,
            params=params or {},
            timestamp=datetime.now()
        )

        self.navigation_history.append(entry)

        # Limit history size
        if len(self.navigation_history) > self.max_history_size:
            self.navigation_history = self.navigation_history[-self.max_history_size:]

        # Update page views
        self.page_views[page] = self.page_views.get(page, 0) + 1

        # Update activity
        self.last_activity = datetime.now()
        self.interaction_count += 1

    def get_form_state(self, form_id: str) -> FormState:
        """Get or create form state"""
        if form_id not in self.form_states:
            self.form_states[form_id] = FormState(form_id=form_id)
        return self.form_states[form_id]

    def mark_form_dirty(self, form_id: str) -> None:
        """Mark form as dirty (unsaved changes)"""
        self.dirty_forms.add(form_id)
        if form_id in self.form_states:
            self.form_states[form_id].is_dirty = True

    def mark_form_clean(self, form_id: str) -> None:
        """Mark form as clean (saved)"""
        self.dirty_forms.discard(form_id)
        if form_id in self.form_states:
            self.form_states[form_id].is_dirty = False
            self.form_states[form_id].last_saved = datetime.now()

    def add_cache_key(self, key: str, dependencies: set[str] = None) -> None:
        """Track cache key with optional dependencies"""
        self.cache_keys.add(key)
        if dependencies:
            self.cache_dependencies[key] = dependencies

    def remove_cache_key(self, key: str) -> None:
        """Remove cache key from tracking"""
        self.cache_keys.discard(key)
        self.cache_dependencies.pop(key, None)

    def has_permission(self, permission: str) -> bool:
        """Check if user has permission"""
        return permission in self.permissions

    def has_role(self, role: str) -> bool:
        """Check if user has role"""
        return role in self.roles

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'current_page': self.current_page,
            'page_params': self.page_params,
            'navigation_history': [entry.to_dict() for entry in self.navigation_history],
            'max_history_size': self.max_history_size,
            'form_states': {k: v.to_dict() for k, v in self.form_states.items()},
            'dirty_forms': list(self.dirty_forms),
            'form_snapshots': {
                k: [s.to_dict() for s in v]
                for k, v in self.form_snapshots.items()
            },
            'cache_keys': list(self.cache_keys),
            'cache_dependencies': {k: list(v) for k, v in self.cache_dependencies.items()},
            'roles': list(self.roles),
            'permissions': list(self.permissions),
            'theme': self.theme,
            'language': self.language,
            'timezone': self.timezone,
            'preferences': self.preferences,
            'page_views': self.page_views,
            'interaction_count': self.interaction_count,
            'session_start': self.session_start.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'UserSession':
        """Create from dictionary"""
        navigation_history = [
            NavigationEntry.from_dict(entry)
            for entry in data.get('navigation_history', [])
        ]

        form_states = {
            k: FormState.from_dict(v)
            for k, v in data.get('form_states', {}).items()
        }

        form_snapshots = {
            k: [FormSnapshot.from_dict(s) for s in v]
            for k, v in data.get('form_snapshots', {}).items()
        }

        return cls(
            session_id=data['session_id'],
            user_id=data.get('user_id'),
            current_page=data.get('current_page', 'home'),
            page_params=data.get('page_params', {}),
            navigation_history=navigation_history,
            max_history_size=data.get('max_history_size', 100),
            form_states=form_states,
            dirty_forms=set(data.get('dirty_forms', [])),
            form_snapshots=form_snapshots,
            cache_keys=set(data.get('cache_keys', [])),
            cache_dependencies={
                k: set(v) for k, v in data.get('cache_dependencies', {}).items()
            },
            roles=set(data.get('roles', [])),
            permissions=set(data.get('permissions', [])),
            theme=data.get('theme', 'auto'),
            language=data.get('language', 'en'),
            timezone=data.get('timezone', 'UTC'),
            preferences=data.get('preferences', {}),
            page_views=data.get('page_views', {}),
            interaction_count=data.get('interaction_count', 0),
            session_start=datetime.fromisoformat(data['session_start']),
            last_activity=datetime.fromisoformat(data['last_activity']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            version=data.get('version', 1)
        )

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> 'UserSession':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


# Session persistence with debouncing
class SessionPersistence:
    """Debounced session state persistence engine"""

    def __init__(self, debounce_ms: int = 500):
        self.debounce_ms = debounce_ms
        self._pending_saves: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def schedule_save(
        self,
        session_id: str,
        session: UserSession,
        save_fn: callable
    ) -> None:
        """Schedule debounced save"""
        with self._lock:
            # Cancel existing timer if any
            if session_id in self._pending_saves:
                self._pending_saves[session_id].cancel()

            # Schedule new save
            timer = threading.Timer(
                self.debounce_ms / 1000.0,
                lambda: self._execute_save(session_id, session, save_fn)
            )
            self._pending_saves[session_id] = timer
            timer.start()

    def _execute_save(
        self,
        session_id: str,
        session: UserSession,
        save_fn: callable
    ) -> None:
        """Execute the actual save"""
        try:
            save_fn(session)
            logger.debug("Session saved", session_id=session_id)
        except Exception as e:
            logger.error(
                "Session save failed",
                session_id=session_id,
                error=str(e))
        finally:
            with self._lock:
                self._pending_saves.pop(session_id, None)

    def flush(self, session_id: str = None) -> None:
        """Immediately execute pending saves"""
        with self._lock:
            if session_id:
                timer = self._pending_saves.get(session_id)
                if timer:
                    timer.cancel()
                    timer.function()
            else:
                # Flush all pending saves
                for timer in self._pending_saves.values():
                    timer.cancel()
                    timer.function()
                self._pending_saves.clear()


# Global session persistence engine
_session_persistence = SessionPersistence()


def get_session_persistence() -> SessionPersistence:
    """Get global session persistence engine"""
    return _session_persistence


# Session management functions
def bootstrap_session(
    session_id: str = None,
    user_id: str = None,
    restore_from_db: bool = True
) -> UserSession:
    """
    Initialize or restore user session

    Args:
        session_id: Optional session ID to restore
        user_id: Optional user ID for the session
        restore_from_db: If True, attempt to restore from database

    Returns:
        UserSession instance
    """
    # Try to restore from Streamlit session_state first
    if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
        if 'user_session' in st.session_state:
            logger.debug("Restored session from session_state")
            return st.session_state.user_session

    # Try to restore from database
    if restore_from_db and session_id:
        try:
            from .session_repository import SessionRepository
            repo = SessionRepository()
            session_data = repo.get_session(session_id)

            if session_data:
                session = UserSession.from_dict(session_data)
                logger.info(
                    "Session restored from database",
                    session_id=session_id)

                # Store in session_state if available
                if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
                    st.session_state.user_session = session

                return session
        except Exception as e:
            logger.warning(
                "Failed to restore session from database",
                error=str(e))

    # Create new session
    session = UserSession(
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id
    )

    logger.info("New session created", session_id=session.session_id)

    # Store in session_state if available
    if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
        st.session_state.user_session = session

    return session


def get_current_session() -> UserSession:
    """Get current user session"""
    if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
        if 'user_session' not in st.session_state:
            st.session_state.user_session = bootstrap_session()
        return st.session_state.user_session

    # Fallback for non-Streamlit contexts
    return bootstrap_session()


def persist_input(key: str, val: Any) -> None:
    """
    Immediately persist input to session_state and schedule DB write

    Args:
        key: Input key
        val: Input value
    """
    # Update session_state immediately
    if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
        st.session_state[key] = val

    # Get current session
    session = get_current_session()
    session.last_activity = datetime.now()
    session.interaction_count += 1
    session.updated_at = datetime.now()

    # Schedule debounced database write
    try:
        from .session_repository import SessionRepository
        repo = SessionRepository()

        def save_fn(sess: UserSession):
            repo.save_session(sess)

        persistence = get_session_persistence()
        persistence.schedule_save(session.session_id, session, save_fn)

        logger.debug("Input persisted", key=key)
    except Exception as e:
        logger.error("Failed to schedule session save", key=key, error=str(e))


def save_session(session: UserSession, immediate: bool = False) -> None:
    """
    Save session to database

    Args:
        session: UserSession to save
        immediate: If True, save immediately without debouncing
    """
    try:
        from .session_repository import SessionRepository
        repo = SessionRepository()

        if immediate:
            repo.save_session(session)
            logger.info(
                "Session saved immediately",
                session_id=session.session_id)
        else:
            def save_fn(sess: UserSession):
                repo.save_session(sess)

            persistence = get_session_persistence()
            persistence.schedule_save(session.session_id, session, save_fn)
            logger.debug(
                "Session save scheduled",
                session_id=session.session_id)
    except Exception as e:
        logger.error(
            "Failed to save session",
            session_id=session.session_id,
            error=str(e))


def recover_session(session_id: str) -> UserSession | None:
    """
    Recover session from database after browser refresh

    Args:
        session_id: Session ID to recover

    Returns:
        Recovered UserSession or None
    """
    try:
        from .session_repository import SessionRepository
        repo = SessionRepository()
        session_data = repo.get_session(session_id)

        if session_data:
            session = UserSession.from_dict(session_data)
            logger.info("Session recovered", session_id=session_id)

            # Store in session_state if available
            if STREAMLIT_AVAILABLE and st and hasattr(st, 'session_state'):
                st.session_state.user_session = session

            return session
    except Exception as e:
        logger.error(
            "Failed to recover session",
            session_id=session_id,
            error=str(e))

    return None


def cleanup_expired_sessions(max_age_hours: int = 24) -> int:
    """
    Clean up expired sessions

    Args:
        max_age_hours: Maximum session age in hours

    Returns:
        Number of sessions cleaned up
    """
    try:
        from .session_repository import SessionRepository
        repo = SessionRepository()
        count = repo.cleanup_expired_sessions(max_age_hours)
        logger.info("Expired sessions cleaned up", count=count)
        return count
    except Exception as e:
        logger.error("Failed to cleanup expired sessions", error=str(e))
        return 0
