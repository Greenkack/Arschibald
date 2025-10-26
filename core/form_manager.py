"""Form State Management with Undo/Redo

This module provides comprehensive form state management with undo/redo functionality,
validation, auto-save, and conflict resolution.

Key Features:
- Enhanced FormState with snapshot management
- Undo/Redo system with configurable history depth
- Real-time validation with debounced execution
- Auto-save with conflict resolution
- Form dependency tracking
- Transactional form persistence
"""

import json
import threading
import uuid
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
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

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None


# Database Models

class FormDataModel(Base):
    """Database model for form data"""
    __tablename__ = 'form_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    data = Column(Text, nullable=False)  # JSON
    # JSON - renamed to avoid SQLAlchemy conflict
    form_metadata = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    # SQLite doesn't have boolean
    is_dirty = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<FormDataModel(form_id='{
            self.form_id}', version={
            self.version})>"


class FormSnapshotModel(Base):
    """Database model for form snapshots (undo/redo)"""
    __tablename__ = 'form_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(String(255), nullable=False, unique=True, index=True)
    form_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    data = Column(Text, nullable=False)  # JSON
    description = Column(String(500), nullable=True)
    snapshot_type = Column(
        String(50),
        default='manual',
        nullable=False)  # manual, auto, checkpoint
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<FormSnapshotModel(snapshot_id='{
            self.snapshot_id}', form_id='{
            self.form_id}')>"


class FormValidationModel(Base):
    """Database model for form validation state"""
    __tablename__ = 'form_validation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    errors = Column(Text, nullable=True)  # JSON
    warnings = Column(Text, nullable=True)  # JSON
    is_valid = Column(Integer, default=1, nullable=False)
    validated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<FormValidationModel(form_id='{
            self.form_id}', is_valid={
            bool(
                self.is_valid)})>"


# Data Classes

@dataclass
class FormSnapshot:
    """Form state snapshot for undo/redo"""
    snapshot_id: str
    form_id: str
    data: dict[str, Any]
    timestamp: datetime
    description: str = ""
    snapshot_type: str = "manual"  # manual, auto, checkpoint
    user_id: str | None = None
    session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'snapshot_id': self.snapshot_id,
            'form_id': self.form_id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'snapshot_type': self.snapshot_type,
            'user_id': self.user_id,
            'session_id': self.session_id
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FormSnapshot':
        """Create from dictionary"""
        return cls(
            snapshot_id=data['snapshot_id'],
            form_id=data['form_id'],
            data=data['data'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            description=data.get('description', ''),
            snapshot_type=data.get('snapshot_type', 'manual'),
            user_id=data.get('user_id'),
            session_id=data.get('session_id')
        )


@dataclass
class ValidationResult:
    """Form validation result"""
    is_valid: bool
    errors: dict[str, list[str]] = field(default_factory=dict)
    warnings: dict[str, list[str]] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=datetime.now)

    def add_error(self, field: str, error: str) -> None:
        """Add validation error"""
        if field not in self.errors:
            self.errors[field] = []
        if error not in self.errors[field]:
            self.errors[field].append(error)
        self.is_valid = False

    def add_warning(self, field: str, warning: str) -> None:
        """Add validation warning"""
        if field not in self.warnings:
            self.warnings[field] = []
        if warning not in self.warnings[field]:
            self.warnings[field].append(warning)

    def has_errors(self) -> bool:
        """Check if has errors"""
        return bool(self.errors)

    def has_warnings(self) -> bool:
        """Check if has warnings"""
        return bool(self.warnings)

    def get_all_errors(self) -> list[str]:
        """Get all error messages"""
        all_errors = []
        for field_errors in self.errors.values():
            all_errors.extend(field_errors)
        return all_errors

    def get_all_warnings(self) -> list[str]:
        """Get all warning messages"""
        all_warnings = []
        for field_warnings in self.warnings.values():
            all_warnings.extend(field_warnings)
        return all_warnings

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'validated_at': self.validated_at.isoformat()
        }


