# Synchronization System - Quick Reference

## Quick Start

### 1. Create Sync Schedule
```http
POST /api/v1/sync/schedule
{
  "device_id": "my-device",
  "sync_interval": 300,
  "auto_sync": true
}
```

### 2. Sync Data
```http
POST /api/v1/sync/batch
{
  "device_id": "my-device",
  "operations": [{
    "entity_type": "project",
    "entity_id": 123,
    "operation_type": "update",
    "changes": {...},
    "client_timestamp": "2024-01-15T10:30:00Z",
    "version": 2
  }]
}
```

### 3. Check Status
```http
GET /api/v1/sync/status?device_id=my-device
```

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/sync/operations` | POST | Create single sync operation |
| `/sync/batch` | POST | Batch sync multiple operations |
| `/sync/status` | GET | Get sync status |
| `/sync/conflicts` | GET | List conflicts |
| `/sync/conflicts/{id}/resolve` | POST | Resolve conflict |
| `/sync/schedule` | POST | Create/update schedule |
| `/sync/schedule` | GET | Get schedule |
| `/sync/manual` | POST | Trigger manual sync |
| `/sync/offline/queue` | POST | Add to offline queue |
| `/sync/offline/process` | POST | Process offline queue |
| `/sync/logs` | GET | Get sync logs |
| `/sync/statistics` | GET | Get statistics |

## Conflict Resolution Strategies

| Strategy | Description |
|----------|-------------|
| `server_wins` | Server data takes precedence |
| `client_wins` | Client data takes precedence |
| `latest_wins` | Most recent timestamp wins |
| `manual` | User manually resolves |
| `merge` | Automatically merge changes |

## Operation Types

- `create` - Create new entity
- `update` - Update existing entity
- `delete` - Delete entity

## Sync Status Values

- `pending` - Waiting to be processed
- `in_progress` - Currently processing
- `completed` - Successfully completed
- `failed` - Failed with error
- `conflict` - Conflict detected

## Common Patterns

### Offline Operation
```typescript
// When offline, add to queue
await syncService.addToOfflineQueue({
  entity_type: 'project',
  operation_type: 'update',
  data: {...},
  priority: 5
});

// When online, process queue
await syncService.processOfflineQueue();
```

### Conflict Handling
```typescript
// Get conflicts
const conflicts = await syncService.getConflicts();

// Resolve with strategy
await syncService.resolveConflict(conflictId, {
  resolution_strategy: 'server_wins'
});
```

### Manual Sync
```typescript
// Trigger immediate sync
await syncService.triggerManualSync('device-id');
```

## Configuration

### Sync Intervals
- Minimum: 60 seconds
- Maximum: 86400 seconds (24 hours)
- Recommended: 300 seconds (5 minutes)

### Priority Levels
- 0: Low priority
- 5: Normal priority
- 10: High priority

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid request data |
| 401 | Authentication required |
| 404 | Resource not found |
| 409 | Conflict detected |
| 500 | Server error |

## Monitoring

### Key Metrics
```http
GET /api/v1/sync/statistics
```

Returns:
- Total syncs
- Success rate
- Conflict rate
- Average duration
- Queue size

### Recent Logs
```http
GET /api/v1/sync/logs?limit=50
```

## Tips

✅ **DO:**
- Sync frequently to minimize conflicts
- Use batch operations for efficiency
- Monitor sync statistics
- Handle conflicts promptly
- Queue operations when offline

❌ **DON'T:**
- Set sync interval too low (< 60s)
- Ignore conflicts
- Sync without version control
- Skip error handling
- Force sync without reviewing conflicts

## Support

For detailed documentation, see:
- [Synchronization System Guide](./SYNCHRONIZATION_SYSTEM_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
