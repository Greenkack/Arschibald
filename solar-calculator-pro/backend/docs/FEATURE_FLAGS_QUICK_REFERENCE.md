# Feature Flags Quick Reference

## Quick Start

### 1. Create a Feature Flag

```bash
curl -X POST http://localhost:8000/api/v1/feature-flags/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "my.feature",
    "name": "My Feature",
    "enabled": true,
    "flag_type": "global"
  }'
```

### 2. Check if Feature is Enabled

```bash
curl -X POST http://localhost:8000/api/v1/feature-flags/check \
  -H "Content-Type: application/json" \
  -d '{
    "key": "my.feature"
  }'
```

### 3. Use in Code

```python
from backend.services.feature_flag_service import FeatureFlagService

service = FeatureFlagService(db)
result = service.is_feature_enabled("my.feature", user_id=123)

if result.enabled:
    # Feature is enabled
    pass
```

## Flag Types Cheat Sheet

| Type | Use Case | Example |
|------|----------|---------|
| `global` | All users | Feature rollout to everyone |
| `user` | Specific users | Beta testing, VIP features |
| `role` | User roles | Admin-only features |
| `percentage` | Gradual rollout | A/B testing, canary deployment |

## Common Commands

### List All Flags

```bash
curl http://localhost:8000/api/v1/feature-flags/ \
  -H "Authorization: Bearer <token>"
```

### Enable a Flag

```bash
curl -X PUT http://localhost:8000/api/v1/feature-flags/{id} \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### Disable a Flag

```bash
curl -X PUT http://localhost:8000/api/v1/feature-flags/{id} \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Update Rollout Percentage

```bash
curl -X PUT http://localhost:8000/api/v1/feature-flags/{id} \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"rollout_percentage": 50}'
```

### Delete a Flag

```bash
curl -X DELETE http://localhost:8000/api/v1/feature-flags/{id} \
  -H "Authorization: Bearer <token>"
```

## Code Snippets

### Backend: Check Feature

```python
from backend.services.feature_flag_service import FeatureFlagService

service = FeatureFlagService(db)
result = service.is_feature_enabled("solar.advanced", user_id=123)

if result.enabled:
    return advanced_calculation()
else:
    return standard_calculation()
```

### Backend: Decorator

```python
from backend.middleware.feature_flag_middleware import require_feature_flag

@router.get("/advanced")
@require_feature_flag("solar.advanced")
async def advanced_endpoint(request: Request):
    return {"message": "Advanced features"}
```

### Frontend: Check Feature

```typescript
const response = await api.post('/api/v1/feature-flags/check', {
    key: 'solar.advanced'
});

if (response.data.enabled) {
    // Show advanced features
}
```

### Frontend: Bulk Check

```typescript
const response = await api.post('/api/v1/feature-flags/check-bulk', {
    keys: ['solar.advanced', 'pdf.templates', 'crm.forecasting']
});

const flags = response.data.flags;
// flags = { 'solar.advanced': true, 'pdf.templates': false, ... }
```

## Naming Convention

```
<module>.<feature>.<subfeature>

Examples:
✅ solar.advanced_features
✅ solar.advanced_features.shading
✅ pdf.new_templates
✅ crm.forecasting.advanced

❌ SolarAdvanced
❌ new-feature
❌ feature_1
```

## Flag Lifecycle

1. **Create** → Disabled, no users
2. **Test** → Enabled for test users
3. **Beta** → Enabled for beta users/roles
4. **Rollout** → Percentage: 10% → 25% → 50% → 100%
5. **Stable** → Global flag, enabled
6. **Cleanup** → Remove from code, delete flag

## Database Migration

```bash
# Create tables
python backend/migrations/add_feature_flags.py

# Rollback
python backend/migrations/add_feature_flags.py downgrade
```

## Testing

