"""
Migration API Endpoints
Provides REST API for migration wizard UI
Requirements: 5.5, 5.6, 5.7
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
import json
from datetime import datetime

from ...migrations.migration_manager import MigrationManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/migration", tags=["migration"])

# Global migration state
migration_state = {
    "status": "idle",  # idle, running, completed, failed
    "progress": 0,
    "current_step": "",
    "details": [],
    "errors": [],
    "report": None
}

# Migration manager instance
migration_manager: Optional[MigrationManager] = None


class MigrationConfig(BaseModel):
    """Migration configuration"""
    source_path: str
    target_path: str
    backup_enabled: bool = True
    validate_after_migration: bool = True


class MigrationStatus(BaseModel):
    """Migration status response"""
    status: str
    progress: int
    current_step: str
    details: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


@router.post("/start")
async def start_migration(
    config: MigrationConfig,
    background_tasks: BackgroundTasks
):
    """
    Start migration process
    
    Args:
        config: Migration configuration
        background_tasks: FastAPI background tasks
    
    Returns:
        Migration start confirmation
    """
    global migration_state, migration_manager
    
    if migration_state["status"] == "running":
        raise HTTPException(
            status_code=400,
            detail="Migration is already running"
        )
    
    try:
        # Initialize migration manager
        migration_manager = MigrationManager(
            source_path=Path(config.source_path),
            target_path=Path(config.target_path)
        )
        
        # Reset state
        migration_state = {
            "status": "running",
            "progress": 0,
            "current_step": "Initialisierung",
            "details": [],
            "errors": [],
            "report": None
        }
        
        # Run migration in background
        background_tasks.add_task(run_migration_task)
        
        logger.info("Migration started")
        
        return {
            "success": True,
            "message": "Migration started successfully",
            "status": migration_state["status"]
        }
        
    except Exception as e:
        logger.error(f"Failed to start migration: {str(e)}", exc_info=True)
        migration_state["status"] = "failed"
        migration_state["errors"].append({
            "id": f"error_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "step": "initialization",
            "severity": "error",
            "message": str(e),
            "details": None,
            "stackTrace": None
        })
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start migration: {str(e)}"
        )


async def run_migration_task():
    """Background task to run migration"""
    global migration_state, migration_manager
    
    try:
        if not migration_manager:
            raise Exception("Migration manager not initialized")
        
        # Update progress callback
        def update_progress(step: str, progress: int, details: Dict[str, Any]):
            migration_state["current_step"] = step
            migration_state["progress"] = progress
            migration_state["details"].append({
                "step": step,
                "status": "running",
                "message": details.get("message", ""),
                "startTime": datetime.now().isoformat(),
                "itemsProcessed": details.get("items_processed", 0),
                "totalItems": details.get("total_items", 0)
            })
        
        # Run migration
        update_progress("Backup", 10, {"message": "Erstelle Backup..."})
        
        report = migration_manager.run_full_migration()
        
        # Update final state
        if report["success"]:
            migration_state["status"] = "completed"
            migration_state["progress"] = 100
            migration_state["current_step"] = "Abgeschlossen"
        else:
            migration_state["status"] = "failed"
            migration_state["errors"].extend([
                {
                    "id": f"error_{i}",
                    "timestamp": datetime.now().isoformat(),
                    "step": "migration",
                    "severity": "error",
                    "message": error,
                    "details": None,
                    "stackTrace": None
                }
                for i, error in enumerate(report.get("errors", []))
            ])
        
        migration_state["report"] = report
        
        logger.info(f"Migration completed with status: {migration_state['status']}")
        
    except Exception as e:
        logger.error(f"Migration task failed: {str(e)}", exc_info=True)
        migration_state["status"] = "failed"
        migration_state["errors"].append({
            "id": f"error_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "step": "execution",
            "severity": "error",
            "message": str(e),
            "details": None,
            "stackTrace": None
        })


@router.get("/status", response_model=MigrationStatus)
async def get_migration_status():
    """
    Get current migration status
    
    Returns:
        Current migration status
    """
    return MigrationStatus(
        status=migration_state["status"],
        progress=migration_state["progress"],
        current_step=migration_state["current_step"],
        details=migration_state["details"],
        errors=migration_state["errors"]
    )


@router.get("/report")
async def get_migration_report():
    """
    Get migration report
    
    Returns:
        Detailed migration report
    """
    if migration_state["report"] is None:
        raise HTTPException(
            status_code=404,
            detail="Migration report not available"
        )
    
    return migration_state["report"]


@router.post("/rollback")
async def rollback_migration():
    """
    Rollback migration
    
    Returns:
        Rollback result
    """
    global migration_state, migration_manager
    
    if migration_state["status"] == "running":
        raise HTTPException(
            status_code=400,
            detail="Cannot rollback while migration is running"
        )
    
    if not migration_manager:
        raise HTTPException(
            status_code=400,
            detail="No migration to rollback"
        )
    
    try:
        rollback_result = migration_manager._rollback_migration()
        
        if rollback_result["success"]:
            # Reset state
            migration_state = {
                "status": "idle",
                "progress": 0,
                "current_step": "",
                "details": [],
                "errors": [],
                "report": None
            }
            
            logger.info("Migration rolled back successfully")
            
            return {
                "success": True,
                "message": "Migration rolled back successfully",
                "details": rollback_result
            }
        else:
            raise Exception(rollback_result["message"])
            
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Rollback failed: {str(e)}"
        )


@router.post("/validate")
async def validate_migration():
    """
    Validate migration
    
    Returns:
        Validation result
    """
    global migration_manager
    
    if not migration_manager:
        raise HTTPException(
            status_code=400,
            detail="No migration to validate"
        )
    
    try:
        validation_result = migration_manager._validate_migration()
        
        logger.info(f"Migration validation: {validation_result['success']}")
        
        return {
            "success": validation_result["success"],
            "message": validation_result["message"],
            "checks": validation_result["checks"]
        }
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/check")
async def check_migration_available():
    """
    Check if migration is available
    
    Returns:
        Migration availability status
    """
    # Check if source data exists
    # This is a placeholder - implement actual check logic
    
    return {
        "available": True,
        "source_path": "/path/to/streamlit/data",
        "estimated_size": "500 MB",
        "estimated_duration": "10-15 minutes"
    }
