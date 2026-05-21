# User Management - Quick Reference Guide

## Quick Start

### For Administrators

**Access User Management:**
1. Navigate to Admin Panel
2. Click "User Management" tab

**Create a User:**
```
Admin Panel → User Management → Create User Button
Fill form → Select role → Click Create
```

**Edit a User:**
```
Find user in list → Click pencil icon → Modify → Click Update
```

**View Activity Logs:**
```
User Management → Activity Logs tab → Use filters
```

### For Developers

**Import Components:**
```typescript
import UserList from '../components/admin/UserList';
import UserForm from '../components/admin/UserForm';
import UserActivityLog from '../components/admin/UserActivityLog';
import UserSettings from '../components/admin/UserSettings';
```

**API Calls:**
```typescript
// Create user
await api.post('/api/v1/users/', userData);

// Get users
await api.get('/api/v1/users/', { params: { skip: 0, limit: 10 } });

// Update user
await api.put(`/api/v1/users/${userId}`, updateData);

// Delete user
await api.delete(`/api/v1/users/${userId}`);

// Get activity logs
await api.get('/api/v1/users/activity/logs');

// Update settings
await api.put('/api/v1/users/me/settings', settings);
```

## User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **super_admin** | Full system access | All operations, cannot be deleted |
| **admin** | Administrative access | User management, system settings |
| **manager** | Management access | Project management, reports |
| **user** | Standard user | Create/edit own projects |
| **viewer** | Read-only access | View projects and data |

## User Statuses

| Status | Description |
|--------|-------------|
| **active** | User can log in and use system |
| **inactive** | User account disabled |
| **suspended** | Temporarily blocked |
| **pending** | Awaiting activation |

## API Endpoints

### User Management
```
POST   /api/v1/users/                    Create user (admin)
GET    /api/v1/users/                    List users (admin)
GET    /api/v1/users/me                  Get current user
GET    /api/v1/users/{id}                Get user (admin)
PUT    /api/v1/users/{id}                Update user (admin)
DELETE /api/v1/users/{id}                Delete user (admin)
POST   /api/v1/users/me/change-password  Change password
```

### Activity Logs
```
GET    /api/v1/users/activity/logs       Get activity logs (admin)
```

### Settings
```
GET    /api/v1/users/me/settings         Get settings
PUT    /api/v1/users/me/settings         Update settings
```

### Roles
```
POST   /api/v1/users/roles               Create role (admin)
GET    /api/v1/users/roles               List roles (admin)
PUT    /api/v1/users/roles/{id}          Update role (admin)
DELETE /api/v1/users/roles/{id}          Delete role (admin)
```

## Common Tasks

### Create User Programmatically
```python
from backend.services.user_service import UserService
from backend.models.user_schemas import UserCreate

service = UserService(db)
user_data = UserCreate(
    username="john.doe",
    email="john@example.com",
    password="SecurePass123",
    first_name="John",
    last_name="Doe",
    role="user",
    status="active"
)
user = service.create_user(user_data)
```

### Log User Activity
```python
service.log_activity(
    user_id=current_user.id,
    action="create_project",
    resource="project",
    resource_id=project.id,
    details={"name": project.name},
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)
```

### Check User Permissions
```python
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

## Validation Rules

### Username
- 3-50 characters
- Alphanumeric with _ or - allowed
- Unique across system

### Email
- Valid email format
- Unique across system

### Password
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Activity Log Actions

Common actions tracked:
- `create_user` - User created
- `update_user` - User updated
- `delete_user` - User deleted
- `change_password` - Password changed
- `update_settings` - Settings updated
- `login` - User logged in
- `logout` - User logged out

## Settings Options

### Theme
- `light` - Light theme
- `dark` - Dark theme
- `auto` - System preference

### Language
- `de` - Deutsch
- `en` - English

### Date Format
- `DD.MM.YYYY` - German format
- `MM/DD/YYYY` - US format
- `YYYY-MM-DD` - ISO format

### Number Format
- `de-DE` - German (1.234,56)
- `en-US` - English (1,234.56)

## Troubleshooting

### User Creation Fails
- Check username is unique
- Check email is unique
- Verify password meets requirements
- Ensure all required fields provided

### Cannot Delete User
- Super admin users cannot be deleted
- Check user has no dependent records
- Verify admin permissions

### Activity Logs Not Showing
- Check user has admin role
- Verify filters are not too restrictive
- Check date range

### Settings Not Saving
- Verify user is authenticated
- Check network connection
- Verify valid setting values

## Security Notes

- Passwords are hashed with bcrypt
- JWT tokens required for all operations
- Admin operations require admin role
- All actions are logged
- IP addresses are tracked
- User agents are recorded

## Component Props

### UserList
```typescript
interface UserListProps {
  onEdit: (user: User) => void;
  onView: (user: User) => void;
  refreshTrigger?: number;
}
```

### UserForm
```typescript
interface UserFormProps {
  visible: boolean;
  user: User | null;
  onHide: () => void;
  onSuccess: () => void;
}
```

### UserActivityLog
```typescript
interface UserActivityLogProps {
  userId?: number;  // Optional: filter by specific user
}
```

## Database Queries

### Get Active Users
```python
users = db.query(User).filter(User.status == UserStatus.ACTIVE).all()
```

### Get Users by Role
```python
admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
```

### Get Recent Activity
```python
logs = db.query(UserActivityLog)\
    .order_by(desc(UserActivityLog.timestamp))\
    .limit(100)\
    .all()
```

## Best Practices

1. **Always validate input** - Use Pydantic schemas
2. **Log important actions** - Use activity logging
3. **Check permissions** - Use role-based access control
4. **Handle errors gracefully** - Provide user-friendly messages
5. **Use transactions** - For multi-step operations
6. **Test thoroughly** - Unit and integration tests
7. **Document changes** - Update activity logs

## Support

For issues or questions:
1. Check this quick reference
2. Review TASK_52_USER_MANAGEMENT_COMPLETE.md
3. Check API documentation
4. Review component source code
5. Contact development team

---

**Last Updated:** 2024
**Version:** 1.0.0
**Status:** Production Ready
