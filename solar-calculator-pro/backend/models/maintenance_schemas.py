"""
Pydantic schemas for system maintenance
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class MaintenanceOperationType(str, Enum):
    DATABASE = "database"
    CACHE = "cache"
    LOGS = "logs"
    TEMP_FILES = "temp_files"
    DIAGNOSTICS = "diagnostics"
    REPAIR = "repair"


class MaintenanceStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"


class DiagnosticStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


# Database Maintenance
class DatabaseMaintenanceRequest(BaseModel):
    operation: str = Field(..., description="vacuum, analyze, reindex, optimize")
    tables: Optional[List[str]] = Field(None, description="Specific tables to maintain")
    full: bool = Field(False, description="Full maintenance operation")


class DatabaseMaintenanceResponse(BaseModel):
    operation: str
    status: MaintenanceStatus
    tables_processed: List[str]
    duration_seconds: float
    details: Dict[str, Any]


# Cache Management
class CacheStatsResponse(BaseModel):
    total_entries: int
    total_size_bytes: int
    total_size_mb: float
    cache_types: Dict[str, int]
    hit_rate: float
    oldest_entry: Optional[datetime]
    newest_entry: Optional[datetime]


class CacheClearRequest(BaseModel):
    cache_type: Optional[str] = Field(None, description="Specific cache type to clear")
    older_than_days: Optional[int] = Field(None, description="Clear entries older than X days")
    unused_only: bool = Field(False, description="Clear only unused entries")


class CacheClearResponse(BaseModel):
    entries_cleared: int
    size_freed_mb: float
    duration_seconds: float


# Log Management
class LogStatsResponse(BaseModel):
    total_log_files: int
    total_size_bytes: int
    total_size_mb: float
    log_types: Dict[str, int]
    oldest_log: Optional[datetime]
    newest_log: Optional[datetime]
    error_count_24h: int
    warning_count_24h: int


class LogCleanupRequest(BaseModel):
    older_than_days: int = Field(30, description="Delete logs older than X days")
    log_level: Optional[str] = Field(None, description="Specific log level to clean")
    compress_before_delete: bool = Field(True, description="Compress logs before deletion")


class LogCleanupResponse(BaseModel):
    files_deleted: int
    files_compressed: int
    size_freed_mb: float
    duration_seconds: float


# Temp File Cleanup
class TempFileStatsResponse(BaseModel):
    total_files: int
    total_size_bytes: int
    total_size_mb: float
    file_types: Dict[str, int]
    oldest_file: Optional[datetime]
    files_to_delete: int


class TempFileCleanupRequest(BaseModel):
    older_than_hours: int = Field(24, description="Delete files older than X hours")
    file_types: Optional[List[str]] = Field(None, description="Specific file types to clean")
    force: bool = Field(False, description="Force delete even if recently accessed")


class TempFileCleanupResponse(BaseModel):
    files_deleted: int
    size_freed_mb: float
    duration_seconds: float


# System Diagnostics
class DiagnosticResult(BaseModel):
    diagnostic_type: str
    status: DiagnosticStatus
    metrics: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    checked_at: datetime


class SystemDiagnosticsResponse(BaseModel):
    overall_status: DiagnosticStatus
    diagnostics: List[DiagnosticResult]
    summary: Dict[str, Any]


class DiagnosticRequest(BaseModel):
    diagnostic_types: Optional[List[str]] = Field(
        None, 
        description="Specific diagnostics to run: database, disk, memory, cpu, network, services"
    )
    detailed: bool = Field(False, description="Include detailed metrics")


# Repair Tools
class RepairOperation(str, Enum):
    FIX_PERMISSIONS = "fix_permissions"
    REBUILD_INDEX = "rebuild_index"
    REPAIR_DATABASE = "repair_database"
    RESET_CACHE = "reset_cache"
    FIX_ORPHANED_FILES = "fix_orphaned_files"
    REPAIR_CORRUPTED_DATA = "repair_corrupted_data"


class RepairRequest(BaseModel):
    operation: RepairOperation
    target: Optional[str] = Field(None, description="Specific target for repair")
    dry_run: bool = Field(True, description="Simulate repair without making changes")
    backup_first: bool = Field(True, description="Create backup before repair")


class RepairResponse(BaseModel):
    operation: RepairOperation
    status: MaintenanceStatus
    items_repaired: int
    items_failed: int
    backup_created: Optional[str]
    details: Dict[str, Any]
    duration_seconds: float


# Maintenance Schedule
class MaintenanceSchedule(BaseModel):
    id: Optional[int]
    operation_type: MaintenanceOperationType
    operation_name: str
    schedule_cron: str = Field(..., description="Cron expression for schedule")
    enabled: bool = True
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    config: Dict[str, Any] = {}


class MaintenanceLogResponse(BaseModel):
    id: int
    operation_type: str
    operation_name: str
    status: MaintenanceStatus
    details: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    performed_by: Optional[str]

    class Config:
        from_attributes = True
