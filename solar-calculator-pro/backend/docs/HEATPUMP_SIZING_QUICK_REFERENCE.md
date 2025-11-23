# Heat Pump Sizing Service - Quick Reference

## Quick Start

```python
from backend.services.heatpump_sizing_service import (
    HeatPumpSizingService,
    BuildingType,
    InsulationStandard,
    ClimateZone
)

service = HeatPumpSizingService()
service.initialize()
```

## Core Methods

### 1. Calculate Heat Load
```python
heat_load = service.calculate_heat_load(
    building_area_m2=150.0,
    building_volume_m3=375.0,
    building_type=BuildingType.SINGLE_FAMILY,
    insulation_standard=InsulationStandard.ENEV_2009,
    climate_zone=ClimateZone.ZONE_2
)
# Returns: HeatLoadCalculation
```

### 2. Analyze Insulation
```python
insulation = service.analyze_insulation(
    building_area_m2=150.0,
    insulation_standard=InsulationStandard.STANDARD,
    climate_zone=ClimateZone.ZONE_2
)
# Returns: InsulationAnalysis
```

### 3. Climate-Based Sizing
```python
sizing = service.calculate_climate_sizing(
    design_heat_load_kw=10.5,
    climate_zone=ClimateZone.ZONE_2,
    bivalent_operation=True
)
# Returns: ClimateSizing
```

### 4. Backup Heating
```python
backup = service.calculate_backup_heating(
    design_heat_load_kw=10.5,
    heat_pump_capacity_kw=7.5,
    climate_zone=ClimateZone.ZONE_2
)
# Returns: BackupHeating
```

### 5. Sizing Warnings
```python
warnings = service.analyze_sizing_warnings(
    design_heat_load_kw=10.5,
    heat_pump_capacity_kw=12.0,
    climate_zone=ClimateZone.ZONE_2
)
# Returns: SizingWarnings
```

### 6. Seasonal Performance
```python
seasonal = service.predict_seasonal_performance(
    heat_pump_capacity_kw=8.0,
    climate_zone=ClimateZone.ZONE_2,
    heat_pump_type="air_source"
)
# Returns: SeasonalPrediction
```

## Enums

### BuildingType
- `SINGLE_FAMILY`, `MULTI_FAMILY`, `APARTMENT`, `COMMERCIAL`

### InsulationStandard
- `OLD_BUILDING`, `STANDARD`, `ENEV_2009`, `ENEV_2014`
- `KFW_55`, `KFW_40`, `PASSIVE_HOUSE`

### ClimateZone
- `ZONE_1` (Coastal, -10°C)
- `ZONE_2` (Lowlands, -12°C)
- `ZONE_3` (Central, -14°C)
- `ZONE_4` (Mountains, -16°C)

## Key Results

### Heat Load
- `total_heat_load_kw`: Total heat load with safety margin
- `specific_heat_load_w_m2`: Heat load per m²
- `transmission_heat_loss_kw`: Heat loss through envelope
- `ventilation_heat_loss_kw`: Heat loss through ventilation

### Insulation
- `insulation_quality_score`: 0-100 score
- `average_u_value_w_m2k`: Average U-value
- `improvement_potential_percent`: Potential improvement
- `recommended_improvements`: List of recommendations

### Sizing
- `recommended_capacity_kw`: Recommended HP capacity
- `bivalent_point_c`: Bivalent point temperature
- `sizing_factor`: Sizing factor (0.6-1.1)

### Warnings
- `is_oversized`: Boolean
- `is_undersized`: Boolean
- `warnings`: List of warning messages
- `recommendations`: List of recommendations
- `optimal_size_range_kw`: (min, max) tuple

## Sizing Rules

### Bivalent Operation
- Size for 60-80% of design load
- Backup heating covers peak demand
- More efficient, lower cost

### Monovalent Operation
- Size for 100-110% of design load
- No backup heating needed
- Higher capacity, higher cost

## U-Value Quick Reference

| Standard | Walls | Roof | Floor | Windows |
|----------|-------|------|-------|---------|
| Old | 1.4 | 1.2 | 1.0 | 3.0 |
| Standard | 0.9 | 0.8 | 0.7 | 2.0 |
| EnEV 2009 | 0.35 | 0.24 | 0.35 | 1.3 |
| KfW 55 | 0.20 | 0.14 | 0.20 | 0.9 |
| Passive | 0.10 | 0.10 | 0.10 | 0.6 |

## Common Patterns

### Complete Sizing Workflow
```python
# 1. Calculate heat load
heat_load = service.calculate_heat_load(...)

# 2. Analyze insulation
insulation = service.analyze_insulation(...)

# 3. Determine sizing
sizing = service.calculate_climate_sizing(
    design_heat_load_kw=heat_load.total_heat_load_kw,
    ...
)

# 4. Check for backup needs
backup = service.calculate_backup_heating(
    design_heat_load_kw=heat_load.total_heat_load_kw,
    heat_pump_capacity_kw=sizing.recommended_capacity_kw,
    ...
)

# 5. Validate sizing
warnings = service.analyze_sizing_warnings(
    design_heat_load_kw=heat_load.total_heat_load_kw,
    heat_pump_capacity_kw=sizing.recommended_capacity_kw,
    ...
)

# 6. Predict performance
seasonal = service.predict_seasonal_performance(
    heat_pump_capacity_kw=sizing.recommended_capacity_kw,
    ...
)
```

## Tips

✅ **DO:**
- Always calculate heat load first
- Analyze insulation before sizing
- Use bivalent operation for cost savings
- Check sizing warnings
- Predict seasonal performance

❌ **DON'T:**
- Oversize by more than 20%
- Undersize by more than 15%
- Ignore insulation improvements
- Skip backup heating analysis
- Forget climate zone selection

## Error Handling

All methods include automatic error handling and logging:
```python
try:
    result = service.calculate_heat_load(...)
except Exception as e:
    # Error is logged automatically
    print(f"Error: {e}")
```

## Performance

- Calculation time: <10ms per method
- Suitable for real-time applications
- Results can be cached
- No external dependencies

## See Also

- Full Guide: `HEATPUMP_SIZING_GUIDE.md`
- Advanced Service: `HEATPUMP_ADVANCED_SERVICE_GUIDE.md`
- API Documentation: Auto-generated from code