```python
# Test enabled state
def test_feature_enabled():
    flag = create_flag("test.feature", enabled=True)
    result = service.is_feature_enabled("test.feature")
    assert result.enabled is True

# Test disabled state
def test_feature_disabled():
    flag = create_flag("test.feature", enabled=False)
    result = service.is_feature_enabled("test.feature")
    assert result.enabled is False
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Flag not working | Check if flag exists, verify enabled status |
| Inconsistent behavior | Clear cache: `feature_flag_cache.clear()` |
| Performance slow | Use bulk check, enable caching |
| 403 Forbidden | Check user has required role/permission |
| 404 Not Found | Verify flag key is correct (lowercase) |

## Cache Control

```python
from backend.middleware.feature_flag_middleware import feature_flag_cache

# Clear all cache
feature_flag_cache.clear()

# Check cache
value = feature_flag_cache.get("my.feature", user_id=123)

# Set cache
feature_flag_cache.set("my.feature", True, user_id=123)
```

## Middleware Setup

```python
from backend.middleware.feature_flag_middleware import FeatureFlagMiddleware

app.add_middleware(
    FeatureFlagMiddleware,
    route_flags={
        "/api/v1/solar/advanced": "solar.advanced_features",
        "/api/v1/pdf/templates": "pdf.new_templates"
    }
)
```

## Role Management

```bash
# Create role
curl -X POST http://localhost:8000/api/v1/feature-flags/roles/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "beta_tester", "description": "Beta testers"}'

# List roles
curl http://localhost:8000/api/v1/feature-flags/roles/ \
  -H "Authorization: Bearer <token>"
```

## Environment Variables

```bash
# Database URL
DATABASE_URL=sqlite:///./solar_calculator.db

# Cache TTL (seconds)
FEATURE_FLAG_CACHE_TTL=300
```

## API Response Examples

### Check Response

```json
{
    "key": "solar.advanced",
    "enabled": true,
    "reason": "Global flag"
}
```

### Bulk Check Response

```json
{
    "flags": {
        "solar.advanced": true,
        "pdf.templates": false,
        "crm.forecasting": true
    }
}
```

### Flag Response

```json
{
    "id": 1,
    "key": "solar.advanced",
    "name": "Advanced Solar Features",
    "description": "Enable advanced solar calculations",
    "enabled": true,
    "flag_type": "global",
    "rollout_percentage": 0,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "created_by": 1,
    "user_ids": [],
    "role_ids": []
}
```

## Performance Tips

1. **Use bulk check** for multiple flags
2. **Enable caching** (default: 5 minutes)
3. **Use middleware** for route-based checks
4. **Minimize flag checks** in hot paths
5. **Monitor cache hit rate** (target: >90%)

## Security Checklist

- ✅ Require authentication for management endpoints
- ✅ Restrict create/update/delete to admins
- ✅ Validate all inputs
- ✅ Apply rate limiting
- ✅ Audit flag changes
- ✅ Use HTTPS in production

## Common Patterns

### Gradual Rollout

```python
# Week 1: 10%
update_flag("new.feature", rollout_percentage=10)

# Week 2: 25%
update_flag("new.feature", rollout_percentage=25)

# Week 3: 50%
update_flag("new.feature", rollout_percentage=50)

# Week 4: 100%
update_flag("new.feature", flag_type="global", enabled=True)
```

### A/B Testing

```python
if is_enabled("experiment.variant_a", user_id):
    return variant_a()
elif is_enabled("experiment.variant_b", user_id):
    return variant_b()
else:
    return control()
```

### Beta Program

```python
# Create beta role and flag
create_role("beta_tester")
create_flag("beta.features", flag_type="role", role_ids=[role_id])

# Assign users to beta
assign_role_to_user(user_id, role_id)
```

## Support

- **Documentation**: `/backend/docs/FEATURE_FLAGS_GUIDE.md`
- **Tests**: `/backend/tests/test_feature_flag_service.py`
- **Logs**: `/backend/logs/feature_flags.log`
