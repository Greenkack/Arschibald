# Security & Access Control System

Comprehensive security system with authentication, authorization, data protection, and security monitoring.

## Features

### Task 9.1: Authentication System
- **User Authentication**: Secure password hashing with bcrypt
- **Session Management**: Configurable session timeouts and token-based authentication
- **Multi-Factor Authentication (MFA)**: TOTP-based 2FA support
- **Account Security**: Account lockout after failed attempts, password expiration
- **Authentication Audit Logging**: Complete audit trail of authentication events

### Task 9.2: Authorization & RBAC
- **Role-Based Access Control**: Hierarchical role system with inheritance
- **Granular Permissions**: Resource and action-based permission system
- **Dynamic Permission Evaluation**: Support for complex permission expressions
- **Permission Caching**: High-performance permission lookups with caching
- **Decorators**: `@require_permission` and `@require_role` for easy access control

### Task 9.3: Data Protection
- **PII Identification**: Automatic detection of personally identifiable information
- **Data Masking**: Mask emails, phone numbers, credit cards, and other sensitive data
- **Data Encryption**: Encrypt sensitive data at rest
- **Data Access Logging**: Track all access to sensitive data for compliance
- **Data Retention Policies**: Automatic cleanup of expired data

### Task 9.4: Security Monitoring
- **Threat Detection**: Detect brute force, SQL injection, XSS, and anomalous behavior
- **Security Event Logging**: Comprehensive logging of security events
- **Real-time Monitoring**: Monitor failed logins, suspicious IPs, and user activity
- **Security Reports**: Generate detailed security reports and statistics
- **Alerting**: Configurable alerts for high-severity security events

## Installation

```bash
# Install required dependencies
pip install bcrypt pyotp

# Initialize security tables
from core.security import init_all_security_tables, create_default_roles_and_permissions

init_all_security_tables()
create_default_roles_and_permissions()
```

## Quick Start

### Authentication

```python
from core.security import AuthenticationManager

auth_manager = AuthenticationManager()

# Register user
user = auth_manager.register_user(
    email="user@example.com",
    password="SecurePass123!",
    full_name="John Doe"
)

# Authenticate
result = auth_manager.authenticate(
    email="user@example.com",
    password="SecurePass123!",
    ip_address="192.168.1.100"
)

if result.status.value == "success":
    print(f"Session token: {result.session_token}")
```

### Authorization

```python
from core.security import AuthorizationManager

authz_manager = AuthorizationManager()

# Create role and permission
role = authz_manager.create_role(name="admin")
permission = authz_manager.create_permission(
    name="users:delete",
    resource="users",
    action="delete"
)

# Assign permission to role
authz_manager.assign_permission_to_role(role.id, permission.id)

# Assign role to user
authz_manager.assign_role_to_user(user.id, role.id)

# Check permission
if authz_manager.has_permission(user.id, "users:delete"):
    print("User can delete users")
```

### Data Protection

```python
from core.security import DataProtectionManager

data_protection = DataProtectionManager()

# Mask PII
masked_email = data_protection.mask_email("john.doe@example.com")
masked_phone = data_protection.mask_phone("555-123-4567")

# Mask dictionary
user_data = {
    "email": "john@example.com",
    "phone": "555-123-4567",
    "age": 30
}
masked_data = data_protection.mask_dict(user_data)

# Encrypt sensitive data
encrypted = data_protection.encrypt_data("sensitive information")
decrypted = data_protection.decrypt_data(encrypted)
```

### Security Monitoring

```python
from core.security import SecurityMonitor, SecurityEventType, SecuritySeverity

security_monitor = SecurityMonitor()

# Log security event
security_monitor.log_security_event(
    event_type=SecurityEventType.FAILED_LOGIN,
    severity=SecuritySeverity.MEDIUM,
    description="Failed login attempt",
    ip_address="192.168.1.100"
)

# Validate input
is_safe = security_monitor.validate_input(user_input, "comment_field")

# Get security statistics
stats = security_monitor.get_security_stats(days=7)
print(f"Total events: {stats['total_events']}")

# Generate security report
report = security_monitor.generate_security_report(days=30)
```

## Architecture

### Database Models

- **User**: User accounts with authentication credentials
- **Role**: Roles for RBAC with hierarchical support
- **Permission**: Granular permissions for resources and actions
- **UserSessionModel**: Active user sessions with expiration
- **AuthenticationAuditLog**: Audit trail of authentication events
- **SecurityEvent**: Security events and incidents
- **DataAccessLog**: Log of data access for compliance

