# System Maintenance Tools - Complete Guide

## Overview

The System Maintenance Tools provide comprehensive functionality for maintaining, monitoring, and repairing the Solar Calculator Pro application. This system includes database maintenance, cache management, log cleanup, temp file management, system diagnostics, and repair tools.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Database Maintenance](#database-maintenance)
5. [Cache Management](#cache-management)
6. [Log Management](#log-management)
7. [Temp File Cleanup](#temp-file-cleanup)
8. [System Diagnostics](#system-diagnostics)
9. [Repair Tools](#repair-tools)
10. [Automation](#automation)
11. [Best Practices](#best-practices)

## Features

### Core Capabilities

- **Database Maintenance**: Vacuum, analyze, reindex, and optimize database tables
- **Cache Management**: Monitor cache usage, clear unused entries, manage cache lifecycle
- **Log Management**: Track log files, cleanup old logs, compress before deletion
- **Temp File Cleanup**: Identify and remove temporary files based on age and usage
- **System Diagnostics**: Monitor database, disk, memory, CPU, network, and services
- **Repair Tools**: Fix permissions, rebuild indexes, repair corrupted data
- **Maintenance Logs**: Track all maintenance operations with detailed logging
- **Quick Actions**: One-click cleanup and health checks

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Maintenance System                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Database   │  │    Cache     │  │     Logs     │      │
│  │ Maintenance  │  │  Management  │  │  Management  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Temp Files  │  │    System    │  │    Repair    │      │
│  │   Cleanup    │  │ Diagnostics  │  │    Tools     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Maintenance Logging & Tracking            │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**maintenance_logs**: Track all maintenance operations
- operation_type, operation_name, status
- details (JSON), error_message
- started_at, completed_at, duration_seconds
- performed_by

**system_diagnostics**: Store diagnostic results
- diagnostic_type, status (healthy/warning/critical)
- metrics (JSON), issues, recommendations
- checked_at

**cache_entries**: Manage cache lifecycle
- cache_key, cache_type, size_bytes
- hit_count, last_accessed, created_at
- expires_at, is_valid

**temp_files**: Track temporary files
- file_path, file_type, size_bytes
- created_by, created_at, last_accessed
- should_delete, delete_after

## API Endpoints

### Base URL
```
/api/v1/maintenance
```

### Database Maintenance

#### Perform Database Maintenance
```http
POST /database
Content-Type: application/json

{
  "operation": "vacuum|analyze|reindex|optimize",
  "tables": ["table1", "table2"],  // optional
  "full": false
}
```

**Operations:**
- `vacuum`: Clean up dead tuples and reclaim space
- `analyze`: Update statistics for query optimization
- `reindex`: Rebuild database indexes
- `optimize`: Combination of vacuum and analyze

**Response:**
```json
{
  "operation": "vacuum",
  "status": "success",
  "tables_processed": ["users", "projects", "calculations"],
  "duration_seconds": 2.45,
  "details": {
    "operation": "VACUUM"
  }
}
```

### Cache Management

#### Get Cache Statistics
```http
GET /cache/stats
```

**Response:**
```json
{
  "total_entries": 1250,
  "total_size_bytes": 52428800,
  "total_size_mb": 50.0,
  "cache_types": {
    "calculation": 800,
    "product": 300,
    "pdf": 150
  },
  "hit_rate": 85.5,
  "oldest_entry": "2024-01-01T00:00:00Z",
  "newest_entry": "2024-01-15T12:00:00Z"
}
```

#### Clear Cache
```http
POST /cache/clear
Content-Type: application/json

{
  "cache_type": "calculation",  // optional
  "older_than_days": 7,          // optional
  "unused_only": false
}
```

**Response:**
```json
{
  "entries_cleared": 450,
  "size_freed_mb": 15.5,
  "duration_seconds": 0.85
}
```

### Log Management

#### Get Log Statistics
```http
GET /logs/stats
```

**Response:**
```json
{
  "total_log_files": 45,
  "total_size_bytes": 104857600,
  "total_size_mb": 100.0,
  "log_types": {
    "app": 20,
    "error": 15,
    "access": 10
  },
  "oldest_log": "2023-12-01T00:00:00Z",
  "newest_log": "2024-01-15T12:00:00Z",
  "error_count_24h": 12,
  "warning_count_24h": 45
}
```

#### Cleanup Logs
```http
POST /logs/cleanup
Content-Type: application/json

{
  "older_than_days": 30,
  "log_level": "ERROR",           // optional
  "compress_before_delete": true
}
```

**Response:**
```json
{
  "files_deleted": 15,
  "files_compressed": 15,
  "size_freed_mb": 45.5,
  "duration_seconds": 3.2
}
```

### Temp File Cleanup

#### Get Temp File Statistics
```http
GET /temp-files/stats
```

**Response:**
```json
{
  "total_files": 234,
  "total_size_bytes": 524288000,
  "total_size_mb": 500.0,
  "file_types": {
    "pdf": 120,
    "image": 80,
    "cache": 34
  },
  "oldest_file": "2024-01-01T00:00:00Z",
  "files_to_delete": 45
}
```

#### Cleanup Temp Files
```http
POST /temp-files/cleanup
Content-Type: application/json

{
  "older_than_hours": 24,
  "file_types": ["pdf", "image"],  // optional
  "force": false
}
```

**Response:**
```json
{
  "files_deleted": 45,
  "size_freed_mb": 125.5,
  "duration_seconds": 1.8
}
```

### System Diagnostics

#### Run Diagnostics
```http
POST /diagnostics
Content-Type: application/json

{
  "diagnostic_types": ["database", "disk", "memory", "cpu", "network", "services"],
  "detailed": false
}
```

**Response:**
```json
{
  "overall_status": "healthy",
  "diagnostics": [
    {
      "diagnostic_type": "database",
      "status": "healthy",
      "metrics": {
        "connection": "OK",
        "table_count": 25,
        "size_mb": 1250.5
      },
      "issues": [],
      "recommendations": [],
      "checked_at": "2024-01-15T12:00:00Z"
    },
    {
      "diagnostic_type": "disk",
      "status": "warning",
      "metrics": {
        "total_gb": 500.0,
        "used_gb": 425.0,
        "free_gb": 75.0,
        "percent_used": 85.0
      },
      "issues": ["Disk usage high: 85.0%"],
      "recommendations": ["Consider cleaning up old files"],
      "checked_at": "2024-01-15T12:00:00Z"
    }
  ],
  "summary": {
    "total_diagnostics": 6,
    "healthy": 4,
    "warnings": 2,
    "critical": 0
  }
}
```

### Repair Tools

#### Perform Repair
```http
POST /repair
Content-Type: application/json

{
  "operation": "fix_permissions|rebuild_index|repair_database|reset_cache|fix_orphaned_files|repair_corrupted_data",
  "target": "specific_table",  // optional
  "dry_run": true,
  "backup_first": true
}
```

**Response:**
```json
{
  "operation": "rebuild_index",
  "status": "success",
  "items_repaired": 15,
  "items_failed": 0,
  "backup_created": "/backups/backup_20240115_120000.sql",
  "details": {},
  "duration_seconds": 5.2
}
```

### Maintenance Logs

#### Get Maintenance Logs
```http
GET /logs?operation_type=database&limit=100
```

**Response:**
```json
[
  {
    "id": 1,
    "operation_type": "database",
    "operation_name": "vacuum",
    "status": "success",
    "details": {
      "tables_processed": ["users", "projects"]
    },
    "error_message": null,
    "started_at": "2024-01-15T12:00:00Z",
    "completed_at": "2024-01-15T12:00:05Z",
    "duration_seconds": 5.2,
    "performed_by": "admin"
  }
]
```

### Quick Actions

#### Quick Cleanup
```http
POST /quick-cleanup
```

Performs:
- Cache cleanup (unused entries)
- Log cleanup (older than 30 days)
- Temp file cleanup (older than 24 hours)
- Database vacuum

**Response:**
```json
{
  "status": "success",
  "message": "Quick cleanup completed",
  "results": {
    "cache": {
      "entries_cleared": 450,
      "size_freed_mb": 15.5
    },
    "logs": {
      "files_deleted": 15,
      "size_freed_mb": 45.5
    },
    "temp_files": {
      "files_deleted": 45,
      "size_freed_mb": 125.5
    },
    "database": {
      "tables_processed": 25
    }
  }
}
```

#### Health Check
```http
GET /health-check
```

**Response:**
```json
{
  "status": "healthy",
  "summary": {
    "total_diagnostics": 4,
    "healthy": 3,
    "warnings": 1,
    "critical": 0
  },
  "diagnostics": [
    {
      "type": "database",
      "status": "healthy",
      "metrics": {
        "connection": "OK",
        "table_count": 25
      }
    }
  ]
}
```

## Database Maintenance

### When to Run

- **Vacuum**: Weekly or after large deletions
- **Analyze**: After significant data changes
- **Reindex**: Monthly or when query performance degrades
- **Optimize**: Weekly as part of routine maintenance

### Best Practices

1. **Schedule during low-traffic periods**
2. **Monitor duration and impact**
3. **Use full vacuum sparingly** (locks tables)
4. **Analyze after bulk imports**
5. **Reindex if queries slow down**

### Example Usage

```python
from backend.services.maintenance_service import MaintenanceService
from backend.models.maintenance_schemas import DatabaseMaintenanceRequest

service = MaintenanceService(db)

# Weekly optimization
result = service.perform_database_maintenance(
    DatabaseMaintenanceRequest(
        operation="optimize",
        full=False
    ),
    user="scheduler"
)
```

## Cache Management

### Cache Types

- **calculation**: Solar and heat pump calculations
- **product**: Product database queries
- **pdf**: Generated PDF documents
- **api**: API response caching

### Cleanup Strategies

1. **Unused entries**: Clear entries with zero hits
2. **Age-based**: Clear entries older than X days
3. **Type-specific**: Clear specific cache types
4. **Size-based**: Clear when cache exceeds threshold

### Example Usage

```python
# Clear unused cache entries
result = service.clear_cache(
    CacheClearRequest(unused_only=True),
    user="admin"
)

# Clear old calculation cache
result = service.clear_cache(
    CacheClearRequest(
        cache_type="calculation",
        older_than_days=7
    ),
    user="admin"
)
```

## Log Management

### Log Types

- **app.log**: Application logs
- **error.log**: Error logs
- **access.log**: API access logs
- **maintenance.log**: Maintenance operation logs

### Cleanup Policy

- Keep logs for 30 days by default
- Compress logs before deletion
- Archive critical error logs
- Monitor error/warning counts

### Example Usage

```python
# Cleanup old logs
result = service.cleanup_logs(
    LogCleanupRequest(
        older_than_days=30,
        compress_before_delete=True
    ),
    user="admin"
)
```

## Temp File Cleanup

### File Types

- **pdf**: Temporary PDF files
- **image**: Temporary images
- **cache**: Temporary cache files
- **upload**: Temporary upload files

### Cleanup Policy

- Delete files older than 24 hours
- Force delete if marked for deletion
- Track file access patterns
- Clean up orphaned files

### Example Usage

```python
# Cleanup old temp files
result = service.cleanup_temp_files(
    TempFileCleanupRequest(
        older_than_hours=24,
        file_types=["pdf", "image"]
    ),
    user="admin"
)
```

## System Diagnostics

### Diagnostic Types

1. **Database**: Connection, size, table count
2. **Disk**: Space usage, I/O performance
3. **Memory**: RAM usage, available memory
4. **CPU**: CPU usage, load average
5. **Network**: Connectivity, bandwidth
6. **Services**: Service health status

### Status Levels

- **Healthy**: All metrics within normal range
- **Warning**: Metrics approaching thresholds
- **Critical**: Immediate attention required

### Thresholds

- Disk usage > 90%: Critical
- Disk usage > 80%: Warning
- Memory usage > 90%: Critical
- Memory usage > 80%: Warning
- CPU usage > 90%: Critical
- CPU usage > 80%: Warning

### Example Usage

```python
# Run full diagnostics
result = service.run_diagnostics(
    DiagnosticRequest(
        diagnostic_types=["database", "disk", "memory", "cpu"],
        detailed=True
    )
)

# Check overall status
if result.overall_status == DiagnosticStatus.CRITICAL:
    # Send alert
    pass
```

## Repair Tools

### Available Repairs

1. **fix_permissions**: Fix file and directory permissions
2. **rebuild_index**: Rebuild database indexes
3. **repair_database**: Repair database integrity
4. **reset_cache**: Reset all caches
5. **fix_orphaned_files**: Clean up orphaned files
6. **repair_corrupted_data**: Repair corrupted data

### Safety Features

- **Dry run mode**: Simulate without changes
- **Backup first**: Create backup before repair
- **Detailed logging**: Track all repair operations
- **Rollback support**: Restore from backup if needed

### Example Usage

```python
# Dry run first
result = service.perform_repair(
    RepairRequest(
        operation=RepairOperation.REBUILD_INDEX,
        dry_run=True,
        backup_first=False
    ),
    user="admin"
)

# Actual repair with backup
result = service.perform_repair(
    RepairRequest(
        operation=RepairOperation.REBUILD_INDEX,
        dry_run=False,
        backup_first=True
    ),
    user="admin"
)
```

## Automation

### Scheduled Maintenance

Create cron jobs for regular maintenance:

```bash
# Daily quick cleanup at 2 AM
0 2 * * * curl -X POST http://localhost:8000/api/v1/maintenance/quick-cleanup

# Weekly database optimization on Sunday at 3 AM
0 3 * * 0 curl -X POST http://localhost:8000/api/v1/maintenance/database \
  -H "Content-Type: application/json" \
  -d '{"operation": "optimize"}'

# Monthly full vacuum on 1st at 4 AM
0 4 1 * * curl -X POST http://localhost:8000/api/v1/maintenance/database \
  -H "Content-Type: application/json" \
  -d '{"operation": "vacuum", "full": true}'
```

### Monitoring Integration

```python
# Check health every 5 minutes
import schedule
import requests

def check_health():
    response = requests.get("http://localhost:8000/api/v1/maintenance/health-check")
    data = response.json()
    
    if data["status"] != "healthy":
        send_alert(data)

schedule.every(5).minutes.do(check_health)
```

## Best Practices

### General

1. **Schedule maintenance during low-traffic periods**
2. **Monitor maintenance operation duration**
3. **Keep maintenance logs for audit trail**
4. **Test repairs in dry-run mode first**
5. **Always create backups before repairs**

### Database

1. **Vacuum regularly** to prevent bloat
2. **Analyze after bulk operations**
3. **Reindex when queries slow down**
4. **Monitor table sizes**
5. **Use full vacuum sparingly**

### Cache

1. **Clear unused entries regularly**
2. **Monitor cache hit rates**
3. **Set appropriate expiration times**
4. **Clear cache after major updates**

### Logs

1. **Rotate logs regularly**
2. **Compress old logs**
3. **Monitor error rates**
4. **Archive critical logs**
5. **Set up log alerts**

### Diagnostics

1. **Run diagnostics regularly**
2. **Set up automated alerts**
3. **Track trends over time**
4. **Act on warnings promptly**
5. **Document recurring issues**

## Troubleshooting

### Common Issues

**Issue**: Database maintenance takes too long
- **Solution**: Run during off-peak hours, use incremental vacuum

**Issue**: Cache grows too large
- **Solution**: Reduce expiration times, clear unused entries more frequently

**Issue**: Disk space warnings
- **Solution**: Clean up old logs and temp files, archive old data

**Issue**: High memory usage
- **Solution**: Restart services, investigate memory leaks

**Issue**: Repair operations fail
- **Solution**: Check logs, ensure sufficient disk space, verify permissions

## Support

For issues or questions:
- Check maintenance logs: `/api/v1/maintenance/logs`
- Run diagnostics: `/api/v1/maintenance/diagnostics`
- Review documentation
- Contact system administrator
