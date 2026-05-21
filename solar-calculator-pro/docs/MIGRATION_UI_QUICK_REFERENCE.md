# Migration UI - Quick Reference Guide

## Overview
The Migration UI provides a wizard-based interface for migrating data from Streamlit to the Electron application.

## Quick Start

### 1. Access Migration
```typescript
// Navigate to migration page
<Route path="/migration" element={<Migration />} />
```

### 2. Start Migration
```typescript
import { useMigration } from '../hooks/useMigration';

const { startMigration, migrationState } = useMigration();

// Start migration
await startMigration({
  sourcePath: '/path/to/streamlit/data',
  targetPath: '/path/to/electron/data',
  backupEnabled: true,
  validateAfterMigration: true
});
```

### 3. Monitor Progress
```typescript
// Migration state updates automatically
console.log(migrationState.progress); // 0-100
console.log(migrationState.currentStep); // Current step name
console.log(migrationState.status); // idle, running, completed, failed
```

## Components

### MigrationWizard
Main wizard component with 5 steps.

```typescript
import { MigrationWizard } from './components/migration/MigrationWizard';

<MigrationWizard />
```

### MigrationProgress
Real-time progress display.

```typescript
import { MigrationProgress } from './components/migration/MigrationProgress';

<MigrationProgress
  progress={75}
  currentStep="Datenbankmigration"
  details={stepDetails}
/>
```

### MigrationErrorReport
Error display and management.

```typescript
import { MigrationErrorReport } from './components/migration/MigrationErrorReport';

<MigrationErrorReport errors={migrationErrors} />
```

### MigrationReport
Comprehensive migration report.

```typescript
import { MigrationReport } from './components/migration/MigrationReport';

<MigrationReport report={reportData} />
```

## API Endpoints

### Start Migration
```bash
POST /api/v1/migration/start
Content-Type: application/json

{
  "source_path": "/path/to/source",
  "target_path": "/path/to/target",
  "backup_enabled": true,
  "validate_after_migration": true
}
```

### Get Status
```bash
GET /api/v1/migration/status

Response:
{
  "status": "running",
  "progress": 45,
  "current_step": "Datenbankmigration",
  "details": [...],
  "errors": [...]
}
```

### Get Report
```bash
GET /api/v1/migration/report

Response:
{
  "started_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T10:15:00",
  "success": true,
  "steps": [...],
  ...
}
```

### Rollback
```bash
POST /api/v1/migration/rollback

Response:
{
  "success": true,
  "message": "Migration rolled back successfully"
}
```

## Migration Steps

### Step 1: Vorbereitung (Preparation)
- Review checklist
- Ensure prerequisites
- Estimate duration

### Step 2: Backup
- Automatic backup creation
- Backup location displayed
- Backup verification

### Step 3: Migration
- Database migration
- Settings migration
- Project data migration
- User data migration
- File migration

### Step 4: Validierung (Validation)
- Database integrity check
- File count verification
- Data integrity verification
- Referential integrity check

### Step 5: Abschluss (Completion)
- Success confirmation
- Report generation
- Next steps guidance

## Error Handling

### Error Severity Levels
- **Error**: Critical issues requiring attention
- **Warning**: Non-critical issues
- **Info**: Informational messages

### Error Actions
```typescript
// View error details
<Button onClick={() => viewErrorDetails(error)} />

// Export errors
<Button onClick={() => exportErrors()} />

// Rollback on error
<Button onClick={() => rollbackMigration()} />
```

## Rollback Process

### Automatic Rollback
Triggered on critical failures:
1. Migration stops
2. Target directory removed
3. Backup restored
4. State reset

### Manual Rollback
User-initiated:
1. Click "Rollback durchführen"
2. Confirm in dialog
3. Wait for completion
4. Review rollback report

## Report Features

### Statistics
- Databases migrated
- Tables migrated
- Records migrated
- Settings migrated
- Projects migrated
- Users migrated

### Tabs
- **Übersicht**: Statistics and charts
- **Schritte**: Step results
- **Validierung**: Validation checks
- **Pfade**: File paths
- **Fehler**: Error list
- **Rollback**: Rollback info

### Export
```typescript
// Export as JSON
exportReport(); // Downloads migration-report-{timestamp}.json

// Export as PDF (planned)
exportPDF(); // Downloads migration-report-{timestamp}.pdf
```

## Hook Usage

### useMigration Hook
```typescript
const {
  migrationState,      // Current state
  startMigration,      // Start function
  rollbackMigration,   // Rollback function
  validateMigration,   // Validate function
  getMigrationReport,  // Get report function
  checkMigrationAvailable, // Check availability
  isLoading,          // Loading state
  error               // Error message
} = useMigration();
```

### State Structure
```typescript
interface MigrationState {
  status: 'idle' | 'running' | 'completed' | 'failed';
  progress: number; // 0-100
  currentStep: string;
  details: StepDetail[];
  errors: MigrationError[];
}
```

## Styling

### CSS Variables
```css
--primary-color: Primary theme color
--surface-card: Card background
--surface-ground: Ground background
--text-color: Primary text
--text-color-secondary: Secondary text
--green-500: Success color
--red-500: Error color
--orange-500: Warning color
--blue-500: Info color
```

### Responsive Breakpoints
- Desktop: > 768px
- Mobile: ≤ 768px

## Best Practices

### 1. Pre-Migration
- Close Streamlit application
- Ensure sufficient disk space
- Verify administrator rights
- Review checklist

### 2. During Migration
- Don't close application
- Don't modify data
- Monitor progress
- Note any errors

### 3. Post-Migration
- Review report
- Verify data
- Test functionality
- Keep backup

### 4. Error Recovery
- Review error details
- Export error log
- Attempt rollback if needed
- Contact support with error details

## Troubleshooting

### Migration Won't Start
- Check source path exists
- Verify target path writable
- Ensure no other migration running
- Check disk space

### Migration Stuck
- Check backend logs
- Verify database connections
- Check file permissions
- Review error report

### Validation Fails
- Review validation checks
- Check data integrity
- Verify file counts
- Consider rollback

### Rollback Fails
- Check backup exists
- Verify permissions
- Review error logs
- Manual restore may be needed

## Performance Tips

- Close unnecessary applications
- Ensure stable network (if applicable)
- Use SSD for better performance
- Allocate sufficient RAM

## Security Notes

- Backup is encrypted
- API requires authentication
- Sensitive data not logged
- Secure file path handling

## Support

### Error Reporting
1. Export error log (JSON)
2. Include migration report
3. Note system information
4. Contact support

### Documentation
- User manual: `/docs/USER_MANUAL.md`
- API docs: `/docs/API_DOCUMENTATION.md`
- Developer guide: `/docs/DEVELOPER_GUIDE.md`

## Version History

- **v1.0.0**: Initial release
  - 5-step wizard
  - Real-time progress
  - Error reporting
  - Rollback functionality
  - Comprehensive reports

## Related Documentation

- [Migration Manager](../backend/migrations/README.md)
- [Task 64 Complete](../TASK_64_COMPLETE.md)
- [Setup Guide](./SETUP_GUIDE.md)
