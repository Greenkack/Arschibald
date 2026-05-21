# Feature Flag System Guide

## Overview

The Feature Flag System provides a flexible way to control feature availability in the Solar Calculator Pro application. It supports multiple flag types including global, user-based, role-based, and percentage rollout flags.

## Table of Contents

1. [Feature Flag Types](#feature-flag-types)
2. [API Endpoints](#api-endpoints)
3. [Usage Examples](#usage-examples)
4. [Middleware Integration](#middleware-integration)
5. [Best Practices](#best-practices)
6. [Caching](#caching)

## Feature Flag Types

### 1. Global Flags

Global flags are the simplest type - they're either on or off for everyone.

```python
{
    "key": "solar.advanced_features",
    "name": "Advanced Solar Features",
    "enabled": true,
    "flag_type": "global"
}
```

**Use Case**: Enable/disable features for all users at once.

### 2. User-Based Flags

User-based flags are enabled only for specific users.

```python
{
    "key": "beta.new_calculator",
    "name": "New Calculator Beta",
    "enabled": true,
    "flag_type": "user",
    "user_ids": [1, 2, 3]
}
```

**Use Case**: Beta testing with specific users, VIP features.

### 3. Role-Based Flags

Role-based flags are enabled for users with specific roles.

```python
{
    "key": "admin.advanced_settings",
    "name": "Advanced Admin Settings",
    "enabled": true,
    "flag_type": "role",
    "role_ids": [1]  # Admin role
}
```

**Use Case**: Role-specific features, permission-based access.

### 4. Percentage Rollout

Percentage rollout flags enable features for a percentage of users.

```python
{
    "key": "experiment.new_ui",
    "name": "New UI Experiment",
    "enabled": true,
    "flag_type": "percentage",
    "rollout_percentage": 25  # 25% of users
}
```

**Use Case**: Gradual rollouts, A/B testing, canary deployments.

## API Endpoints

### Create Feature Flag

```http
POST /api/v1/feature-flags/
Content-Type: application/json
Authorization: Bearer <token>

{
    "key": "solar.advanced_features",
    "name": "Advanced Solar Features",
    "description": "Enable advanced solar calculation features",
    "enabled": true,
    "flag_type": "global"
}
```

### List Feature Flags

```http
GET /api/v1/feature-flags/?skip=0&limit=100
Authorization: Bearer <token>
```

### Get Feature Flag

```http
GET /api/v1/feature-flags/{flag_id}
Authorization: Bearer <token>
```

### Update Feature Flag

```http
PUT /api/v1/feature-flags/{flag_id}
Content-Type: application/json
Authorization: Bearer <token>

{
    "enabled": false,
    "rollout_percentage": 50
}
```

### Delete Feature Flag

```http
DELETE /api/v1/feature-flags/{flag_id}
Authorization: Bearer <token>
```

### Check Feature Flag

```http
POST /api/v1/feature-flags/check
Content-Type: application/json

{
    "key": "solar.advanced_features",
    "user_id": 123  # Optional
}
```

**Response:**

```json
{
    "key": "solar.advanced_features",
    "enabled": true,
    "reason": "Global flag"
}
```

### Check Multiple Feature Flags

```http
POST /api/v1/feature-flags/check-bulk
Content-Type: application/json

{
    "keys": ["solar.advanced_features", "pdf.new_templates", "crm.forecasting"],
    "user_id": 123  # Optional
}
```

**Response:**

```json
{
    "flags": {
        "solar.advanced_features": true,
        "pdf.new_templates": false,
        "crm.forecasting": true
    }
}
```

## Usage Examples

### Backend Service Usage

```python
from backend.services.feature_flag_service import FeatureFlagService
from backend.core.dependencies import get_db

# In your endpoint
def my_endpoint(db: Session = Depends(get_db)):
    service = FeatureFlagService(db)
    
    # Check if feature is enabled
    result = service.is_feature_enabled("solar.advanced_features", user_id=123)
    
    if result.enabled:
        # Feature is enabled
        return advanced_calculation()
    else:
        # Feature is disabled
        return standard_calculation()
```

### Using the Decorator

```python
from backend.middleware.feature_flag_middleware import require_feature_flag
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/advanced")
@require_feature_flag("solar.advanced_features")
async def advanced_endpoint(request: Request):
    """This endpoint requires the solar.advanced_features flag"""
    return {"message": "Advanced features enabled"}
```

### Frontend Usage

```typescript
// Check feature flag from frontend
const checkFeature = async (key: string) => {
    const response = await api.post('/api/v1/feature-flags/check', {
        key: key
    });
    return response.data.enabled;
};

// Usage in component
const isAdvancedEnabled = await checkFeature('solar.advanced_features');

if (isAdvancedEnabled) {
    // Show advanced features
}
```

### Bulk Check in Frontend

```typescript
// Check multiple features at once
const checkFeatures = async (keys: string[]) => {
    const response = await api.post('/api/v1/feature-flags/check-bulk', {
        keys: keys
    });
    return response.data.flags;
};

// Usage
const features = await checkFeatures([
    'solar.advanced_features',
    'pdf.new_templates',
    'crm.forecasting'
]);

if (features['solar.advanced_features']) {
    // Show advanced solar features
}
```

## Middleware Integration

### Route-Based Feature Flags

Configure middleware to check feature flags for specific routes:

```python
from backend.middleware.feature_flag_middleware import FeatureFlagMiddleware

# In main.py
app.add_middleware(
    FeatureFlagMiddleware,
    route_flags={
        "/api/v1/solar/advanced": "solar.advanced_features",
        "/api/v1/pdf/templates": "pdf.new_templates",
        "/api/v1/crm/forecasting": "crm.forecasting"
    }
)
```

Now any request to these routes will automatically check the feature flag.

## Best Practices

### 1. Naming Conventions

Use a hierarchical naming scheme:

```
<module>.<feature>.<subfeature>

Examples:
- solar.advanced_features
- solar.advanced_features.shading_analysis
- pdf.new_templates
- crm.forecasting.advanced
```

### 2. Feature Flag Lifecycle

1. **Development**: Create flag, set to disabled
2. **Testing**: Enable for specific test users
3. **Beta**: Enable for beta users or small percentage
4. **Rollout**: Gradually increase percentage
5. **Full Release**: Convert to global flag or remove
6. **Cleanup**: Remove flag from code after full rollout

### 3. Documentation

Always document:
- What the flag controls
- When it was created
- Target rollout date
- Cleanup date

### 4. Monitoring

Monitor feature flag usage:
- Track which flags are checked most frequently
- Monitor performance impact
- Track user feedback for flagged features

### 5. Testing

Test both enabled and disabled states:

```python
def test_feature_enabled():
    # Test with feature enabled
    pass

def test_feature_disabled():
    # Test with feature disabled
    pass
```

## Caching

The feature flag system includes built-in caching to reduce database queries.

### Cache Behavior

- Cache TTL: 5 minutes (configurable)
- Cache is cleared on flag updates
- Cache is per-user for user-based and percentage flags
- Cache is global for global flags

### Manual Cache Control

```python
from backend.middleware.feature_flag_middleware import feature_flag_cache

# Clear cache manually
feature_flag_cache.clear()

# Check cache
cached_value = feature_flag_cache.get("solar.advanced_features", user_id=123)
```

## Role Management

### Create Role

```http
POST /api/v1/feature-flags/roles/
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "beta_tester",
    "description": "Beta testing role"
}
```

### Assign Role to Feature Flag

```http
PUT /api/v1/feature-flags/{flag_id}
Content-Type: application/json
Authorization: Bearer <token>

{
    "role_ids": [1, 2, 3]
}
```

## Migration

Run the migration to create feature flag tables:

```bash
cd backend
python migrations/add_feature_flags.py
```

To rollback:

```bash
python migrations/add_feature_flags.py downgrade
```

## Common Patterns

### Gradual Rollout

```python
# Week 1: 10% rollout
update_flag("new.feature", rollout_percentage=10)

# Week 2: 25% rollout
update_flag("new.feature", rollout_percentage=25)

# Week 3: 50% rollout
update_flag("new.feature", rollout_percentage=50)

# Week 4: 100% rollout
update_flag("new.feature", flag_type="global", enabled=True)
```

### A/B Testing

```python
# Create two flags for A/B test
create_flag("experiment.variant_a", rollout_percentage=50)
create_flag("experiment.variant_b", rollout_percentage=50)

# In code
if is_enabled("experiment.variant_a", user_id):
    return variant_a()
elif is_enabled("experiment.variant_b", user_id):
    return variant_b()
else:
    return control()
```

### Beta Program

```python
# Create beta role
create_role("beta_tester")

# Create beta flag
create_flag(
    "beta.new_features",
    flag_type="role",
    role_ids=[beta_tester_role_id]
)

# Assign users to beta role
assign_role_to_user(user_id, beta_tester_role_id)
```

## Troubleshooting

### Flag Not Working

1. Check if flag exists: `GET /api/v1/feature-flags/`
2. Check flag status: `POST /api/v1/feature-flags/check`
3. Clear cache: `feature_flag_cache.clear()`
4. Check user/role associations

### Performance Issues

1. Reduce cache TTL if flags change frequently
2. Use bulk check for multiple flags
3. Consider using middleware for route-based checks
4. Monitor database query performance

### Inconsistent Behavior

1. Ensure cache is cleared after updates
2. Check for race conditions in concurrent updates
3. Verify user ID is passed correctly
4. Check percentage rollout hash consistency

## Security Considerations

1. **Authentication**: Most endpoints require authentication
2. **Authorization**: Only admins should create/update/delete flags
3. **Audit Logging**: Track who creates/modifies flags
4. **Rate Limiting**: Apply rate limits to check endpoints
5. **Input Validation**: All inputs are validated via Pydantic

## Performance Metrics

- Flag check latency: < 10ms (cached)
- Flag check latency: < 50ms (uncached)
- Cache hit rate: > 90%
- Database queries per check: 0-2

## Support

For issues or questions:
- Check logs: `backend/logs/feature_flags.log`
- Review tests: `backend/tests/test_feature_flag_service.py`
- Contact: dev-team@solarcalculator.com