@dataclass
class FormState:
    """Enhanced form state with comprehensive undo/redo functionality"""
    form_id: str
    data: dict[str, Any] = field(default_factory=dict)

    # Validation
    errors: dict[str, list[str]] = field(default_factory=dict)
    warnings: dict[str, list[str]] = field(default_factory=dict)
    validation_schema: dict[str, Any] | None = None
    last_validation: ValidationResult | None = None

    # History for undo/redo
    snapshots: deque[FormSnapshot] = field(default_factory=deque)
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
    user_id: str | None = None
    session_id: str | None = None

    # Dependencies
    depends_on: set[str] = field(default_factory=set)
    dependents: set[str] = field(default_factory=set)

    # Metadata tracking
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize form state"""
        # Convert list to deque if needed
        if isinstance(self.snapshots, list):
            self.snapshots = deque(self.snapshots, maxlen=self.max_snapshots)
        elif not isinstance(self.snapshots, deque):
            self.snapshots = deque(maxlen=self.max_snapshots)
        else:
            # If it's already a deque, ensure maxlen is set correctly
            if self.snapshots.maxlen != self.max_snapshots:
                self.snapshots = deque(
                    self.snapshots, maxlen=self.max_snapshots)

    def update_data(
            self,
            key: str,
            value: Any,
            create_snapshot: bool = True) -> None:
        """
        Update form data

        Args:
            key: Data key
            value: Data value
            create_snapshot: Whether to create snapshot before update
        """
        # Create snapshot before update if requested
        if create_snapshot and self.data.get(key) != value:
            self.create_snapshot(
                description=f"Before updating {key}",
                snapshot_type="auto")

        # Update data
        self.data[key] = value
        self.is_dirty = True
        self.updated_at = datetime.now()

    def update_multiple(
            self, updates: dict[str, Any], create_snapshot: bool = True) -> None:
        """
        Update multiple form fields

        Args:
            updates: Dictionary of updates
            create_snapshot: Whether to create snapshot before update
        """
        if create_snapshot:
            self.create_snapshot(
                description="Before bulk update",
                snapshot_type="auto")

        self.data.update(updates)
        self.is_dirty = True
        self.updated_at = datetime.now()

    def create_snapshot(
        self,
        description: str = "",
        snapshot_type: str = "manual"
    ) -> FormSnapshot:
        """
        Create form snapshot for undo/redo

        Args:
            description: Snapshot description
            snapshot_type: Type of snapshot (manual, auto, checkpoint)

        Returns:
            Created FormSnapshot
        """
        snapshot = FormSnapshot(
            snapshot_id=str(uuid.uuid4()),
            form_id=self.form_id,
            data=self.data.copy(),
            timestamp=datetime.now(),
            description=description,
            snapshot_type=snapshot_type,
            user_id=self.user_id,
            session_id=self.session_id
        )

        # If we're not at the end of history, remove future snapshots
        if self.current_snapshot_index < len(self.snapshots) - 1:
            # Remove snapshots after current index
            while len(self.snapshots) > self.current_snapshot_index + 1:
                self.snapshots.pop()

        # Add new snapshot (deque will automatically enforce maxlen)
        self.snapshots.append(snapshot)

        # Update current index (accounting for deque maxlen enforcement)
        self.current_snapshot_index = len(self.snapshots) - 1

        logger.debug(
            "Form snapshot created",
            form_id=self.form_id,
            snapshot_id=snapshot.snapshot_id,
            type=snapshot_type
        )

        return snapshot

    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.current_snapshot_index > 0

    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.current_snapshot_index < len(self.snapshots) - 1

    def undo(self) -> bool:
        """
        Undo to previous snapshot

        Returns:
            True if undo was successful
        """
        if not self.can_undo():
            logger.warning(
                "Cannot undo: no previous snapshot",
                form_id=self.form_id)
            return False

        self.current_snapshot_index -= 1
        snapshot = self.snapshots[self.current_snapshot_index]
        self.data = snapshot.data.copy()
        self.is_dirty = True
        self.updated_at = datetime.now()

        logger.info(
            "Form undo",
            form_id=self.form_id,
            snapshot_id=snapshot.snapshot_id,
            index=self.current_snapshot_index
        )

        return True

    def redo(self) -> bool:
        """
        Redo to next snapshot

        Returns:
            True if redo was successful
        """
        if not self.can_redo():
            logger.warning(
                "Cannot redo: no next snapshot",
                form_id=self.form_id)
            return False

        self.current_snapshot_index += 1
        snapshot = self.snapshots[self.current_snapshot_index]
        self.data = snapshot.data.copy()
        self.is_dirty = True
        self.updated_at = datetime.now()

        logger.info(
            "Form redo",
            form_id=self.form_id,
            snapshot_id=snapshot.snapshot_id,
            index=self.current_snapshot_index
        )

        return True

    def get_snapshot_history(self) -> list[FormSnapshot]:
        """Get list of all snapshots"""
        return list(self.snapshots)

    def get_current_snapshot(self) -> FormSnapshot | None:
        """Get current snapshot"""
        if 0 <= self.current_snapshot_index < len(self.snapshots):
            return self.snapshots[self.current_snapshot_index]
        return None

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore specific snapshot

        Args:
            snapshot_id: Snapshot ID to restore

        Returns:
            True if restore was successful
        """
        for i, snapshot in enumerate(self.snapshots):
            if snapshot.snapshot_id == snapshot_id:
                self.current_snapshot_index = i
                self.data = snapshot.data.copy()
                self.is_dirty = True
                self.updated_at = datetime.now()

                logger.info(
                    "Form snapshot restored",
                    form_id=self.form_id,
                    snapshot_id=snapshot_id
                )

                return True

        logger.warning(
            "Snapshot not found",
            form_id=self.form_id,
            snapshot_id=snapshot_id
        )
        return False

    def cleanup_old_snapshots(self, keep_count: int = None) -> int:
        """
        Clean up old snapshots

        Args:
            keep_count: Number of snapshots to keep (uses max_snapshots if None)

        Returns:
            Number of snapshots removed
        """
        keep = keep_count or self.max_snapshots
        removed = 0

        while len(self.snapshots) > keep:
            self.snapshots.popleft()
            removed += 1
            if self.current_snapshot_index > 0:
                self.current_snapshot_index -= 1

        if removed > 0:
            logger.info(
                "Old snapshots cleaned up",
                form_id=self.form_id,
                removed=removed
            )

        return removed

    def add_dependency(self, form_id: str) -> None:
        """Add form dependency"""
        self.depends_on.add(form_id)

    def add_dependent(self, form_id: str) -> None:
        """Add dependent form"""
        self.dependents.add(form_id)

    def remove_dependency(self, form_id: str) -> None:
        """Remove form dependency"""
        self.depends_on.discard(form_id)

    def remove_dependent(self, form_id: str) -> None:
        """Remove dependent form"""
        self.dependents.discard(form_id)

    def mark_clean(self) -> None:
        """Mark form as clean (saved)"""
        self.is_dirty = False
        self.last_saved = datetime.now()

    def mark_dirty(self) -> None:
        """Mark form as dirty (unsaved changes)"""
        self.is_dirty = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'form_id': self.form_id,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings,
            'validation_schema': self.validation_schema,
            'last_validation': self.last_validation.to_dict() if self.last_validation else None,
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
            'version': self.version,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'depends_on': list(
                self.depends_on),
            'dependents': list(
                self.dependents),
            'metadata': self.metadata}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FormState':
        """Create from dictionary"""
        snapshots = deque(
            [FormSnapshot.from_dict(s) for s in data.get('snapshots', [])],
            maxlen=data.get('max_snapshots', 50)
        )

        last_saved = datetime.fromisoformat(
            data['last_saved']) if data.get('last_saved') else None

        # Reconstruct validation result if present
        last_validation = None
        if data.get('last_validation'):
            val_data = data['last_validation']
            last_validation = ValidationResult(
                is_valid=val_data['is_valid'],
                errors=val_data.get('errors', {}),
                warnings=val_data.get('warnings', {}),
                validated_at=datetime.fromisoformat(val_data['validated_at'])
            )

        return cls(
            form_id=data['form_id'],
            data=data.get('data', {}),
            errors=data.get('errors', {}),
            warnings=data.get('warnings', {}),
            validation_schema=data.get('validation_schema'),
            last_validation=last_validation,
            snapshots=snapshots,
            current_snapshot_index=data.get('current_snapshot_index', -1),
            max_snapshots=data.get('max_snapshots', 50),
            is_dirty=data.get('is_dirty', False),
            last_saved=last_saved,
            auto_save=data.get('auto_save', True),
            save_debounce_ms=data.get('save_debounce_ms', 500),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            version=data.get('version', 1),
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            depends_on=set(data.get('depends_on', [])),
            dependents=set(data.get('dependents', [])),
            metadata=data.get('metadata', {})
        )


