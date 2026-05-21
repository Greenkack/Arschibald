"""
Synchronization Pydantic Schemas
Defines request/response schemas for synchronization API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SyncStatusEnum(str, Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class ConflictResolutionEnum(str, Enum):
    """Conflict resolution strategy"""
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    MANUAL = "manual"
    MERGE = "merge"
    LATEST_WINS = "latest_wins"


class SyncOperationCreate(BaseModel):
    """Create synchronization operation"""
    entity_type: str = Field(..., description="Type of entity to sync")
    entity_id: int = Field(..., description="ID of entity to sync")
    operation_type: str = Field(..., description="Operation type: create, update, delete")
    data_snapshot: Optional[Dict[str, Any]] = Field(None, description="Current data state")
    changes: Dict[str, Any] = Field(..., description="Changes to apply")
    client_timestamp: datetime = Field(..., description="Client timestamp")
    version: int = Field(1, description="Data version")
    parent_version: Optional[int] = Field(None, description="Parent version for conflict detection")


class SyncOperationResponse(BaseModel):
    """Synchronization operation response"""
    id: int
    user_id: int
    device_id: str
    entity_type: str
    entity_id: int
    operation_type: str
    status: SyncStatusEnum
    conflict_resolution: Optional[ConflictResolutionEnum]
    client_timestamp: datetime
    server_timestamp: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    version: int
    
    class Config:
        from_attributes = True


class SyncBatchRequest(BaseModel):
    """Batch synchronization request"""
    device_id: str = Field(..., description="Device identifier")
    operations: List[SyncOperationCreate] = Field(..., description="List of sync operations")
    force_sync: bool = Field(False, description="Force sync even if conflicts exist")


class SyncBatchResponse(BaseModel):
    """Batch synchronization response"""
    sync_session_id: str
    total_operations: int
    completed: int
    failed: int
    conflicts: int
    operations: List[SyncOperationResponse]


class ConflictDetails(BaseModel):
    """Conflict details"""
    id: int
    sync_operation_id: int
    entity_type: str
    entity_id: int
    conflict_type: str
    server_data: Dict[str, Any]
    client_data: Dict[str, Any]
    server_version: int
    client_version: int
    server_timestamp: datetime
    client_timestamp: datetime
    resolved: bool
    
    class Config:
        from_attributes = True


class ConflictResolutionRequest(BaseModel):
    """Conflict resolution request"""
    conflict_id: int
    resolution_strategy: ConflictResolutionEnum
    resolved_data: Optional[Dict[str, Any]] = None


class SyncScheduleCreate(BaseModel):
    """Create sync schedule"""
    device_id: str
    enabled: bool = True
    sync_interval: int = Field(300, ge=60, le=86400, description="Sync interval in seconds")
    auto_sync: bool = True
    sync_on_startup: bool = True
    sync_on_shutdown: bool = True
    entity_types: Optional[List[str]] = None


class SyncScheduleResponse(BaseModel):
    """Sync schedule response"""
    id: int
    user_id: int
    device_id: str
    enabled: bool
    sync_interval: int
    auto_sync: bool
    sync_on_startup: bool
    sync_on_shutdown: bool
    entity_types: Optional[List[str]]
    last_sync_at: Optional[datetime]
    last_sync_status: Optional[SyncStatusEnum]
    next_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SyncStatusResponse(BaseModel):
    """Synchronization status response"""
    device_id: str
    is_syncing: bool
    last_sync_at: Optional[datetime]
    last_sync_status: Optional[SyncStatusEnum]
    pending_operations: int
    conflicts_count: int
    offline_queue_size: int
    next_sync_at: Optional[datetime]


class OfflineSyncQueueItem(BaseModel):
    """Offline sync queue item"""
    entity_type: str
    entity_id: Optional[int]
    operation_type: str
    data: Dict[str, Any]
    priority: int = 0


class OfflineSyncQueueResponse(BaseModel):
    """Offline sync queue response"""
    id: int
    entity_type: str
    entity_id: Optional[int]
    operation_type: str
    priority: int
    queued_at: datetime
    processed: bool
    
    class Config:
        from_attributes = True


class SyncLogEntry(BaseModel):
    """Sync log entry"""
    id: int
    sync_session_id: str
    event_type: str
    message: str
    details: Optional[Dict[str, Any]]
    operations_total: int
    operations_completed: int
    operations_failed: int
    conflicts_detected: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SyncStatistics(BaseModel):
    """Synchronization statistics"""
    total_syncs: int
    successful_syncs: int
    failed_syncs: int
    total_conflicts: int
    resolved_conflicts: int
    pending_conflicts: int
    average_sync_duration: float
    last_24h_syncs: int
    data_synced_mb: float
