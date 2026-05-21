# Price Matrix Versioning - Quick Reference

## Quick Start

### Create a New Version

```python
from backend.services.price_matrix_version_service import PriceMatrixVersionService
from backend.models.price_matrix_version_schemas import PriceMatrixVersionCreate

service = PriceMatrixVersionService(db)

version = service.create_version(
    PriceMatrixVersionCreate(
        matrix_id=1,
        version_name="Q1 2024 Pricing",
        description="Updated pricing",
        matrix_data={"modules": {...}}
    ),
    user_id=1
)
```

### Approval Workflow

```python
# 1. Submit for approval
service.submit_for_approval(version_id, user_id=1)

# 2. Approve
service.approve_version(
    version_id,
    PriceMatrixVersionApprove(approval_notes="Approved"),
    user_id=2
)

# 3. Activate
service.activate_version(version_id, user_id=1)
```

### Compare Versions

```python
comparison = service.compare_versions(
    PriceMatrixVersionCompare(
        version_a_id=1,
        version_b_id=2,
        include_details=True
    ),
    user_id=1
)

print(f"Total changes: {comparison.summary['total_changes']}")
```

### Rollback

```python
result = service.rollback_to_version(
    version_id=1,
    data=PriceMatrixVersionRollback(
        rollback_reason="Reverting changes",
        create_backup=True
    ),
    user_id=1
)
```

## API Endpoints Cheat Sheet

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create version | POST | `/api/v1/price-matrix/versioning/versions` |
| Get version | GET | `/api/v1/price-matrix/versioning/versions/{id}` |
| Update version | PUT | `/api/v1/price-matrix/versioning/versions/{id}` |
| Delete version | DELETE | `/api/v1/price-matrix/versioning/versions/{id}` |
| Submit for approval | POST | `/api/v1/price-matrix/versioning/versions/{id}/submit` |
| Approve version | POST | `/api/v1/price-matrix/versioning/versions/{id}/approve` |
| Reject version | POST | `/api/v1/price-matrix/versioning/versions/{id}/reject` |
| Activate version | POST | `/api/v1/price-matrix/versioning/versions/{id}/activate` |
| Compare versions | POST | `/api/v1/price-matrix/versioning/versions/compare` |
| Rollback | POST | `/api/v1/price-matrix/versioning/versions/{id}/rollback` |
| Get history | GET | `/api/v1/price-matrix/versioning/matrices/{id}/history` |
| Get changes | GET | `/api/v1/price-matrix/versioning/versions/{id}/changes` |

## Version Status Flow

```
DRAFT → PENDING → APPROVED → ACTIVE → ARCHIVED
              ↓
          REJECTED
```

## Common Operations

### Get Active Version

```python
active = service.get_active_version(matrix_id=1)
```

### Get All Versions

```python
versions, count = service.get_versions_by_matrix(
    matrix_id=1,
    status=VersionStatus.APPROVED,
    limit=100,
    offset=0
)
```

### Get Version History

```python
history = service.get_version_history(matrix_id=1, limit=50)
```

### Get Version Changes

```python
changes, count = service.get_version_changes(version_id=1)
```

## Migration Rules

### Rename Key

```json
{
  "rename_currency": {
    "type": "rename_key",
    "old_key": "currency",
    "new_key": "currency_code"
  }
}
```

### Add Default Value

```json
{
  "add_timestamp": {
    "type": "add_default",
    "key": "created_at",
    "default": "2024-01-01T00:00:00Z"
  }
}
```

### Remove Key

```json
{
  "remove_old_field": {
    "type": "remove_key",
    "key": "deprecated_field"
  }
}
```

## Error Handling

```python
try:
    version = service.create_version(data, user_id)
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

✅ **DO:**
- Use descriptive version names
- Include detailed descriptions
- Always use approval workflow for production
- Create backups before rollback
- Compare versions before activation

❌ **DON'T:**
- Skip approval workflow
- Use generic version names
- Rollback without backup
- Activate without comparison
- Delete active versions

## Permissions

| Operation | Required Permission |
|-----------|-------------------|
| Create version | `price_matrix.version.create` |
| Update version | `price_matrix.version.update` |
| Delete version | `price_matrix.version.delete` |
| Approve version | `price_matrix.version.approve` |
| Activate version | `price_matrix.version.activate` |
| Rollback | `price_matrix.version.rollback` |

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Cannot update version in approved status" | Create new version based on approved one |
| "Can only activate approved versions" | Submit and approve version first |
| "No active version to rollback from" | Activate a version before rollback |
| "Versions must belong to the same matrix" | Ensure both versions are from same matrix |

## Related Commands

```bash
# Run migration
python backend/migrations/add_price_matrix_versioning_tables.py

# Run tests
pytest backend/tests/test_price_matrix_versioning.py -v

# Check version status
curl -X GET http://localhost:8000/api/v1/price-matrix/versioning/versions/1
```

## Support

For detailed documentation, see:
- [Complete Versioning Guide](./PRICE_MATRIX_VERSIONING_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Price Matrix System Guide](./PRICE_MATRIX_SYSTEM_GUIDE.md)