def init_form_tables():
    """Initialize form management tables in database"""
    db_manager = get_db_manager()
    Base.metadata.create_all(
        bind=db_manager.engine,
        tables=[
            FormDataModel.__table__,
            FormSnapshotModel.__table__,
            FormValidationModel.__table__
        ]
    )
    logger.info("Form management tables initialized")


# Form Repository

class FormRepository:
    """Repository for form data persistence"""

    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or get_db_manager()

    def save_form(
        self,
        form_id: str,
        data: dict[str, Any],
        user_id: str = None,
        session_id: str = None,
        metadata: dict[str, Any] = None
    ) -> FormDataModel:
        """
        Save form data with transaction

        Args:
            form_id: Form ID
            data: Form data
            user_id: User ID
            session_id: Session ID
            metadata: Additional metadata

        Returns:
            Saved FormDataModel
        """
        with self.db_manager.session_scope() as db_session:
            # Check if form exists
            existing = db_session.query(FormDataModel).filter(
                FormDataModel.form_id == form_id,
                FormDataModel.session_id == session_id,
                FormDataModel.deleted_at.is_(None)
            ).first()

            # Serialize data
            data_json = json.dumps(data, default=str)
            metadata_json = json.dumps(metadata or {}, default=str)

            if existing:
                # Update existing
                existing.data = data_json
                existing.form_metadata = metadata_json
                existing.updated_at = datetime.utcnow()
                existing.version += 1
                existing.is_dirty = 0

                logger.info(
                    "Form updated",
                    form_id=form_id,
                    version=existing.version
                )

                return existing
            # Create new
            new_form = FormDataModel(
                form_id=form_id,
                user_id=user_id,
                session_id=session_id,
                data=data_json,
                form_metadata=metadata_json,
                version=1,
                is_dirty=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db_session.add(new_form)
            db_session.flush()

            logger.info("Form created", form_id=form_id)

            return new_form

    def load_form(
        self,
        form_id: str,
        session_id: str
    ) -> dict[str, Any] | None:
        """
        Load form data

        Args:
            form_id: Form ID
            session_id: Session ID

        Returns:
            Form data dictionary or None
        """
        with self.db_manager.session_scope() as db_session:
            form = db_session.query(FormDataModel).filter(
                FormDataModel.form_id == form_id,
                FormDataModel.session_id == session_id,
                FormDataModel.deleted_at.is_(None)
            ).first()

            if form:
                try:
                    data = json.loads(form.data)
                    metadata = json.loads(
                        form.form_metadata) if form.form_metadata else {}

                    return {
                        'data': data,
                        'metadata': metadata,
                        'version': form.version,
                        'created_at': form.created_at,
                        'updated_at': form.updated_at
                    }
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to parse form data",
                        form_id=form_id,
                        error=str(e)
                    )

            return None

    def delete_form(
        self,
        form_id: str,
        session_id: str,
        soft: bool = True
    ) -> bool:
        """
        Delete form data

        Args:
            form_id: Form ID
            session_id: Session ID
            soft: Whether to soft delete

        Returns:
            True if deleted
        """
        with self.db_manager.session_scope() as db_session:
            form = db_session.query(FormDataModel).filter(
                FormDataModel.form_id == form_id,
                FormDataModel.session_id == session_id
            ).first()

            if not form:
                return False

            if soft:
                form.deleted_at = datetime.utcnow()
            else:
                db_session.delete(form)

            logger.info(
                "Form deleted",
                form_id=form_id,
                soft=soft
            )

            return True

    def save_snapshot(self, snapshot: FormSnapshot) -> FormSnapshotModel:
        """
        Save form snapshot

        Args:
            snapshot: FormSnapshot to save

        Returns:
            Saved FormSnapshotModel
        """
        with self.db_manager.session_scope() as db_session:
            # Check if snapshot exists
            existing = db_session.query(FormSnapshotModel).filter(
                FormSnapshotModel.snapshot_id == snapshot.snapshot_id
            ).first()

            if existing:
                logger.warning(
                    "Snapshot already exists",
                    snapshot_id=snapshot.snapshot_id
                )
                return existing

            # Create new snapshot
            data_json = json.dumps(snapshot.data, default=str)

            new_snapshot = FormSnapshotModel(
                snapshot_id=snapshot.snapshot_id,
                form_id=snapshot.form_id,
                user_id=snapshot.user_id,
                session_id=snapshot.session_id,
                data=data_json,
                description=snapshot.description,
                snapshot_type=snapshot.snapshot_type,
                created_at=snapshot.timestamp
            )
            db_session.add(new_snapshot)
            db_session.flush()

            logger.debug(
                "Snapshot saved",
                snapshot_id=snapshot.snapshot_id,
                form_id=snapshot.form_id
            )

            return new_snapshot

    def load_snapshots(
        self,
        form_id: str,
        session_id: str = None,
        limit: int = None
    ) -> list[FormSnapshot]:
        """
        Load form snapshots

        Args:
            form_id: Form ID
            session_id: Optional session ID filter
            limit: Maximum number of snapshots to load

        Returns:
            List of FormSnapshot objects
        """
        with self.db_manager.session_scope() as db_session:
            query = db_session.query(FormSnapshotModel).filter(
                FormSnapshotModel.form_id == form_id
            )

            if session_id:
                query = query.filter(
                    FormSnapshotModel.session_id == session_id)

            query = query.order_by(FormSnapshotModel.created_at.desc())

            if limit:
                query = query.limit(limit)

            snapshots = []
            for model in query.all():
                try:
                    data = json.loads(model.data)
                    snapshot = FormSnapshot(
                        snapshot_id=model.snapshot_id,
                        form_id=model.form_id,
                        data=data,
                        timestamp=model.created_at,
                        description=model.description or "",
                        snapshot_type=model.snapshot_type,
                        user_id=model.user_id,
                        session_id=model.session_id
                    )
                    snapshots.append(snapshot)
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to parse snapshot data",
                        snapshot_id=model.snapshot_id,
                        error=str(e)
                    )

            return snapshots

    def cleanup_old_snapshots(
        self,
        form_id: str,
        keep_count: int = 50
    ) -> int:
        """
        Clean up old snapshots

        Args:
            form_id: Form ID
            keep_count: Number of snapshots to keep

        Returns:
            Number of snapshots deleted
        """
        with self.db_manager.session_scope() as db_session:
            # Get all snapshots ordered by creation time
            snapshots = db_session.query(FormSnapshotModel).filter(
                FormSnapshotModel.form_id == form_id
            ).order_by(FormSnapshotModel.created_at.desc()).all()

            if len(snapshots) <= keep_count:
                return 0

            # Delete old snapshots
            to_delete = snapshots[keep_count:]
            count = 0

            for snapshot in to_delete:
                db_session.delete(snapshot)
                count += 1

            logger.info(
                "Old snapshots cleaned up",
                form_id=form_id,
                deleted=count
            )

            return count

    def save_validation(
        self,
        form_id: str,
        session_id: str,
        validation_result: ValidationResult
    ) -> FormValidationModel:
        """
        Save validation result

        Args:
            form_id: Form ID
            session_id: Session ID
            validation_result: ValidationResult to save

        Returns:
            Saved FormValidationModel
        """
        with self.db_manager.session_scope() as db_session:
            # Check if validation exists
            existing = db_session.query(FormValidationModel).filter(
                FormValidationModel.form_id == form_id,
                FormValidationModel.session_id == session_id
            ).first()

            errors_json = json.dumps(validation_result.errors)
            warnings_json = json.dumps(validation_result.warnings)

            if existing:
                existing.errors = errors_json
                existing.warnings = warnings_json
                existing.is_valid = 1 if validation_result.is_valid else 0
                existing.validated_at = validation_result.validated_at
                return existing
            new_validation = FormValidationModel(
                form_id=form_id,
                session_id=session_id,
                errors=errors_json,
                warnings=warnings_json,
                is_valid=1 if validation_result.is_valid else 0,
                validated_at=validation_result.validated_at
            )
            db_session.add(new_validation)
            db_session.flush()
            return new_validation

    def load_validation(
        self,
        form_id: str,
        session_id: str
    ) -> ValidationResult | None:
        """
        Load validation result

        Args:
            form_id: Form ID
            session_id: Session ID

        Returns:
            ValidationResult or None
        """
        with self.db_manager.session_scope() as db_session:
            validation = db_session.query(FormValidationModel).filter(
                FormValidationModel.form_id == form_id,
                FormValidationModel.session_id == session_id
            ).first()

            if validation:
                try:
                    errors = json.loads(
                        validation.errors) if validation.errors else {}
                    warnings = json.loads(
                        validation.warnings) if validation.warnings else {}

                    return ValidationResult(
                        is_valid=bool(validation.is_valid),
                        errors=errors,
                        warnings=warnings,
                        validated_at=validation.validated_at
                    )
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to parse validation data",
                        form_id=form_id,
                        error=str(e)
                    )

            return None


