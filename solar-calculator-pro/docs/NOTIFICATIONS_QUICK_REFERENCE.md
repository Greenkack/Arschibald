# Notifications System - Quick Reference

## Quick Start

### Backend: Create a Notification

```python
from backend.services.notification_service import NotificationService
from backend.models.notification_schemas import NotificationCreate, NotificationChannel

service = NotificationService(db)
notification = service.create_notification(NotificationCreate(
    user_id=1,
    type="info",
    priority="normal",
    title="Hello!",
    message="This is a test notification",
    channels=[NotificationChannel.IN_APP, NotificationChannel.DESKTOP]
))
```

### Frontend: Display Notifications

```tsx
import { NotificationCenter } from './components/notifications/NotificationCenter';

<NotificationCenter onNotificationClick={(n) => console.log(n)} />
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/` | List notifications |
| POST | `/api/v1/notifications/` | Create notification |
| GET | `/api/v1/notifications/{id}` | Get notification |
| PATCH | `/api/v1/notifications/{id}` | Update notification |
| DELETE | `/api/v1/notifications/{id}` | Delete notification |
| POST | `/api/v1/notifications/mark-all-read` | Mark all as read |
| GET | `/api/v1/notifications/unread-count` | Get unread count |
| GET | `/api/v1/notifications/statistics` | Get statistics |
| POST | `/api/v1/notifications/bulk` | Create bulk notifications |
| GET | `/api/v1/notifications/preferences/me` | Get preferences |
| PUT | `/api/v1/notifications/preferences/me` | Update preferences |
| POST | `/api/v1/notifications/from-template/{key}` | Create from template |

## Notification Types

- `info` - General information
- `success` - Success messages
- `warning` - Warning messages
- `error` - Error messages
- `calculation_complete` - Calculation completed
- `pdf_generated` - PDF generated
- `project_updated` - Project updated
- `system_alert` - System alert
- `user_mention` - User mentioned
- `task_assigned` - Task assigned

## Priority Levels

- `low` - Non-urgent updates
- `normal` - Standard notifications
- `high` - Important notifications
- `urgent` - Critical alerts

## Delivery Channels

- `in_app` - In-app notification center
- `desktop` - Native OS notifications
- `email` - Email notifications
- `sms` - SMS notifications

## Common Operations

### Mark as Read

```python
service.update_notification(
    notification_id=1,
    user_id=1,
    update_data=NotificationUpdate(is_read=True)
)
```

### Create from Template

```python
service.create_from_template(
    template_key="calculation_complete",
    user_id=1,
    variables={"project_name": "ABC", "system_size": "10.5"}
)
```

### Bulk Create

```python
service.create_bulk_notifications(BulkNotificationCreate(
    user_ids=[1, 2, 3],
    notification=NotificationBase(
        type="info",
        title="Announcement",
        message="System maintenance tonight"
    ),
    channels=[NotificationChannel.IN_APP]
))
```

### Update Preferences

```python
service.create_or_update_preferences(
    user_id=1,
    preferences_data=NotificationPreferenceUpdate(
        enable_desktop=True,
        enable_quiet_hours=True,
        quiet_hours_start="22:00",
        quiet_hours_end="08:00"
    )
)
```

## Frontend Components

### NotificationCenter Props

```typescript
interface NotificationCenterProps {
  onNotificationClick?: (notification: Notification) => void;
}
```

### Notification Object

```typescript
interface Notification {
  id: number;
  type: string;
  priority: string;
  title: string;
  message: string;
  category?: string;
  action_url?: string;
  action_label?: string;
  icon?: string;
  is_read: boolean;
  created_at: string;
  actions?: NotificationAction[];
}
```

## Database Tables

- `notifications` - Main notification records
- `notification_actions` - Interactive actions
- `notification_preferences` - User preferences
- `notification_templates` - Reusable templates

## Configuration

### Environment Variables

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_FROM=noreply@solarcalculator.com

# SMS Configuration (optional)
SMS_PROVIDER=twilio
SMS_ACCOUNT_SID=your-account-sid
SMS_AUTH_TOKEN=your-auth-token
SMS_FROM_NUMBER=+1234567890
```

## Best Practices

1. ✅ Use templates for common notifications
2. ✅ Set appropriate priority levels
3. ✅ Provide action URLs when applicable
4. ✅ Respect user preferences
5. ✅ Set expiration dates for time-sensitive notifications
6. ✅ Use bulk operations for multiple users
7. ✅ Clean up old notifications regularly

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Notifications not appearing | Check user preferences and enabled channels |
| Desktop notifications not working | Verify OS permissions and Electron settings |
| Email not sending | Check SMTP configuration |
| High database load | Implement pagination and cleanup old notifications |

## Performance Tips

- Use pagination for large notification lists
- Implement cleanup job for old notifications
- Cache unread counts
- Use indexes on user_id, is_read, created_at
- Batch database operations when possible

## Security Checklist

- ✅ Authentication required for all endpoints
- ✅ Users can only access their own notifications
- ✅ Admin role required for bulk operations
- ✅ SQL injection protection
- ✅ XSS protection
- ✅ Rate limiting on creation

## Support

For detailed documentation, see: `NOTIFICATIONS_SYSTEM_GUIDE.md`

For API reference, see: `/api/v1/docs` (Swagger UI)

For issues, contact: support@solarcalculator.com
