"""
Synchronization Service
Core service for data synchronization with conflict resolution
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import logging

from backend.models.sync_models import (
    SyncOperation, SyncSchedule, SyncConflict, SyncLog, OfflineSyncQueue,
    SyncStatus, ConflictResolution
)
from backend.models.sync_schemas import (
    SyncOperationCreate, SyncBatchRequest, ConflictResolutionRequest,
    SyncStatusEnum, ConflictResolutionEnum
)

logger = logging.getLogger(__name__)


class SyncService:
    """Service for managing data synchronization"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_sync_operation(
        self,
        user_id: int,
        device_id: str,
        operation: SyncOperationCreate
    ) -> SyncOperation:
        """Create a new sync operation"""
        try:
            # Check for conflicts
            conflict = self._detect_conflict(
                user_id,
                operation.entity_type,
                operation.entity_id,
                operation.version,
                operation.parent_version
            )
            
            sync_op = SyncOperation(
                user_id=user_id,
                device_id=device_id,
                entity_type=operation.entity_type,
                entity_id=operation.entity_id,
                operation_type=operation.operation_type,
                status=SyncStatus.CONFLICT if conflict else SyncStatus.PENDING,
                data_snapshot=operation.data_snapshot,
                changes=operation.changes,
                client_timestamp=operation.client_timestamp,
                version=operation.version,
                parent_version=operation.parent_version
            )
            
            self.db.add(sync_op)
            self.db.commit()
            self.db.refresh(sync_op)
            
            # Create conflict record if detected
            if conflict:
                self._create_conflict_record(sync_op, conflict)
            
            logger.info(f"Created sync operation {sync_op.id} for {operation.entity_type}:{operation.entity_id}")
            return sync_op
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating sync operation: {str(e)}")
            raise
    
    def process_batch_sync(
        self,
        user_id: int,
        batch_request: SyncBatchRequest
    ) -> Tuple[str, List[SyncOperation]]:
        """Process batch synchronization request"""
        sync_session_id = str(uuid.uuid4())
        operations = []
        
        try:
            # Log sync start
            self._log_sync_event(
                user_id,
                batch_request.device_id,
                sync_session_id,
                "start",
                f"Starting batch sync with {len(batch_request.operations)} operations"
            )
            
            for op_request in batch_request.operations:
                try:
                    sync_op = self.create_sync_operation(
                        user_id,
                        batch_request.device_id,
                        op_request
                    )
                    
                    # Process if no conflict or force sync
                    if sync_op.status != SyncStatus.CONFLICT or batch_request.force_sync:
                        self._execute_sync_operation(sync_op)
                    
                    operations.append(sync_op)
                    
                except Exception as e:
                    logger.error(f"Error processing operation: {str(e)}")
                    # Continue with other operations
            
            # Log sync completion
            completed = sum(1 for op in operations if op.status == SyncStatus.COMPLETED)
            failed = sum(1 for op in operations if op.status == SyncStatus.FAILED)
            conflicts = sum(1 for op in operations if op.status == SyncStatus.CONFLICT)
            
            self._log_sync_event(
                user_id,
                batch_request.device_id,
                sync_session_id,
                "complete",
                f"Batch sync completed: {completed} completed, {failed} failed, {conflicts} conflicts",
                {
                    "total": len(operations),
                    "completed": completed,
                    "failed": failed,
                    "conflicts": conflicts
                }
            )
            
            return sync_session_id, operations
            
        except Exception as e:
            logger.error(f"Error in batch sync: {str(e)}")
            self._log_sync_event(
                user_id,
                batch_request.device_id,
                sync_session_id,
                "error",
                f"Batch sync failed: {str(e)}"
            )
            raise
    
    def _detect_conflict(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        client_version: int,
        parent_version: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """Detect synchronization conflicts"""
        # Get latest server version
        latest_op = self.db.query(SyncOperation).filter(
            and_(
                SyncOperation.user_id == user_id,
                SyncOperation.entity_type == entity_type,
                SyncOperation.entity_id == entity_id,
                SyncOperation.status == SyncStatus.COMPLETED
            )
        ).order_by(desc(SyncOperation.version)).first()
        
        if not latest_op:
            return None
        
        # Check version conflict
        if parent_version and latest_op.version != parent_version:
            return {
                "type": "version",
                "server_version": latest_op.version,
                "client_version": client_version,
                "server_data": latest_op.data_snapshot,
                "server_timestamp": latest_op.server_timestamp
            }
        
        return None
    
    def _create_conflict_record(
        self,
        sync_op: SyncOperation,
        conflict_info: Dict[str, Any]
    ):
        """Create conflict record"""
        conflict = SyncConflict(
            sync_operation_id=sync_op.id,
            user_id=sync_op.user_id,
            entity_type=sync_op.entity_type,
            entity_id=sync_op.entity_id,
            conflict_type=conflict_info["type"],
            server_data=conflict_info["server_data"],
            client_data=sync_op.changes,
            server_version=conflict_info["server_version"],
            client_version=sync_op.version,
            server_timestamp=conflict_info["server_timestamp"],
            client_timestamp=sync_op.client_timestamp
        )
        
        self.db.add(conflict)
        self.db.commit()
        
        logger.warning(f"Conflict detected for {sync_op.entity_type}:{sync_op.entity_id}")
    
    def _execute_sync_operation(self, sync_op: SyncOperation):
        """Execute synchronization operation"""
        try:
            sync_op.status = SyncStatus.IN_PROGRESS
            self.db.commit()
            
            # Apply changes based on operation type
            if sync_op.operation_type == "create":
                self._apply_create(sync_op)
            elif sync_op.operation_type == "update":
                self._apply_update(sync_op)
            elif sync_op.operation_type == "delete":
                self._apply_delete(sync_op)
            
            sync_op.status = SyncStatus.COMPLETED
            sync_op.completed_at = datetime.now()
            self.db.commit()
            
            logger.info(f"Sync operation {sync_op.id} completed successfully")
            
        except Exception as e:
            sync_op.status = SyncStatus.FAILED
            sync_op.error_message = str(e)
            sync_op.retry_count += 1
            self.db.commit()
            
            logger.error(f"Sync operation {sync_op.id} failed: {str(e)}")
            raise
    
    def _apply_create(self, sync_op: SyncOperation):
        """Apply create operation"""
        # Implementation depends on entity type
        # This is a placeholder - actual implementation would interact with entity services
        logger.info(f"Applying create for {sync_op.entity_type}:{sync_op.entity_id}")
    
    def _apply_update(self, sync_op: SyncOperation):
        """Apply update operation"""
        # Implementation depends on entity type
        logger.info(f"Applying update for {sync_op.entity_type}:{sync_op.entity_id}")
    
    def _apply_delete(self, sync_op: SyncOperation):
        """Apply delete operation"""
        # Implementation depends on entity type
        logger.info(f"Applying delete for {sync_op.entity_type}:{sync_op.entity_id}")
    
    def resolve_conflict(
        self,
        user_id: int,
        resolution_request: ConflictResolutionRequest
    ) -> SyncConflict:
        """Resolve synchronization conflict"""
        conflict = self.db.query(SyncConflict).filter(
            and_(
                SyncConflict.id == resolution_request.conflict_id,
                SyncConflict.user_id == user_id
            )
        ).first()
        
        if not conflict:
            raise ValueError("Conflict not found")
        
        if conflict.resolved:
            raise ValueError("Conflict already resolved")
        
        # Apply resolution strategy
        resolved_data = self._apply_resolution_strategy(
            conflict,
            resolution_request.resolution_strategy,
            resolution_request.resolved_data
        )
        
        # Update conflict record
        conflict.resolution_strategy = resolution_request.resolution_strategy
        conflict.resolved = True
        conflict.resolved_at = datetime.now()
        conflict.resolved_by = user_id
        conflict.resolved_data = resolved_data
        
        # Update sync operation
        sync_op = self.db.query(SyncOperation).filter(
            SyncOperation.id == conflict.sync_operation_id
        ).first()
        
        if sync_op:
            sync_op.status = SyncStatus.COMPLETED
            sync_op.conflict_resolution = resolution_request.resolution_strategy
            sync_op.changes = resolved_data
            self._execute_sync_operation(sync_op)
        
        self.db.commit()
        logger.info(f"Conflict {conflict.id} resolved with strategy {resolution_request.resolution_strategy}")
        
        return conflict
    
    def _apply_resolution_strategy(
        self,
        conflict: SyncConflict,
        strategy: ConflictResolutionEnum,
        manual_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply conflict resolution strategy"""
        if strategy == ConflictResolutionEnum.SERVER_WINS:
            return conflict.server_data
        elif strategy == ConflictResolutionEnum.CLIENT_WINS:
            return conflict.client_data
        elif strategy == ConflictResolutionEnum.LATEST_WINS:
            if conflict.server_timestamp > conflict.client_timestamp:
                return conflict.server_data
            return conflict.client_data
        elif strategy == ConflictResolutionEnum.MANUAL:
            if not manual_data:
                raise ValueError("Manual resolution requires resolved_data")
            return manual_data
        elif strategy == ConflictResolutionEnum.MERGE:
            # Simple merge strategy - can be enhanced
            merged = {**conflict.server_data, **conflict.client_data}
            return merged
        
        raise ValueError(f"Unknown resolution strategy: {strategy}")
    
    def get_sync_status(self, user_id: int, device_id: str) -> Dict[str, Any]:
        """Get synchronization status"""
        # Get pending operations
        pending = self.db.query(SyncOperation).filter(
            and_(
                SyncOperation.user_id == user_id,
                SyncOperation.device_id == device_id,
                SyncOperation.status.in_([SyncStatus.PENDING, SyncStatus.IN_PROGRESS])
            )
        ).count()
        
        # Get conflicts
        conflicts = self.db.query(SyncConflict).filter(
            and_(
                SyncConflict.user_id == user_id,
                SyncConflict.resolved == False
            )
        ).count()
        
        # Get offline queue size
        offline_queue = self.db.query(OfflineSyncQueue).filter(
            and_(
                OfflineSyncQueue.user_id == user_id,
                OfflineSyncQueue.device_id == device_id,
                OfflineSyncQueue.processed == False
            )
        ).count()
        
        # Get last sync
        last_sync = self.db.query(SyncLog).filter(
            and_(
                SyncLog.user_id == user_id,
                SyncLog.device_id == device_id,
                SyncLog.event_type == "complete"
            )
        ).order_by(desc(SyncLog.created_at)).first()
        
        # Get schedule
        schedule = self.db.query(SyncSchedule).filter(
            and_(
                SyncSchedule.user_id == user_id,
                SyncSchedule.device_id == device_id
            )
        ).first()
        
        return {
            "device_id": device_id,
            "is_syncing": pending > 0,
            "last_sync_at": last_sync.created_at if last_sync else None,
            "last_sync_status": last_sync.event_type if last_sync else None,
            "pending_operations": pending,
            "conflicts_count": conflicts,
            "offline_queue_size": offline_queue,
            "next_sync_at": schedule.next_sync_at if schedule else None
        }
    
    def _log_sync_event(
        self,
        user_id: int,
        device_id: str,
        sync_session_id: str,
        event_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log synchronization event"""
        log_entry = SyncLog(
            user_id=user_id,
            device_id=device_id,
            sync_session_id=sync_session_id,
            event_type=event_type,
            message=message,
            details=details,
            operations_total=details.get("total", 0) if details else 0,
            operations_completed=details.get("completed", 0) if details else 0,
            operations_failed=details.get("failed", 0) if details else 0,
            conflicts_detected=details.get("conflicts", 0) if details else 0
        )
        
        self.db.add(log_entry)
        self.db.commit()
    
    def add_to_offline_queue(
        self,
        user_id: int,
        device_id: str,
        entity_type: str,
        entity_id: Optional[int],
        operation_type: str,
        data: Dict[str, Any],
        priority: int = 0
    ) -> OfflineSyncQueue:
        """Add operation to offline sync queue"""
        queue_item = OfflineSyncQueue(
            user_id=user_id,
            device_id=device_id,
            entity_type=entity_type,
            entity_id=entity_id,
            operation_type=operation_type,
            data=data,
            priority=priority
        )
        
        self.db.add(queue_item)
        self.db.commit()
        self.db.refresh(queue_item)
        
        logger.info(f"Added operation to offline queue: {entity_type}:{entity_id}")
        return queue_item
    
    def process_offline_queue(self, user_id: int, device_id: str) -> List[SyncOperation]:
        """Process offline sync queue"""
        # Get queued items
        queue_items = self.db.query(OfflineSyncQueue).filter(
            and_(
                OfflineSyncQueue.user_id == user_id,
                OfflineSyncQueue.device_id == device_id,
                OfflineSyncQueue.processed == False
            )
        ).order_by(desc(OfflineSyncQueue.priority), OfflineSyncQueue.queued_at).all()
        
        operations = []
        
        for item in queue_items:
            try:
                # Create sync operation
                sync_op_request = SyncOperationCreate(
                    entity_type=item.entity_type,
                    entity_id=item.entity_id or 0,
                    operation_type=item.operation_type,
                    changes=item.data,
                    client_timestamp=item.queued_at,
                    version=1
                )
                
                sync_op = self.create_sync_operation(user_id, device_id, sync_op_request)
                self._execute_sync_operation(sync_op)
                
                # Mark as processed
                item.processed = True
                item.processed_at = datetime.now()
                
                operations.append(sync_op)
                
            except Exception as e:
                item.error_message = str(e)
                logger.error(f"Error processing offline queue item {item.id}: {str(e)}")
        
        self.db.commit()
        logger.info(f"Processed {len(operations)} items from offline queue")
        
        return operations
