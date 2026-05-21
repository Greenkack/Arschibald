"""
Synchronization System Demo
Demonstrates the synchronization system functionality
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.services.sync_service import SyncService
from backend.services.sync_scheduler import sync_scheduler
from backend.models.sync_schemas import (
    SyncOperationCreate, SyncBatchRequest, ConflictResolutionRequest,
    ConflictResolutionEnum
)


def demo_basic_sync():
    """Demonstrate basic synchronization"""
    print("\n" + "="*60)
    print("DEMO: Basic Synchronization")
    print("="*60)
    
    db = SessionLocal()
    try:
        sync_service = SyncService(db)
        
        # Create sync operation
        print("\n1. Creating sync operation...")
        operation = SyncOperationCreate(
            entity_type="project",
            entity_id=123,
            operation_type="update",
            changes={"name": "Updated Project", "status": "active"},
            client_timestamp=datetime.now(),
            version=2,
            parent_version=1
        )
        
        sync_op = sync_service.create_sync_operation(
            user_id=1,
            device_id="demo-device-1",
            operation=operation
        )
        
        print(f" Sync operation created: ID={sync_op.id}, Status={sync_op.status.value}")
        
        # Get sync status
        print("\n2. Getting sync status...")
        status = sync_service.get_sync_status(1, "demo-device-1")
        print(f" Sync status:")
        print(f"  - Pending operations: {status['pending_operations']}")
        print(f"  - Conflicts: {status['conflicts_count']}")
        print(f"  - Offline queue: {status['offline_queue_size']}")
        
    finally:
        db.close()


def demo_batch_sync():
    """Demonstrate batch synchronization"""
    print("\n" + "="*60)
    print("DEMO: Batch Synchronization")
    print("="*60)
    
    db = SessionLocal()
    try:
        sync_service = SyncService(db)
        
        # Create batch request
        print("\n1. Creating batch sync request...")
        operations = [
            SyncOperationCreate(
                entity_type="project",
                entity_id=101,
                operation_type="update",
                changes={"name": "Project 1"},
                client_timestamp=datetime.now(),
                version=1
            ),
            SyncOperationCreate(
                entity_type="customer",
                entity_id=201,
                operation_type="create",
                changes={"name": "New Customer", "email": "customer@example.com"},
                client_timestamp=datetime.now(),
                version=1
            ),
            SyncOperationCreate(
                entity_type="product",
                entity_id=301,
                operation_type="update",
                changes={"price": 999.99},
                client_timestamp=datetime.now(),
                version=2
            )
        ]
        
        batch_request = SyncBatchRequest(
            device_id="demo-device-1",
            operations=operations,
            force_sync=False
        )
        
        # Process batch
        print(f" Processing {len(operations)} operations...")
        sync_session_id, results = sync_service.process_batch_sync(1, batch_request)
        
        print(f"\n Batch sync completed:")
        print(f"  - Session ID: {sync_session_id}")
        print(f"  - Total operations: {len(results)}")
        print(f"  - Completed: {sum(1 for r in results if r.status.value == 'completed')}")
        print(f"  - Failed: {sum(1 for r in results if r.status.value == 'failed')}")
        print(f"  - Conflicts: {sum(1 for r in results if r.status.value == 'conflict')}")
        
    finally:
        db.close()


def demo_conflict_resolution():
    """Demonstrate conflict detection and resolution"""
    print("\n" + "="*60)
    print("DEMO: Conflict Resolution")
    print("="*60)
    
    db = SessionLocal()
    try:
        sync_service = SyncService(db)
        
        # Create operation that will cause conflict
        print("\n1. Creating operation with version conflict...")
        operation1 = SyncOperationCreate(
            entity_type="project",
            entity_id=999,
            operation_type="update",
            changes={"name": "Server Version"},
            client_timestamp=datetime.now(),
            version=1
        )
        
        sync_op1 = sync_service.create_sync_operation(
            user_id=1,
            device_id="demo-device-1",
            operation=operation1
        )
        print(f" First operation: Status={sync_op1.status.value}")
        
        # Create conflicting operation
        print("\n2. Creating conflicting operation...")
        operation2 = SyncOperationCreate(
            entity_type="project",
            entity_id=999,
            operation_type="update",
            changes={"name": "Client Version"},
            client_timestamp=datetime.now() + timedelta(seconds=5),
            version=2,
            parent_version=1  # This will cause conflict if server is at version 2
        )
        
        sync_op2 = sync_service.create_sync_operation(
            user_id=1,
            device_id="demo-device-2",
            operation=operation2
        )
        print(f" Second operation: Status={sync_op2.status.value}")
        
        # Check for conflicts
        print("\n3. Checking for conflicts...")
        from backend.models.sync_models import SyncConflict
        conflicts = db.query(SyncConflict).filter(
            SyncConflict.user_id == 1,
            SyncConflict.resolved == False
        ).all()
        
        if conflicts:
            print(f" Found {len(conflicts)} conflict(s)")
            
            # Resolve first conflict
            conflict = conflicts[0]
            print(f"\n4. Resolving conflict {conflict.id}...")
            print(f"  - Server data: {conflict.server_data}")
            print(f"  - Client data: {conflict.client_data}")
            print(f"  - Resolution strategy: latest_wins")
            
            resolution = ConflictResolutionRequest(
                conflict_id=conflict.id,
                resolution_strategy=ConflictResolutionEnum.LATEST_WINS
            )
            
            resolved = sync_service.resolve_conflict(1, resolution)
            print(f" Conflict resolved: {resolved.resolved}")
        else:
            print(" No conflicts detected")
        
    finally:
        db.close()


def demo_sync_scheduling():
    """Demonstrate sync scheduling"""
    print("\n" + "="*60)
    print("DEMO: Sync Scheduling")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Create schedule
        print("\n1. Creating sync schedule...")
        schedule = sync_scheduler.create_schedule(
            db=db,
            user_id=1,
            device_id="demo-device-1",
            sync_interval=300,  # 5 minutes
            auto_sync=True,
            sync_on_startup=True,
            entity_types=["project", "customer", "product"]
        )
        
        print(f" Schedule created:")
        print(f"  - Sync interval: {schedule.sync_interval}s")
        print(f"  - Auto sync: {schedule.auto_sync}")
        print(f"  - Next sync: {schedule.next_sync_at}")
        
        # Trigger manual sync
        print("\n2. Triggering manual sync...")
        sync_scheduler.trigger_manual_sync(1, "demo-device-1")
        print(" Manual sync triggered")
        
        # Disable schedule
        print("\n3. Disabling schedule...")
        sync_scheduler.disable_schedule(db, 1, "demo-device-1")
        print(" Schedule disabled")
        
    finally:
        db.close()


def demo_offline_queue():
    """Demonstrate offline sync queue"""
    print("\n" + "="*60)
    print("DEMO: Offline Sync Queue")
    print("="*60)
    
    db = SessionLocal()
    try:
        sync_service = SyncService(db)
        
        # Add operations to offline queue
        print("\n1. Adding operations to offline queue...")
        operations = [
            ("project", 101, "update", {"name": "Offline Update 1"}, 5),
            ("customer", 201, "create", {"name": "Offline Customer"}, 10),
            ("product", 301, "update", {"price": 799.99}, 3)
        ]
        
        for entity_type, entity_id, op_type, data, priority in operations:
            queue_item = sync_service.add_to_offline_queue(
                user_id=1,
                device_id="demo-device-1",
                entity_type=entity_type,
                entity_id=entity_id,
                operation_type=op_type,
                data=data,
                priority=priority
            )
            print(f" Added to queue: {entity_type}:{entity_id} (priority={priority})")
        
        # Get queue status
        print("\n2. Checking offline queue...")
        status = sync_service.get_sync_status(1, "demo-device-1")
        print(f" Offline queue size: {status['offline_queue_size']}")
        
        # Process queue
        print("\n3. Processing offline queue...")
        results = sync_service.process_offline_queue(1, "demo-device-1")
        print(f" Processed {len(results)} operations from queue")
        
    finally:
        db.close()


def demo_sync_statistics():
    """Demonstrate sync statistics"""
    print("\n" + "="*60)
    print("DEMO: Sync Statistics")
    print("="*60)
    
    db = SessionLocal()
    try:
        from backend.models.sync_models import SyncOperation, SyncConflict, SyncStatus
        from sqlalchemy import and_, func
        
        # Get statistics
        print("\n1. Gathering sync statistics...")
        
        total_syncs = db.query(SyncOperation).filter(
            SyncOperation.user_id == 1
        ).count()
        
        successful = db.query(SyncOperation).filter(
            and_(
                SyncOperation.user_id == 1,
                SyncOperation.status == SyncStatus.COMPLETED
            )
        ).count()
        
        failed = db.query(SyncOperation).filter(
            and_(
                SyncOperation.user_id == 1,
                SyncOperation.status == SyncStatus.FAILED
            )
        ).count()
        
        conflicts = db.query(SyncConflict).filter(
            SyncConflict.user_id == 1
        ).count()
        
        resolved = db.query(SyncConflict).filter(
            and_(
                SyncConflict.user_id == 1,
                SyncConflict.resolved == True
            )
        ).count()
        
        print(f"\n Sync Statistics:")
        print(f"  - Total syncs: {total_syncs}")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {failed}")
        print(f"  - Success rate: {(successful/total_syncs*100) if total_syncs > 0 else 0:.1f}%")
        print(f"  - Total conflicts: {conflicts}")
        print(f"  - Resolved conflicts: {resolved}")
        print(f"  - Pending conflicts: {conflicts - resolved}")
        
    finally:
        db.close()


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("SYNCHRONIZATION SYSTEM DEMO")
    print("="*60)
    print("\nThis demo showcases the synchronization system features:")
    print("1. Basic synchronization")
    print("2. Batch synchronization")
    print("3. Conflict detection and resolution")
    print("4. Sync scheduling")
    print("5. Offline sync queue")
    print("6. Sync statistics")
    
    try:
        demo_basic_sync()
        demo_batch_sync()
        demo_conflict_resolution()
        demo_sync_scheduling()
        demo_offline_queue()
        demo_sync_statistics()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nAll synchronization features demonstrated successfully!")
        print("\nFor more information, see:")
        print("- docs/SYNCHRONIZATION_SYSTEM_GUIDE.md")
        print("- docs/SYNCHRONIZATION_QUICK_REFERENCE.md")
        
    except Exception as e:
        print(f"\n Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
