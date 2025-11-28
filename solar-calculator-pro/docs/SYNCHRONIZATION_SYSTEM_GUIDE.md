# Synchronization System Guide

## Overview

The Synchronization System provides robust data synchronization capabilities for the Solar Calculator Pro application, enabling seamless data sync across multiple devices with conflict resolution, offline support, and automatic scheduling.

## Features

### 1. Data Sync Framework
- **Batch Synchronization**: Sync multiple operations in a single request
- **Entity-Based Sync**: Sync specific entity types (projects, customers, products, etc.)
- **Version Control**: Track data versions to detect conflicts
- **Operation Types**: Support for create, update, and delete operations

### 2. Conflict Resolution
- **Automatic Detection**: Detect conflicts based on version mismatches
- **Multiple Strategies**:
  - **Server Wins**: Server data takes precedence
  - **Client Wins**: Client data takes precedence
  - **Latest Wins**: Most recent timestamp wins
  - **Manual**: User manually resolves conflict
  - **Merge**: Automatically merge non-conflicting changes
- **Conflict Tracking**: Full audit trail of conflicts and resolutions

### 3. Sync Scheduling
- **Automatic Sync**: Schedule periodic synchronization
- **Configurable Intervals**: Set sync frequency (60s - 24h)
- **Event-Based Sync**: Sync on startup/shutdown
- **Manual Trigger**: Manually trigger sync anytime

### 4. Offline Sync
- **Offline Queue**: Queue operations when offline
- **Priority System**: Prioritize critical operations
- **Automatic Processing**: Process queue when connection restored
- **Error Handling**: Retry failed operations with exponential backoff

### 5. Status Tracking
- **Real-Time Status**: Monitor sync progress
- **Detailed Logs**: Complete sync activity history
- **Statistics**: Track sync performance and success rates
- **Conflict Monitoring**: View pending and resolved conflicts

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Application                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Sync Client Service                    │ │
│  │  • Queue offline operations                         │ │
│  │  • Batch sync requests                              │ │
│  │  • Handle conflicts                                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Backend Server                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Sync Service                           │ │
│  │  • Process sync operations                          │ │
│  │  • Detect conflicts                                 │ │
│  │  • Apply resolution strategies                      │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Sync Scheduler                         │ │
│  │  • Schedule automatic syncs                         │ │
│  │  • Process offline queue                            │ │
│  │  • Manage sync intervals                            │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Database                               │ │
│  │  • sync_operations                                  │ │
│  │  • sync_conflicts                                   │ │
│  │  • sync_schedules                                   │ │
│  │  • sync_logs                                        │ │
│  │  • offline_sync_queue                               │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

### Sync Operations

#### Create Sync Operation
```http
POST /api/v1/sync/operations?device_id={device_id}
Content-Type: application/json

{
  "entity_type": "project",
  "entity_id": 123,
  "operation_type": "update",
  "changes": {
    "name": "Updated Project Name",
    "status": "active"
  },
  "client_timestamp": "2024-01-15T10:30:00Z",
  "version": 2,
  "parent_version": 1
}
```

#### Batch Sync
```http
POST /api/v1/sync/batch
Content-Type: application/json

{
  "device_id": "device-123",
  "operations": [
    {
      "entity_type": "project",
      "entity_id": 123,
      "operation_type": "update",
      "changes": {...},
      "client_timestamp": "2024-01-15T10:30:00Z",
      "version": 2
    },
    {
      "entity_type": "customer",
      "entity_id": 456,
      "operation_type": "create",
      "changes": {...},
      "client_timestamp": "2024-01-15T10:31:00Z",
      "version": 1
    }
  ],
  "force_sync": false
}
```

#### Get Sync Status
```http
GET /api/v1/sync/status?device_id={device_id}
```

Response:
```json
{
  "device_id": "device-123",
  "is_syncing": false,
  "last_sync_at": "2024-01-15T10:30:00Z",
  "last_sync_status": "completed",
  "pending_operations": 0,
  "conflicts_count": 2,
  "offline_queue_size": 5,
  "next_sync_at": "2024-01-15T10:35:00Z"
}
```

### Conflict Management

#### Get Conflicts
```http
GET /api/v1/sync/conflicts?device_id={device_id}&resolved=false
```

#### Resolve Conflict
```http
POST /api/v1/sync/conflicts/{conflict_id}/resolve
Content-Type: application/json

{
  "conflict_id": 789,
  "resolution_strategy": "server_wins"
}
```

Or with manual resolution:
```json
{
  "conflict_id": 789,
  "resolution_strategy": "manual",
  "resolved_data": {
    "name": "Manually Resolved Name",
    "status": "active"
  }
}
```

### Sync Scheduling

#### Create/Update Schedule
```http
POST /api/v1/sync/schedule
Content-Type: application/json

{
  "device_id": "device-123",
  "enabled": true,
  "sync_interval": 300,
  "auto_sync": true,
  "sync_on_startup": true,
  "sync_on_shutdown": true,
  "entity_types": ["project", "customer", "product"]
}
```

