# Heat Pump Sizing Service - Complete Guide

## Overview

The Heat Pump Sizing Service provides comprehensive calculations for properly sizing heat pumps based on building characteristics, climate conditions, and insulation quality. This service implements industry-standard calculations according to DIN EN 12831.

## Features

### 1. Heat Load Calculations (DIN EN 12831)
- Transmission heat loss through building envelope
- Ventilation heat loss
- Internal and solar heat gains
- Safety margins
- Specific heat load per m²

### 2. Building Insulation Analysis
- U-value analysis for walls, roof, floor, and windows
- Insulation quality scoring (0-100)
- Improvement potential assessment
- Specific recommendations for upgrades
- Annual heat loss calculations

### 3. Climate-Based Sizing
- German climate zone support (4 zones)
- Design outdoor temperatures
- Heating degree days
- Bivalent vs. monovalent operation
- Optimal sizing factors

### 4. Backup Heating Calculations
- Backup heating requirements
- Activation temperature determination
- Annual backup hours estimation
- Cost analysis (electric vs. gas)
- Backup percentage of total heating

### 5. Oversizing/Undersizing Warnings
- Optimal size range determination
- Oversizing impact on efficiency
- Undersizing comfort implications
- Detailed warnings and recommendations
- Efficiency impact calculations

### 6. Seasonal Performance Predictions
- Capacity variations by season
- COP predictions for each season
- Annual SCOP calculation
- Monthly performance profiles
- Capacity degradation analysis

## Installation

```python
from backend.services.heatpump_sizing_service import HeatPumpSizingService

# Initialize service
service = HeatPumpSizingService()
service.initialize()
```

## Usage Examples

### Example 1: Complete Heat Load Calculation

```python
from backend.services.heatpump_sizing_service import (
    HeatPumpSizingService,
    BuildingType,
    InsulationStandard,
    ClimateZone
)

service = HeatPumpSizingService()
service.initialize()

# Calculate heat load
heat_load = service.calculate_heat_load(
    building_area_m2=150.0,
    building_volume_m3=375.0,
    building_type=BuildingType.SINGLE_FAMILY,
    insulation_standard=InsulationStandard.ENEV_2009,
    climate_zone=ClimateZone.ZONE_2,
    indoor_temp_c=20.0,
    air_change_rate_h=0.5
)

print(f"Total Heat Load: {heat_load.total_heat_load_kw:.2f} kW")
print(f"Transmission Loss: {heat_load.transmission_heat_loss_kw:.2f} kW")
print(f"Ventilation Loss: {heat_load.ventilation_heat_loss_kw:.2f} kW")
print(f"Specific Heat Load: {heat_load.specific_heat_load_w_m2:.1f} W/m²")
```

### Example 2: Insulation Analysis

```python
# Analyze building insulation
insulation = service.analyze_insulation(
    building_area_m2=150.0,
    insulation_standard=InsulationStandard.STANDARD,
    climate_zone=ClimateZone.ZONE_2
)

print(f"Insulation Quality Score: {insulation.insulation_quality_score:.1f}/100")
print(f"Average U-Value: {insulation.average_u_value_w_m2k:.2f} W/m²K")
print(f"Improvement Potential: {insulation.improvement_potential_percent:.1f}%")
print("\nRecommendations:")
for rec in insulation.recommended_improvements:
    print(f"  - {rec}")
```

### Example 3: Climate-Based Sizing

```python
# Calculate climate-based sizing
climate_sizing = service.calculate_climate_sizing(
    design_heat_load_kw=10.5,
    climate_zone=ClimateZone.ZONE_2,
    bivalent_operation=True,
    monovalent_limit_c=-7.0
)

print(f"Recommended Capacity: {climate_sizing.recommended_capacity_kw:.2f} kW")
print(f"Bivalent Point: {climate_sizing.bivalent_point_c}°C")
print(f"Sizing Factor: {climate_sizing.sizing_factor:.2f}")
```

### Example 4: Backup Heating Analysis

```python
# Calculate backup heating requirements
backup = service.calculate_backup_heating(
    design_heat_load_kw=10.5,
    heat_pump_capacity_kw=7.5,
    climate_zone=ClimateZone.ZONE_2,
    bivalent_point_c=-5.0,
    backup_type="electric"
)

if backup.backup_required:
    print(f"Backup Capacity Needed: {backup.backup_capacity_kw:.2f} kW")
    print(f"Activation Temperature: {backup.backup_activation_temp_c}°C")
    print(f"Annual Backup Hours: {backup.annual_backup_hours:.0f} hours")
    print(f"Annual Backup Cost: {backup.backup_cost_eur_year:.2f} EUR")
```