# Global form repository
_form_repository: FormRepository | None = None
_repo_lock = threading.Lock()


def get_form_repository() -> FormRepository:
    """Get global form repository"""
    global _form_repository

    with _repo_lock:
        if _form_repository is None:
            _form_repository = FormRepository()

    return _form_repository


# Convenience function for transactional form save

def save_form(
    form_id: str,
    data: dict[str, Any],
    user_id: str = None,
    session_id: str = None,
    metadata: dict[str, Any] = None
) -> dict[str, Any]:
    """
    Save form data with transaction

    Args:
        form_id: Form ID
        data: Form data
        user_id: User ID
        session_id: Session ID
        metadata: Additional metadata

    Returns:
        Saved form data dictionary
    """
    repo = get_form_repository()

    try:
        form_model = repo.save_form(
            form_id=form_id,
            data=data,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata
        )

        logger.info(
            "Form saved successfully",
            form_id=form_id,
            version=form_model.version
        )

        return {
            'form_id': form_id,
            'data': data,
            'version': form_model.version,
            'updated_at': form_model.updated_at
        }
    except Exception as e:
        logger.error(
            "Form save failed",
            form_id=form_id,
            error=str(e)
        )
        raise


# Form Validation Engine

class FormValidator:
    """Form validation engine with configurable rules"""

    def __init__(self):
        self._validators: dict[str, list[Callable]] = {}
        self._debounce_timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def register_validator(
        self,
        form_id: str,
        field: str,
        validator: Callable[[Any], tuple[bool, str | None]]
    ) -> None:
        """
        Register field validator

        Args:
            form_id: Form ID
            field: Field name
            validator: Validation function returning (is_valid, error_message)
        """
        key = f"{form_id}.{field}"

        with self._lock:
            if key not in self._validators:
                self._validators[key] = []
            self._validators[key].append(validator)

        logger.debug(
            "Validator registered",
            form_id=form_id,
            field=field
        )

    def register_form_validator(
        self,
        form_id: str,
        validator: Callable[[dict[str, Any]], tuple[bool, dict[str, list[str]]]]
    ) -> None:
        """
        Register form-level validator

        Args:
            form_id: Form ID
            validator: Validation function returning (is_valid, errors_dict)
        """
        key = f"{form_id}.__form__"

        with self._lock:
            if key not in self._validators:
                self._validators[key] = []
            self._validators[key].append(validator)

        logger.debug("Form validator registered", form_id=form_id)

    def validate_field(
        self,
        form_id: str,
        field: str,
        value: Any
    ) -> ValidationResult:
        """
        Validate single field

        Args:
            form_id: Form ID
            field: Field name
            value: Field value

        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        key = f"{form_id}.{field}"

        validators = self._validators.get(key, [])

        for validator in validators:
            try:
                is_valid, error_msg = validator(value)
                if not is_valid and error_msg:
                    result.add_error(field, error_msg)
            except Exception as e:
                logger.error(
                    "Validator failed",
                    form_id=form_id,
                    field=field,
                    error=str(e)
                )
                result.add_error(field, f"Validation error: {str(e)}")

        return result

    def validate_form(
        self,
        form_id: str,
        data: dict[str, Any]
    ) -> ValidationResult:
        """
        Validate entire form

        Args:
            form_id: Form ID
            data: Form data

        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)

        # Validate individual fields
        for field, value in data.items():
            field_result = self.validate_field(form_id, field, value)
            if not field_result.is_valid:
                result.is_valid = False
                result.errors.update(field_result.errors)
            result.warnings.update(field_result.warnings)

        # Run form-level validators
        key = f"{form_id}.__form__"
        form_validators = self._validators.get(key, [])

        for validator in form_validators:
            try:
                is_valid, errors_dict = validator(data)
                if not is_valid:
                    result.is_valid = False
                    for field, errors in errors_dict.items():
                        for error in errors:
                            result.add_error(field, error)
            except Exception as e:
                logger.error(
                    "Form validator failed",
                    form_id=form_id,
                    error=str(e)
                )
                result.add_error("__form__", f"Validation error: {str(e)}")

        return result

    def validate_debounced(
        self,
        form_id: str,
        data: dict[str, Any],
        callback: Callable[[ValidationResult], None],
        debounce_ms: int = 300
    ) -> None:
        """
        Validate form with debouncing

        Args:
            form_id: Form ID
            data: Form data
            callback: Callback function to receive validation result
            debounce_ms: Debounce delay in milliseconds
        """
        with self._lock:
            # Cancel existing timer
            if form_id in self._debounce_timers:
                self._debounce_timers[form_id].cancel()

            # Schedule new validation
            def validate_and_callback():
                result = self.validate_form(form_id, data)
                callback(result)

                with self._lock:
                    self._debounce_timers.pop(form_id, None)

            timer = threading.Timer(
                debounce_ms / 1000.0,
                validate_and_callback
            )
            self._debounce_timers[form_id] = timer
            timer.start()

    def clear_validators(self, form_id: str) -> None:
        """Clear all validators for form"""
        with self._lock:
            keys_to_remove = [
                k for k in self._validators.keys() if k.startswith(
                    f"{form_id}.")]
            for key in keys_to_remove:
                del self._validators[key]

        logger.debug("Validators cleared", form_id=form_id)


