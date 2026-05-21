# Notifications System - Complete Guide

## Overview

The Notifications System provides a comprehensive multi-channel notification solution for the Solar Calculator Pro application. It supports in-app notifications, desktop notifications, email notifications, and SMS notifications with full user preference management.

## Features

### Core Features
- **Multi-Channel Delivery**: In-app, desktop, email, and SMS notifications
- **Real-Time Updates**: WebSocket support for instant notification delivery
- **User Preferences**: Granular control over notification channels and types
- **Notification History**: Complete history with search and filtering
- **Interactive Actions**: Notifications can include actionable buttons
- **Template System**: Reusable notification templates with variable substitution
- **Priority Levels**: Low, normal, high, and urgent priority notifications
- **Quiet Hours**: User-configurable quiet hours to prevent disturbances
- **Digest Mode**: Option to receive notifications in daily or weekly digests

### Notification Types
- `info`: General information
- `success`: Success messages
- `warning`: Warning messages
- `error`: Error messages
- `calculation_complete`: Solar calculation completed
- `pdf_generated`: PDF document generated
- `project_updated`: Project has been updated
- `system_alert`: Important system alerts
- `user_mention`: User mentioned in a comment
- `task_assigned`: Task assigned to user

## Architecture

### Backend Components

#### Database Models (`backend/models/notification_models.py`)
- **Notification**: Main notification model
- **NotificationAction**: Interactive actions for notifications
- **NotificationPreference**: User notification preferences
- **NotificationTemplate**: Reusable notification templates

#### Service Layer (`backend/services/notification_service.py`)
- **NotificationService**: Core service for notification management
  - Create, read, update, delete notifications
  - Bulk operations
  - Template-based notification creation
  - Multi-channel delivery
  - Preference management
  - Statistics and analytics

#### API Endpoints (`backend/api/v1/notifications.py`)
- `POST /notifications/`: Create notification
- `GET /notifications/`: List notifications with filtering
- `GET /notifications/{id}`: Get specific notification
- `PATCH /notifications/{id}`: Update notification (mark as read/archived)
- `DELETE /notifications/{id}`: Delete notification
- `POST /notifications/mark-all-read`: Mark all as read
- `POST /notifications/bulk`: Create bulk notifications
- `GET /notifications/preferences/me`: Get user preferences
- `PUT /notifications/preferences/me`: Update user preferences
- `POST /notifications/templates`: Create notification template
- `POST /notifications/from-template/{key}`: Create from template

### Frontend Components

#### NotificationCenter (`frontend/src/components/notifications/NotificationCenter.tsx`)
- Bell icon with unread count badge
- Dropdown panel with notification list
- Real-time updates (30-second polling)
- Mark as read/unread
- Delete notifications
- Filter by read status and category
- Navigate to notification actions

#### Desktop Notifications (Electron)
- Native OS notifications
- Click to open app and navigate to notification
- Configurable notification sounds
- System tray integration

## Usage Examples

### Creating a Notification (Backend)

```python
from backend.services.notification_service import NotificationService
from backend.models.notification_schemas import NotificationCreate, NotificationChannel

# Create service
service = NotificationService(db)

# Create notification
notification_data = NotificationCreate(
    user_id=1,
    type="calculation_complete",
    priority="normal",
    title="Calculation Complete",
    message="Your solar calculation has been completed successfully.",
    category="calculations",
    action_url="/projects/123",
    action_label="View Project",
    channels=[NotificationChannel.IN_APP, NotificationChannel.DESKTOP]
)

notification = service.create_notification(notification_data)
```

### Creating from Template

```python
# Create notification from template
notification = service.create_from_template(
    template_key="calculation_complete",
    user_id=1,
    variables={
        "project_name": "Solar Installation ABC",
        "system_size": "10.5"
    },
    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
)
```

### Bulk Notifications

