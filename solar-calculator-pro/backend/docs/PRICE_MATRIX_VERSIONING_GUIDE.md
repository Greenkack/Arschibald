# Price Matrix Versioning System - Complete Guide

## Overview

The Price Matrix Versioning System provides comprehensive version control for price matrices, including:

- **Version Management**: Create, update, and manage multiple versions
- **Approval Workflow**: Submit, approve, or reject versions
- **Version Comparison**: Compare differences between versions
- **Version Rollback**: Rollback to previous versions with backup
- **Version History**: Track all changes and modifications
- **Version Migration**: Migrate data between versions with custom rules

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Version Lifecycle](#version-lifecycle)
3. [API Endpoints](#api-endpoints)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Core Concepts

### Version Status

Versions can have the following statuses:

- **draft**: Initial state, can be edited
- **pending**: Submitted for approval, awaiting review
- **approved**: Approved by reviewer, ready for activation
- **rejected**: Rejected by reviewer, needs revision
- **active**: Currently active version in use
- **archived**: Previously active, now archived

### Version Number

Each version has an auto-incrementing version number starting from 1. Version numbers are unique within a matrix.

### Active Version

Only one version can be active at a time for each matrix. The active version is used for all price calculations.

## Version Lifecycle

```
┌─────────┐
│  DRAFT  │ ◄─── Create new version
└────┬────┘
     │ Submit for approval
     ▼
┌─────────┐
│ PENDING │
└────┬────┘
     │
     ├─── Approve ───► ┌──────────┐
     │                 │ APPROVED │
     │                 └────┬─────┘
     │                      │ Activate
     │                      ▼
     │                 ┌────────┐
     │                 │ ACTIVE │
     │                 └────┬───┘
     │                      │ New version activated
     │                      ▼
     │                 ┌──────────┐
     │                 │ ARCHIVED │
     │                 └──────────┘
     │
     └─── Reject ────► ┌──────────┐
                       │ REJECTED │
                       └──────────┘
```

## API Endpoints

### Version CRUD

#### Create Version

```http
POST /api/v1/price-matrix/versioning/versions
Content-Type: application/json

{
  "matrix_id": 1,
  "version_name": "Q1 2024 Pricing",
  "description": "Updated pricing for Q1 2024",
  "matrix_data": {
    "modules": {
      "5": {"10kWh": 15000, "15kWh": 18000},
      "10": {"10kWh": 25000, "15kWh": 28000}
    }
  },
  "metadata": {
    "author": "John Doe",
    "department": "Pricing"
  }
}
```

#### Get Version

```http
GET /api/v1/price-matrix/versioning/versions/{version_id}
```

#### Get All Versions for Matrix

```http
GET /api/v1/price-matrix/versioning/matrices/{matrix_id}/versions?status=draft&limit=100&offset=0
```

#### Get Active Version

```http
GET /api/v1/price-matrix/versioning/matrices/{matrix_id}/versions/active
```

#### Update Version

```http
PUT /api/v1/price-matrix/versioning/versions/{version_id}
Content-Type: application/json

{
  "version_name": "Updated Q1 2024 Pricing",
  "description": "Revised pricing with corrections",
  "matrix_data": { ... }
}
```

#### Delete Version

```http
DELETE /api/v1/price-matrix/versioning/versions/{version_id}
```

### Approval Workflow

#### Submit for Approval

```http
POST /api/v1/price-matrix/versioning/versions/{version_id}/submit
```

#### Approve Version

```http
POST /api/v1/price-matrix/versioning/versions/{version_id}/approve
Content-Type: application/json

{
  "approval_notes": "Pricing looks good, approved for activation"
}
```

#### Reject Version

```http
POST /api/v1/price-matrix/versioning/versions/{version_id}/reject
Content-Type: application/json

{
  "rejection_reason": "Prices need to be adjusted for market conditions"
}
```

#### Activate Version

```http
POST /api/v1/price-matrix/versioning/versions/{version_id}/activate
```

### Version Comparison

#### Compare Two Versions

```http
POST /api/v1/price-matrix/versioning/versions/compare
Content-Type: application/json

{
  "version_a_id": 1,
  "version_b_id": 2,
  "include_details": true
}
```

**Response:**

```json
{
  "id": 1,
  "version_a_id": 1,
  "version_b_id": 2,
  "differences": {
    "added": [
      {"key": "modules.20.10kWh", "new_value": 45000}
    ],
    "removed": [],
    "modified": [
      {
        "key": "modules.5.10kWh",
        "old_value": 15000,
        "new_value": 16000
      }
    ],
    "unchanged_count": 5
  },
  "summary": {
    "total_added": 1,
    "total_removed": 0,
    "total_modified": 1,
    "total_unchanged": 5,
    "total_changes": 2
  },
  "compared_by": 1,
  "compared_at": "2024-01-15T10:30:00Z"
}
```

### Version Rollback

#### Rollback to Version

```http
POST /api/v1/price-matrix/versioning/versions/{version_id}/rollback
Content-Type: application/json

{
  "rollback_reason": "Reverting due to pricing errors in current version",
  "create_backup": true
}
```

**Response:**

```json
{
  "success": true,
  "rolled_back_to_version": 1,
  "previous_version": 3,
  "backup_version_id": 4,
  "rollback_time": 0.234
}
```

### Version History

#### Get Version History

```http
GET /api/v1/price-matrix/versioning/matrices/{matrix_id}/history?limit=50&offset=0
```

#### Get Version Changes

```http
GET /api/v1/price-matrix/versioning/versions/{version_id}/changes?limit=100&offset=0
```

### Version Migration

#### Migrate Version Data

```http
POST /api/v1/price-matrix/versioning/versions/migrate?from_version_id=1&to_version_id=2
Content-Type: application/json

{
  "rename_currency": {
    "type": "rename_key",
    "old_key": "currency",
    "new_key": "currency_code"
  },
  "add_timestamp": {
    "type": "add_default",
    "key": "migrated_at",
    "default": "2024-01-15T10:00:00Z"
  }
}
```

## Usage Examples

### Example 1: Creating and Activating a New Version

```python
from backend.services.price_matrix_version_service import PriceMatrixVersionService
from backend.models.price_matrix_version_schemas import (
    PriceMatrixVersionCreate,
    PriceMatrixVersionApprove
)

# Initialize service
service = PriceMatrixVersionService(db)

# Create new version
version_data = PriceMatrixVersionCreate(
    matrix_id=1,
    version_name="Q2 2024 Pricing",
    description="Updated pricing for Q2 2024",
    matrix_data={
        "modules": {
            "5": {"10kWh": 16000, "15kWh": 19000},
            "10": {"10kWh": 26000, "15kWh": 29000}
        }
    }
)

version = service.create_version(version_data, user_id=1)
print(f"Created version {version.version_number}")

# Submit for approval
version = service.submit_for_approval(version.id, user_id=1)
print(f"Version status: {version.status}")

# Approve version
approval_data = PriceMatrixVersionApprove(
    approval_notes="Pricing approved for Q2"
)
version = service.approve_version(version.id, approval_data, user_id=2)
print(f"Version approved by user {version.approved_by}")

# Activate version
version = service.activate_version(version.id, user_id=1)
print(f"Version {version.version_number} is now active")
```

### Example 2: Comparing Versions

```python
from backend.models.price_matrix_version_schemas import PriceMatrixVersionCompare

# Compare two versions
comparison_data = PriceMatrixVersionCompare(
    version_a_id=1,
    version_b_id=2,
    include_details=True
)

comparison = service.compare_versions(comparison_data, user_id=1)

print(f"Total changes: {comparison.summary['total_changes']}")
print(f"Added: {comparison.summary['total_added']}")
print(f"Modified: {comparison.summary['total_modified']}")
print(f"Removed: {comparison.summary['total_removed']}")

# Print detailed differences
for change in comparison.differences['modified']:
    print(f"Changed: {change['key']}")
    print(f"  Old: {change['old_value']}")
    print(f"  New: {change['new_value']}")
```

### Example 3: Rolling Back to Previous Version

```python
from backend.models.price_matrix_version_schemas import PriceMatrixVersionRollback

# Rollback to version 1
rollback_data = PriceMatrixVersionRollback(
    rollback_reason="Current version has errors",
    create_backup=True
)

result = service.rollback_to_version(
    version_id=1,
    data=rollback_data,
    user_id=1
)

if result["success"]:
    print(f"Rolled back to version {result['rolled_back_to_version']}")
    print(f"Backup created: version {result['backup_version_id']}")
else:
    print("Rollback failed")
```

### Example 4: Viewing Version History

```python
# Get version history
history = service.get_version_history(matrix_id=1, limit=10)

print(f"Total versions: {history['total_count']}")
print(f"Active version: {history['active_version'].version_number}")

for version in history['versions']:
    print(f"Version {version.version_number}: {version.version_name}")
    print(f"  Status: {version.status}")
    print(f"  Created: {version.created_at}")
```

## Best Practices

### 1. Version Naming

Use clear, descriptive version names:

```
✅ Good:
- "Q1 2024 Pricing Update"
- "Emergency Price Correction - Jan 2024"
- "Annual Review 2024"

❌ Bad:
- "Version 1"
- "Update"
- "New prices"
```

### 2. Version Descriptions

Include detailed descriptions:

```python
description = """
Updated pricing for Q1 2024:
- Increased module prices by 5% due to supply chain costs
- Added new 25kWh battery storage option
- Adjusted installation costs for new regions
"""
```

### 3. Approval Workflow

Always use the approval workflow for production changes:

1. Create version in **draft** status
2. Review and test thoroughly
3. Submit for approval
4. Have another team member approve
5. Activate only after approval

### 4. Backup Before Rollback

Always create a backup when rolling back:

```python
rollback_data = PriceMatrixVersionRollback(
    rollback_reason="Detailed reason here",
    create_backup=True  # Always True for production
)
```

### 5. Version Comparison

Compare versions before activation:

```python
# Compare new version with current active
comparison = service.compare_versions(
    PriceMatrixVersionCompare(
        version_a_id=active_version.id,
        version_b_id=new_version.id,
        include_details=True
    ),
    user_id=user_id
)

# Review changes before activating
if comparison.summary['total_changes'] > 100:
    print("Warning: Large number of changes detected")
```

## Troubleshooting

### Issue: Cannot Update Version

**Error**: "Cannot update version in approved status"

**Solution**: Only draft versions can be updated. Create a new version based on the approved one:

```python
# Get approved version
approved_version = service.get_version(version_id)

# Create new draft version with same data
new_version = service.create_version(
    PriceMatrixVersionCreate(
        matrix_id=approved_version.matrix_id,
        version_name=f"{approved_version.version_name} - Revision",
        matrix_data=approved_version.matrix_data
    ),
    user_id=user_id
)

# Now update the new draft version
service.update_version(new_version.id, update_data, user_id)
```

### Issue: Cannot Activate Version

**Error**: "Can only activate approved versions"

**Solution**: Version must be approved before activation:

```python
# Submit for approval
service.submit_for_approval(version_id, user_id)

# Approve
service.approve_version(
    version_id,
    PriceMatrixVersionApprove(),
    approver_user_id
)

# Now activate
service.activate_version(version_id, user_id)
```

### Issue: Rollback Failed

**Error**: "No active version to rollback from"

**Solution**: Ensure there is an active version before rolling back:

```python
# Check for active version
active_version = service.get_active_version(matrix_id)

if not active_version:
    print("No active version found. Activate a version first.")
else:
    # Proceed with rollback
    service.rollback_to_version(target_version_id, rollback_data, user_id)
```

### Issue: Version Comparison Shows Too Many Changes

**Problem**: Comparison shows unexpected number of changes

**Solution**: Use detailed comparison to identify specific changes:

```python
comparison = service.compare_versions(
    PriceMatrixVersionCompare(
        version_a_id=v1_id,
        version_b_id=v2_id,
        include_details=True  # Get detailed differences
    ),
    user_id=user_id
)

# Review each change
for change in comparison.differences['modified']:
    print(f"Key: {change['key']}")
    print(f"Old: {change['old_value']}")
    print(f"New: {change['new_value']}")
```

## Security Considerations

1. **Access Control**: Ensure proper user permissions for version operations
2. **Audit Trail**: All changes are logged with user ID and timestamp
3. **Approval Workflow**: Require approval from different user than creator
4. **Backup**: Always create backups before destructive operations
5. **Validation**: Validate matrix data before creating versions

## Performance Tips

1. **Pagination**: Use limit and offset for large version lists
2. **Caching**: Cache active version for frequent access
3. **Comparison**: Use `include_details=False` for quick comparisons
4. **History**: Limit history queries to recent versions
5. **Migration**: Test migration rules on small datasets first

## Related Documentation

- [Price Matrix System Guide](./PRICE_MATRIX_SYSTEM_GUIDE.md)
- [Price Matrix Validation Guide](./PRICE_MATRIX_VALIDATION_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
