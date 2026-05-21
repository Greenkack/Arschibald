# Database Management Integration Guide

## Quick Integration Steps

### Step 1: Import the Component

Add the Database Management component to your Admin Panel:

```typescript
// frontend/src/pages/Admin.tsx

import { DatabaseManagement } from '../components/admin/DatabaseManagement';

export const Admin: React.FC = () => {
  return (
    <div className="admin-panel">
      <TabView>
        {/* Existing tabs */}
        <TabPanel header="User Management">
          <UserManagement />
        </TabPanel>
        
        <TabPanel header="System Settings">
          <SystemSettings />
        </TabPanel>
        
        {/* NEW: Database Management Tab */}
        <TabPanel header="Database Management">
          <DatabaseManagement />
        </TabPanel>
      </TabView>
    </div>
  );
};
```

### Step 2: Verify Backend Integration

The backend is already integrated in `main.py`. Verify it's working:

```bash
# Start the backend
cd solar-calculator-pro/backend
python main.py

# Test the health endpoint
curl http://localhost:8000/api/v1/database/health
```

Expected response:
```json
{
  "success": true,
  "healthy": true,
  "size_mb": 45.2,
  "table_count": 12,
  "total_rows": 15234,
  "checked_at": "2024-11-19T10:30:00"
}
```

### Step 3: Create Required Directories

The service will create these automatically, but you can pre-create them:

```bash
mkdir -p backups/database
mkdir -p exports/database
```

### Step 4: Test the Integration

1. **Start the application**
   ```bash
   npm run electron:dev
   ```

2. **Navigate to Admin Panel**
   - Click on "Admin" in the sidebar
   - Click on "Database Management" tab

3. **Test Basic Operations**
   - View statistics
   - Create a backup
   - Check integrity
   - Export a table

## Advanced Integration

### Add to Navigation Menu

```typescript
// frontend/src/components/layout/Sidebar.tsx

const menuItems = [
  // ... existing items
  {
    label: 'Admin',
    icon: 'pi pi-cog',
    items: [
      {
        label: 'User Management',
        icon: 'pi pi-users',
        to: '/admin/users'
      },
      {
        label: 'System Settings',
        icon: 'pi pi-sliders-h',
        to: '/admin/settings'
      },
      {
        label: 'Database Management',  // NEW
        icon: 'pi pi-database',
        to: '/admin/database'
      }
    ]
  }
];
```

### Add Route

```typescript
// frontend/src/routes/index.tsx

import { DatabaseManagement } from '../components/admin/DatabaseManagement';

const routes = [
  // ... existing routes
  {
    path: '/admin/database',
    element: <DatabaseManagement />
  }
];
```

### Add to Dashboard Widget

```typescript
// frontend/src/pages/Dashboard.tsx

<Card title="Database Health">
  <div className="database-health">
    <div className="health-metric">
      <span>Size:</span>
      <strong>{dbHealth.size_mb} MB</strong>
    </div>
    <div className="health-metric">
      <span>Status:</span>
      <strong className={dbHealth.healthy ? 'text-green' : 'text-red'}>
        {dbHealth.healthy ? 'Healthy' : 'Issues Detected'}
      </strong>
    </div>
    <Button
      label="Manage Database"
      icon="pi pi-database"
      onClick={() => navigate('/admin/database')}
      className="p-button-sm"
    />
  </div>
</Card>
```

## Configuration

### Environment Variables

Add to `.env`:

```env
# Database Configuration
DATABASE_URL=sqlite:///database.db
BACKUP_DIR=backups/database
EXPORT_DIR=exports/database
MAX_BACKUP_AGE_DAYS=30
AUTO_BACKUP_ENABLED=true
AUTO_BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
```

### Backend Configuration

```python
# backend/config.py

class Settings(BaseSettings):
    # ... existing settings
    
    # Database Management
    DATABASE_URL: str = "sqlite:///database.db"
    BACKUP_DIR: str = "backups/database"
    EXPORT_DIR: str = "exports/database"
    MAX_BACKUP_AGE_DAYS: int = 30
    AUTO_BACKUP_ENABLED: bool = True
    AUTO_BACKUP_SCHEDULE: str = "0 2 * * *"
```

## Scheduled Backups (Optional)

### Add Scheduler

```python
# backend/services/backup_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from .database_management_service import DatabaseManagementService

class BackupScheduler:
    def __init__(self, db_service: DatabaseManagementService):
        self.db_service = db_service
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        # Schedule daily backup at 2 AM
        self.scheduler.add_job(
            self.create_scheduled_backup,
            'cron',
            hour=2,
            minute=0
        )
        self.scheduler.start()
    
    def create_scheduled_backup(self):
        self.db_service.create_backup(
            description="Scheduled backup",
            compress=True
        )
```

### Initialize in Main

```python
# backend/main.py

from services.backup_scheduler import BackupScheduler

@app.on_event("startup")
async def startup_event():
    if settings.AUTO_BACKUP_ENABLED:
        scheduler = BackupScheduler(db_service)
        scheduler.start()
```

