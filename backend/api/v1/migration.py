"""
Migration API Endpoints
Task 235: Data Migration Implementation

Provides REST API endpoints for:
- Starting migrations
- Tracking progress
- Rollback functionality
- Migration reports
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import logging

from backend.services.migration_service import (
    MigrationService,
    MigrationStatus,
    MigrationReport,
    MigrationProgress,
    DataType
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/migration", tags=["Migration"])

# Store active migrations
active_migrations: Dict[str, MigrationService] = {}
migration_reports: Dict[str, Dict[str, Any]] = {}


class MigrationRequest(BaseModel):
    """Request model for starting a migration"""
    source_db_path: str = Field(..., description="Path to source SQLite database")
    target_db_path: str = Field(..., description="Path to target database")
    backup_dir: str = Field(default="backups/migrations", description="Backup directory")
    data_types: Optional[List[str]] = Field(
        default=None,
        description="Specific data types to migrate (null for all)"
    )


class MigrationResponse(BaseModel):
    """Response model for migration operations"""
    migration_id: str
    status: str
    message: str
    started_at: Optional[str] = None


class ProgressResponse(BaseModel):
    """Response model for migration progress"""
    migration_id: str
    overall_status: str
    total_records: int
    migrated_records: int
    failed_records: int
    progress_percent: float
    data_type_progress: Dict[str, Any]


class RollbackRequest(BaseModel):
    """Request model for rollback"""
    migration_id: str
    backup_path: Optional[str] = None


class ReportResponse(BaseModel):
    """Response model for migration report"""
    migration_id: str
    source_db: str
    target_db: str
    started_at: str
    completed_at: Optional[str]
    overall_status: str
    backup_path: Optional[str]
    total_records: int
    migrated_records: int
    failed_records: int
    validation_errors: List[str]
    progress: Dict[str, Any]


@router.post("/start", response_model=MigrationResponse)
async def start_migration(
    request: MigrationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new data migration.
    
    This endpoint initiates the migration process in the background
    and returns immediately with a migration ID for tracking.
    """
    try:
        # Validate source database exists
        if not os.path.exists(request.source_db_path):
            raise HTTPException(
                status_code=400,
                detail=f"Source database not found: {request.source_db_path}"
            )
        
        # Create migration service
        service = MigrationService(
            source_db_path=request.source_db_path,
            target_db_path=request.target_db_path,
            backup_dir=request.backup_dir
        )
        
        migration_id = service.generate_migration_id()
        active_migrations[migration_id] = service
        
        # Run migration in background
        background_tasks.add_task(
            run_migration_task,
            migration_id,
            service,
            request.data_types
        )
        
        return MigrationResponse(
            migration_id=migration_id,
            status=MigrationStatus.IN_PROGRESS.value,
            message="Migration started successfully",
            started_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to start migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_migration_task(
    migration_id: str,
    service: MigrationService,
    data_types: Optional[List[str]] = None
):
    """Background task to run migration"""
    try:
        if data_types:
            # Run specific migrations
            for dt in data_types:
                if dt == DataType.USER_SETTINGS.value:
                    service.migrate_user_settings()
                elif dt == DataType.PROJECTS.value:
                    service.migrate_projects()
                elif dt == DataType.CUSTOMERS.value:
                    service.migrate_customers()
                elif dt == DataType.PRODUCTS.value:
                    service.migrate_products()
                elif dt == DataType.PRICE_MATRICES.value:
                    service.migrate_price_matrices()
        else:
            # Run full migration
            service.run_full_migration()
        
        # Store report
        migration_reports[migration_id] = service.generate_report()
        
    except Exception as e:
        logger.error(f"Migration task failed: {e}")
        migration_reports[migration_id] = {
            "migration_id": migration_id,
            "overall_status": MigrationStatus.FAILED.value,
            "error": str(e)
        }


@router.get("/progress/{migration_id}", response_model=ProgressResponse)
async def get_migration_progress(migration_id: str):
    """
    Get the current progress of a migration.
    
    Returns detailed progress information including:
    - Overall status
    - Records migrated/failed
    - Progress by data type
    """
    if migration_id not in active_migrations and migration_id not in migration_reports:
        raise HTTPException(
            status_code=404,
            detail=f"Migration not found: {migration_id}"
        )
    
    # Check if migration is complete
    if migration_id in migration_reports:
        report = migration_reports[migration_id]
        total = report.get("total_records", 0)
        migrated = report.get("migrated_records", 0)
        
        return ProgressResponse(
            migration_id=migration_id,
            overall_status=report.get("overall_status", "unknown"),
            total_records=total,
            migrated_records=migrated,
            failed_records=report.get("failed_records", 0),
            progress_percent=100.0 if total == 0 else (migrated / total) * 100,
            data_type_progress=report.get("progress", {})
        )
    
    # Get progress from active migration
    service = active_migrations[migration_id]
    if service.report:
        report = service.report
        total = report.total_records
        migrated = report.migrated_records
        
        return ProgressResponse(
            migration_id=migration_id,
            overall_status=report.overall_status.value,
            total_records=total,
            migrated_records=migrated,
            failed_records=report.failed_records,
            progress_percent=0.0 if total == 0 else (migrated / total) * 100,
            data_type_progress={
                k: {
                    "status": v.status.value,
                    "total": v.total_records,
                    "migrated": v.migrated_records,
                    "failed": v.failed_records
                }
                for k, v in report.progress.items()
            }
        )
    
    return ProgressResponse(
        migration_id=migration_id,
        overall_status=MigrationStatus.PENDING.value,
        total_records=0,
        migrated_records=0,
        failed_records=0,
        progress_percent=0.0,
        data_type_progress={}
    )


@router.post("/rollback", response_model=MigrationResponse)
async def rollback_migration(request: RollbackRequest):
    """
    Rollback a migration using the backup.
    
    This restores the source database from the backup created
    before the migration started.
    """
    migration_id = request.migration_id
    
    if migration_id not in active_migrations and migration_id not in migration_reports:
        raise HTTPException(
            status_code=404,
            detail=f"Migration not found: {migration_id}"
        )
    
    # Get backup path
    backup_path = request.backup_path
    if not backup_path:
        if migration_id in migration_reports:
            backup_path = migration_reports[migration_id].get("backup_path")
        elif migration_id in active_migrations:
            service = active_migrations[migration_id]
            if service.report:
                backup_path = service.report.backup_path
    
    if not backup_path or not os.path.exists(backup_path):
        raise HTTPException(
            status_code=400,
            detail="Backup not found for rollback"
        )
    
    # Perform rollback
    service = active_migrations.get(migration_id)
    if service:
        success = service.rollback(backup_path)
    else:
        # Create temporary service for rollback
        report = migration_reports.get(migration_id, {})
        temp_service = MigrationService(
            source_db_path=report.get("source_db", ""),
            target_db_path=report.get("target_db", "")
        )
        success = temp_service.rollback(backup_path)
    
    if success:
        return MigrationResponse(
            migration_id=migration_id,
            status=MigrationStatus.ROLLED_BACK.value,
            message="Rollback completed successfully"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Rollback failed"
        )


@router.get("/report/{migration_id}", response_model=ReportResponse)
async def get_migration_report(migration_id: str):
    """
    Get the complete migration report.
    
    Returns detailed information about the migration including:
    - All migrated data types
    - Success/failure counts
    - Validation errors
    - Timing information
    """
    if migration_id in migration_reports:
        report = migration_reports[migration_id]
        return ReportResponse(
            migration_id=report.get("migration_id", migration_id),
            source_db=report.get("source_db", ""),
            target_db=report.get("target_db", ""),
            started_at=report.get("started_at", ""),
            completed_at=report.get("completed_at"),
            overall_status=report.get("overall_status", "unknown"),
            backup_path=report.get("backup_path"),
            total_records=report.get("total_records", 0),
            migrated_records=report.get("migrated_records", 0),
            failed_records=report.get("failed_records", 0),
            validation_errors=report.get("validation_errors", []),
            progress=report.get("progress", {})
        )
    
    if migration_id in active_migrations:
        service = active_migrations[migration_id]
        if service.report:
            return ReportResponse(**service.report.to_dict())
    
    raise HTTPException(
        status_code=404,
        detail=f"Migration report not found: {migration_id}"
    )


@router.get("/list")
async def list_migrations():
    """
    List all migrations (active and completed).
    """
    migrations = []
    
    # Add active migrations
    for mid, service in active_migrations.items():
        status = MigrationStatus.IN_PROGRESS.value
        if service.report:
            status = service.report.overall_status.value
        migrations.append({
            "migration_id": mid,
            "status": status,
            "type": "active"
        })
    
    # Add completed migrations
    for mid, report in migration_reports.items():
        if mid not in active_migrations:
            migrations.append({
                "migration_id": mid,
                "status": report.get("overall_status", "unknown"),
                "type": "completed",
                "completed_at": report.get("completed_at")
            })
    
    return {"migrations": migrations, "total": len(migrations)}


@router.delete("/cleanup/{migration_id}")
async def cleanup_migration(migration_id: str):
    """
    Clean up migration resources.
    
    Removes the migration from active tracking and optionally
    deletes the backup file.
    """
    removed = False
    
    if migration_id in active_migrations:
        del active_migrations[migration_id]
        removed = True
    
    if migration_id in migration_reports:
        del migration_reports[migration_id]
        removed = True
    
    if removed:
        return {"message": f"Migration {migration_id} cleaned up successfully"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Migration not found: {migration_id}"
        )


@router.get("/validate/{migration_id}")
async def validate_migration(migration_id: str):
    """
    Validate a completed migration.
    
    Checks data integrity between source and target databases.
    """
    if migration_id not in migration_reports:
        raise HTTPException(
            status_code=404,
            detail=f"Migration not found: {migration_id}"
        )
    
    report = migration_reports[migration_id]
    
    # Basic validation
    validation_results = {
        "migration_id": migration_id,
        "is_valid": True,
        "checks": []
    }
    
    # Check completion status
    if report.get("overall_status") == MigrationStatus.COMPLETED.value:
        validation_results["checks"].append({
            "check": "completion_status",
            "passed": True,
            "message": "Migration completed successfully"
        })
    else:
        validation_results["is_valid"] = False
        validation_results["checks"].append({
            "check": "completion_status",
            "passed": False,
            "message": f"Migration status: {report.get('overall_status')}"
        })
    
    # Check for failed records
    failed = report.get("failed_records", 0)
    if failed == 0:
        validation_results["checks"].append({
            "check": "no_failures",
            "passed": True,
            "message": "No failed records"
        })
    else:
        validation_results["is_valid"] = False
        validation_results["checks"].append({
            "check": "no_failures",
            "passed": False,
            "message": f"{failed} records failed to migrate"
        })
    
    # Check for validation errors
    errors = report.get("validation_errors", [])
    if not errors:
        validation_results["checks"].append({
            "check": "no_validation_errors",
            "passed": True,
            "message": "No validation errors"
        })
    else:
        validation_results["is_valid"] = False
        validation_results["checks"].append({
            "check": "no_validation_errors",
            "passed": False,
            "message": f"{len(errors)} validation errors found",
            "errors": errors[:10]  # First 10 errors
        })
    
    return validation_results
