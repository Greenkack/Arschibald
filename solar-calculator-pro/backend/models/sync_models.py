"""
Synchronization Database Models
Defines database models for data synchronization system
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from backend.core.database import Base


class SyncStatus(str, enum.Enum):
    """Synchronization status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class ConflictResolution(str, enum.Enum):
    """Conflict resolution strategy enumeration"""
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    MANUAL = "manual"
    MERGE = "merge"
    LATEST_WINS = "latest_wins"


class SyncOperation(Base):
    """Synchronization operation tracking"""
    __tablename__ = "sync_operations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)  # project, customer, product, etc.
    entity_id = Column(Integer, nullable=False, index=True)
    operation_type = Column(String(50), nullable=False)  # create, update, delete
    status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, index=True)
    conflict_resolution = Column(SQLEnum(ConflictResolution), nullable=True)
    
    # Data
    data_snapshot = Column(JSON, nullable=True)  # Current data state
    changes = Column(JSON, nullable=True)  # Changes to apply
    conflict_data = Column(JSON, nullable=True)  # Conflicting data if any
    
    # Metadata
    client_timestamp = Column(DateTime, nullable=False)
    server_timestamp = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_version = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SyncSchedule(Base):
    """Synchronization schedule configuration"""
    __tablename__ = "sync_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    
    # Schedule configuration
    enabled = Column(Boolean, default=True)
    sync_interval = Column(Integer, default=300)  # seconds
    auto_sync = Column(Boolean, default=True)
    sync_on_startup = Column(Boolean, default=True)
    sync_on_shutdown = Column(Boolean, default=True)
    
    # Entity filters
    entity_types = Column(JSON, nullable=True)  # List of entity types to sync
    
    # Last sync info
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(SQLEnum(SyncStatus), nullable=True)
    next_sync_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SyncConflict(Base):
    """Synchronization conflict tracking"""
    __tablename__ = "sync_conflicts"

    id = Column(Integer, primary_key=True, index=True)
    sync_operation_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Conflict details
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    conflict_type = Column(String(50), nullable=False)  # version, data, delete
    
    # Conflicting data
    server_data = Column(JSON, nullable=False)
    client_data = Column(JSON, nullable=False)
    server_version = Column(Integer, nullable=False)
    client_version = Column(Integer, nullable=False)
    server_timestamp = Column(DateTime, nullable=False)
    client_timestamp = Column(DateTime, nullable=False)
    
    # Resolution
    resolution_strategy = Column(SQLEnum(ConflictResolution), nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, nullable=True)
    resolved_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SyncLog(Base):
    """Synchronization activity log"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    
    # Log details
    sync_session_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # start, complete, error, conflict
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Statistics
    operations_total = Column(Integer, default=0)
    operations_completed = Column(Integer, default=0)
    operations_failed = Column(Integer, default=0)
    conflicts_detected = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())


class OfflineSyncQueue(Base):
    """Queue for offline synchronization operations"""
    __tablename__ = "offline_sync_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    
    # Operation details
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)  # Null for create operations
    operation_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)
    
    # Queue management
    priority = Column(Integer, default=0)  # Higher = more important
    queued_at = Column(DateTime, server_default=func.now())
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