# Global form validator
_form_validator: FormValidator | None = None
_validator_lock = threading.Lock()


def get_form_validator() -> FormValidator:
    """Get global form validator"""
    global _form_validator

    with _validator_lock:
        if _form_validator is None:
            _form_validator = FormValidator()

    return _form_validator


# Form Auto-Save System

class FormAutoSave:
    """Auto-save system with debouncing and conflict resolution"""

    def __init__(
        self,
        repository: FormRepository = None,
        debounce_ms: int = 500
    ):
        self.repository = repository or get_form_repository()
        self.debounce_ms = debounce_ms
        self._pending_saves: dict[str, threading.Timer] = {}
        self._save_status: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def schedule_save(
        self,
        form_state: FormState,
        callback: Callable[[bool, str | None], None] | None = None
    ) -> None:
        """
        Schedule auto-save with debouncing

        Args:
            form_state: FormState to save
            callback: Optional callback(success, error_message)
        """
        form_id = form_state.form_id

        with self._lock:
            # Cancel existing timer
            if form_id in self._pending_saves:
                self._pending_saves[form_id].cancel()

            # Update save status
            self._save_status[form_id] = {
                'status': 'pending',
                'scheduled_at': datetime.now()
            }

            # Schedule new save
            def execute_save():
                self._execute_save(form_state, callback)

            timer = threading.Timer(
                self.debounce_ms / 1000.0,
                execute_save
            )
            self._pending_saves[form_id] = timer
            timer.start()

            logger.debug(
                "Auto-save scheduled",
                form_id=form_id,
                debounce_ms=self.debounce_ms
            )

    def _execute_save(
        self,
        form_state: FormState,
        callback: Callable[[bool, str | None], None] | None
    ) -> None:
        """Execute the actual save"""
        form_id = form_state.form_id

        try:
            # Update save status
            with self._lock:
                self._save_status[form_id] = {
                    'status': 'saving',
                    'started_at': datetime.now()
                }

            # Save form data
            self.repository.save_form(
                form_id=form_state.form_id,
                data=form_state.data,
                user_id=form_state.user_id,
                session_id=form_state.session_id,
                metadata=form_state.metadata
            )

            # Mark form as clean
            form_state.mark_clean()

            # Update save status
            with self._lock:
                self._save_status[form_id] = {
                    'status': 'saved',
                    'saved_at': datetime.now()
                }
                self._pending_saves.pop(form_id, None)

            logger.info("Form auto-saved", form_id=form_id)

            # Call callback
            if callback:
                callback(True, None)

        except Exception as e:
            error_msg = str(e)
            logger.error(
                "Form auto-save failed",
                form_id=form_id,
                error=error_msg
            )

            # Update save status
            with self._lock:
                self._save_status[form_id] = {
                    'status': 'error',
                    'error': error_msg,
                    'failed_at': datetime.now()
                }
                self._pending_saves.pop(form_id, None)

            # Call callback
            if callback:
                callback(False, error_msg)

    def flush(self, form_id: str = None) -> None:
        """
        Immediately execute pending saves

        Args:
            form_id: Optional form ID to flush (all if None)
        """
        with self._lock:
            if form_id:
                timer = self._pending_saves.get(form_id)
                if timer:
                    timer.cancel()
                    timer.function()
            else:
                # Flush all
                for timer in list(self._pending_saves.values()):
                    timer.cancel()
                    timer.function()
                self._pending_saves.clear()

    def get_save_status(self, form_id: str) -> dict[str, Any] | None:
        """Get save status for form"""
        with self._lock:
            return self._save_status.get(form_id)

    def resolve_conflict(
        self,
        form_id: str,
        session_id: str,
        local_data: dict[str, Any],
        local_updated_at: datetime,
        strategy: str = 'last_write_wins'
    ) -> tuple[dict[str, Any], bool]:
        """
        Resolve save conflict

        Args:
            form_id: Form ID
            session_id: Session ID
            local_data: Local form data
            local_updated_at: Local update timestamp
            strategy: Conflict resolution strategy

        Returns:
            Tuple of (resolved_data, was_conflict)
        """
        try:
            # Load remote data
            remote_form = self.repository.load_form(form_id, session_id)

            if not remote_form:
                # No conflict, use local data
                return local_data, False

            remote_data = remote_form['data']
            remote_updated_at = remote_form['updated_at']

            if strategy == 'last_write_wins':
                if local_updated_at > remote_updated_at:
                    logger.info(
                        "Conflict resolved: local wins",
                        form_id=form_id
                    )
                    return local_data, True
                logger.info(
                    "Conflict resolved: remote wins",
                    form_id=form_id
                )
                return remote_data, True

            if strategy == 'prefer_local':
                return local_data, True

            if strategy == 'prefer_remote':
                return remote_data, True

            if strategy == 'merge':
                # Simple merge: remote data + local changes
                merged = remote_data.copy()
                merged.update(local_data)
                logger.info(
                    "Conflict resolved: merged",
                    form_id=form_id
                )
                return merged, True

            raise ValueError(
                f"Unknown conflict resolution strategy: {strategy}")

        except Exception as e:
            logger.error(
                "Conflict resolution failed",
                form_id=form_id,
                error=str(e)
            )
            return local_data, False

    def recover_form(
        self,
        form_id: str,
        session_id: str
    ) -> FormState | None:
        """
        Recover form after unexpected termination

        Args:
            form_id: Form ID
            session_id: Session ID

        Returns:
            Recovered FormState or None
        """
        try:
            # Load form data
            form_data = self.repository.load_form(form_id, session_id)

            if not form_data:
                return None

            # Load snapshots
            snapshots = self.repository.load_snapshots(
                form_id, session_id, limit=50)

            # Load validation
            validation = self.repository.load_validation(form_id, session_id)

            # Create FormState
            form_state = FormState(
                form_id=form_id,
                data=form_data['data'],
                session_id=session_id,
                version=form_data['version'],
                created_at=form_data['created_at'],
                updated_at=form_data['updated_at'],
                last_saved=form_data['updated_at'],
                is_dirty=False
            )

            # Restore snapshots
            form_state.snapshots = deque(
                snapshots, maxlen=form_state.max_snapshots)
            form_state.current_snapshot_index = len(
                snapshots) - 1 if snapshots else -1

            # Restore validation
            if validation:
                form_state.last_validation = validation
                form_state.errors = validation.errors
                form_state.warnings = validation.warnings

            logger.info(
                "Form recovered",
                form_id=form_id,
                snapshots=len(snapshots)
            )

            return form_state

        except Exception as e:
            logger.error(
                "Form recovery failed",
                form_id=form_id,
                error=str(e)
            )
            return None


