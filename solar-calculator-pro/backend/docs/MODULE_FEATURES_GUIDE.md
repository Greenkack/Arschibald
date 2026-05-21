# Module-Level Feature Toggles Guide

## Overview

The Module Feature system provides granular control over major application modules and their sub-features. This allows administrators to enable or disable entire modules or specific features within modules.

## Architecture

### Module Hierarchy

```
Module (e.g., Solar Calculator)
├── Sub-Feature 1 (e.g., Basic Calculation)
├── Sub-Feature 2 (e.g., Advanced Calculation)
├── Sub-Feature 3 (e.g., Shading Analysis)
└── ...
```

**Important**: A sub-feature is only active if both the parent module AND the sub-feature are enabled.

## Available Modules

### 1. Solar Calculator (`module.solar_calculator`)

**Sub-Features:**
- `module.solar_calculator.basic_calculation` - Basic solar system calculations
- `module.solar_calculator.advanced_calculation` - Advanced calculations with optimization
- `module.solar_calculator.shading_analysis` - Shading analysis and loss calculations
- `module.solar_calculator.battery_storage` - Battery storage sizing and ROI
- `module.solar_calculator.financial_analysis` - Detailed financial projections
- `module.solar_calculator.weather_integration` - Weather data integration
- `module.solar_calculator.monitoring` - Real-time monitoring integration

### 2. Heat Pump (`module.heat_pump`)

**Sub-Features:**
- `module.heat_pump.basic_calculation` - Basic heat pump sizing
- `module.heat_pump.advanced_calculation` - Advanced calculations
- `module.heat_pump.dynamic_tariff` - Dynamic tariff optimization
- `module.heat_pump.pv_integration` - Combined PV + Heat Pump optimization
- `module.heat_pump.environmental_analysis` - Environmental impact analysis

### 3. Price Matrix (`module.price_matrix`)

**Sub-Features:**
- `module.price_matrix.upload` - Upload and manage price matrices
- `module.price_matrix.formula_engine` - Excel formula engine (INDEX/MATCH)
- `module.price_matrix.validation` - Matrix structure validation
- `module.price_matrix.versioning` - Version control
- `module.price_matrix.extras` - Extras and special products
- `module.price_matrix.multi_currency` - Multi-currency support

### 4. PDF Generation (`module.pdf_generation`)

**Sub-Features:**
- `module.pdf_generation.basic` - Basic PDF generation
- `module.pdf_generation.advanced_templates` - Advanced template system
- `module.pdf_generation.multi_language` - Multi-language support
- `module.pdf_generation.custom_branding` - Custom branding and logos
- `module.pdf_generation.batch_processing` - Batch PDF generation
- `module.pdf_generation.chart_integration` - Chart integration

### 5. CRM (`module.crm`)

**Sub-Features:**
- `module.crm.customer_management` - Customer database management
- `module.crm.offer_tracking` - Offer creation and tracking
- `module.crm.task_management` - Task and activity management
- `module.crm.communication` - Email and communication tracking
- `module.crm.lead_scoring` - Automated lead scoring
- `module.crm.forecasting` - Sales forecasting
- `module.crm.contract_management` - Contract and warranty management

### 6. 3D Visualization (`module.3d_visualization`)

**Sub-Features:**
- `module.3d_visualization.basic` - Basic 3D visualization
- `module.3d_visualization.advanced_rendering` - Photo-realistic rendering
- `module.3d_visualization.auto_placement` - Automatic module placement
- `module.3d_visualization.collision_detection` - Collision detection
- `module.3d_visualization.animation` - 360° animations
- `module.3d_visualization.export` - Export to various formats
- `module.3d_visualization.mounting_system` - Mounting system visualization

## Backend Usage

### Initialize Module Features

