# Database Audit System - Complete Guide

## Overview

The Database Audit System provides comprehensive tracking and logging of all database changes, data access, user actions, and compliance events. This system is essential for security, compliance, and troubleshooting.

## Features

### 1. Change Tracking
- **Automatic logging** of all CREATE, UPDATE, DELETE operations
- **Before/after values** for all changes
- **Calculated differences** showing exactly what changed
- **Complete audit trail** for every database record

### 2. Data Access Logging
- Track all **read operations** (SELECT, SEARCH, EXPORT)
- Monitor **who accessed what data** and when
- Record **query parameters** and result counts
- Identify **unusual access patterns**

### 3. User Action Logging
- Log all **user activities** (login, logout, calculations, PDF generation)
- Track **action duration** and performance
- Record **success/failure status** with error messages
- Categorize actions by type (AUTH, CALCULATION, REPORT, etc.)

### 4. Compliance Logging
- Track **GDPR compliance** events
- Monitor **data retention** policies
- Log **security events**
- Record **privacy-related** activities

### 5. Audit Reports
- Generate **comprehensive reports** for any time period
- **Multiple report types**: Audit, Access, Compliance, Security
- **Export formats**: PDF, Excel, CSV, JSON
- **Automated summaries** with key statistics

## Architecture

### Database Tables

#### audit_logs
Tracks all database changes (CREATE, UPDATE, DELETE).

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    user_id INTEGER,
    username VARCHAR(255),
    action VARCHAR(50) NOT NULL,  -- CREATE, UPDATE, DELETE
    table_name VARCHAR(255) NOT NULL,
    record_id VARCHAR(255),
    old_values JSON,
    new_values JSON,
    changes JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255)
);
```

#### data_access_logs
Tracks data access (read operations).

```sql
CREATE TABLE data_access_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    user_id INTEGER,
    username VARCHAR(255),
    table_name VARCHAR(255) NOT NULL,
    record_id VARCHAR(255),
    query_type VARCHAR(50) NOT NULL,  -- SELECT, SEARCH, EXPORT
    query_params JSON,
    result_count INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255)
);
```

#### user_action_logs
Tracks user actions and activities.

```sql
CREATE TABLE user_action_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    user_id INTEGER,
    username VARCHAR(255),
    action_type VARCHAR(100) NOT NULL,
    action_category VARCHAR(50) NOT NULL,  -- AUTH, CALCULATION, REPORT, etc.
    action_details JSON,
    status VARCHAR(50) NOT NULL,  -- SUCCESS, FAILURE, ERROR
    error_message TEXT,
    duration_ms INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255)
);
```

#### compliance_logs
Tracks compliance events.

```sql
CREATE TABLE compliance_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    compliance_type VARCHAR(100) NOT NULL,  -- GDPR, DATA_RETENTION, etc.
    event_type VARCHAR(100) NOT NULL,
    user_id INTEGER,
    username VARCHAR(255),
    affected_data JSON,
    compliance_status VARCHAR(50) NOT NULL,  -- COMPLIANT, NON_COMPLIANT, PENDING
    details JSON,
    notes TEXT
);
```

#### audit_reports
Stores generated audit reports.

```sql
CREATE TABLE audit_reports (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL,
    created_by_id INTEGER NOT NULL,
    report_type VARCHAR(100) NOT NULL,  -- AUDIT, ACCESS, COMPLIANCE, SECURITY
    report_name VARCHAR(255) NOT NULL,
    date_from DATETIME NOT NULL,
    date_to DATETIME NOT NULL,
    filters JSON,
    summary JSON,
    file_path VARCHAR(500),
    file_format VARCHAR(20),  -- PDF, EXCEL, CSV, JSON
    status VARCHAR(50) NOT NULL  -- GENERATING, COMPLETED, FAILED
);
```

## API Endpoints

### Change Tracking

#### Create Audit Log
```http
POST /api/v1/audit/logs
Content-Type: application/json

{
  "user_id": 1,
  "username": "john.doe",
  "action": "UPDATE",
  "table_name": "projects",
  "record_id": "123",
  "old_values": {"status": "draft"},
  "new_values": {"status": "active"},
  "ip_address": "192.168.1.100",
  "session_id": "abc123"
}
```

#### Get Audit Logs
```http
GET /api/v1/audit/logs?user_id=1&action=UPDATE&date_from=2024-01-01&limit=100
```

#### Get Record History
```http
GET /api/v1/audit/logs/record/projects/123
```

### Data Access Logging

#### Create Data Access Log
```http
POST /api/v1/audit/access
Content-Type: application/json

{
  "user_id": 1,
  "username": "john.doe",
  "table_name": "customers",
  "query_type": "SELECT",
  "query_params": {"filter": "active"},
  "result_count": 50,
  "ip_address": "192.168.1.100"
}
```

#### Get Data Access Logs
```http
GET /api/v1/audit/access?user_id=1&table_name=customers&limit=100
```

### User Action Logging

#### Create User Action Log
```http
POST /api/v1/audit/actions
Content-Type: application/json

{
  "user_id": 1,
  "username": "john.doe",
  "action_type": "SOLAR_CALCULATION",
  "action_category": "CALCULATION",
  "action_details": {"system_size": 10.5},
  "status": "SUCCESS",
  "duration_ms": 1250,
  "ip_address": "192.168.1.100"
}
```

#### Get User Action Logs
```http
GET /api/v1/audit/actions?user_id=1&action_category=CALCULATION&limit=100
```

### Compliance Logging

#### Create Compliance Log
```http
POST /api/v1/audit/compliance
Content-Type: application/json

