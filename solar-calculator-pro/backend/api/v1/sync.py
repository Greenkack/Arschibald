"""
Synchronization API Endpoints
RESTful API for data synchronization
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.core.dependencies import get_db, get_current_user
from backend.services.sync_service import SyncService
from backend.services.sync_scheduler import sync_scheduler
from backend.models.sync_schemas import (
    SyncOperationCreate, SyncOperationResponse, SyncBatchRequest, SyncBatchResponse,
    ConflictDetails, ConflictResolutionRequest, SyncScheduleCreate, SyncScheduleResponse,
    SyncStatusResponse, OfflineSyncQueueItem, OfflineSyncQueueResponse,
    SyncLogEntry, SyncStatistics
)
from backend.models.sync_models import SyncConflict, SyncLog, OfflineSyncQueue
from sqlalchemy import and_, desc, func

router = APIRouter(prefix="/sync", tags=["synchronization"])


@router.post("/operations", response_model=SyncOperationResponse)
async def create_sync_operation(
    operation: SyncOperationCreate,
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a single synchronization operation"""
    sync_service = SyncService(db)
    
    try:
        sync_op = sync_service.create_sync_operation(
            user_id=current_user["id"],
            device_id=device_id,
            operation=operation
        )
        return sync_op
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sync operation: {str(e)}"
        )


