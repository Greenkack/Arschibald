"""
Backup API Endpoints
Provides REST API for backup management
Requirements: 5.5
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path
import logging

from ...services.backup_service import BackupService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backup", tags=["backup"])

# Initialize backup service
# TODO: Configure paths from application settings
DATA_PATH = Path("./data")
BACKUP_PATH = Path("./backups")
backup_service = BackupService(DATA_PATH, BACKUP_PATH)


class BackupCreateRequest(BaseModel):
    """Request model for creating a backup"""
    backup_name: Optional[str] = Field(None, description="Custom backup name (auto-generated if not provided)")
    description: str = Field("", description="Backup description")
    include_databases: bool = Field(True, description="Include database files")
    include_settings: bool = Field(True, description="Include settings files")
    include_user_data: bool = Field(True, description="Include user data")
    include_projects: bool = Field(True, description="Include project data")
    compress: bool = Field(True, description="Compress backup into ZIP file")


class BackupRestoreRequest(BaseModel):
    """Request model for restoring a backup"""
    backup_name: str = Field(..., description="Name of backup to restore")
    verify_before_restore: bool = Field(True, description="Verify backup integrity before restoring")


class BackupResponse(BaseModel):
    """Response model for backup operations"""
    success: bool
    message: str
    backup_name: Optional[str] = None
    files_count: Optional[int] = None
    size_bytes: Optional[int] = None


@router.post("/create", response_model=BackupResponse)
async def create_backup(request: BackupCreateRequest, background_tasks: BackgroundTasks):
    """
    Create a new backup
    
    Creates a backup of application data including databases, settings,
    user data, and projects. The backup can be compressed into a ZIP file.
    
    - **backup_name**: Optional custom name (auto-generated if not provided)
    - **description**: Optional description for the backup
    - **include_databases**: Include database files (default: true)
    - **include_settings**: Include settings files (default: true)
    - **include_user_data**: Include user data (default: true)
    - **include_projects**: Include project data (default: true)
    - **compress**: Compress backup into ZIP file (default: true)
    """
    try:
        logger.info(f"Creating backup: {request.backup_name or 'auto-generated'}")
        
        result = backup_service.create_backup(
            backup_name=request.backup_name,
            description=request.description,
            include_databases=request.include_databases,
            include_settings=request.include_settings,
            include_user_data=request.include_user_data,
            include_projects=request.include_projects,
            compress=request.compress
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "Backup creation failed"))
        
        return BackupResponse(
            success=True,
            message=result["message"],
            backup_name=result["backup_name"],
            files_count=result["files_backed_up"],
            size_bytes=result["total_size_bytes"]
        )
        
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore", response_model=BackupResponse)
async def restore_backup(request: BackupRestoreRequest):
    """
    Restore data from a backup
    
    Restores application data from a previously created backup.
    Automatically creates a backup of current data before restoring.
    
    - **backup_name**: Name of backup to restore
    - **verify_before_restore**: Verify backup integrity before restoring (default: true)
    """
    try:
        logger.info(f"Restoring backup: {request.backup_name}")
        
        result = backup_service.restore_backup(
            backup_name=request.backup_name,
            verify_before_restore=request.verify_before_restore
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "Backup restoration failed"))
        
        return BackupResponse(
            success=True,
            message=result["message"],
            backup_name=request.backup_name,
            files_count=result["files_restored"]
        )
        
    except Exception as e:
        logger.error(f"Backup restoration failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_backups():
    """
    List all available backups
    
    Returns a list of all backups with their metadata including:
    - Backup name
    - Creation timestamp
    - Description
    - File count
    - Size
    - Components included
    """
    try:
        logger.debug("Listing backups")
        
        backups = backup_service.list_backups()
        
        return {
            "success": True,
            "count": len(backups),
            "backups": backups
        }
        
    except Exception as e:
        logger.error(f"Failed to list backups: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify/{backup_name}")
async def verify_backup(backup_name: str):
    """
    Verify backup integrity
    
    Performs integrity checks on a backup including:
    - Metadata validation
    - File integrity check
    - Database integrity check
    
    - **backup_name**: Name of backup to verify
    """
    try:
        logger.info(f"Verifying backup: {backup_name}")
        
        result = backup_service.verify_backup(backup_name)
        
        return {
            "success": True,
            "valid": result["valid"],
            "message": result["message"],
            "checks": result["checks"]
        }
        
    except Exception as e:
        logger.error(f"Backup verification failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{backup_name}", response_model=BackupResponse)
async def delete_backup(backup_name: str):
    """
    Delete a backup
    
    Permanently deletes a backup from the backup storage.
    This operation cannot be undone.
    
    - **backup_name**: Name of backup to delete
    """
    try:
        logger.info(f"Deleting backup: {backup_name}")
        
        result = backup_service.delete_backup(backup_name)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "Backup deletion failed"))
        
        return BackupResponse(
            success=True,
            message=result["message"],
            backup_name=backup_name
        )
        
    except Exception as e:
        logger.error(f"Backup deletion failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{backup_name}")
async def get_backup_info(backup_name: str):
    """
    Get detailed information about a backup
    
    Returns detailed metadata about a specific backup including:
    - Creation timestamp
    - Description
    - Components included
    - File count
    - Size
    - Compression status
    
    - **backup_name**: Name of backup
    """
    try:
        logger.debug(f"Getting backup info: {backup_name}")
        
        backups = backup_service.list_backups()
        backup_info = next((b for b in backups if b["backup_name"] == backup_name), None)
        
        if not backup_info:
            raise HTTPException(status_code=404, detail=f"Backup not found: {backup_name}")
        
        return {
            "success": True,
            "backup": backup_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get backup info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