{
  "compliance_type": "GDPR",
  "event_type": "DATA_EXPORT",
  "user_id": 1,
  "username": "john.doe",
  "affected_data": {"table": "customers", "count": 100},
  "compliance_status": "COMPLIANT",
  "details": {"export_format": "CSV"}
}
```

#### Get Compliance Logs
```http
GET /api/v1/audit/compliance?compliance_type=GDPR&limit=100
```

### Audit Reports

#### Create Audit Report
```http
POST /api/v1/audit/reports
Content-Type: application/json

{
  "report_type": "AUDIT",
  "report_name": "Monthly Audit Report - January 2024",
  "date_from": "2024-01-01T00:00:00",
  "date_to": "2024-01-31T23:59:59",
  "file_format": "PDF"
}
```

#### Get Audit Reports
```http
GET /api/v1/audit/reports?report_type=AUDIT&limit=100
```

### Statistics

#### Get Audit Statistics
```http
GET /api/v1/audit/statistics/audit?date_from=2024-01-01&date_to=2024-01-31
```

Response:
```json
{
  "total_changes": 1250,
  "changes_by_action": {
    "CREATE": 450,
    "UPDATE": 650,
    "DELETE": 150
  },
  "changes_by_table": {
    "projects": 500,
    "customers": 400,
    "products": 350
  },
  "most_active_users": [
    {"username": "john.doe", "change_count": 450},
    {"username": "jane.smith", "change_count": 380}
  ]
}
```

#### Get Access Statistics
```http
GET /api/v1/audit/statistics/access?date_from=2024-01-01&date_to=2024-01-31
```

#### Get Compliance Statistics
```http
GET /api/v1/audit/statistics/compliance?date_from=2024-01-01&date_to=2024-01-31
```

## Usage Examples

### Python Service Usage

```python
from backend.services.audit_service import AuditService
from backend.models.audit_schemas import (
    AuditLogCreate, ActionType, 
    UserActionLogCreate, ActionCategory, ActionStatus
)

# Initialize service
audit_service = AuditService(db)

# Log a database change
audit_log = audit_service.log_change(AuditLogCreate(
    user_id=1,
    username="john.doe",
    action=ActionType.UPDATE,
    table_name="projects",
    record_id="123",
    old_values={"status": "draft"},
    new_values={"status": "active"},
    ip_address="192.168.1.100"
))

# Log a user action
action_log = audit_service.log_user_action(UserActionLogCreate(
    user_id=1,
    username="john.doe",
    action_type="SOLAR_CALCULATION",
    action_category=ActionCategory.CALCULATION,
    action_details={"system_size": 10.5},
    status=ActionStatus.SUCCESS,
    duration_ms=1250
))

# Get audit statistics
stats = audit_service.get_audit_statistics(
    date_from=datetime(2024, 1, 1),
    date_to=datetime(2024, 1, 31)
)
print(f"Total changes: {stats.total_changes}")
```

### Automatic Change Tracking

To automatically track changes, use SQLAlchemy event listeners:

```python
from sqlalchemy import event
from sqlalchemy.orm import Session

@event.listens_for(Session, 'before_flush')
def receive_before_flush(session, flush_context, instances):
    """Automatically log all changes before flush"""
    audit_service = AuditService(session)
    
    for obj in session.new:
        # Log CREATE
        audit_service.log_change(AuditLogCreate(
            action=ActionType.CREATE,
            table_name=obj.__tablename__,
            record_id=str(obj.id) if hasattr(obj, 'id') else None,
            new_values=obj_to_dict(obj)
        ))
    
    for obj in session.dirty:
        # Log UPDATE
        old_values = get_old_values(obj)
        new_values = obj_to_dict(obj)
        
        audit_service.log_change(AuditLogCreate(
            action=ActionType.UPDATE,
            table_name=obj.__tablename__,
            record_id=str(obj.id),
            old_values=old_values,
            new_values=new_values
        ))
    
    for obj in session.deleted:
        # Log DELETE
        audit_service.log_change(AuditLogCreate(
            action=ActionType.DELETE,
            table_name=obj.__tablename__,
            record_id=str(obj.id),
            old_values=obj_to_dict(obj)
        ))
```

## Best Practices

### 1. Performance
- Use **indexes** on frequently queried columns (timestamp, user_id, table_name)
- Implement **data retention policies** to archive old logs
- Use **batch operations** for bulk logging
- Consider **async logging** for high-volume operations

### 2. Security
- **Encrypt sensitive data** in audit logs
- Implement **access controls** (users can only see their own logs)
- **Protect audit logs** from tampering (write-only for most users)
- **Regular backups** of audit data

### 3. Compliance
- **Retain logs** according to regulatory requirements
- **Document** all compliance events
- **Regular audits** of the audit system itself
- **Automated alerts** for non-compliant events

### 4. Monitoring
- **Dashboard** for real-time audit metrics
- **Alerts** for unusual patterns
- **Regular reports** for management
- **Trend analysis** for security insights

## Troubleshooting

### High Volume of Logs
- Implement **log rotation** and archiving
- Use **sampling** for high-frequency operations
- Consider **separate database** for audit logs
- Implement **compression** for old logs

### Performance Issues
- Check **index usage** on audit tables
- Optimize **query patterns**
- Consider **read replicas** for reporting
- Implement **caching** for statistics

### Missing Logs
- Verify **event listeners** are registered
- Check **transaction handling**
- Ensure **proper error handling**
- Review **logging configuration**

## Requirements Mapping

This implementation satisfies the following requirements:

- **11.1**: Security audit logging and user authentication tracking
- **12.1**: Comprehensive API documentation and compliance reporting

## Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Security Guide](./SECURITY_GUIDE.md)
- [Database Schema](./DATABASE_SCHEMA_COMPLETE.md)
- [Compliance Guide](./COMPLIANCE_GUIDE.md)
