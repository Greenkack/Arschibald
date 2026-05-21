# System Maintenance Tools - Quick Reference

## Quick Start

```bash
# Run migration
python backend/migrations/add_maintenance_tables.py

# Test the system
python backend/demo_maintenance.py
```

## Common Operations

### Quick Cleanup (One Command)
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/quick-cleanup
```

### Health Check
```bash
curl http://localhost:8000/api/v1/maintenance/health-check
```

## Database Maintenance

### Vacuum Database
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/database \
  -H "Content-Type: application/json" \
  -d '{"operation": "vacuum", "full": false}'
```

### Analyze Database
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/database \
  -H "Content-Type: application/json" \
  -d '{"operation": "analyze"}'
```

### Optimize Database
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/database \
  -H "Content-Type: application/json" \
  -d '{"operation": "optimize"}'
```

## Cache Management

### Get Cache Stats
```bash
curl http://localhost:8000/api/v1/maintenance/cache/stats
```

### Clear Unused Cache
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"unused_only": true}'
```

### Clear Old Cache
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"older_than_days": 7}'
```

## Log Management

### Get Log Stats
```bash
curl http://localhost:8000/api/v1/maintenance/logs/stats
```

### Cleanup Old Logs
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/logs/cleanup \
  -H "Content-Type: application/json" \
  -d '{"older_than_days": 30, "compress_before_delete": true}'
```

## Temp File Cleanup

### Get Temp File Stats
```bash
curl http://localhost:8000/api/v1/maintenance/temp-files/stats
```

### Cleanup Temp Files
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/temp-files/cleanup \
  -H "Content-Type: application/json" \
  -d '{"older_than_hours": 24}'
```

## System Diagnostics

### Run Full Diagnostics
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/diagnostics \
  -H "Content-Type: application/json" \
  -d '{"detailed": true}'
```

### Quick Diagnostics
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/diagnostics \
  -H "Content-Type: application/json" \
  -d '{"diagnostic_types": ["database", "disk", "memory"], "detailed": false}'
```

## Repair Tools

### Dry Run Repair
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/repair \
  -H "Content-Type: application/json" \
  -d '{"operation": "rebuild_index", "dry_run": true, "backup_first": false}'
```

### Rebuild Indexes
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/repair \
  -H "Content-Type: application/json" \
  -d '{"operation": "rebuild_index", "dry_run": false, "backup_first": true}'
```

### Reset Cache
```bash
curl -X POST http://localhost:8000/api/v1/maintenance/repair \
  -H "Content-Type: application/json" \
  -d '{"operation": "reset_cache", "dry_run": false, "backup_first": false}'
```

## Maintenance Logs

### Get Recent Logs
```bash
curl "http://localhost:8000/api/v1/maintenance/logs?limit=10"
```

### Get Database Maintenance Logs
```bash
curl "http://localhost:8000/api/v1/maintenance/logs?operation_type=database&limit=20"
```

## Python Usage

### Database Maintenance
```python
from backend.services.maintenance_service import MaintenanceService
from backend.models.maintenance_schemas import DatabaseMaintenanceRequest

service = MaintenanceService(db)
result = service.perform_database_maintenance(
    DatabaseMaintenanceRequest(operation="optimize"),
    user="admin"
)
```

### Cache Management
```python
from backend.models.maintenance_schemas import CacheClearRequest

# Get stats
stats = service.get_cache_stats()

# Clear cache
result = service.clear_cache(
    CacheClearRequest(unused_only=True),
    user="admin"
)
```

### System Diagnostics
```python
from backend.models.maintenance_schemas import DiagnosticRequest

result = service.run_diagnostics(
    DiagnosticRequest(detailed=True)
)

if result.overall_status == "critical":
    # Send alert
    pass
```

## Scheduled Maintenance

### Daily Cleanup (Cron)
```cron
# Daily at 2 AM
0 2 * * * curl -X POST http://localhost:8000/api/v1/maintenance/quick-cleanup
```

### Weekly Optimization (Cron)
```cron
# Sunday at 3 AM
0 3 * * 0 curl -X POST http://localhost:8000/api/v1/maintenance/database \
  -H "Content-Type: application/json" \
  -d '{"operation": "optimize"}'
```

### Monthly Full Vacuum (Cron)
```cron
# 1st of month at 4 AM
0 4 1 * * curl -X POST http://localhost:8000/api/v1/maintenance/database \
  -H "Content-Type: application/json" \
  -d '{"operation": "vacuum", "full": true}'
```

## Status Codes

- **200**: Success
- **401**: Unauthorized
- **500**: Internal server error

## Response Format

All endpoints return JSON:
```json
{
  "status": "success",
  "data": {...},
  "message": "Operation completed"
}
```

## Diagnostic Status Levels

- **healthy**: ✅ All systems normal
- **warning**: ⚠️ Attention needed
- **critical**: ❌ Immediate action required

## Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Disk Usage | > 80% | > 90% |
| Memory Usage | > 80% | > 90% |
| CPU Usage | > 80% | > 90% |
| Database Size | > 5GB | > 10GB |

## Best Practices

1. ✅ Run quick cleanup daily
2. ✅ Optimize database weekly
3. ✅ Monitor diagnostics regularly
4. ✅ Clear cache when needed
5. ✅ Backup before repairs
6. ✅ Test repairs in dry-run mode
7. ✅ Keep maintenance logs
8. ✅ Set up automated alerts

## Troubleshooting

### Maintenance Takes Too Long
- Run during off-peak hours
- Use incremental operations
- Check system resources

### Cache Growing Too Large
- Reduce expiration times
- Clear unused entries more frequently
- Monitor cache hit rates

### Disk Space Warnings
- Clean up old logs
- Remove temp files
- Archive old data

### High Memory Usage
- Restart services
- Check for memory leaks
- Clear caches

## Support

- Documentation: `/docs/SYSTEM_MAINTENANCE_GUIDE.md`
- Logs: `/api/v1/maintenance/logs`
- Diagnostics: `/api/v1/maintenance/diagnostics`
- Health Check: `/api/v1/maintenance/health-check`
