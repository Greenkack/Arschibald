# Module Features Quick Reference

## Module Keys

```python
# Main Modules
SOLAR_CALCULATOR = "module.solar_calculator"
HEAT_PUMP = "module.heat_pump"
PRICE_MATRIX = "module.price_matrix"
PDF_GENERATION = "module.pdf_generation"
CRM = "module.crm"
VISUALIZATION_3D = "module.3d_visualization"
```

## Quick Start

### Backend

```python
from backend.services.module_feature_service import ModuleFeatureService

# Initialize (run once)
service = ModuleFeatureService(db)
service.initialize_module_features()

# Check module
is_enabled = service.is_module_enabled(
    ModuleFeatureService.SOLAR_CALCULATOR,
    user_id=123
)

# Check sub-feature
is_enabled = service.is_sub_feature_enabled(
    ModuleFeatureService.SOLAR_CALCULATOR,
    ModuleFeatureService.SOLAR_SHADING_ANALYSIS,
    user_id=123
)

# Toggle module
service.enable_module(ModuleFeatureService.SOLAR_CALCULATOR)
service.disable_module(ModuleFeatureService.SOLAR_CALCULATOR)
```

### Frontend

```typescript
import { useModuleFeatures, MODULE_KEYS } from '@/hooks/useModuleFeatures';

function MyComponent() {
  const { isModuleEnabled, isSubFeatureEnabled } = useModuleFeatures();
  
  const solarEnabled = isModuleEnabled('solar_calculator');
  const shadingEnabled = isSubFeatureEnabled(
    'solar_calculator',
    'module.solar_calculator.shading_analysis'
  );
  
  return solarEnabled ? <SolarCalculator /> : null;
}
```

## API Endpoints

```bash
# Initialize
POST /api/v1/module-features/initialize

# Get status
GET /api/v1/module-features/status

# Toggle module
POST /api/v1/module-features/toggle-module
{
  "module_key": "module.solar_calculator",
  "enabled": true
}

# Toggle sub-feature
POST /api/v1/module-features/toggle-sub-feature
{
  "sub_feature_key": "module.solar_calculator.shading_analysis",
  "enabled": true
}

# Check module
GET /api/v1/module-features/check-module/{module_key}

# Check sub-feature
GET /api/v1/module-features/check-sub-feature/{module_key}/{sub_feature_key}
```

## Module Structure

```
Solar Calculator (module.solar_calculator)
├── Basic Calculation (module.solar_calculator.basic_calculation)
├── Advanced Calculation (module.solar_calculator.advanced_calculation)
├── Shading Analysis (module.solar_calculator.shading_analysis)
├── Battery Storage (module.solar_calculator.battery_storage)
├── Financial Analysis (module.solar_calculator.financial_analysis)
├── Weather Integration (module.solar_calculator.weather_integration)
└── Monitoring (module.solar_calculator.monitoring)

Heat Pump (module.heat_pump)
├── Basic Calculation (module.heat_pump.basic_calculation)
├── Advanced Calculation (module.heat_pump.advanced_calculation)
├── Dynamic Tariff (module.heat_pump.dynamic_tariff)
├── PV Integration (module.heat_pump.pv_integration)
└── Environmental Analysis (module.heat_pump.environmental_analysis)

Price Matrix (module.price_matrix)
├── Upload (module.price_matrix.upload)
├── Formula Engine (module.price_matrix.formula_engine)
├── Validation (module.price_matrix.validation)
├── Versioning (module.price_matrix.versioning)
├── Extras (module.price_matrix.extras)
└── Multi-Currency (module.price_matrix.multi_currency)

PDF Generation (module.pdf_generation)
├── Basic (module.pdf_generation.basic)
├── Advanced Templates (module.pdf_generation.advanced_templates)
├── Multi-Language (module.pdf_generation.multi_language)
├── Custom Branding (module.pdf_generation.custom_branding)
├── Batch Processing (module.pdf_generation.batch_processing)
└── Chart Integration (module.pdf_generation.chart_integration)

CRM (module.crm)
├── Customer Management (module.crm.customer_management)
├── Offer Tracking (module.crm.offer_tracking)
├── Task Management (module.crm.task_management)
├── Communication (module.crm.communication)
├── Lead Scoring (module.crm.lead_scoring)
├── Forecasting (module.crm.forecasting)
└── Contract Management (module.crm.contract_management)

3D Visualization (module.3d_visualization)
├── Basic (module.3d_visualization.basic)
├── Advanced Rendering (module.3d_visualization.advanced_rendering)
├── Auto Placement (module.3d_visualization.auto_placement)
├── Collision Detection (module.3d_visualization.collision_detection)
├── Animation (module.3d_visualization.animation)
├── Export (module.3d_visualization.export)
└── Mounting System (module.3d_visualization.mounting_system)
```

## Common Patterns

### Protect API Endpoint

```python
@router.get("/solar/calculate")
async def calculate_solar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ModuleFeatureService(db)
    
    if not service.is_module_enabled(
        ModuleFeatureService.SOLAR_CALCULATOR,
        current_user.id
    ):
        raise HTTPException(403, "Module not enabled")
    
    # Proceed with calculation
    ...
```

### Conditional UI Rendering

```typescript
function Dashboard() {
  const { isModuleEnabled } = useModuleFeatures();
  
  return (
    <div>
      {isModuleEnabled('solar_calculator') && <SolarWidget />}
      {isModuleEnabled('heat_pump') && <HeatPumpWidget />}
      {isModuleEnabled('crm') && <CRMWidget />}
    </div>
  );
}
```

### Admin Toggle UI

```typescript
import { ModuleFeatureManager } from '@/components/admin/ModuleFeatureManager';

function AdminModules() {
  return <ModuleFeatureManager />;
}
```

## Default States

**Enabled by Default:**
- All main modules
- All basic calculation features
- All core features (upload, validation, basic generation)

**Disabled by Default:**
- Advanced/experimental features
- External integrations (weather, monitoring)
- Premium features (lead scoring, forecasting, advanced rendering)

## Notes

- Sub-features require parent module to be enabled
- Changes take effect immediately (cached for 5 minutes)
- Only admins can toggle features
- All changes are logged
- Feature checks are user-specific
