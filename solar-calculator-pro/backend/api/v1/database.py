"""
Database Management API Endpoints

Provides REST API endpoints for database management operations:
- Backup and restore
- Optimization
- Statistics
- Data export
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ...services.database_management_service import DatabaseManagementService
from ...core.dependencies import get_database_url
from ...core.auth_dependencies import get_current_user

router = APIRouter(prefix="/database", tags=["database"])


# ==================== Request/Response Models ====================

class BackupCreateRequest(BaseModel):
    """Request model for creating a backup"""
    description: Optional[str] = ""
    compress: bool = True


class BackupRestoreRequest(BaseModel):
    """Request model for restoring a backup"""
    backup_filename: str
    create_backup_before: bool = True


class BackupDeleteRequest(BaseModel):
    """Request model for deleting a backup"""
    backup_filename: str


class ExportTableRequest(BaseModel):
    """Request model for exporting a table"""
    table_name: str
    format: str = "csv"  # csv or json


class ExportDatabaseRequest(BaseModel):
    """Request model for exporting full database"""
    format: str = "json"  # json or sql


# ==================== Dependency Functions ====================

def get_db_service(database_url: str = Depends(get_database_url)) -> DatabaseManagementService:
    """Get database management service instance"""
    return DatabaseManagementService(database_url)


# ==================== Backup Endpoints ====================

@router.post("/backup")
async def create_backup(
    request: BackupCreateRequest,
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a database backup
    
    Requires authentication.
    """
    result = db_service.create_backup(
        description=request.description,
        compress=request.compress
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


@router.get("/backups")
async def list_backups(
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    List all available backups
    
    Requires authentication.
    """
    backups = db_service.list_backups()
    
    return {
        'success': True,
        'backups': backups,
        'count': len(backups)
    }


@router.post("/restore")
async def restore_backup(
    request: BackupRestoreRequest,
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Restore database from backup
    
    Requires authentication.
    WARNING: This will replace the current database!
    """
    result = db_service.restore_backup(
        backup_filename=request.backup_filename,
        create_backup_before=request.create_backup_before
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


@router.delete("/backup")
async def delete_backup(
    request: BackupDeleteRequest,
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a backup file
    
    Requires authentication.
    """
    result = db_service.delete_backup(request.backup_filename)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


# ==================== Optimization Endpoints ====================

@router.post("/optimize")
async def optimize_database(
    background_tasks: BackgroundTasks,
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Optimize database (VACUUM, ANALYZE, REINDEX)
    
    Requires authentication.
    This operation may take some time for large databases.
    """
    result = db_service.optimize_database()
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


@router.get("/integrity")
async def check_integrity(
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Check database integrity
    
    Requires authentication.
    """
    result = db_service.check_integrity()
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


# ==================== Statistics Endpoints ====================

@router.get("/statistics")
async def get_statistics(
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive database statistics
    
    Requires authentication.
    Returns information about database size, tables, rows, indexes, etc.
    """
    result = db_service.get_statistics()
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


# ==================== Export Endpoints ====================

@router.post("/export/table")
async def export_table(
    request: ExportTableRequest,
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Export a specific table to CSV or JSON
    
    Requires authentication.
    """
    if request.format == 'csv':
        result = db_service.export_table_to_csv(request.table_name)
    elif request.format == 'json':
        result = db_service.export_table_to_json(request.table_name)
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'json'")
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


@router.post("/export/full")
async def export_full_database(
    request: ExportDatabaseRequest,
    background_tasks: BackgroundTasks,
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Export entire database to JSON or SQL format
    
    Requires authentication.
    This operation may take some time for large databases.
    """
    if request.format not in ['json', 'sql']:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'sql'")
    
    result = db_service.export_full_database(format=request.format)
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


# ==================== Health Check ====================

@router.get("/health")
async def database_health(
    db_service: DatabaseManagementService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get database health status
    
    Requires authentication.
    Returns quick health check including size and integrity.
    """
    stats = db_service.get_statistics()
    integrity = db_service.check_integrity()
    
    return {
        'success': True,
        'healthy': integrity.get('integrity_ok', False),
        'size_mb': stats.get('database', {}).get('size_mb', 0),
        'table_count': stats.get('tables', {}).get('count', 0),
        'total_rows': stats.get('tables', {}).get('total_rows', 0),
        'checked_at': datetime.now().isoformat()
    }