```python
from backend.services.module_feature_service import ModuleFeatureService
from backend.core.dependencies import get_db

# Initialize all module features (run once during setup)
db = next(get_db())
service = ModuleFeatureService(db)
results = service.initialize_module_features(created_by=admin_user_id)

print(f"Created: {sum(1 for v in results.values() if v == 'created')}")
print(f"Existing: {sum(1 for v in results.values() if v == 'already_exists')}")
```

### Check Module Status

```python
# Check if a module is enabled
is_enabled = service.is_module_enabled(
    ModuleFeatureService.SOLAR_CALCULATOR,
    user_id=123
)

# Check if a sub-feature is enabled (checks parent module too)
is_enabled = service.is_sub_feature_enabled(
    ModuleFeatureService.SOLAR_CALCULATOR,
    ModuleFeatureService.SOLAR_SHADING_ANALYSIS,
    user_id=123
)

# Get status of all modules
status = service.get_module_status(user_id=123)
```

### Toggle Modules and Sub-Features

```python
# Enable a module
service.enable_module(ModuleFeatureService.SOLAR_CALCULATOR)

# Disable a module
service.disable_module(ModuleFeatureService.SOLAR_CALCULATOR)

# Enable a sub-feature
service.enable_sub_feature(ModuleFeatureService.SOLAR_SHADING_ANALYSIS)

# Disable a sub-feature
service.disable_sub_feature(ModuleFeatureService.SOLAR_SHADING_ANALYSIS)
```

### Use in API Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException
from backend.services.module_feature_service import ModuleFeatureService

router = APIRouter()

@router.get("/solar/calculate")
async def calculate_solar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ModuleFeatureService(db)
    
    # Check if module is enabled
    if not service.is_module_enabled(
        ModuleFeatureService.SOLAR_CALCULATOR,
        current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Solar Calculator module is not enabled"
        )
    
    # Check if sub-feature is enabled
    if not service.is_sub_feature_enabled(
        ModuleFeatureService.SOLAR_CALCULATOR,
        ModuleFeatureService.SOLAR_ADVANCED_CALC,
        current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Advanced calculation feature is not enabled"
        )
    
    # Proceed with calculation
    ...
```

## API Endpoints

### Initialize Features

```http
POST /api/v1/module-features/initialize
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "results": {
    "module.solar_calculator": "created",
    "module.heat_pump": "created",
    ...
  },
  "total": 50,
  "created": 45,
  "existing": 5,
  "errors": 0
}
```

### Get Module Status

```http
GET /api/v1/module-features/status?user_id=123
Authorization: Bearer <token>
```

**Response:**
```json
{
  "modules": {
    "solar_calculator": {
      "enabled": true,
      "sub_features": {
        "module.solar_calculator.basic_calculation": true,
        "module.solar_calculator.advanced_calculation": true,
        "module.solar_calculator.shading_analysis": false,
        ...
      }
    },
    ...
  }
}
```

### Toggle Module

```http
POST /api/v1/module-features/toggle-module
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "module_key": "module.solar_calculator",
  "enabled": true
}
```

### Toggle Sub-Feature

```http
POST /api/v1/module-features/toggle-sub-feature
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "sub_feature_key": "module.solar_calculator.shading_analysis",
  "enabled": true
}
```

### Check Module

```http
GET /api/v1/module-features/check-module/module.solar_calculator?user_id=123
Authorization: Bearer <token>
```

### Check Sub-Feature

```http
GET /api/v1/module-features/check-sub-feature/module.solar_calculator/module.solar_calculator.shading_analysis?user_id=123
Authorization: Bearer <token>
```

## Frontend Usage

### Using Hooks

```typescript
import { useModuleFeatures, MODULE_KEYS, SOLAR_SUB_FEATURES } from '@/hooks/useModuleFeatures';