### Example 5: Sizing Warnings

```python
# Analyze sizing and get warnings
warnings = service.analyze_sizing_warnings(
    design_heat_load_kw=10.5,
    heat_pump_capacity_kw=12.0,
    climate_zone=ClimateZone.ZONE_2,
    bivalent_operation=True
)

print(f"Oversized: {warnings.is_oversized}")
print(f"Undersized: {warnings.is_undersized}")
print(f"Optimal Range: {warnings.optimal_size_range_kw[0]:.1f} - {warnings.optimal_size_range_kw[1]:.1f} kW")
print("\nWarnings:")
for warning in warnings.warnings:
    print(f"  ⚠ {warning}")
print("\nRecommendations:")
for rec in warnings.recommendations:
    print(f"  → {rec}")
```

### Example 6: Seasonal Performance Prediction

```python
# Predict seasonal performance
seasonal = service.predict_seasonal_performance(
    heat_pump_capacity_kw=8.0,
    climate_zone=ClimateZone.ZONE_2,
    heat_pump_type="air_source",
    flow_temperature_c=35.0
)

print(f"Winter Capacity: {seasonal.winter_capacity_kw:.2f} kW (COP: {seasonal.winter_cop:.2f})")
print(f"Spring Capacity: {seasonal.spring_capacity_kw:.2f} kW (COP: {seasonal.spring_cop:.2f})")
print(f"Summer Capacity: {seasonal.summer_capacity_kw:.2f} kW (COP: {seasonal.summer_cop:.2f})")
print(f"Autumn Capacity: {seasonal.autumn_capacity_kw:.2f} kW (COP: {seasonal.autumn_cop:.2f})")
print(f"Annual SCOP: {seasonal.annual_scop:.2f}")
print(f"Capacity Degradation: {seasonal.capacity_degradation_percent:.1f}%")
```

## Data Models

### HeatLoadCalculation
```python
@dataclass
class HeatLoadCalculation:
    design_heat_load_kw: float
    transmission_heat_loss_kw: float
    ventilation_heat_loss_kw: float
    heat_gain_kw: float
    safety_margin_kw: float
    total_heat_load_kw: float
    specific_heat_load_w_m2: float
    calculation_method: str
    design_outdoor_temp_c: float
    design_indoor_temp_c: float
```

### InsulationAnalysis
```python
@dataclass
class InsulationAnalysis:
    u_value_walls_w_m2k: float
    u_value_roof_w_m2k: float
    u_value_floor_w_m2k: float
    u_value_windows_w_m2k: float
    average_u_value_w_m2k: float
    insulation_quality_score: float  # 0-100
    improvement_potential_percent: float
    recommended_improvements: List[str]
    annual_heat_loss_kwh: float
```

### ClimateSizing
```python
@dataclass
class ClimateSizing:
    climate_zone: ClimateZone
    design_outdoor_temp_c: float
    average_winter_temp_c: float
    heating_degree_days: float
    bivalent_point_c: float
    recommended_capacity_kw: float
    capacity_at_bivalent_kw: float
    monovalent_limit_c: float
    sizing_factor: float
```

## Enumerations

### BuildingType
- `SINGLE_FAMILY`: Single family house
- `MULTI_FAMILY`: Multi-family building
- `APARTMENT`: Apartment
- `COMMERCIAL`: Commercial building

### InsulationStandard
- `OLD_BUILDING`: Before 1977
- `STANDARD`: 1977-2002
- `ENEV_2009`: EnEV 2009
- `ENEV_2014`: EnEV 2014
- `KFW_55`: KfW 55
- `KFW_40`: KfW 40
- `PASSIVE_HOUSE`: Passive house

### ClimateZone (Germany)
- `ZONE_1`: Coastal (mild) - Design temp: -10°C
- `ZONE_2`: Lowlands - Design temp: -12°C
- `ZONE_3`: Central Germany - Design temp: -14°C
- `ZONE_4`: Mountains (cold) - Design temp: -16°C

## Technical Details

### Heat Load Calculation Method (DIN EN 12831)

The service implements the standard DIN EN 12831 calculation method:

1. **Transmission Heat Loss (Q_T)**:
   ```
   Q_T = Σ(A × U × ΔT)
   ```
   Where:
   - A = Surface area (m²)
   - U = U-value (W/m²K)
   - ΔT = Temperature difference (K)

2. **Ventilation Heat Loss (Q_V)**:
   ```
   Q_V = V × n × ρ × c × ΔT / 3600
   ```
   Where:
   - V = Building volume (m³)
   - n = Air change rate (1/h)
   - ρ = Air density (1.2 kg/m³)
   - c = Specific heat capacity (1005 J/kg·K)

3. **Total Heat Load**:
   ```
   Q_total = Q_T + Q_V - Q_gains + Q_safety
   ```

### U-Value Standards

The service includes U-value standards for different insulation levels:

| Standard | Walls | Roof | Floor | Windows |
|----------|-------|------|-------|---------|
| Old Building | 1.4 | 1.2 | 1.0 | 3.0 |
| Standard | 0.9 | 0.8 | 0.7 | 2.0 |
| EnEV 2009 | 0.35 | 0.24 | 0.35 | 1.3 |
| EnEV 2014 | 0.28 | 0.20 | 0.28 | 1.1 |
| KfW 55 | 0.20 | 0.14 | 0.20 | 0.9 |
| KfW 40 | 0.15 | 0.12 | 0.15 | 0.8 |
| Passive House | 0.10 | 0.10 | 0.10 | 0.6 |

### Climate Data

Design outdoor temperatures and heating degree days for German climate zones:

| Zone | Region | Design Temp | Heating Degree Days |
|------|--------|-------------|---------------------|
| 1 | Coastal | -10°C | 3000 |
| 2 | Lowlands | -12°C | 3300 |
| 3 | Central | -14°C | 3600 |
| 4 | Mountains | -16°C | 4000 |

## Best Practices

### 1. Sizing Strategy
- **Bivalent Operation**: Size for 60-80% of design load
- **Monovalent Operation**: Size for 100-110% of design load
- Avoid oversizing >20% to prevent cycling
- Avoid undersizing >15% to ensure comfort

### 2. Insulation First
- Always analyze insulation before sizing
- Improve insulation to reduce heat load
- Target at least EnEV 2014 standard
- Windows are often the weakest point

### 3. Climate Considerations
- Use correct climate zone for location
- Consider bivalent point (-5°C to -7°C typical)
- Account for backup heating in cold climates
- Verify design temperatures with local data

### 4. Backup Heating
- Required when HP capacity < design load
- Electric backup: simple but expensive
- Gas backup: more economical for frequent use
- Aim for <10% backup heating percentage

### 5. Performance Monitoring
- Track actual vs. predicted performance
- Monitor seasonal COP variations
- Check capacity at different temperatures
- Adjust sizing for future installations

## Error Handling

The service includes comprehensive error handling:

```python
try:
    heat_load = service.calculate_heat_load(...)
except Exception as e:
    print(f"Calculation failed: {e}")
    # Service logs error automatically
```

All methods are decorated with:
- `@log_service_call`: Automatic logging
- `@handle_service_errors`: Error wrapping and handling

## Performance

- All calculations are optimized for speed
- Results can be cached for repeated queries
- Typical calculation time: <10ms
- Suitable for real-time sizing tools

## Integration

### With Heat Pump Advanced Service

```python
from backend.services.heatpump_sizing_service import HeatPumpSizingService
from backend.services.heatpump_advanced_service import HeatPumpAdvancedService

sizing_service = HeatPumpSizingService()
advanced_service = HeatPumpAdvancedService()

# Calculate sizing
heat_load = sizing_service.calculate_heat_load(...)
climate_sizing = sizing_service.calculate_climate_sizing(...)

# Use sizing for advanced calculations
cop_result = advanced_service.calculate_cop(
    heat_pump_type=HeatPumpType.AIR_SOURCE,
    outdoor_temp_c=climate_sizing.design_outdoor_temp_c,
    ...
)
```

## Support

For questions or issues:
- Check the example usage above
- Review the inline code documentation
- Contact the development team

## Version History

- **v1.0.0** (2024-01): Initial release
  - Heat load calculations (DIN EN 12831)
  - Insulation analysis
  - Climate-based sizing
  - Backup heating calculations
  - Sizing warnings
  - Seasonal predictions
