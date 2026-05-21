# Data Encryption System - Quick Reference

## Quick Start

```python
from backend.services.encryption_service import get_encryption_service

# Get encryption service
encryption_service = get_encryption_service()

# Encrypt a field
encrypted = encryption_service.encrypt_database_field("sensitive_data", "email")

# Decrypt a field
decrypted = encryption_service.decrypt_database_field(encrypted, "email")
```

## Common Operations

### Database Encryption

```python
# Encrypt single field
encrypted_value = encryption_service.encrypt_database_field(
    value="data",
    field_name="field_name",
    user_id="user123"
)

# Encrypt multiple fields in a row
encrypted_row = encryption_service.encrypt_database_row(
    row_data={"field1": "value1", "field2": "value2"},
    encrypted_fields=["field1", "field2"],
    user_id="user123"
)
```

### File Encryption

```python
# Encrypt file
encrypted_path = encryption_service.encrypt_file(
    input_path="/path/to/file.pdf",
    user_id="user123"
)

# Encrypt file data in memory
encrypted_data = encryption_service.encrypt_file_data(
    file_data=b"file contents",
    user_id="user123"
)
```

### Communication Encryption

```python
# Encrypt API payload
encrypted_payload = encryption_service.encrypt_api_payload(
    payload={"key": "value"},
    user_id="user123"
)

# Encrypt WebSocket message
encrypted_msg = encryption_service.encrypt_websocket_message(
    message="sensitive message",
    user_id="user123"
)
```

### Key Management

```python
# Generate key
key = encryption_service.generate_key("my_key", user_id="admin")

# Rotate key
new_key = encryption_service.rotate_key("my_key", user_id="admin")

# List keys
keys = encryption_service.list_keys()

# Delete key
encryption_service.delete_key("old_key", user_id="admin")
```

### Audit Logging

```python
# Get audit logs
logs = encryption_service.get_audit_log(
    start_date=datetime(2024, 1, 1),
    operation="encrypt_field"
)

# Get statistics
stats = encryption_service.get_audit_statistics()
```

## API Endpoints

### Database Encryption

```bash
POST /api/v1/encryption/database/encrypt-field
POST /api/v1/encryption/database/decrypt-field
POST /api/v1/encryption/database/encrypt-row
POST /api/v1/encryption/database/decrypt-row
```

### File Encryption

```bash
POST /api/v1/encryption/file/encrypt
POST /api/v1/encryption/file/decrypt
```

### Communication Encryption

```bash
POST /api/v1/encryption/communication/encrypt-payload
POST /api/v1/encryption/communication/decrypt-payload
```

### Key Management

```bash
POST /api/v1/encryption/keys/generate
POST /api/v1/encryption/keys/rotate
GET  /api/v1/encryption/keys/list
DELETE /api/v1/encryption/keys/{key_name}
```

### Audit & Status

```bash
POST /api/v1/encryption/audit/log
GET  /api/v1/encryption/audit/statistics
GET  /api/v1/encryption/status
GET  /api/v1/encryption/validate
```

## Configuration

### Environment Variables

```bash
ENCRYPTION_MASTER_PASSWORD=your_secure_password
DATABASE_URL=sqlite:///./solar_calculator.db
ENCRYPTION_AUDIT_ENABLED=true
ENCRYPTION_KEY_ROTATION_DAYS=90
```

### Database Settings

```sql
-- Enable encryption
UPDATE encryption_settings SET setting_value = 'true' 
WHERE setting_key = 'encryption_enabled';

-- Set algorithm
UPDATE encryption_settings SET setting_value = 'Fernet' 
WHERE setting_key = 'default_algorithm';
```

## Security Checklist

- [ ] Set strong master password
- [ ] Enable audit logging
- [ ] Configure key rotation schedule
- [ ] Restrict admin access to key operations
- [ ] Backup encryption keys securely
- [ ] Review audit logs regularly
- [ ] Test encryption/decryption regularly
- [ ] Document encrypted fields

## Troubleshooting

### Decryption Fails
```python
# Check if key exists
keys = encryption_service.list_keys()
print(f"Available keys: {keys}")

# Validate encryption system
validation = encryption_service.validate_encryption()
print(f"Validation results: {validation}")
```

### Key Not Found
```python
# Generate missing key
encryption_service.generate_key("missing_key", user_id="admin")
```

### Permission Denied
```python
# Verify user role
if current_user.get('role') != 'admin':
    raise HTTPException(status_code=403, detail="Admin access required")
```

## Performance Tips

1. **Batch operations**: Encrypt multiple fields at once
2. **Cache keys**: Keys are cached in memory
3. **Async operations**: Use async for large files
4. **Don't index**: Don't index encrypted fields

## Data Classification

| Level | Encryption | Key Rotation | Examples |
|-------|-----------|--------------|----------|
| Public | Optional | N/A | Public documents |
| Internal | Recommended | 180 days | Internal memos |
| Confidential | Required | 90 days | Customer data |
| Restricted | Required | 30 days | SSN, Credit cards |

## Common Patterns

### Encrypt User Data

```python
user_data = {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
}

encrypted_user = encryption_service.encrypt_database_row(
    row_data=user_data,
    encrypted_fields=["email", "phone"],
    user_id="admin"
)
```

### Encrypt File Upload

```python
@app.post("/upload")
async def upload_file(file: UploadFile):
    file_data = await file.read()
    encrypted_data = encryption_service.encrypt_file_data(
        file_data=file_data,
        user_id=current_user.id
    )
    # Store encrypted_data
    return {"status": "encrypted and stored"}
```

### Secure API Communication

```python
@app.post("/secure-endpoint")
async def secure_endpoint(encrypted_payload: dict):
    # Decrypt incoming payload
    payload = encryption_service.decrypt_api_payload(
        encrypted_payload=encrypted_payload,
        user_id=current_user.id
    )
    
    # Process payload
    result = process_data(payload)
    
    # Encrypt response
    encrypted_response = encryption_service.encrypt_api_payload(
        payload=result,
        user_id=current_user.id
    )
    
    return encrypted_response
```

## Migration Script

```python
# Encrypt existing data
from backend.services.encryption_service import get_encryption_service
from backend.core.database import SessionLocal

encryption_service = get_encryption_service()
db = SessionLocal()

# Encrypt all user emails
users = db.query(User).all()
for user in users:
    if not user.email.startswith('gAAAAA'):  # Not encrypted
        user.email = encryption_service.encrypt_database_field(
            value=user.email,
            field_name="email",
            user_id="migration"
        )

db.commit()
print(f"Encrypted {len(users)} user emails")
```

## Testing

```python
# Test encryption/decryption
def test_encryption():
    service = get_encryption_service()
    
    # Test data
    original = "test_data"
    
    # Encrypt
    encrypted = service.encrypt_database_field(original, "test_field")
    assert encrypted != original
    
    # Decrypt
    decrypted = service.decrypt_database_field(encrypted, "test_field")
    assert decrypted == original
    
    print("✅ Encryption test passed")

test_encryption()
```

## Support

- 📖 Full Guide: `docs/ENCRYPTION_SYSTEM_GUIDE.md`
- 🔧 API Docs: `/docs` (Swagger UI)
- 📊 Audit Logs: `/api/v1/encryption/audit/log`
- ✅ Validation: `/api/v1/encryption/validate`
