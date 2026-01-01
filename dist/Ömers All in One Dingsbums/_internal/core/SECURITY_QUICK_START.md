# Security System - Quick Start Guide

Get started with the Security & Access Control System in 5 minutes.

## Installation

```bash
# Install dependencies
pip install bcrypt pyotp

# Initialize database tables
python -c "from core.security import init_all_security_tables, create_default_roles_and_permissions; init_all_security_tables(); create_default_roles_and_permissions()"
```

## 1. User Authentication (2 minutes)

```python
from core.security import AuthenticationManager

# Initialize
auth_manager = AuthenticationManager()

# Register a user
user = auth_manager.register_user(
    email="user@example.com",
    password="SecurePass123!",
    full_name="John Doe"
)

# Login
result = auth_manager.authenticate(
    email="user@example.com",
    password="SecurePass123!",
    ip_address="192.168.1.100"
)

if result.status.value == "success":
    print(f"✓ Logged in! Token: {result.session_token[:20]}...")
    
    # Validate session
    user = auth_manager.session_manager.validate_session(result.session_token)
    print(f"✓ Session valid for: {user.email}")
    
    # Logout
    auth_manager.logout(result.session_token)
    print("✓ Logged out")
```

## 2. Role-Based Access Control (2 minutes)

```python
from core.security import AuthorizationManager

# Initialize
authz_manager = AuthorizationManager()

# Create role
admin_role = authz_manager.create_role(
    name="admin",
    description="Administrator"
)

# Create permission
delete_perm = authz_manager.create_permission(
    name="users:delete",
    resource="users",
    action="delete"
)

# Assign permission to role
authz_manager.assign_permission_to_role(admin_role.id, delete_perm.id)

# Assign role to user
authz_manager.assign_role_to_user(user.id, admin_role.id)

# Check permission
if authz_manager.has_permission(user.id, "users:delete"):
    print("✓ User can delete users")
```

## 3. Data Protection (1 minute)

```python
from core.security import DataProtectionManager

# Initialize
data_protection = DataProtectionManager()

# Mask sensitive data
print(data_protection.mask_email("john.doe@example.com"))
# Output: j*******e@example.com

print(data_protection.mask_phone("555-123-4567"))
# Output: *******4567

# Mask dictionary
user_data = {
    "email": "john@example.com",
    "phone": "555-123-4567",
    "name": "John Doe"
}
masked = data_protection.mask_dict(user_data)
print(f"✓ Masked data: {masked}")
```

## 4. Security Monitoring (1 minute)

```python
from core.security import SecurityMonitor, SecurityEventType, SecuritySeverity

# Initialize
security_monitor = SecurityMonitor()

# Log security event
security_monitor.log_security_event(
    event_type=SecurityEventType.FAILED_LOGIN,
    severity=SecuritySeverity.MEDIUM,
    description="Failed login attempt",
    ip_address="192.168.1.100"
)

# Validate input (detect SQL injection, XSS)
safe_input = "Hello World"
unsafe_input = "SELECT * FROM users"

print(f"✓ '{safe_input}' is safe: {security_monitor.validate_input(safe_input, 'comment')}")
print(f"✓ '{unsafe_input}' is safe: {security_monitor.validate_input(unsafe_input, 'comment')}")

# Get security stats
stats = security_monitor.get_security_stats(days=7)
print(f"✓ Security events (7 days): {stats['total_events']}")
```

## Complete Example