# Global auto-save system
_auto_save: FormAutoSave | None = None
_auto_save_lock = threading.Lock()


def get_auto_save() -> FormAutoSave:
    """Get global auto-save system"""
    global _auto_save

    with _auto_save_lock:
        if _auto_save is None:
            _auto_save = FormAutoSave()

    return _auto_save


# Form Manager - High-level API

class FormManager:
    """High-level form management with undo/redo, validation, and auto-save"""

    def __init__(
        self,
        repository: FormRepository = None,
        validator: FormValidator = None,
        auto_save: FormAutoSave = None
    ):
        self.repository = repository or get_form_repository()
        self.validator = validator or get_form_validator()
        self.auto_save = auto_save or get_auto_save()
        self._forms: dict[str, FormState] = {}
        self._lock = threading.Lock()

    def get_form(
        self,
        form_id: str,
        session_id: str,
        user_id: str = None,
        auto_save_enabled: bool = True,
        max_snapshots: int = 50
    ) -> FormState:
        """
        Get or create form state

        Args:
            form_id: Form ID
            session_id: Session ID
            user_id: User ID
            auto_save_enabled: Whether to enable auto-save
            max_snapshots: Maximum number of snapshots to keep

        Returns:
            FormState instance
        """
        key = f"{session_id}:{form_id}"

        with self._lock:
            if key in self._forms:
                return self._forms[key]

            # Try to recover from database
            form_state = self.auto_save.recover_form(form_id, session_id)

            if not form_state:
                # Create new form state
                form_state = FormState(
                    form_id=form_id,
                    session_id=session_id,
                    user_id=user_id,
                    auto_save=auto_save_enabled,
                    max_snapshots=max_snapshots
                )

                logger.info("New form created", form_id=form_id)
            else:
                logger.info("Form recovered", form_id=form_id)

            self._forms[key] = form_state
            return form_state

    def update_field(
        self,
        form_id: str,
        session_id: str,
        field: str,
        value: Any,
        create_snapshot: bool = True,
        validate: bool = True
    ) -> ValidationResult:
        """
        Update form field

        Args:
            form_id: Form ID
            session_id: Session ID
            field: Field name
            value: Field value
            create_snapshot: Whether to create snapshot
            validate: Whether to validate

        Returns:
            ValidationResult
        """
        form_state = self.get_form(form_id, session_id)

        # Update data
        form_state.update_data(field, value, create_snapshot=create_snapshot)

        # Validate if requested
        validation_result = ValidationResult(is_valid=True)
        if validate:
            validation_result = self.validator.validate_field(
                form_id, field, value)

            # Update form state with validation results
            if validation_result.has_errors():
                form_state.errors[field] = validation_result.errors.get(
                    field, [])
            else:
                form_state.errors.pop(field, None)

            if validation_result.has_warnings():
                form_state.warnings[field] = validation_result.warnings.get(
                    field, [])
            else:
                form_state.warnings.pop(field, None)

            form_state.last_validation = validation_result

        # Schedule auto-save if enabled
        if form_state.auto_save:
            self.auto_save.schedule_save(form_state)

        return validation_result

    def update_multiple(
        self,
        form_id: str,
        session_id: str,
        updates: dict[str, Any],
        create_snapshot: bool = True,
        validate: bool = True
    ) -> ValidationResult:
        """
        Update multiple form fields

        Args:
            form_id: Form ID
            session_id: Session ID
            updates: Dictionary of field updates
            create_snapshot: Whether to create snapshot
            validate: Whether to validate

        Returns:
            ValidationResult
        """
        form_state = self.get_form(form_id, session_id)

        # Update data
        form_state.update_multiple(updates, create_snapshot=create_snapshot)

        # Validate if requested
        validation_result = ValidationResult(is_valid=True)
        if validate:
            validation_result = self.validator.validate_form(
                form_id, form_state.data)

            # Update form state with validation results
            form_state.errors = validation_result.errors
            form_state.warnings = validation_result.warnings
            form_state.last_validation = validation_result

        # Schedule auto-save if enabled
        if form_state.auto_save:
            self.auto_save.schedule_save(form_state)

        return validation_result

    def save(
        self,
        form_id: str,
        session_id: str,
        immediate: bool = True
    ) -> bool:
        """
        Save form

        Args:
            form_id: Form ID
            session_id: Session ID
            immediate: Whether to save immediately

        Returns:
            True if save was successful
        """
        form_state = self.get_form(form_id, session_id)

        if immediate:
            try:
                self.repository.save_form(
                    form_id=form_state.form_id,
                    data=form_state.data,
                    user_id=form_state.user_id,
                    session_id=form_state.session_id,
                    metadata=form_state.metadata
                )
                form_state.mark_clean()
                logger.info("Form saved", form_id=form_id)
                return True
            except Exception as e:
                logger.error("Form save failed", form_id=form_id, error=str(e))
                return False
        else:
            self.auto_save.schedule_save(form_state)
            return True

    def undo(self, form_id: str, session_id: str) -> bool:
        """Undo form change"""
        form_state = self.get_form(form_id, session_id)
        success = form_state.undo()

        if success and form_state.auto_save:
            self.auto_save.schedule_save(form_state)

        return success

    def redo(self, form_id: str, session_id: str) -> bool:
        """Redo form change"""
        form_state = self.get_form(form_id, session_id)
        success = form_state.redo()

        if success and form_state.auto_save:
            self.auto_save.schedule_save(form_state)

        return success

    def can_undo(self, form_id: str, session_id: str) -> bool:
        """Check if undo is available"""
        form_state = self.get_form(form_id, session_id)
        return form_state.can_undo()

    def can_redo(self, form_id: str, session_id: str) -> bool:
        """Check if redo is available"""
        form_state = self.get_form(form_id, session_id)
        return form_state.can_redo()

    def create_snapshot(
        self,
        form_id: str,
        session_id: str,
        description: str = "",
        snapshot_type: str = "manual",
        persist: bool = True
    ) -> FormSnapshot:
        """
        Create form snapshot

        Args:
            form_id: Form ID
            session_id: Session ID
            description: Snapshot description
            snapshot_type: Snapshot type
            persist: Whether to persist to database

        Returns:
            Created FormSnapshot
        """
        form_state = self.get_form(form_id, session_id)
        snapshot = form_state.create_snapshot(description, snapshot_type)

        if persist:
            self.repository.save_snapshot(snapshot)

        return snapshot

    def get_snapshot_history(
        self,
        form_id: str,
        session_id: str
    ) -> list[FormSnapshot]:
        """Get snapshot history"""
        form_state = self.get_form(form_id, session_id)
        return form_state.get_snapshot_history()

    def restore_snapshot(
        self,
        form_id: str,
        session_id: str,
        snapshot_id: str
    ) -> bool:
        """Restore specific snapshot"""
        form_state = self.get_form(form_id, session_id)
        success = form_state.restore_snapshot(snapshot_id)

        if success and form_state.auto_save:
            self.auto_save.schedule_save(form_state)

        return success

    def validate(
        self,
        form_id: str,
        session_id: str,
        debounced: bool = False,
        debounce_ms: int = 300
    ) -> ValidationResult | None:
        """
        Validate form

        Args:
            form_id: Form ID
            session_id: Session ID
            debounced: Whether to use debounced validation
            debounce_ms: Debounce delay in milliseconds

        Returns:
            ValidationResult (None if debounced)
        """
        form_state = self.get_form(form_id, session_id)

        if debounced:
            def callback(result: ValidationResult):
                form_state.last_validation = result
                form_state.errors = result.errors
                form_state.warnings = result.warnings

            self.validator.validate_debounced(
                form_id,
                form_state.data,
                callback,
                debounce_ms
            )
            return None
        result = self.validator.validate_form(form_id, form_state.data)
        form_state.last_validation = result
        form_state.errors = result.errors
        form_state.warnings = result.warnings
        return result

    def reset(
        self,
        form_id: str,
        session_id: str,
        create_snapshot: bool = True
    ) -> None:
        """
        Reset form to initial state

        Args:
            form_id: Form ID
            session_id: Session ID
            create_snapshot: Whether to create snapshot before reset
        """
        form_state = self.get_form(form_id, session_id)

        if create_snapshot:
            form_state.create_snapshot(
                description="Before reset",
                snapshot_type="checkpoint")

        form_state.data.clear()
        form_state.errors.clear()
        form_state.warnings.clear()
        form_state.is_dirty = True
        form_state.updated_at = datetime.now()

        if form_state.auto_save:
            self.auto_save.schedule_save(form_state)

        logger.info("Form reset", form_id=form_id)

    def get_save_status(self, form_id: str) -> dict[str, Any] | None:
        """Get save status"""
        return self.auto_save.get_save_status(form_id)

    def is_dirty(self, form_id: str, session_id: str) -> bool:
        """Check if form has unsaved changes"""
        form_state = self.get_form(form_id, session_id)
        return form_state.is_dirty

    def is_valid(self, form_id: str, session_id: str) -> bool:
        """Check if form is valid"""
        form_state = self.get_form(form_id, session_id)
        if form_state.last_validation:
            return form_state.last_validation.is_valid
        return True

    def cleanup_old_snapshots(
        self,
        form_id: str,
        keep_count: int = 50
    ) -> int:
        """Clean up old snapshots"""
        return self.repository.cleanup_old_snapshots(form_id, keep_count)