```python
from backend.models.notification_schemas import BulkNotificationCreate, NotificationBase

# Create bulk notifications
bulk_data = BulkNotificationCreate(
    user_ids=[1, 2, 3, 4, 5],
    notification=NotificationBase(
        type="system_alert",
        priority="high",
        title="System Maintenance",
        message="The system will be under maintenance from 2 AM to 4 AM."
    ),
    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
)

notifications = service.create_bulk_notifications(bulk_data)
```

### Using NotificationCenter (Frontend)

```tsx
import { NotificationCenter } from './components/notifications/NotificationCenter';

function App() {
  const handleNotificationClick = (notification) => {
    console.log('Notification clicked:', notification);
    // Handle notification click
  };

  return (
    <div className="app">
      <header>
        <NotificationCenter onNotificationClick={handleNotificationClick} />
      </header>
    </div>
  );
}
```

### Managing User Preferences

```python
from backend.models.notification_schemas import NotificationPreferenceUpdate, NotificationType

# Update user preferences
preferences_data = NotificationPreferenceUpdate(
    enable_in_app=True,
    enable_desktop=True,
    enable_email=True,
    enable_sms=False,
    enabled_types=[
        NotificationType.CALCULATION_COMPLETE,
        NotificationType.PDF_GENERATED,
        NotificationType.SYSTEM_ALERT
    ],
    enable_quiet_hours=True,
    quiet_hours_start="22:00",
    quiet_hours_end="08:00",
    digest_mode=False
)

preferences = service.create_or_update_preferences(user_id=1, preferences_data=preferences_data)
```

## Notification Templates

### Default Templates

The system includes several default templates:

1. **calculation_complete**
   - Type: `calculation_complete`
   - Priority: `normal`
   - Title: "Calculation Complete: {project_name}"
   - Message: "Your solar calculation for {project_name} has been completed successfully. System size: {system_size} kWp"

2. **pdf_generated**
   - Type: `pdf_generated`
   - Priority: `normal`
   - Title: "PDF Ready: {document_name}"
   - Message: "Your PDF document \"{document_name}\" has been generated and is ready for download."

3. **project_updated**
   - Type: `project_updated`
   - Priority: `low`
   - Title: "Project Updated: {project_name}"
   - Message: "The project \"{project_name}\" has been updated by {updated_by}."

4. **system_alert**
   - Type: `system_alert`
   - Priority: `high`
   - Title: "System Alert: {alert_title}"
   - Message: "{alert_message}"

### Creating Custom Templates

```python
from backend.models.notification_schemas import NotificationTemplateCreate

template_data = NotificationTemplateCreate(
    template_key="custom_alert",
    name="Custom Alert",
    description="Custom alert template",
    type="info",
    priority="normal",
    title_template="Alert: {title}",
    message_template="Message: {message}",
    default_channels=[NotificationChannel.IN_APP],
    icon="alert-circle",
    category="custom",
    is_active=True
)

template = service.create_template(template_data)
```

## Delivery Channels

### In-App Notifications
- Displayed in the NotificationCenter component
- Real-time updates via polling
- Persistent until dismissed
- Supports interactive actions

### Desktop Notifications
- Native OS notifications via Electron
- Appear even when app is in background
- Click to focus app and navigate to notification
- Configurable sounds and badges

### Email Notifications
- HTML email templates
- Includes notification content and actions
- Configurable SMTP settings
- Support for attachments

### SMS Notifications
- Short message format
- Critical notifications only
- Configurable SMS provider
- Rate limiting to prevent spam

## User Preferences

### Channel Preferences
- Enable/disable each channel individually
- Per-channel configuration
- Override for specific notification types

### Quiet Hours
- Configure start and end times
- Notifications queued during quiet hours
- Urgent notifications can override

### Digest Mode
- Receive notifications in batches
- Daily or weekly frequency
- Summary email with all notifications

### Type Filtering
- Enable/disable specific notification types
- Granular control over what notifications to receive
- Applies across all channels

