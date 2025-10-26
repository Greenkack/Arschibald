# Data Protection System - Quick Start Guide

## 5-Minute Setup

### Step 1: Initialize Database

```python
from core.security import init_all_security_tables

# Initialize all security tables
init_all_security_tables()
```

### Step 2: Mask PII

```python
from core.security import get_data_protection_manager

manager = get_data_protection_manager()

# Mask email
email = "john.doe@example.com"
masked = manager.mask_email(email)
print(masked)  # j*******e@example.com

# Mask phone
phone = "555-123-4567"
masked = manager.mask_phone(phone)
print(masked)  # *******4567
```

### Step 3: Identify and Mask PII in Data

```python
# Your data
user_data = {
    "user_id": "12345",
    "email": "john.doe@example.com",
    "phone": "555-123-4567",
    "name": "John Doe",
    "status": "active"
}

# Auto-identify PII
pii_fields = manager.identify_pii_fields(user_data)
print(f"Found {len(pii_fields)} PII fields")

# Mask PII
masked_data = manager.mask_dict(user_data, pii_fields)
print(masked_data)
```

### Step 4: Log Data Access

```python
from core.security import log_data_access

# Log when accessing PII
log_data_access(
    user_id="admin123",
    resource_type="users",
    resource_id="user456",
    action="READ",
    pii_fields=["email", "phone"],
    ip_address="192.168.1.100"
)
```

### Step 5: Set Retention Policies

```python
from core.security import get_data_retention_policy

policy = get_data_retention_policy()

# Set retention periods
policy.set_policy("audit_logs", 90)  # 90 days
policy.set_policy("sessions", 30)    # 30 days
policy.set_policy("data_access_logs", 180)  # 180 days
```

## Common Use Cases

### Use Case 1: Safe Logging

```python
manager = get_data_protection_manager()

# Before logging, mask PII
user_data = {"email": "john@example.com", "action": "login"}
pii_fields = manager.identify_pii_fields(user_data)
masked_data = manager.mask_dict(user_data, pii_fields)

# Safe to log
logger.info("User action", data=masked_data)
```

### Use Case 2: Encrypt Sensitive Data

```python
manager = get_data_protection_manager()

# Encrypt before storing
ssn = "123-45-6789"
encrypted = manager.encrypt_data(ssn)

# Store encrypted value
user.encrypted_ssn = encrypted

# Decrypt when needed
decrypted = manager.decrypt_data(user.encrypted_ssn)
```

### Use Case 3: Compliance Logging

```python
from core.security import log_data_access

def get_user_profile(user_id: str, requesting_user: str):
    # Get user
    user = db.query(User).get(user_id)
    
    # Log access
    log_data_access(
        user_id=requesting_user,
        resource_type="users",
        resource_id=user_id,
        action="READ",
        pii_fields=["email", "phone", "address"]
    )
    
    return user
```

### Use Case 4: Automatic Cleanup

```python
from core.security import get_data_retention_policy, DataAccessLog

policy = get_data_retention_policy()

# Set policy
policy.set_policy("data_access_logs", 180)

# Clean up expired data
count = policy.cleanup_expired_data("data_access_logs", DataAccessLog)
print(f"Cleaned up {count} expired records")
```

## Complete Example

```python
from core.security import (
    get_data_protection_manager,
    log_data_access,
    get_data_retention_policy,
    init_all_security_tables
)

# Initialize
init_all_security_tables()
manager = get_data_protection_manager()
policy = get_data_retention_policy()

# Set retention policy
policy.set_policy("data_access_logs", 180)

# Handle user data
user_data = {
    "user_id": "12345",
    "email": "john.doe@example.com",
    "phone": "555-123-4567",
    "ssn": "123-45-6789",
    "status": "active"
}

# 1. Identify PII
pii_fields = manager.identify_pii_fields(user_data)
print(f"Identified {len(pii_fields)} PII fields")

# 2. Encrypt sensitive data
if "ssn" in user_data:
    user_data["ssn"] = manager.encrypt_data(user_data["ssn"])

# 3. Log access
log_data_access(
    user_id="admin123",
    resource_type="users",
    resource_id=user_data["user_id"],
    action="WRITE",
    pii_fields=list(pii_fields.keys())
)

# 4. Mask for display
masked_data = manager.mask_dict(user_data, pii_fields)
print("Masked data:", masked_data)

print("✓ Data protection workflow complete!")
```

## Testing

```bash
# Run all tests
pytest core/test_data_protection.py -v

# Run specific test
pytest core/test_data_protection.py::TestPIIMasking -v

# Run with coverage
pytest core/test_data_protection.py --cov=core.security --cov-report=html
```

## Next Steps

1. ✅ Review `DATA_PROTECTION_README.md` for detailed documentation
2. ✅ Check `example_data_protection_usage.py` for more examples
3. ✅ Configure retention policies for your data
4. ✅ Set up scheduled cleanup jobs
5. ✅ Integrate with your logging system

## Key Functions

```python
# Get manager
manager = get_data_protection_manager()

# Masking
manager.mask_email(email)
manager.mask_phone(phone)
manager.mask_credit_card(card)
manager.mask_pii(text, field_type)
manager.mask_dict(data, pii_fields)

# Identification
manager.identify_pii_fields(data)

# Encryption
manager.encrypt_data(data)
manager.decrypt_data(encrypted)

# Logging
log_data_access(user_id, resource_type, resource_id, action, pii_fields)

# Retention
policy = get_data_retention_policy()
policy.set_policy(resource_type, retention_days)
policy.cleanup_expired_data(resource_type, model_class)
```

## Configuration

Set in environment or `config.py`:

```python
SECRET_KEY=your-secret-key-here  # For encryption
PII_MASKING_ENABLED=true
ENCRYPTION_ENABLED=true
ACCESS_LOGGING_ENABLED=true
AUDIT_LOG_RETENTION=90
SESSION_RETENTION=30
ACCESS_LOG_RETENTION=180
```

## Troubleshooting

**PII not detected?**
- Check field names match patterns
- Add custom patterns if needed

**Encryption fails?**
- Verify SECRET_KEY is set
- Check key is not default value

**Access logs not created?**
- Run `init_all_security_tables()`
- Check database connection

## Support

- 📖 Full docs: `DATA_PROTECTION_README.md`
- 💡 Examples: `example_data_protection_usage.py`
- 🧪 Tests: `test_data_protection.py`
