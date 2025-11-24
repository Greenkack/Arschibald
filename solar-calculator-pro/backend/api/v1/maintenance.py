"""
API endpoints for system maintenance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db
from backend.core.auth_dependencies import get_current_user
from backend.services.maintenance_service import MaintenanceService
from backend.models.maintenance_schemas import (
    DatabaseMaintenanceRequest, DatabaseMaintenanceResponse,
    CacheStatsResponse, CacheClearRequest, CacheClearResponse,
    LogStatsResponse, LogCleanupRequest, LogCleanupResponse,
    TempFileStatsResponse, TempFileCleanupRequest, TempFileCleanupResponse,
    SystemDiagnosticsResponse, DiagnosticRequest,
    RepairRequest, RepairResponse,
    MaintenanceLogResponse
)

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


def get_maintenance_service(db: Session = Depends(get_db)) -> MaintenanceService:
    """Dependency to get maintenance service"""
    return MaintenanceService(db)


# ==================== Database Maintenance ====================

@router.post("/database", response_model=DatabaseMaintenanceResponse)
async def perform_database_maintenance(
    request: DatabaseMaintenanceRequest,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Perform database maintenance operations
    
    Operations:
    - vacuum: Clean up dead tuples and reclaim space
    - analyze: Update statistics for query optimization
    - reindex: Rebuild database indexes
    - optimize: Combination of vacuum and analyze
    """
    try:
        return service.perform_database_maintenance(request, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database maintenance failed: {str(e)}"
        )


# ==================== Cache Management ====================

@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """Get cache statistics"""
    return service.get_cache_stats()


@router.post("/cache/clear", response_model=CacheClearResponse)
async def clear_cache(
    request: CacheClearRequest,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Clear cache entries
    
    Options:
    - cache_type: Clear specific cache type
    - older_than_days: Clear entries older than X days
    - unused_only: Clear only unused entries
    """
    try:
        return service.clear_cache(request, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache clear failed: {str(e)}"
        )


# ==================== Log Management ====================

@router.get("/logs/stats", response_model=LogStatsResponse)
async def get_log_stats(
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """Get log file statistics"""
    return service.get_log_stats()


@router.post("/logs/cleanup", response_model=LogCleanupResponse)
async def cleanup_logs(
    request: LogCleanupRequest,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Clean up old log files
    
    Options:
    - older_than_days: Delete logs older than X days (default: 30)
    - log_level: Clean specific log level
    - compress_before_delete: Compress logs before deletion (default: true)
    """
    try:
        return service.cleanup_logs(request, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Log cleanup failed: {str(e)}"
        )


# ==================== Temp File Cleanup ====================

@router.get("/temp-files/stats", response_model=TempFileStatsResponse)
async def get_temp_file_stats(
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """Get temporary file statistics"""
    return service.get_temp_file_stats()


@router.post("/temp-files/cleanup", response_model=TempFileCleanupResponse)
async def cleanup_temp_files(
    request: TempFileCleanupRequest,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Clean up temporary files
    
    Options:
    - older_than_hours: Delete files older than X hours (default: 24)
    - file_types: Clean specific file types
    - force: Force delete even if recently accessed
    """
    try:
        return service.cleanup_temp_files(request, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Temp file cleanup failed: {str(e)}"
        )


# ==================== System Diagnostics ====================

@router.post("/diagnostics", response_model=SystemDiagnosticsResponse)
async def run_diagnostics(
    request: DiagnosticRequest,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Run system diagnostics
    
    Diagnostic types:
    - database: Database health and performance
    - disk: Disk space and I/O
    - memory: Memory usage
    - cpu: CPU usage
    - network: Network connectivity
    - services: Service health
    """
    try:
        return service.run_diagnostics(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnostics failed: {str(e)}"
        )


# ==================== Repair Tools ====================

@router.post("/repair", response_model=RepairResponse)
async def perform_repair(
    request: RepairRequest,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Perform repair operations
    
    Operations:
    - fix_permissions: Fix file permissions
    - rebuild_index: Rebuild database indexes
    - repair_database: Repair database integrity
    - reset_cache: Reset all caches
    - fix_orphaned_files: Clean up orphaned files
    - repair_corrupted_data: Repair corrupted data
    
    Options:
    - dry_run: Simulate repair without making changes (default: true)
    - backup_first: Create backup before repair (default: true)
    """
    try:
        return service.perform_repair(request, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Repair operation failed: {str(e)}"
        )


# ==================== Maintenance Logs ====================

@router.get("/logs", response_model=List[MaintenanceLogResponse])
async def get_maintenance_logs(
    operation_type: Optional[str] = None,
    limit: int = 100,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Get maintenance operation logs
    
    Parameters:
    - operation_type: Filter by operation type (database, cache, logs, temp_files, diagnostics, repair)
    - limit: Maximum number of logs to return (default: 100)
    """
    return service.get_maintenance_logs(operation_type, limit)


# ==================== Quick Actions ====================

@router.post("/quick-cleanup")
async def quick_cleanup(
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Perform quick cleanup of all maintenance areas
    
    This endpoint runs:
    - Cache cleanup (unused entries)
    - Log cleanup (older than 30 days)
    - Temp file cleanup (older than 24 hours)
    - Database vacuum
    """
    results = {}
    
    try:
        # Clear unused cache
        cache_result = service.clear_cache(
            CacheClearRequest(unused_only=True),
            current_user
        )
        results["cache"] = {
            "entries_cleared": cache_result.entries_cleared,
            "size_freed_mb": cache_result.size_freed_mb
        }
        
        # Cleanup old logs
        log_result = service.cleanup_logs(
            LogCleanupRequest(older_than_days=30),
            current_user
        )
        results["logs"] = {
            "files_deleted": log_result.files_deleted,
            "size_freed_mb": log_result.size_freed_mb
        }
        
        # Cleanup temp files
        temp_result = service.cleanup_temp_files(
            TempFileCleanupRequest(older_than_hours=24),
            current_user
        )
        results["temp_files"] = {
            "files_deleted": temp_result.files_deleted,
            "size_freed_mb": temp_result.size_freed_mb
        }
        
        # Vacuum database
        db_result = service.perform_database_maintenance(
            DatabaseMaintenanceRequest(operation="vacuum", full=False),
            current_user
        )
        results["database"] = {
            "tables_processed": len(db_result.tables_processed)
        }
        
        return {
            "status": "success",
            "message": "Quick cleanup completed",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick cleanup failed: {str(e)}"
        )


@router.get("/health-check")
async def health_check(
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: str = Depends(get_current_user)
):
    """
    Quick health check of critical systems
    
    Returns status of:
    - Database connection
    - Disk space
    - Memory usage
    - CPU usage
    """
    try:
        diagnostics = service.run_diagnostics(
            DiagnosticRequest(
                diagnostic_types=["database", "disk", "memory", "cpu"],
                detailed=False
            )
        )
        
        return {
            "status": diagnostics.overall_status.value,
            "summary": diagnostics.summary,
            "diagnostics": [
                {
                    "type": d.diagnostic_type,
                    "status": d.status.value,
                    "metrics": d.metrics
                }
                for d in diagnostics.diagnostics
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