## Monitoring Integration

### Add Health Check to Dashboard

```typescript
// frontend/src/hooks/useDatabaseHealth.ts

export const useDatabaseHealth = () => {
  const [health, setHealth] = useState(null);
  
  useEffect(() => {
    const checkHealth = async () => {
      const response = await api.get('/api/v1/database/health');
      setHealth(response.data);
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 60000); // Every minute
    
    return () => clearInterval(interval);
  }, []);
  
  return health;
};
```

### Use in Dashboard

```typescript
// frontend/src/pages/Dashboard.tsx

const Dashboard = () => {
  const dbHealth = useDatabaseHealth();
  
  return (
    <div className="dashboard">
      {dbHealth && !dbHealth.healthy && (
        <Message
          severity="warn"
          text="Database integrity issues detected. Please check Database Management."
        />
      )}
      {/* ... rest of dashboard */}
    </div>
  );
};
```

## Notifications

### Email Notifications (Optional)

```python
# backend/services/notification_service.py

class NotificationService:
    async def send_backup_notification(self, backup_info):
        # Send email notification
        await send_email(
            to=admin_email,
            subject="Database Backup Created",
            body=f"Backup created: {backup_info['filename']}"
        )
```

### Toast Notifications

Already implemented in the component. Customize as needed:

```typescript
toast.current?.show({
  severity: 'success',
  summary: 'Backup Created',
  detail: 'Database backup created successfully',
  life: 3000
});
```

## Security Considerations

### Role-Based Access

```typescript
// frontend/src/components/admin/DatabaseManagement.tsx

const DatabaseManagement = () => {
  const { user } = useAuth();
  
  if (!user.roles.includes('admin')) {
    return <Message severity="error" text="Access denied" />;
  }
  
  // ... rest of component
};
```

### Backend Authorization

```python
# backend/api/v1/database.py

from ...core.auth_dependencies import require_admin

@router.post("/backup")
async def create_backup(
    request: BackupCreateRequest,
    current_user: dict = Depends(require_admin)  # Admin only
):
    # ... implementation
```

## Troubleshooting

### Issue: Backup Creation Fails

**Solution:**
```bash
# Check disk space
df -h

# Check permissions
chmod 755 backups/database

# Check logs
tail -f logs/app.log
```

### Issue: Restore Fails

**Solution:**
```python
# Verify backup file
import gzip
with gzip.open('backup.db.gz', 'rb') as f:
    # Should not raise error
    data = f.read()
```

### Issue: Export Takes Too Long

**Solution:**
```python
# Export in batches
for table in tables:
    db_service.export_table_to_csv(table)
```

## Testing

### Backend Tests

```python
# tests/test_database_management.py

def test_create_backup(db_service):
    result = db_service.create_backup("Test backup", True)
    assert result['success'] == True
    assert 'backup_path' in result

def test_optimize_database(db_service):
    result = db_service.optimize_database()
    assert result['success'] == True
    assert result['space_saved_mb'] >= 0
```

### Frontend Tests

```typescript
// tests/DatabaseManagement.test.tsx

describe('DatabaseManagement', () => {
  it('should display statistics', async () => {
    render(<DatabaseManagement />);
    await waitFor(() => {
      expect(screen.getByText(/Database Size/i)).toBeInTheDocument();
    });
  });
  
  it('should create backup', async () => {
    render(<DatabaseManagement />);
    fireEvent.click(screen.getByText(/Create Backup/i));
    // ... test backup creation
  });
});
```

## Performance Tips

1. **Compress Backups**: Always use compression (saves ~70% space)
2. **Schedule Optimization**: Run during low-traffic periods
3. **Batch Exports**: Export large tables individually
4. **Monitor Size**: Set up alerts for database size
5. **Clean Old Backups**: Implement retention policy

## Best Practices

1. **Regular Backups**: Daily automated backups
2. **Test Restores**: Regularly test backup restoration
3. **Monitor Health**: Check integrity weekly
4. **Optimize Regularly**: Monthly optimization
5. **Document Changes**: Add descriptions to backups
6. **Secure Storage**: Store backups securely
7. **Retention Policy**: Keep 30 days of backups

## Support

For issues or questions:
1. Check logs: `logs/app.log`
2. Review documentation: `DATABASE_MANAGEMENT_QUICK_REFERENCE.md`
3. Test API directly: Use Swagger UI at `/docs`
4. Check file permissions: Ensure write access to backup/export dirs

## Next Steps

1. ✅ Integrate into Admin Panel
2. ✅ Test all operations
3. ⏳ Setup scheduled backups (optional)
4. ⏳ Configure email notifications (optional)
5. ⏳ Implement retention policy (optional)
6. ⏳ Add monitoring dashboard widget (optional)

## Conclusion

The Database Management system is now ready for use. Follow the integration steps above to add it to your admin panel. The system is production-ready and includes all necessary features for comprehensive database management.