# Global form manager
_form_manager: FormManager | None = None
_manager_lock = threading.Lock()


def get_form_manager() -> FormManager:
    """Get global form manager"""
    global _form_manager

    with _manager_lock:
        if _form_manager is None:
            _form_manager = FormManager()

    return _form_manager


# Convenience functions for common operations

def create_form(
    form_id: str,
    session_id: str,
    user_id: str = None,
    initial_data: dict[str, Any] = None
) -> FormState:
    """Create new form"""
    manager = get_form_manager()
    form_state = manager.get_form(form_id, session_id, user_id)

    if initial_data:
        form_state.data.update(initial_data)

    return form_state


def update_form_field(
    form_id: str,
    session_id: str,
    field: str,
    value: Any
) -> ValidationResult:
    """Update form field"""
    manager = get_form_manager()
    return manager.update_field(form_id, session_id, field, value)


def save_form_now(form_id: str, session_id: str) -> bool:
    """Save form immediately"""
    manager = get_form_manager()
    return manager.save(form_id, session_id, immediate=True)


def undo_form(form_id: str, session_id: str) -> bool:
    """Undo form change"""
    manager = get_form_manager()
    return manager.undo(form_id, session_id)


def redo_form(form_id: str, session_id: str) -> bool:
    """Redo form change"""
    manager = get_form_manager()
    return manager.redo(form_id, session_id)


def validate_form(form_id: str, session_id: str) -> ValidationResult:
    """Validate form"""
    manager = get_form_manager()
    return manager.validate(form_id, session_id, debounced=False)


def reset_form(form_id: str, session_id: str) -> None:
    """Reset form"""
    manager = get_form_manager()
    manager.reset(form_id, session_id)
