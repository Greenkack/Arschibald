# Database Management - Quick Reference

## Overview

The Database Management system provides comprehensive tools for managing the application database, including backup/restore, optimization, statistics, and data export functionality.

## Features

### 1. Backup Operations
- **Create Backup**: Create compressed or uncompressed database backups
- **List Backups**: View all available backups with metadata
- **Restore Backup**: Restore database from a backup file
- **Delete Backup**: Remove old backup files

### 2. Optimization Tools
- **VACUUM**: Reclaim unused space
- **ANALYZE**: Update query optimizer statistics
- **REINDEX**: Rebuild all indexes
- **Integrity Check**: Verify database integrity

### 3. Statistics Display
- Database size and page information
- Table count and row statistics
- Index information
- Per-table details (rows, columns)

### 4. Data Export
- **Table Export**: Export individual tables to CSV or JSON
- **Full Database Export**: Export entire database to JSON or SQL
- Multiple format support

## API Endpoints

### Backup Endpoints

```
POST   /api/v1/database/backup          - Create backup
GET    /api/v1/database/backups         - List backups
POST   /api/v1/database/restore         - Restore backup
DELETE /api/v1/database/backup          - Delete backup
```

### Optimization Endpoints

```
POST   /api/v1/database/optimize        - Optimize database
GET    /api/v1/database/integrity       - Check integrity
```

### Statistics Endpoints

```
GET    /api/v1/database/statistics      - Get database statistics
GET    /api/v1/database/health          - Get health status
```

### Export Endpoints

```
POST   /api/v1/database/export/table    - Export table
POST   /api/v1/database/export/full     - Export full database
```

## Usage Examples

### Backend (Python)

```python
from services.database_management_service import DatabaseManagementService

# Initialize service
db_service = DatabaseManagementService('sqlite:///database.db')

# Create backup
result = db_service.create_backup(
    description="Before major update",
    compress=True
)

# Optimize database
result = db_service.optimize_database()

# Get statistics
stats = db_service.get_statistics()
print(f"Database size: {stats['database']['size_mb']} MB")
print(f"Total rows: {stats['tables']['total_rows']}")

# Export table
result = db_service.export_table_to_csv('users')
```

### Frontend (React)

```typescript
import api from './services/api';

// Create backup
const createBackup = async () => {
  const response = await api.post('/api/v1/database/backup', {
    description: 'Manual backup',
    compress: true
  });
  console.log('Backup created:', response.data.backup_path);
};

// Get statistics
const getStats = async () => {
  const response = await api.get('/api/v1/database/statistics');
  console.log('Database size:', response.data.database.size_mb, 'MB');
};

// Optimize database
const optimize = async () => {
  const response = await api.post('/api/v1/database/optimize');
  console.log('Space saved:', response.data.space_saved_mb, 'MB');
};

// Export table
const exportTable = async () => {
  const response = await api.post('/api/v1/database/export/table', {
    table_name: 'users',
    format: 'csv'
  });
  console.log('Exported:', response.data.rows_exported, 'rows');
};
```

## Component Usage

```tsx
import { DatabaseManagement } from './components/admin/DatabaseManagement';

function AdminPanel() {
  return (
    <div>
      <h1>Database Management</h1>
      <DatabaseManagement />
    </div>
  );
}
```

## Best Practices

### Backup Strategy
1. **Regular Backups**: Create backups before major operations
2. **Compression**: Always use compression for storage efficiency
3. **Retention**: Keep multiple backup versions
4. **Testing**: Regularly test backup restoration

### Optimization
1. **Schedule**: Run optimization during low-traffic periods
2. **Frequency**: Optimize weekly or after bulk operations
3. **Monitoring**: Check space savings and performance improvements

### Export
1. **Format Selection**: Use JSON for full data, CSV for tables
2. **Large Tables**: Export large tables individually
3. **Scheduling**: Schedule exports during off-peak hours

## Security Considerations

1. **Authentication**: All endpoints require authentication
2. **Authorization**: Restrict to admin users only
3. **Backup Storage**: Store backups in secure location
4. **Export Data**: Handle exported data securely

## Troubleshooting

### Backup Issues
- **Problem**: Backup creation fails
- **Solution**: Check disk space and file permissions

### Optimization Issues
- **Problem**: Optimization takes too long
- **Solution**: Run during maintenance window, consider database size

### Export Issues
- **Problem**: Export fails for large tables
- **Solution**: Export in smaller batches or use streaming

## File Locations

### Backend
- Service: `backend/services/database_management_service.py`
- API: `backend/api/v1/database.py`
- Dependencies: `backend/core/dependencies.py`

### Frontend
- Component: `frontend/src/components/admin/DatabaseManagement.tsx`
- Styles: `frontend/src/components/admin/DatabaseManagement.css`

### Storage
- Backups: `backups/database/`
- Exports: `exports/database/`

## Configuration

### Environment Variables
```env
DATABASE_URL=sqlite:///database.db
BACKUP_DIR=backups/database
EXPORT_DIR=exports/database
```

### Service Configuration
```python
# Customize backup directory
db_service = DatabaseManagementService(
    database_url='sqlite:///database.db'
)
db_service.backup_dir = Path('custom/backup/path')
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/api/v1/database/health
```

### Statistics
```bash
curl http://localhost:8000/api/v1/database/statistics
```

## Requirements Validation

This implementation satisfies:
- ✅ **Requirement 5.1**: Database migration and compatibility
- ✅ **Requirement 5.5**: Data backup and restore functionality
- ✅ Database backup interface
- ✅ Database restore functionality
- ✅ Database optimization tools
- ✅ Data export functionality
- ✅ Database statistics display

## Next Steps

1. Integrate with Admin Panel navigation
2. Add scheduled backup functionality
3. Implement backup retention policies
4. Add email notifications for backup operations
5. Create backup verification tools