#### Get Schedule
```http
GET /api/v1/sync/schedule?device_id={device_id}
```

#### Enable/Disable Schedule
```http
POST /api/v1/sync/schedule/enable?device_id={device_id}
POST /api/v1/sync/schedule/disable?device_id={device_id}
```

#### Manual Sync Trigger
```http
POST /api/v1/sync/manual?device_id={device_id}
```

### Offline Queue

#### Add to Offline Queue
```http
POST /api/v1/sync/offline/queue?device_id={device_id}
Content-Type: application/json

{
  "entity_type": "project",
  "entity_id": 123,
  "operation_type": "update",
  "data": {
    "name": "Updated Name"
  },
  "priority": 5
}
```

#### Get Offline Queue
```http
GET /api/v1/sync/offline/queue?device_id={device_id}
```

#### Process Offline Queue
```http
POST /api/v1/sync/offline/process?device_id={device_id}
```

### Logs and Statistics

#### Get Sync Logs
```http
GET /api/v1/sync/logs?device_id={device_id}&limit=100
```

#### Get Statistics
```http
GET /api/v1/sync/statistics?device_id={device_id}
```

Response:
```json
{
  "total_syncs": 1250,
  "successful_syncs": 1200,
  "failed_syncs": 25,
  "total_conflicts": 50,
  "resolved_conflicts": 45,
  "pending_conflicts": 5,
  "average_sync_duration": 2.5,
  "last_24h_syncs": 48,
  "data_synced_mb": 125.5
}
```

## Usage Examples

### Python Backend Example

```python
from backend.services.sync_service import SyncService
from backend.services.sync_scheduler import sync_scheduler
from backend.models.sync_schemas import SyncOperationCreate

# Create sync service
sync_service = SyncService(db)

# Create sync operation
operation = SyncOperationCreate(
    entity_type="project",
    entity_id=123,
    operation_type="update",
    changes={"name": "New Name"},
    client_timestamp=datetime.now(),
    version=2,
    parent_version=1
)

sync_op = sync_service.create_sync_operation(
    user_id=1,
    device_id="device-123",
    operation=operation
)

# Setup sync schedule
schedule = sync_scheduler.create_schedule(
    db=db,
    user_id=1,
    device_id="device-123",
    sync_interval=300,  # 5 minutes
    auto_sync=True
)

# Add to offline queue
queue_item = sync_service.add_to_offline_queue(
    user_id=1,
    device_id="device-123",
    entity_type="project",
    entity_id=123,
    operation_type="update",
    data={"name": "Offline Update"},
    priority=5
)
```

### TypeScript Frontend Example

```typescript
import { syncService } from './services/syncService';

// Create sync operation
const operation = {
  entity_type: 'project',
  entity_id: 123,
  operation_type: 'update',
  changes: { name: 'New Name' },
  client_timestamp: new Date().toISOString(),
  version: 2,
  parent_version: 1
};

await syncService.createOperation('device-123', operation);

// Batch sync
const batchRequest = {
  device_id: 'device-123',
  operations: [operation1, operation2, operation3],
  force_sync: false
};

const result = await syncService.batchSync(batchRequest);

// Get sync status
const status = await syncService.getStatus('device-123');

// Resolve conflict
await syncService.resolveConflict(conflictId, {
  resolution_strategy: 'server_wins'
});

// Setup schedule
await syncService.createSchedule({
  device_id: 'device-123',
  enabled: true,
  sync_interval: 300,
  auto_sync: true
});
```

## Best Practices

### 1. Conflict Prevention
- Use optimistic locking with version numbers
- Sync frequently to minimize conflicts
- Implement proper data validation

### 2. Offline Support
- Queue all operations when offline
- Prioritize critical operations
- Provide user feedback on queue status

### 3. Performance
- Batch operations when possible
- Use appropriate sync intervals
- Monitor sync statistics

### 4. Error Handling
- Implement retry logic with exponential backoff
- Log all sync errors
- Provide user-friendly error messages

### 5. Security
- Authenticate all sync requests
- Validate data before applying changes
- Encrypt sensitive data

## Troubleshooting

### Common Issues

#### Sync Not Working
1. Check network connectivity
2. Verify authentication token
3. Check sync schedule is enabled
4. Review sync logs for errors

#### Conflicts Not Resolving
1. Verify resolution strategy is appropriate
2. Check conflict data is valid
3. Ensure user has permissions
4. Review conflict logs

#### Offline Queue Not Processing
1. Check network connectivity
2. Verify schedule is enabled
3. Check for errors in queue items
4. Review processing logs

## Monitoring

### Key Metrics
- Sync success rate
- Average sync duration
- Conflict rate
- Offline queue size
- Failed operations

### Alerts
- High conflict rate
- Sync failures
- Large offline queue
- Long sync duration

## Future Enhancements

- Real-time sync with WebSockets
- Differential sync (only changed fields)
- Compression for large data
- Peer-to-peer sync
- Advanced merge strategies
- Sync analytics dashboard
