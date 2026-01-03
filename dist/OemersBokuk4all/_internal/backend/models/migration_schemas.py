"""
Migration Pydantic Schemas
Task 235: Data Migration Implementation

Defines all request/response models for migration API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime


class MigrationStatusEnum(str, Enum):
    """Migration status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DataTypeEnum(str, Enum):
    """Data types for migration"""
    USER_SETTINGS = "user_settings"
    PROJECTS = "projects"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    PRICE_MATRICES = "price_matrices"
    CRM_DATA = "crm_data"
    PDF_TEMPLATES = "pdf_templates"
    SYSTEM_CONFIG = "system_config"


class MigrationStartRequest(BaseModel):
    """Request to start a new migration"""
    source_db_path: str = Field(
        ...,
        description="Path to the source SQLite database",
        example="/path/to/streamlit/database.db"
    )
    target_db_path: str = Field(
        ...,
        description="Path to the target database",
        example="/path/to/electron/database.db"
    )
    backup_dir: str = Field(
        default="backups/migrations",
        description="Directory for storing backups"
    )
    data_types: Optional[List[DataTypeEnum]] = Field(
        default=None,
        description="Specific data types to migrate. If null, migrates all."
    )
    validate_before: bool = Field(
        default=True,
        description="Validate data before migration"
    )
    create_backup: bool = Field(
        default=True,
        description="Create backup before migration"
    )


class MigrationStartResponse(BaseModel):
    """Response after starting a migration"""
    migration_id: str = Field(..., description="Unique migration identifier")
    status: MigrationStatusEnum = Field(..., description="Current migration status")
    message: str = Field(..., description="Status message")
    started_at: datetime = Field(..., description="Migration start time")
    backup_path: Optional[str] = Field(None, description="Path to backup file")


class DataTypeProgress(BaseModel):
    """Progress for a specific data type"""
    data_type: DataTypeEnum = Field(..., description="Type of data being migrated")
    status: MigrationStatusEnum = Field(..., description="Status of this data type migration")
    total_records: int = Field(0, description="Total records to migrate")
    migrated_records: int = Field(0, description="Successfully migrated records")
    failed_records: int = Field(0, description="Failed records")
    progress_percent: float = Field(0.0, description="Progress percentage")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")


class MigrationProgressResponse(BaseModel):
    """Response with migration progress"""
    migration_id: str = Field(..., description="Migration identifier")
    overall_status: MigrationStatusEnum = Field(..., description="Overall migration status")
    total_records: int = Field(0, description="Total records across all types")
    migrated_records: int = Field(0, description="Total migrated records")
    failed_records: int = Field(0, description="Total failed records")
    progress_percent: float = Field(0.0, description="Overall progress percentage")
    data_type_progress: Dict[str, DataTypeProgress] = Field(
        default_factory=dict,
        description="Progress by data type"
    )
    estimated_time_remaining: Optional[str] = Field(
        None,
        description="Estimated time remaining"
    )


class RollbackRequest(BaseModel):
    """Request to rollback a migration"""
    migration_id: str = Field(..., description="Migration to rollback")
    backup_path: Optional[str] = Field(
        None,
        description="Specific backup to use. If null, uses migration's backup."
    )
    confirm: bool = Field(
        default=False,
        description="Confirm rollback operation"
    )


class RollbackResponse(BaseModel):
    """Response after rollback"""
    migration_id: str = Field(..., description="Migration identifier")
    status: MigrationStatusEnum = Field(..., description="Status after rollback")
    message: str = Field(..., description="Rollback result message")
    backup_used: str = Field(..., description="Backup file used for rollback")
    rolled_back_at: datetime = Field(..., description="Rollback timestamp")


class ValidationError(BaseModel):
    """Single validation error"""
    data_type: DataTypeEnum = Field(..., description="Data type with error")
    record_id: Optional[str] = Field(None, description="Record identifier")
    field: str = Field(..., description="Field with error")
    error: str = Field(..., description="Error description")
    severity: str = Field("error", description="Error severity (error, warning)")


class MigrationReportResponse(BaseModel):
    """Complete migration report"""
    migration_id: str = Field(..., description="Migration identifier")
    source_db: str = Field(..., description="Source database path")
    target_db: str = Field(..., description="Target database path")
    started_at: datetime = Field(..., description="Migration start time")
    completed_at: Optional[datetime] = Field(None, description="Migration completion time")
    duration_seconds: Optional[float] = Field(None, description="Total duration in seconds")
    overall_status: MigrationStatusEnum = Field(..., description="Final status")
    backup_path: Optional[str] = Field(None, description="Backup file path")
    
    # Statistics
    total_records: int = Field(0, description="Total records processed")
    migrated_records: int = Field(0, description="Successfully migrated")
    failed_records: int = Field(0, description="Failed to migrate")
    skipped_records: int = Field(0, description="Skipped records")
    
    # Detailed progress
    progress: Dict[str, DataTypeProgress] = Field(
        default_factory=dict,
        description="Progress by data type"
    )
    
    # Errors
    validation_errors: List[ValidationError] = Field(
        default_factory=list,
        description="Validation errors encountered"
    )
    
    # Recommendations
    recommendations: List[str] = Field(
        default_factory=list,
        description="Post-migration recommendations"
    )


class MigrationListItem(BaseModel):
    """Item in migration list"""
    migration_id: str = Field(..., description="Migration identifier")
    status: MigrationStatusEnum = Field(..., description="Current status")
    started_at: datetime = Field(..., description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    source_db: str = Field(..., description="Source database")
    total_records: int = Field(0, description="Total records")
    migrated_records: int = Field(0, description="Migrated records")


class MigrationListResponse(BaseModel):
    """Response with list of migrations"""
    migrations: List[MigrationListItem] = Field(
        default_factory=list,
        description="List of migrations"
    )
    total: int = Field(0, description="Total number of migrations")


class ValidationRequest(BaseModel):
    """Request to validate migration"""
    migration_id: str = Field(..., description="Migration to validate")
    check_data_integrity: bool = Field(
        default=True,
        description="Check data integrity between source and target"
    )
    check_record_counts: bool = Field(
        default=True,
        description="Verify record counts match"
    )
    sample_size: int = Field(
        default=100,
        description="Number of records to sample for validation"
    )


class ValidationCheck(BaseModel):
    """Single validation check result"""
    check_name: str = Field(..., description="Name of the check")
    passed: bool = Field(..., description="Whether check passed")
    message: str = Field(..., description="Check result message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class ValidationResponse(BaseModel):
    """Response from migration validation"""
    migration_id: str = Field(..., description="Migration identifier")
    is_valid: bool = Field(..., description="Overall validation result")
    checks: List[ValidationCheck] = Field(
        default_factory=list,
        description="Individual check results"
    )
    validated_at: datetime = Field(..., description="Validation timestamp")


class CleanupRequest(BaseModel):
    """Request to cleanup migration resources"""
    migration_id: str = Field(..., description="Migration to cleanup")
    delete_backup: bool = Field(
        default=False,
        description="Also delete backup file"
    )
    confirm: bool = Field(
        default=False,
        description="Confirm cleanup operation"
    )


class CleanupResponse(BaseModel):
    """Response after cleanup"""
    migration_id: str = Field(..., description="Migration identifier")
    cleaned_up: bool = Field(..., description="Whether cleanup succeeded")
    message: str = Field(..., description="Cleanup result message")
    backup_deleted: bool = Field(False, description="Whether backup was deleted")
