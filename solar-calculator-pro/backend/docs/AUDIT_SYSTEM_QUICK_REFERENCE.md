# Database Audit System - Quick Reference

## Quick Start

```python
from backend.services.audit_service import AuditService
from backend.models.audit_schemas import AuditLogCreate, ActionType

# Initialize
audit_service = AuditService(db)

# Log a change
audit_service.log_change(AuditLogCreate(
    user_id=1,
    action=ActionType.UPDATE,
    table_name="projects",
    record_id="123",
    old_values={"status": "draft"},
    new_values={"status": "active"}
))
```

## API Endpoints

### Change Tracking
```
POST   /api/v1/audit/logs                    # Create audit log
GET    /api/v1/audit/logs                    # Get audit logs
GET    /api/v1/audit/logs/{id}               # Get specific log
GET    /api/v1/audit/logs/record/{table}/{id} # Get record history
```

### Data Access
```
POST   /api/v1/audit/access                  # Log data access
GET    /api/v1/audit/access                  # Get access logs
```

### User Actions
```
POST   /api/v1/audit/actions                 # Log user action
GET    /api/v1/audit/actions                 # Get action logs
```

### Compliance
```
POST   /api/v1/audit/compliance              # Log compliance event
GET    /api/v1/audit/compliance              # Get compliance logs
```

### Reports
```
POST   /api/v1/audit/reports                 # Create report
GET    /api/v1/audit/reports                 # Get reports
```

### Statistics
```
GET    /api/v1/audit/statistics/audit        # Audit statistics
GET    /api/v1/audit/statistics/access       # Access statistics
GET    /api/v1/audit/statistics/compliance   # Compliance statistics
```

## Action Types

### Audit Actions
- `CREATE` - Record creation
- `UPDATE` - Record modification
- `DELETE` - Record deletion
- `READ` - Record access

### Query Types
- `SELECT` - Single record query
- `SEARCH` - Multiple records search
- `EXPORT` - Data export operation

### Action Categories
- `AUTH` - Authentication/authorization
- `CALCULATION` - Solar/heat pump calculations
- `REPORT` - Report generation
- `ADMIN` - Administrative actions
- `CRM` - CRM operations
- `PRODUCT` - Product management
- `PDF` - PDF generation
- `SYSTEM` - System operations

### Action Status
- `SUCCESS` - Operation completed successfully
- `FAILURE` - Operation failed
- `ERROR` - Operation encountered error

### Compliance Types
- `GDPR` - GDPR compliance events
- `DATA_RETENTION` - Data retention policies
- `SECURITY` - Security events
- `PRIVACY` - Privacy-related events
- `ACCESS_CONTROL` - Access control events

### Report Types
- `AUDIT` - Audit trail report
- `ACCESS` - Data access report
- `COMPLIANCE` - Compliance report
- `SECURITY` - Security report
- `USER_ACTIVITY` - User activity report

## Common Queries

### Get user's recent changes
```http
GET /api/v1/audit/logs?user_id=1&limit=50
```

### Get changes to specific table
```http
GET /api/v1/audit/logs?table_name=projects&date_from=2024-01-01
```

### Get failed actions
```http
GET /api/v1/audit/actions?status=FAILURE&limit=100
```

### Get non-compliant events
```http
GET /api/v1/audit/compliance?compliance_status=NON_COMPLIANT
```

### Get monthly statistics
```http
GET /api/v1/audit/statistics/audit?date_from=2024-01-01&date_to=2024-01-31
```

## Python Examples

### Log Database Change
```python
audit_service.log_change(AuditLogCreate(
    user_id=current_user.id,
    username=current_user.username,
    action=ActionType.UPDATE,
    table_name="customers",
    record_id="456",
    old_values={"email": "old@example.com"},
    new_values={"email": "new@example.com"},
    ip_address=request.client.host
))
```

### Log Data Access
```python
audit_service.log_data_access(DataAccessLogCreate(
    user_id=current_user.id,
    username=current_user.username,
    table_name="customers",
    query_type=QueryType.SEARCH,
    query_params={"filter": "active"},
    result_count=50,
    ip_address=request.client.host
))
```

### Log User Action
```python
audit_service.log_user_action(UserActionLogCreate(
    user_id=current_user.id,
    username=current_user.username,
    action_type="PDF_GENERATION",
    action_category=ActionCategory.PDF,
    action_details={"project_id": 123, "template": "standard"},
    status=ActionStatus.SUCCESS,
    duration_ms=2500
))
```

### Log Compliance Event
```python
audit_service.log_compliance_event(ComplianceLogCreate(
    compliance_type=ComplianceType.GDPR,
    event_type="DATA_EXPORT",
    user_id=current_user.id,
    username=current_user.username,
    affected_data={"table": "customers", "count": 100},
    compliance_status=ComplianceStatus.COMPLIANT,
    details={"export_format": "CSV", "reason": "User request"}
))
```

### Get Record History
```python
history = audit_service.get_record_history("projects", "123")
for log in history:
    print(f"{log.timestamp}: {log.action} by {log.username}")
    print(f"Changes: {log.changes}")
```

### Generate Report
```python
report = audit_service.create_audit_report(
    AuditReportCreate(
        report_type=ReportType.AUDIT,
        report_name="Monthly Audit - January 2024",
        date_from=datetime(2024, 1, 1),
        date_to=datetime(2024, 1, 31),
        file_format=ReportFormat.PDF
    ),
    created_by_id=current_user.id
)
```

### Get Statistics
```python
# Audit statistics
audit_stats = audit_service.get_audit_statistics(
    date_from=datetime(2024, 1, 1),
    date_to=datetime(2024, 1, 31)
)
print(f"Total changes: {audit_stats.total_changes}")
print(f"Most active user: {audit_stats.most_active_users[0]}")

# Access statistics
access_stats = audit_service.get_access_statistics(
    date_from=datetime(2024, 1, 1),
    date_to=datetime(2024, 1, 31)
)
print(f"Total accesses: {access_stats.total_accesses}")

# Compliance statistics
compliance_stats = audit_service.get_compliance_statistics(
    date_from=datetime(2024, 1, 1),
    date_to=datetime(2024, 1, 31)
)
print(f"Compliance rate: {compliance_stats.compliance_rate}%")
```

## Database Tables

- `audit_logs` - All database changes
- `data_access_logs` - Data access tracking
- `user_action_logs` - User activity tracking
- `compliance_logs` - Compliance events
- `audit_reports` - Generated reports

## Key Features

✅ **Automatic change tracking** - All CREATE, UPDATE, DELETE operations  
✅ **Data access logging** - Track who accessed what data  
✅ **User action logging** - Complete activity history  
✅ **Compliance tracking** - GDPR and regulatory compliance  
✅ **Audit reports** - Comprehensive reporting system  
✅ **Statistics** - Real-time metrics and analytics  
✅ **Performance optimized** - Indexed for fast queries  
✅ **Security** - Role-based access control  

## Requirements

- **11.1**: Security audit logging
- **12.1**: API documentation and compliance reporting

## See Also

- [Complete Guide](./AUDIT_SYSTEM_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Security Guide](./SECURITY_GUIDE.md)
