# License Management System - Complete Guide

## Overview

The License Management System provides comprehensive license key generation, validation, feature licensing, expiration handling, and reporting capabilities for the Solar Calculator Pro application.

## Table of Contents

1. [License Types](#license-types)
2. [License Features](#license-features)
3. [API Endpoints](#api-endpoints)
4. [License Workflow](#license-workflow)
5. [Feature Access Control](#feature-access-control)
6. [Hardware Binding](#hardware-binding)
7. [License Validation](#license-validation)
8. [License Renewal](#license-renewal)
9. [Reporting](#reporting)
10. [Best Practices](#best-practices)

## License Types

The system supports five license types:

### 1. Trial License
- **Duration**: 30 days
- **Features**: Limited feature set
- **Users**: 1 user
- **Projects**: 10 projects
- **Calculations**: 100/month
- **Use Case**: Evaluation and testing

### 2. Basic License
- **Duration**: 1 year (renewable)
- **Features**: Core features only
- **Users**: 1 user
- **Projects**: 50 projects
- **Calculations**: 500/month
- **Use Case**: Individual professionals

### 3. Professional License
- **Duration**: 1 year (renewable)
- **Features**: All standard features
- **Users**: 5 users
- **Projects**: Unlimited
- **Calculations**: Unlimited
- **Use Case**: Small to medium businesses

### 4. Enterprise License
- **Duration**: 1 year (renewable)
- **Features**: All features including advanced
- **Users**: Unlimited
- **Projects**: Unlimited
- **Calculations**: Unlimited
- **Use Case**: Large organizations

### 5. Lifetime License
- **Duration**: Lifetime (no expiry)
- **Features**: All features
- **Users**: Unlimited
- **Projects**: Unlimited
- **Calculations**: Unlimited
- **Use Case**: One-time purchase

## License Features

### Core Features (Available in all licenses)
- `solar_calculator` - Basic solar system calculations
- `heatpump_calculator` - Heat pump sizing
- `pdf_generation` - Basic PDF reports

### Professional Features
- `3d_visualization` - 3D roof visualization
- `advanced_pdf` - Extended PDF features
- `crm` - Customer relationship management
- `unlimited_projects` - No project limits
- `multi_user` - Multiple users
- `priority_support` - Priority support

### Enterprise Features
- `multi_pdf` - Multi-company PDF generation
- `product_rotation` - Automatic product rotation
- `white_label` - Custom branding
- `api_access` - REST API access

## API Endpoints

### Create License (Admin Only)

```http
POST /api/v1/licenses/
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "license_type": "professional",
  "user_email": "user@example.com",
  "organization_name": "Example Corp",
  "expires_at": "2025-12-31T23:59:59Z",
  "enabled_features": {
    "3d_visualization": true,
    "crm": true
  },
  "max_users": 5,
  "max_projects": 100,
  "max_calculations_per_month": 1000
}
```

**Response:**
```json
{
  "id": 1,
  "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
  "license_type": "professional",
  "status": "pending",
  "user_email": "user@example.com",
  "organization_name": "Example Corp",
  "issued_at": "2024-01-01T00:00:00Z",
  "expires_at": "2025-12-31T23:59:59Z",
  "enabled_features": {
    "3d_visualization": true,
    "crm": true
  },
  "is_active": false,
  "days_until_expiry": 730
}
```

### Activate License (Public)

```http
POST /api/v1/licenses/activate
Content-Type: application/json

{
  "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
  "hardware_id": "HWID-12345-ABCDE",
  "machine_name": "DESKTOP-PC01"
}
```

**Response:**
```json
{
  "success": true,
  "message": "License activated successfully",
  "license": {
    "id": 1,
    "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
    "status": "active",
    "activated_at": "2024-01-01T10:00:00Z"
  }
}
```

### Validate License (Public)

```http
POST /api/v1/licenses/validate
Content-Type: application/json

{
  "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
  "hardware_id": "HWID-12345-ABCDE",
  "features_to_check": [
    "3d_visualization",
    "crm",
    "multi_pdf"
  ]
}
```

**Response:**
```json
{
  "is_valid": true,
  "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
  "status": "active",
  "license_type": "professional",
  "message": "License is valid",
  "expires_at": "2025-12-31T23:59:59Z",
  "days_until_expiry": 730,
  "enabled_features": {
    "3d_visualization": true,
    "crm": true
  },
  "feature_access": {
    "3d_visualization": true,
    "crm": true,
    "multi_pdf": false
  },
  "warnings": []
}
```

### Renew License (Authenticated)

```http
POST /api/v1/licenses/renew
Content-Type: application/json
Authorization: Bearer <user_token>

{
  "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
  "renewal_period_days": 365,
  "payment_reference": "PAY-12345",
  "payment_amount": 99900,
  "payment_currency": "EUR"
}
```

**Response:**
```json
{
  "license_id": 1,
  "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
  "old_expires_at": "2025-12-31T23:59:59Z",
  "new_expires_at": "2026-12-31T23:59:59Z",
  "renewal_period_days": 365,
  "renewed_at": "2024-01-01T10:00:00Z",
  "message": "License renewed successfully"
}
```

### Generate License Report (Admin Only)

```http
POST /api/v1/licenses/report
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z",
  "license_types": ["professional", "enterprise"],
  "statuses": ["active", "expired"],
  "include_validations": true,
  "include_renewals": true
}
```

**Response:**
```json
{
  "total_licenses": 150,
  "active_licenses": 120,
  "expired_licenses": 20,
  "suspended_licenses": 5,
  "revoked_licenses": 3,
  "pending_licenses": 2,
  "licenses_by_type": {
    "trial": 10,
    "basic": 30,
    "professional": 80,
    "enterprise": 25,
    "lifetime": 5
  },
  "licenses_expiring_soon": [
    {
      "license_key": "A1B2-C3D4-E5F6-G7H8-I9J0",
      "user_email": "user@example.com",
      "expires_at": "2024-02-15T23:59:59Z",
      "days_until_expiry": 15
    }
  ],
  "recent_validations": [...],
  "recent_renewals": [...],
  "generated_at": "2024-01-01T10:00:00Z"
}
```

## License Workflow

### 1. License Creation
```
Admin → Create License → System generates unique key → License status: PENDING
```

### 2. License Activation
```
User → Enter license key → Provide hardware ID → System validates → License status: ACTIVE
```

### 3. License Validation
```
Application → Validate license → Check expiry → Check hardware binding → Check features → Return validation result
```

### 4. License Renewal
```
User → Request renewal → Provide payment → System extends expiry → License status: ACTIVE
```

### 5. License Expiration
```
System → Check expiry daily → If expired → License status: EXPIRED → Notify user
```

## Feature Access Control

### Checking Feature Access

```python
# In your application code
from backend.services.license_service import LicenseService

def check_feature_access(license_key: str, feature_key: str) -> bool:
    service = LicenseService(db)
    
    validation = service.validate_license(
        LicenseValidationRequest(
            license_key=license_key,
            features_to_check=[feature_key]
        )
    )
    
    if not validation.is_valid:
        return False
    
    return validation.feature_access.get(feature_key, False)

# Usage
if check_feature_access(license_key, "3d_visualization"):
    # Allow access to 3D visualization
    show_3d_viewer()
else:
    # Show upgrade prompt
    show_upgrade_dialog()
```

### Feature-Based UI Rendering

```typescript
// In React frontend
import { useFeatureAccess } from '@/hooks/useFeatureAccess';

export const Dashboard = () => {
  const { hasFeature, isLoading } = useFeatureAccess();
  
  return (
    <div>
      {hasFeature('solar_calculator') && <SolarCalculator />}
      {hasFeature('3d_visualization') && <Viewer3D />}
      {hasFeature('crm') && <CRMDashboard />}
      
      {!hasFeature('multi_pdf') && (
        <UpgradePrompt feature="multi_pdf" />
      )}
    </div>
  );
};
```

## Hardware Binding

### Purpose
Hardware binding ties a license to a specific machine, preventing unauthorized sharing.

### Implementation

```python
import platform
import hashlib
import uuid

def get_hardware_id() -> str:
    """Generate unique hardware identifier"""
    # Combine multiple hardware identifiers
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                    for elements in range(0,2*6,2)][::-1])
    
    system = platform.system()
    machine = platform.machine()
    processor = platform.processor()
    
    # Create hash
    unique_string = f"{mac}:{system}:{machine}:{processor}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:32]

# Usage
hardware_id = get_hardware_id()
# Use in activation and validation
```

### Electron Integration

```javascript
// electron/hardware-id.js
const os = require('os');
const crypto = require('crypto');

function getHardwareId() {
  const networkInterfaces = os.networkInterfaces();
  const cpus = os.cpus();
  
  // Get MAC address
  let mac = '';
  for (const name in networkInterfaces) {
    for (const net of networkInterfaces[name]) {
      if (!net.internal && net.mac !== '00:00:00:00:00:00') {
        mac = net.mac;
        break;
      }
    }
    if (mac) break;
  }
  
  // Create unique string
  const uniqueString = `${mac}:${os.platform()}:${os.arch()}:${cpus[0].model}`;
  
  // Hash it
  return crypto.createHash('sha256').update(uniqueString).digest('hex').substring(0, 32);
}

module.exports = { getHardwareId };
```

## License Validation

### Validation Frequency

- **On Application Start**: Always validate
- **Periodic Checks**: Every 24 hours
- **Before Feature Access**: Validate specific features
- **After Network Reconnect**: Re-validate

### Offline Grace Period

```python
# Allow 7 days offline grace period
OFFLINE_GRACE_PERIOD_DAYS = 7

def validate_with_grace_period(license_key: str) -> bool:
    # Try online validation first
    try:
        result = validate_license_online(license_key)
        cache_validation_result(license_key, result)
        return result.is_valid
    except NetworkError:
        # Check cached validation
        cached = get_cached_validation(license_key)
        if cached:
            days_since_validation = (datetime.now() - cached.validated_at).days
            if days_since_validation <= OFFLINE_GRACE_PERIOD_DAYS:
                return cached.is_valid
        return False
```

## License Renewal

### Automatic Renewal Reminders

```python
def send_renewal_reminders():
    """Send renewal reminders for expiring licenses"""
    # Get licenses expiring in 30, 14, 7, and 1 days
    for days in [30, 14, 7, 1]:
        expiring_licenses = get_licenses_expiring_in_days(days)
        
        for license in expiring_licenses:
            send_email(
                to=license.user_email,
                subject=f"License Expiring in {days} Days",
                body=f"""
                Your {license.license_type} license will expire in {days} days.
                
                License Key: {license.license_key}
                Expires: {license.expires_at}
                
                Renew now to continue using all features.
                """
            )
```

### Self-Service Renewal Portal

```typescript
// frontend/src/pages/LicenseRenewal.tsx
export const LicenseRenewal = () => {
  const [licenseKey, setLicenseKey] = useState('');
  const [renewalPeriod, setRenewalPeriod] = useState(365);
  
  const handleRenew = async () => {
    const response = await api.post('/licenses/renew', {
      license_key: licenseKey,
      renewal_period_days: renewalPeriod,
      payment_reference: paymentRef
    });
    
    if (response.data.success) {
      showSuccess('License renewed successfully!');
    }
  };
  
  return (
    <div>
      <h1>Renew Your License</h1>
      <input value={licenseKey} onChange={e => setLicenseKey(e.target.value)} />
      <select value={renewalPeriod} onChange={e => setRenewalPeriod(Number(e.target.value))}>
        <option value={365}>1 Year - €999</option>
        <option value={730}>2 Years - €1799 (10% off)</option>
        <option value={1095}>3 Years - €2549 (15% off)</option>
      </select>
      <button onClick={handleRenew}>Renew Now</button>
    </div>
  );
};
```

## Reporting

### Dashboard Metrics

```python
def get_license_dashboard_metrics():
    """Get key metrics for license dashboard"""
    return {
        "total_revenue": calculate_total_revenue(),
        "active_licenses": count_active_licenses(),
        "churn_rate": calculate_churn_rate(),
        "renewal_rate": calculate_renewal_rate(),
        "average_license_value": calculate_average_value(),
        "licenses_by_type": get_licenses_by_type(),
        "monthly_recurring_revenue": calculate_mrr(),
        "annual_recurring_revenue": calculate_arr()
    }
```

### Export Reports

```python
def export_license_report(format: str = "csv"):
    """Export license report in various formats"""
    licenses = get_all_licenses()
    
    if format == "csv":
        return export_to_csv(licenses)
    elif format == "excel":
        return export_to_excel(licenses)
    elif format == "pdf":
        return export_to_pdf(licenses)
```

## Best Practices

### 1. Security
- ✅ Never expose license keys in client-side code
- ✅ Always validate licenses server-side
- ✅ Use HTTPS for all license API calls
- ✅ Implement rate limiting on validation endpoints
- ✅ Log all license operations for audit trail

### 2. User Experience
- ✅ Provide clear license status indicators
- ✅ Send renewal reminders well in advance
- ✅ Offer grace period for expired licenses
- ✅ Make renewal process simple and quick
- ✅ Provide self-service license management

### 3. Business
- ✅ Track license usage metrics
- ✅ Monitor renewal rates
- ✅ Identify upgrade opportunities
- ✅ Analyze feature usage by license type
- ✅ Automate renewal reminders

### 4. Technical
- ✅ Cache validation results appropriately
- ✅ Implement offline validation with grace period
- ✅ Handle network failures gracefully
- ✅ Use background validation checks
- ✅ Implement proper error handling

## Troubleshooting

### Common Issues

**Issue: License validation fails**
- Check network connectivity
- Verify license key is correct
- Check if license is expired
- Verify hardware ID matches

**Issue: Hardware ID mismatch**
- License may be bound to different machine
- Contact support to transfer license
- Check if hardware has changed

**Issue: Feature not accessible**
- Verify feature is included in license type
- Check if feature is explicitly disabled
- Validate license is active

## Support

For license-related issues:
- Email: license@solarcalculatorpro.com
- Phone: +49 123 456 7890
- Portal: https://support.solarcalculatorpro.com