function MyComponent() {
  const { modules, isModuleEnabled, isSubFeatureEnabled } = useModuleFeatures();
  
  // Check if Solar Calculator module is enabled
  const solarEnabled = isModuleEnabled('solar_calculator');
  
  // Check if shading analysis sub-feature is enabled
  const shadingEnabled = isSubFeatureEnabled(
    'solar_calculator',
    SOLAR_SUB_FEATURES.SHADING_ANALYSIS
  );
  
  return (
    <div>
      {solarEnabled && <SolarCalculator />}
      {shadingEnabled && <ShadingAnalysis />}
    </div>
  );
}
```

### Using Individual Module Hook

```typescript
import { useModule, MODULE_KEYS } from '@/hooks/useModuleFeatures';

function SolarCalculatorPage() {
  const { isEnabled, isLoading } = useModule(MODULE_KEYS.SOLAR_CALCULATOR);
  
  if (isLoading) return <Loading />;
  if (!isEnabled) return <ModuleDisabled />;
  
  return <SolarCalculator />;
}
```

### Using Sub-Feature Hook

```typescript
import { useSubFeature, MODULE_KEYS, SOLAR_SUB_FEATURES } from '@/hooks/useModuleFeatures';

function ShadingAnalysis() {
  const { isEnabled } = useSubFeature(
    MODULE_KEYS.SOLAR_CALCULATOR,
    SOLAR_SUB_FEATURES.SHADING_ANALYSIS
  );
  
  if (!isEnabled) return null;
  
  return <ShadingAnalysisComponent />;
}
```

### Admin UI Component

```typescript
import { ModuleFeatureManager } from '@/components/admin/ModuleFeatureManager';

function AdminPage() {
  return (
    <div>
      <h1>Module Management</h1>
      <ModuleFeatureManager />
    </div>
  );
}
```

## Best Practices

### 1. Always Check Parent Module

When checking sub-features, always ensure the parent module is enabled:

```python
# ✅ Good - checks both module and sub-feature
is_enabled = service.is_sub_feature_enabled(
    module_key,
    sub_feature_key,
    user_id
)

# ❌ Bad - only checks sub-feature
is_enabled = service.feature_service.is_feature_enabled(
    sub_feature_key,
    user_id
)
```

### 2. Use Constants

Always use the predefined constants instead of hardcoding keys:

```python
# ✅ Good
service.is_module_enabled(ModuleFeatureService.SOLAR_CALCULATOR)

# ❌ Bad
service.is_module_enabled("module.solar_calculator")
```

### 3. Handle Disabled Features Gracefully

```python
if not service.is_module_enabled(module_key, user_id):
    return {
        "error": "Module not available",
        "message": "This feature is currently disabled"
    }
```

### 4. Cache Status Checks

The service includes built-in caching, but for frequently accessed features, consider caching at the application level:

```python
# Cache module status for the request
module_status = service.get_module_status(user_id)
# Use cached status for multiple checks
```

## Troubleshooting

### Features Not Showing Up

1. Ensure features are initialized:
   ```bash
   POST /api/v1/module-features/initialize
   ```

2. Check database for feature flags:
   ```sql
   SELECT * FROM feature_flags WHERE key LIKE 'module.%';
   ```

### Sub-Feature Always Disabled

1. Check if parent module is enabled
2. Check if sub-feature itself is enabled
3. Verify user has appropriate permissions

### Cache Issues

Clear the feature flag cache:
```python
service.feature_service._clear_cache()
```

## Migration from Legacy System

When migrating from the Streamlit application:

1. Initialize all module features
2. Enable all modules by default
3. Gradually disable features that are not yet implemented
4. Test each module independently
5. Enable features as they are completed

## Security Considerations

1. Only admins can toggle module features
2. Module status checks are user-specific
3. Feature flags are cached for performance
4. All changes are logged
5. Audit trail is maintained

## Performance

- Feature checks are cached for 5 minutes
- Bulk status checks are optimized
- Database queries use indexes
- Frontend caching reduces API calls

## Related Documentation

- [Feature Flag System Guide](./FEATURE_FLAGS_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Admin Panel Guide](./ADMIN_PANEL_GUIDE.md)