```python
from core.security import (
    AuthenticationManager,
    AuthorizationManager,
    DataProtectionManager,
    SecurityMonitor,
    init_all_security_tables,
    create_default_roles_and_permissions
)

# Initialize
init_all_security_tables()
create_default_roles_and_permissions()

auth_manager = AuthenticationManager()
authz_manager = AuthorizationManager()
data_protection = DataProtectionManager()
security_monitor = SecurityMonitor()

# 1. Register and login
user = auth_manager.register_user(
    email="admin@example.com",
    password="AdminPass123!"
)

result = auth_manager.authenticate(
    email="admin@example.com",
    password="AdminPass123!",
    ip_address="192.168.1.100"
)

print(f"✓ Authenticated: {result.status.value}")

# 2. Assign admin role
from core.security import Role
from core.database import get_db_manager

with get_db_manager().session_scope() as session:
    admin_role = session.query(Role).filter(Role.name == "admin").first()
    if admin_role:
        authz_manager.assign_role_to_user(user.id, admin_role.id)
        print("✓ Admin role assigned")

# 3. Check permissions
permissions = authz_manager.get_user_permissions(user.id)
print(f"✓ User has {len(permissions)} permissions")

# 4. Protect sensitive data
sensitive_data = {
    "email": "admin@example.com",
    "phone": "555-123-4567"
}
masked_data = data_protection.mask_dict(sensitive_data)
print(f"✓ Masked: {masked_data}")

# 5. Monitor security
stats = security_monitor.get_security_stats(days=1)
print(f"✓ Security events today: {stats['total_events']}")

print("\n✓ All systems operational!")
```

## Using Decorators

```python
from core.security import require_permission, require_role

@require_permission("users:delete")
def delete_user(user_id: str, **kwargs):
    """Only users with users:delete permission can call this"""
    print(f"Deleting user {user_id}")

@require_role("admin")
def admin_function(user_id: str, **kwargs):
    """Only users with admin role can call this"""
    print("Admin function executed")

# Call with user_id in kwargs
delete_user(user_id="current_user_id", target_user="user_to_delete")
```

## Enable MFA

```python
# Enable MFA for user
mfa_data = auth_manager.enable_mfa(user.id)

print(f"MFA Secret: {mfa_data['secret']}")
print(f"Scan this QR code: {mfa_data['provisioning_uri']}")

# User scans QR code with authenticator app (Google Authenticator, Authy, etc.)

# Login with MFA
result = auth_manager.authenticate(
    email="user@example.com",
    password="SecurePass123!"
)

if result.requires_mfa:
    # Get MFA token from user
    mfa_token = input("Enter MFA token: ")
    
    result = auth_manager.authenticate(
        email="user@example.com",
        password="SecurePass123!",
        mfa_token=mfa_token
    )
```

## Configuration

Add to `.env`:

```bash
# Security
SECRET_KEY=your-secret-key-here-change-in-production
SESSION_TIMEOUT=86400  # 24 hours in seconds
BCRYPT_ROUNDS=12

# Database
DATABASE_URL=postgresql://user:pass@localhost/app
```

## Next Steps

1. **Read the full documentation**: `core/SECURITY_README.md`
2. **Run the tests**: `pytest core/test_security.py -v`
3. **See more examples**: `python core/example_security_usage.py`
4. **Customize**: Adjust security settings in `.env` for your needs

## Common Tasks

### Change Password
```python
auth_manager.change_password(
    user_id=user.id,
    old_password="OldPass123!",
    new_password="NewPass456!"
)
```

### Revoke All Sessions
```python
auth_manager.session_manager.revoke_all_user_sessions(user.id)
```

### Get Security Report
```python
report = security_monitor.generate_security_report(days=30)
print(f"Critical events: {len(report['critical_events'])}")
```

### Set Data Retention Policy
```python
from core.security import DataRetentionPolicy

retention = DataRetentionPolicy()
retention.set_policy("audit_logs", retention_days=90)
retention.set_policy("sessions", retention_days=30)
```

## Troubleshooting

### bcrypt not installed
```bash
pip install bcrypt
```

### pyotp not installed (for MFA)
```bash
pip install pyotp
```

### Database tables not created
```python
from core.security import init_all_security_tables
init_all_security_tables()
```

### Default roles not created
```python
from core.security import create_default_roles_and_permissions
create_default_roles_and_permissions()
```

## Support

For more information, see:
- Full documentation: `core/SECURITY_README.md`
- Example usage: `core/example_security_usage.py`
- Test suite: `core/test_security.py`