@router.post("/batch", response_model=SyncBatchResponse)
async def batch_sync(
    batch_request: SyncBatchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process batch synchronization"""
    sync_service = SyncService(db)
    
    try:
        sync_session_id, operations = sync_service.process_batch_sync(
            user_id=current_user["id"],
            batch_request=batch_request
        )
        
        return SyncBatchResponse(
            sync_session_id=sync_session_id,
            total_operations=len(operations),
            completed=sum(1 for op in operations if op.status.value == "completed"),
            failed=sum(1 for op in operations if op.status.value == "failed"),
            conflicts=sum(1 for op in operations if op.status.value == "conflict"),
            operations=operations
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch sync failed: {str(e)}"
        )


@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get synchronization status"""
    sync_service = SyncService(db)
    
    try:
        status_data = sync_service.get_sync_status(
            user_id=current_user["id"],
            device_id=device_id
        )
        return SyncStatusResponse(**status_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync status: {str(e)}"
        )


@router.get("/conflicts", response_model=List[ConflictDetails])
async def get_conflicts(
    device_id: str = None,
    resolved: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get synchronization conflicts"""
    query = db.query(SyncConflict).filter(
        and_(
            SyncConflict.user_id == current_user["id"],
            SyncConflict.resolved == resolved
        )
    )
    
    if device_id:
        # Join with SyncOperation to filter by device
        from backend.models.sync_models import SyncOperation
        query = query.join(SyncOperation).filter(SyncOperation.device_id == device_id)
    
    conflicts = query.order_by(desc(SyncConflict.created_at)).all()
    return conflicts


@router.post("/conflicts/{conflict_id}/resolve", response_model=ConflictDetails)
async def resolve_conflict(
    conflict_id: int,
    resolution: ConflictResolutionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Resolve synchronization conflict"""
    sync_service = SyncService(db)
    
    try:
        conflict = sync_service.resolve_conflict(
            user_id=current_user["id"],
            resolution_request=resolution
        )
        return conflict
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve conflict: {str(e)}"
        )


@router.post("/schedule", response_model=SyncScheduleResponse)
async def create_sync_schedule(
    schedule_request: SyncScheduleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create or update synchronization schedule"""
    try:
        schedule = sync_scheduler.create_schedule(
            db=db,
            user_id=current_user["id"],
            device_id=schedule_request.device_id,
            sync_interval=schedule_request.sync_interval,
            auto_sync=schedule_request.auto_sync,
            sync_on_startup=schedule_request.sync_on_startup,
            sync_on_shutdown=schedule_request.sync_on_shutdown,
            entity_types=schedule_request.entity_types
        )
        return schedule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {str(e)}"
        )


@router.get("/schedule", response_model=SyncScheduleResponse)
async def get_sync_schedule(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get synchronization schedule"""
    from backend.models.sync_models import SyncSchedule
    
    schedule = db.query(SyncSchedule).filter(
        and_(
            SyncSchedule.user_id == current_user["id"],
            SyncSchedule.device_id == device_id
        )
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    return schedule


@router.post("/schedule/enable")
async def enable_sync_schedule(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Enable synchronization schedule"""
    try:
        sync_scheduler.enable_schedule(
            db=db,
            user_id=current_user["id"],
            device_id=device_id
        )
        return {"message": "Schedule enabled"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/schedule/disable")
async def disable_sync_schedule(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Disable synchronization schedule"""
    try:
        sync_scheduler.disable_schedule(
            db=db,
            user_id=current_user["id"],
            device_id=device_id
        )
        return {"message": "Schedule disabled"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/manual")
async def trigger_manual_sync(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Trigger manual synchronization"""
    try:
        sync_scheduler.trigger_manual_sync(
            user_id=current_user["id"],
            device_id=device_id
        )
        return {"message": "Manual sync triggered"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger sync: {str(e)}"
        )


@router.post("/offline/queue", response_model=OfflineSyncQueueResponse)
async def add_to_offline_queue(
    queue_item: OfflineSyncQueueItem,
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add operation to offline sync queue"""
    sync_service = SyncService(db)
    
    try:
        item = sync_service.add_to_offline_queue(
            user_id=current_user["id"],
            device_id=device_id,
            entity_type=queue_item.entity_type,
            entity_id=queue_item.entity_id,
            operation_type=queue_item.operation_type,
            data=queue_item.data,
            priority=queue_item.priority
        )
        return item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add to queue: {str(e)}"
        )


@router.get("/offline/queue", response_model=List[OfflineSyncQueueResponse])
async def get_offline_queue(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get offline sync queue"""
    queue_items = db.query(OfflineSyncQueue).filter(
        and_(
            OfflineSyncQueue.user_id == current_user["id"],
            OfflineSyncQueue.device_id == device_id,
            OfflineSyncQueue.processed == False
        )
    ).order_by(desc(OfflineSyncQueue.priority), OfflineSyncQueue.queued_at).all()
    
    return queue_items


@router.post("/offline/process")
async def process_offline_queue(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process offline sync queue"""
    sync_service = SyncService(db)
    
    try:
        operations = sync_service.process_offline_queue(
            user_id=current_user["id"],
            device_id=device_id
        )
        return {
            "message": "Offline queue processed",
            "operations_processed": len(operations)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process queue: {str(e)}"
        )


@router.get("/logs", response_model=List[SyncLogEntry])
async def get_sync_logs(
    device_id: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get synchronization logs"""
    query = db.query(SyncLog).filter(SyncLog.user_id == current_user["id"])
    
    if device_id:
        query = query.filter(SyncLog.device_id == device_id)
    
    logs = query.order_by(desc(SyncLog.created_at)).limit(limit).all()
    return logs


@router.get("/statistics", response_model=SyncStatistics)
async def get_sync_statistics(
    device_id: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get synchronization statistics"""
    from backend.models.sync_models import SyncOperation, SyncStatus
    
    # Base query
    query = db.query(SyncOperation).filter(SyncOperation.user_id == current_user["id"])
    
    if device_id:
        query = query.filter(SyncOperation.device_id == device_id)
    
    # Total syncs
    total_syncs = query.count()
    
    # Successful syncs
    successful_syncs = query.filter(SyncOperation.status == SyncStatus.COMPLETED).count()
    
    # Failed syncs
    failed_syncs = query.filter(SyncOperation.status == SyncStatus.FAILED).count()
    
    # Conflicts
    conflict_query = db.query(SyncConflict).filter(SyncConflict.user_id == current_user["id"])
    total_conflicts = conflict_query.count()
    resolved_conflicts = conflict_query.filter(SyncConflict.resolved == True).count()
    pending_conflicts = total_conflicts - resolved_conflicts
    
    # Average sync duration (in seconds)
    avg_duration = db.query(
        func.avg(
            func.extract('epoch', SyncOperation.completed_at - SyncOperation.server_timestamp)
        )
    ).filter(
        and_(
            SyncOperation.user_id == current_user["id"],
            SyncOperation.status == SyncStatus.COMPLETED,
            SyncOperation.completed_at.isnot(None)
        )
    ).scalar() or 0.0
    
    # Last 24h syncs
    from datetime import datetime, timedelta
    last_24h = datetime.now() - timedelta(hours=24)
    last_24h_syncs = query.filter(SyncOperation.created_at >= last_24h).count()
    
    return SyncStatistics(
        total_syncs=total_syncs,
        successful_syncs=successful_syncs,
        failed_syncs=failed_syncs,
        total_conflicts=total_conflicts,
        resolved_conflicts=resolved_conflicts,
        pending_conflicts=pending_conflicts,
        average_sync_duration=float(avg_duration),
        last_24h_syncs=last_24h_syncs,
        data_synced_mb=0.0  # Placeholder - would need to calculate actual data size
    )