### Core Components

1. **AuthenticationManager**: Handles user registration, login, MFA, password management
2. **SessionManager**: Manages user sessions with token validation
3. **AuthorizationManager**: Implements RBAC with role and permission management
4. **DataProtectionManager**: Provides PII masking and data encryption
5. **SecurityMonitor**: Monitors security events and generates reports
6. **ThreatDetector**: Detects security threats like SQL injection, XSS, brute force

## Security Best Practices

### Password Security
- Minimum 8 characters with uppercase, lowercase, and digits
- Bcrypt hashing with configurable rounds (default: 12)
- Password expiration support
- Force password change on first login

### Session Security
- Secure token generation with `secrets.token_urlsafe()`
- Configurable session timeout (default: 24 hours)
- Session revocation on password change
- IP address and user agent tracking

### Account Security
- Account lockout after 5 failed attempts (configurable)
- 15-minute lockout duration (configurable)
- Automatic unlock after lockout period
- Failed login attempt tracking

### Data Protection
- Automatic PII detection and masking
- Encryption of sensitive data
- Data access logging for compliance
- Configurable data retention policies

### Monitoring
- Real-time threat detection
- Comprehensive audit logging
- Security event alerting
- Regular security reports

## Configuration

Configure security settings in `.env`:

```bash
# Security
SECRET_KEY=your-secret-key-here
SESSION_TIMEOUT=86400  # 24 hours
BCRYPT_ROUNDS=12

# Account Lockout
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION=900  # 15 minutes

# MFA
MFA_ISSUER=YourAppName
```

## API Reference

### AuthenticationManager

```python
# User registration
user = auth_manager.register_user(email, password, **kwargs)

# Authentication
result = auth_manager.authenticate(email, password, mfa_token=None, ip_address=None)

# Password management
success = auth_manager.change_password(user_id, old_password, new_password)

# MFA
mfa_data = auth_manager.enable_mfa(user_id)
success = auth_manager.disable_mfa(user_id)

# Logout
success = auth_manager.logout(session_token)
```

### AuthorizationManager

```python
# Role management
role = authz_manager.create_role(name, description=None, parent_role_id=None)
success = authz_manager.assign_role_to_user(user_id, role_id)
success = authz_manager.remove_role_from_user(user_id, role_id)

# Permission management
permission = authz_manager.create_permission(name, resource, action, description=None)
success = authz_manager.assign_permission_to_role(role_id, permission_id)
success = authz_manager.remove_permission_from_role(role_id, permission_id)

# Permission checks
permissions = authz_manager.get_user_permissions(user_id)
has_perm = authz_manager.has_permission(user_id, permission)
has_role = authz_manager.has_role(user_id, role_name)
can_access = authz_manager.check_resource_permission(user_id, resource, action)
```

### DataProtectionManager

```python
# PII masking
masked = data_protection.mask_email(email)
masked = data_protection.mask_phone(phone)
masked = data_protection.mask_credit_card(card)
masked = data_protection.mask_pii(text, field_type=None)

# Dictionary operations
pii_fields = data_protection.identify_pii_fields(data)
masked_data = data_protection.mask_dict(data, pii_fields=None)

# Encryption
encrypted = data_protection.encrypt_data(data)
decrypted = data_protection.decrypt_data(encrypted)
```

### SecurityMonitor

```python
# Event logging
event = security_monitor.log_security_event(
    event_type, severity, description,
    user_id=None, ip_address=None, **kwargs
)

# Monitoring
security_monitor.monitor_failed_logins(email, ip_address)
security_monitor.monitor_user_activity(user_id)

# Input validation
is_valid = security_monitor.validate_input(input_text, source)

# Reporting
events = security_monitor.get_security_events(**filters)
stats = security_monitor.get_security_stats(days=7)
report = security_monitor.generate_security_report(days=30)
```

## Testing

Run the test suite:

```bash
pytest core/test_security.py -v
```

## Examples

See `core/example_security_usage.py` for comprehensive examples of all features.

## Requirements

- Python 3.10+
- bcrypt (for password hashing)
- pyotp (for MFA support)
- SQLAlchemy (for database)
- structlog (for logging)

## License

Part of the Robust Streamlit Application framework.

