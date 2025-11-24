# License Management - Quick Reference

## Quick Start

### 1. Create a License (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/licenses/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "license_type": "professional",
    "user_email": "user@example.com",
    "max_users": 5
  }'
```

### 2. Activate License (User)
```bash
curl -X POST http://localhost:8000/api/v1/licenses/activate \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
    "hardware_id": "HWID-12345"
  }'
```

### 3. Validate License (Application)
```bash
curl -X POST http://localhost:8000/api/v1/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
    "features_to_check": ["3d_visualization", "crm"]
  }'
```

## License Types

| Type | Duration | Users | Projects | Features |
|------|----------|-------|----------|----------|
| Trial | 30 days | 1 | 10 | Limited |
| Basic | 1 year | 1 | 50 | Core |
| Professional | 1 year | 5 | Unlimited | Standard |
| Enterprise | 1 year | Unlimited | Unlimited | All |
| Lifetime | Forever | Unlimited | Unlimited | All |

## License Status

- `pending` - Created but not activated
- `active` - Active and valid
- `expired` - Past expiration date
- `suspended` - Temporarily disabled
- `revoked` - Permanently disabled

## Key Features by License Type

### Trial
- ✅ Solar Calculator
- ✅ Heat Pump Calculator
- ✅ Basic PDF Generation
- ❌ 3D Visualization
- ❌ CRM
- ❌ Advanced Features

### Basic
- ✅ All Trial features
- ✅ Price Matrix
- ❌ 3D Visualization
- ❌ CRM
- ❌ Advanced PDF

### Professional
- ✅ All Basic features
- ✅ 3D Visualization
- ✅ CRM
- ✅ Advanced PDF
- ✅ Multi-User
- ✅ Unlimited Projects
- ❌ Multi-PDF
- ❌ White Label

### Enterprise
- ✅ All Professional features
- ✅ Multi-PDF Generation
- ✅ Product Rotation
- ✅ White Label
- ✅ API Access
- ✅ Priority Support

### Lifetime
- ✅ All Enterprise features
- ✅ Lifetime validity
- ✅ Free updates

## API Endpoints

### License Management
```
POST   /api/v1/licenses/              Create license (Admin)
GET    /api/v1/licenses/{id}          Get license by ID (Admin)
GET    /api/v1/licenses/key/{key}     Get license by key (User)
PUT    /api/v1/licenses/{id}          Update license (Admin)
POST   /api/v1/licenses/activate      Activate license (Public)
POST   /api/v1/licenses/validate      Validate license (Public)
POST   /api/v1/licenses/renew         Renew license (User)
POST   /api/v1/licenses/report        Generate report (Admin)
```

### Feature Management
```
POST   /api/v1/licenses/features      Create feature (Admin)
GET    /api/v1/licenses/features      List features (User)
```

## Common Operations

### Check if Feature is Available
```python
from backend.services.license_service import LicenseService

service = LicenseService(db)
validation = service.validate_license(
    LicenseValidationRequest(
        license_key="A1B2-C3D4-E5F6-G7H8-I9J0",
        features_to_check=["3d_visualization"]
    )
)

if validation.is_valid and validation.feature_access.get("3d_visualization"):
    # Feature is available
    enable_3d_visualization()
```

### Get Hardware ID
```python
import platform
import hashlib
import uuid

def get_hardware_id():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                    for i in range(0,2*6,2)][::-1])
    unique = f"{mac}:{platform.system()}:{platform.machine()}"
    return hashlib.sha256(unique.encode()).hexdigest()[:32]
```

### Renew License
```python
service = LicenseService(db)
renewal = service.renew_license(
    LicenseRenewalRequest(
        license_key="A1B2-C3D4-E5F6-G7H8-I9J0",
        renewal_period_days=365,
        payment_reference="PAY-12345"
    )
)
```

## Validation Response

```json
{
  "is_valid": true,
  "status": "active",
  "license_type": "professional",
  "expires_at": "2025-12-31T23:59:59Z",
  "days_until_expiry": 365,
  "feature_access": {
    "3d_visualization": true,
    "crm": true,
    "multi_pdf": false
  },
  "warnings": ["License expires in 30 days"]
}
```

## Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 404 | License not found | Check license key |
| 403 | Hardware ID mismatch | Contact support |
| 400 | License expired | Renew license |
| 400 | License suspended | Contact support |
| 400 | License revoked | Contact support |

## Best Practices

1. **Validate on startup** - Always validate license when application starts
2. **Cache results** - Cache validation results for 24 hours
3. **Offline grace** - Allow 7 days offline operation
4. **Feature checks** - Check features before showing UI
5. **Renewal reminders** - Send reminders 30, 14, 7, 1 days before expiry

## Database Schema

```sql
-- Licenses table
CREATE TABLE licenses (
    id INTEGER PRIMARY KEY,
    license_key VARCHAR(255) UNIQUE NOT NULL,
    license_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP,
    hardware_id VARCHAR(255),
    enabled_features JSON,
    max_users INTEGER,
    max_projects INTEGER,
    max_calculations_per_month INTEGER
);

-- License validations table
CREATE TABLE license_validations (
    id INTEGER PRIMARY KEY,
    license_id INTEGER NOT NULL,
    license_key VARCHAR(255) NOT NULL,
    is_valid BOOLEAN NOT NULL,
    validated_at TIMESTAMP NOT NULL,
    hardware_id VARCHAR(255),
    ip_address VARCHAR(45)
);

-- License features table
CREATE TABLE license_features (
    id INTEGER PRIMARY KEY,
    feature_key VARCHAR(100) UNIQUE NOT NULL,
    feature_name VARCHAR(255) NOT NULL,
    available_in_trial BOOLEAN,
    available_in_basic BOOLEAN,
    available_in_professional BOOLEAN,
    available_in_enterprise BOOLEAN,
    available_in_lifetime BOOLEAN
);

-- License renewals table
CREATE TABLE license_renewals (
    id INTEGER PRIMARY KEY,
    license_id INTEGER NOT NULL,
    old_expires_at TIMESTAMP,
    new_expires_at TIMESTAMP NOT NULL,
    renewal_period_days INTEGER NOT NULL,
    renewed_at TIMESTAMP NOT NULL
);
```

## Testing

### Run Migration
```bash
cd solar-calculator-pro/backend
python migrations/add_license_tables.py
```

### Test License Creation
```bash
python -c "
from backend.services.license_service import LicenseService
from backend.models.license_schemas import LicenseCreate
from backend.core.database import SessionLocal

db = SessionLocal()
service = LicenseService(db)

license = service.create_license(LicenseCreate(
    license_type='professional',
    user_email='test@example.com'
))

print(f'Created license: {license.license_key}')
"
```

### Test Validation
```bash
curl -X POST http://localhost:8000/api/v1/licenses/validate \
  -H "Content-Type: application/json" \
  -d '{"license_key": "YOUR-LICENSE-KEY"}'
```

## Support

- **Documentation**: `/docs/LICENSE_MANAGEMENT_GUIDE.md`
- **API Docs**: `http://localhost:8000/docs`
- **Email**: license@solarcalculatorpro.com