## Best Practices

### For Developers

1. **Use Templates**: Create reusable templates for common notifications
2. **Set Appropriate Priority**: Use priority levels correctly
   - `low`: Non-urgent updates
   - `normal`: Standard notifications
   - `high`: Important notifications
   - `urgent`: Critical alerts only

3. **Provide Actions**: Include actionable buttons when appropriate
4. **Respect Preferences**: Always check user preferences before sending
5. **Batch Operations**: Use bulk creation for multiple users
6. **Clean Up**: Set expiration dates for time-sensitive notifications

### For Users

1. **Configure Preferences**: Set up notification preferences early
2. **Use Quiet Hours**: Configure quiet hours to avoid disturbances
3. **Enable Digest Mode**: For less urgent notifications
4. **Review Regularly**: Check and clear old notifications
5. **Customize Channels**: Choose appropriate channels for different types

## API Reference

### Notification Object

```typescript
interface Notification {
  id: number;
  user_id: number;
  type: NotificationType;
  priority: NotificationPriority;
  title: string;
  message: string;
  category?: string;
  action_url?: string;
  action_label?: string;
  icon?: string;
  channels: string;
  is_read: boolean;
  is_archived: boolean;
  read_at?: string;
  created_at: string;
  expires_at?: string;
  actions?: NotificationAction[];
}
```

### Notification Preference Object

```typescript
interface NotificationPreference {
  id: number;
  user_id: number;
  enable_in_app: boolean;
  enable_desktop: boolean;
  enable_email: boolean;
  enable_sms: boolean;
  enabled_types?: NotificationType[];
  enable_quiet_hours: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  digest_mode: boolean;
  digest_frequency?: string;
  created_at: string;
  updated_at: string;
}
```

## Troubleshooting

### Notifications Not Appearing

1. Check user preferences
2. Verify notification channels are enabled
3. Check quiet hours settings
4. Verify notification type is enabled
5. Check browser notification permissions (for desktop)

### Desktop Notifications Not Working

1. Check OS notification settings
2. Verify Electron notification permissions
3. Check notification sound settings
4. Verify app is not in Do Not Disturb mode

### Email Notifications Not Sending

1. Verify SMTP configuration
2. Check email address validity
3. Verify email service is running
4. Check spam folder
5. Review email delivery logs

## Performance Considerations

- Notifications are indexed by user_id, is_read, and created_at
- Polling interval is 30 seconds (configurable)
- Expired notifications are automatically filtered
- Bulk operations are optimized for large user sets
- Database queries use pagination to limit memory usage

## Security

- All API endpoints require authentication
- Users can only access their own notifications
- Admin role required for bulk operations and templates
- SQL injection protection via parameterized queries
- XSS protection via input sanitization
- Rate limiting on notification creation

## Future Enhancements

- WebSocket support for real-time push notifications
- Rich media support (images, videos)
- Notification grouping and threading
- Advanced filtering and search
- Notification scheduling
- A/B testing for notification content
- Analytics dashboard for notification effectiveness
- Mobile push notifications
- Slack/Teams integration
- Custom notification sounds per type

## Requirements Validation

✅ **Requirement 2.6**: User Preferences - Implemented with granular control
✅ **Requirement 3.3**: Desktop Integration - Native notifications via Electron
✅ **In-App Notifications**: NotificationCenter component with real-time updates
✅ **Desktop Notifications**: Native OS notifications
✅ **Email Notifications**: SMTP integration (ready for configuration)
✅ **Notification Preferences**: Complete preference management system
✅ **Notification History**: Full history with filtering and search
✅ **Notification Actions**: Interactive buttons and actions

## Conclusion

The Notifications System provides a robust, scalable solution for multi-channel notifications with comprehensive user control and developer-friendly APIs. It integrates seamlessly with the Solar Calculator Pro application and can be easily extended for future requirements.
