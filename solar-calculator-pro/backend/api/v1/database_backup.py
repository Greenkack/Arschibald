"""
Database Backup and Restore API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ...services.database_backup_service import DatabaseBackupService, BackupMetadata
from ...services.backup_scheduler import BackupScheduler
from ...core.dependencies import get_database_url
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/database/backup", tags=["database-backup"])

# Global instances (in production, use dependency injection)
backup_service: Optional[DatabaseBackupService] = None
backup_scheduler: Optional[BackupScheduler] = None


def get_backup_service() -> DatabaseBackupService:
    """Get backup service instance"""
    global backup_service
    if backup_service is None:
        database_url = get_database_url()
        backup_service = DatabaseBackupService(database_url=database_url)
    return backup_service


def get_backup_scheduler() -> BackupScheduler:
    """Get backup scheduler instance"""
    global backup_scheduler
    if backup_scheduler is None:
        service = get_backup_service()
        backup_scheduler = BackupScheduler(backup_service=service)
    return backup_scheduler


# Request/Response Models

class BackupCreateRequest(BaseModel):
    backup_type: str = "full"  # 'full' or 'incremental'
    parent_backup_id: Optional[str] = None
    encrypt: bool = True
    compress: bool = True


class BackupRestoreRequest(BaseModel):
    backup_id: str
    validate: bool = True
    target_database_url: Optional[str] = None


class BackupListRequest(BaseModel):
    backup_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class RetentionPolicyRequest(BaseModel):
    keep_daily: int = 7
    keep_weekly: int = 4
    keep_monthly: int = 12
    keep_yearly: int = 5


class ScheduleConfigRequest(BaseModel):
    daily_enabled: bool = True
    daily_time: str = "02:00"
    daily_type: str = "incremental"
    
    weekly_enabled: bool = True
    weekly_day: str = "sunday"
    weekly_time: str = "03:00"
    
    monthly_enabled: bool = True
    monthly_day: int = 1
    monthly_time: str = "04:00"
    
    retention_policy: RetentionPolicyRequest = RetentionPolicyRequest()


class BackupResponse(BaseModel):
    backup_id: str
    timestamp: datetime
    backup_type: str
    size_bytes: int
    compressed: bool
    encrypted: bool
    checksum: str
    database_name: str
    tables: List[str]
    parent_backup_id: Optional[str] = None


class BackupInfoResponse(BackupResponse):
    file_exists: bool
    file_path: str
    is_valid: bool


# Endpoints

@router.post("/create", response_model=BackupResponse)
async def create_backup(
    request: BackupCreateRequest,
    background_tasks: BackgroundTasks,
    service: DatabaseBackupService = Depends(get_backup_service)
):
    """
    Create a new database backup
    
    - **backup_type**: Type of backup ('full' or 'incremental')
    - **parent_backup_id**: Required for incremental backups
    - **encrypt**: Whether to encrypt the backup
    - **compress**: Whether to compress the backup
    """
    try:
        if request.backup_type == "full":
            metadata = service.create_full_backup(
                encrypt=request.encrypt,
                compress=request.compress
            )
        elif request.backup_type == "incremental":
            if not request.parent_backup_id:
                # Find most recent full backup
                full_backups = service.list_backups(backup_type='full')
                if not full_backups:
                    raise HTTPException(
                        status_code=400,
                        detail="No full backup found. Create a full backup first."
                    )
                request.parent_backup_id = full_backups[0].backup_id
            
            metadata = service.create_incremental_backup(
                parent_backup_id=request.parent_backup_id,
                encrypt=request.encrypt,
                compress=request.compress
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid backup type: {request.backup_type}"
            )
        
        return BackupResponse(**metadata.to_dict())
        
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
async def restore_backup(
    request: BackupRestoreRequest,
    background_tasks: BackgroundTasks,
    service: DatabaseBackupService = Depends(get_backup_service)
):
    """
    Restore database from backup
    
    - **backup_id**: ID of the backup to restore
    - **validate**: Whether to validate backup before restoring
    - **target_database_url**: Optional target database URL
    """
    try:
        # Run restore in background to avoid timeout
        def restore_task():
            service.restore_backup(
                backup_id=request.backup_id,
                validate=request.validate,
                target_database_url=request.target_database_url
            )
        
        background_tasks.add_task(restore_task)
        
        return {
            "message": "Restore started",
            "backup_id": request.backup_id
        }
        
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[BackupResponse])
async def list_backups(
    backup_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service: DatabaseBackupService = Depends(get_backup_service)
):
    """
    List available backups with optional filtering
    
    - **backup_type**: Filter by backup type ('full' or 'incremental')
    - **start_date**: Filter backups after this date
    - **end_date**: Filter backups before this date
    """
    try:
        backups = service.list_backups(
            backup_type=backup_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return [BackupResponse(**b.to_dict()) for b in backups]
        
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{backup_id}", response_model=BackupInfoResponse)
async def get_backup_info(
    backup_id: str,
    service: DatabaseBackupService = Depends(get_backup_service)
):
    """Get detailed information about a specific backup"""
    try:
        info = service.get_backup_info(backup_id)
        
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"Backup not found: {backup_id}"
            )
        
        return BackupInfoResponse(**info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get backup info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/{backup_id}")
async def validate_backup(
    backup_id: str,
    service: DatabaseBackupService = Depends(get_backup_service)
):
    """Validate backup integrity"""
    try:
        is_valid = service.validate_backup(backup_id)
        
        return {
            "backup_id": backup_id,
            "is_valid": is_valid
        }
        
    except Exception as e:
        logger.error(f"Backup validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{backup_id}")
async def delete_backup(
    backup_id: str,
    service: DatabaseBackupService = Depends(get_backup_service)
):
    """Delete a backup"""
    try:
        service._delete_backup(backup_id)
        
        return {
            "message": "Backup deleted successfully",
            "backup_id": backup_id
        }
        
    except Exception as e:
        logger.error(f"Backup deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retention/apply")
async def apply_retention_policy(
    policy: RetentionPolicyRequest,
    service: DatabaseBackupService = Depends(get_backup_service)
):
    """Apply backup retention policy"""
    try:
        service.apply_retention_policy(
            keep_daily=policy.keep_daily,
            keep_weekly=policy.keep_weekly,
            keep_monthly=policy.keep_monthly,
            keep_yearly=policy.keep_yearly
        )
        
        return {
            "message": "Retention policy applied successfully",
            "policy": policy.dict()
        }
        
    except Exception as e:
        logger.error(f"Failed to apply retention policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Scheduler Endpoints

@router.post("/schedule/configure")
async def configure_schedule(
    config: ScheduleConfigRequest,
    scheduler: BackupScheduler = Depends(get_backup_scheduler)
):
    """Configure automatic backup schedule"""
    try:
        # Stop scheduler if running
        if scheduler.running:
            scheduler.stop()
        
        # Clear existing jobs
        scheduler.scheduler.clear()
        
        # Configure retention policy
        scheduler.set_retention_policy(
            keep_daily=config.retention_policy.keep_daily,
            keep_weekly=config.retention_policy.keep_weekly,
            keep_monthly=config.retention_policy.keep_monthly,
            keep_yearly=config.retention_policy.keep_yearly
        )
        
        # Schedule daily backup
        if config.daily_enabled:
            scheduler.schedule_daily_backup(
                time=config.daily_time,
                backup_type=config.daily_type
            )
        
        # Schedule weekly backup
        if config.weekly_enabled:
            scheduler.schedule_weekly_backup(
                day=config.weekly_day,
                time=config.weekly_time
            )
        
        # Schedule monthly backup
        if config.monthly_enabled:
            scheduler.schedule_monthly_backup(
                day=config.monthly_day,
                time=config.monthly_time
            )
        
        # Schedule retention cleanup
        scheduler.schedule_retention_cleanup()
        
        # Start scheduler
        scheduler.start()
        
        return {
            "message": "Backup schedule configured successfully",
            "config": config.dict()
        }
        
    except Exception as e:
        logger.error(f"Failed to configure schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule/info")
async def get_schedule_info(
    scheduler: BackupScheduler = Depends(get_backup_scheduler)
):
    """Get information about backup schedule"""
    try:
        return scheduler.get_schedule_info()
    except Exception as e:
        logger.error(f"Failed to get schedule info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/start")
async def start_scheduler(
    scheduler: BackupScheduler = Depends(get_backup_scheduler)
):
    """Start the backup scheduler"""
    try:
        scheduler.start()
        return {"message": "Backup scheduler started"}
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/stop")
async def stop_scheduler(
    scheduler: BackupScheduler = Depends(get_backup_scheduler)
):
    """Stop the backup scheduler"""
    try:
        scheduler.stop()
        return {"message": "Backup scheduler stopped"}
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/immediate")
async def run_immediate_backup(
    backup_type: str = "full",
    encrypt: bool = True,
    compress: bool = True,
    scheduler: BackupScheduler = Depends(get_backup_scheduler)
):
    """Run an immediate backup outside of schedule"""
    try:
        metadata = scheduler.run_immediate_backup(
            backup_type=backup_type,
            encrypt=encrypt,
            compress=compress
        )
        
        return BackupResponse(**metadata.to_dict())
        
    except Exception as e:
        logger.error(f"Immediate backup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
