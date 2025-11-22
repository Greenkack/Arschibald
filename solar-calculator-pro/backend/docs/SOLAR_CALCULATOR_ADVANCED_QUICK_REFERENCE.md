# Solar Calculator Advanced Service - Quick Reference

## Import

```python
from backend.services.solar_calculator_advanced_service import get_advanced_solar_service

service = get_advanced_solar_service()
```

## Calculation Variants

### Standard
```python
result = service.calculate_standard(
    roof_area_m2=50.0, latitude=51.5, longitude=10.0,
    orientation=0.0, tilt=30.0, module_power_w=400.0,
    annual_consumption_kwh=4000.0
)
```

### Premium
```python
result = service.calculate_premium(
    roof_area_m2=50.0, latitude=51.5, longitude=10.0,
    orientation=0.0, tilt=30.0, module_power_w=400.0,
    annual_consumption_kwh=4000.0,
    include_shading_analysis=True, include_battery=True
)
```

### Custom
```python
result = service.calculate_custom({
    "roof_area_m2": 50.0, "latitude": 51.5,
    "system_efficiency": 0.87, "degradation_rate_percent": 0.4
})
```

## Module Placement
```python
placements = service.optimize_module_placement(
    roof_area_m2=50.0, roof_length_m=10.0, roof_width_m=5.0,
    module_length_m=1.7, module_width_m=1.0,
    orientation=0.0, tilt=30.0, obstacles=[]
)
```

## Shading Analysis
```python
shading = service.analyze_shading(
    latitude=51.5, longitude=10.0, orientation=0.0, tilt=30.0,
    roof_area_m2=50.0, obstacles=[...]
)
```

## Production Forecast
```python
forecast = service.forecast_energy_production(
    system_size_kwp=10.0, latitude=51.5, longitude=10.0,
    orientation=0.0, tilt=30.0, years=25
)
```

## Battery Analysis
```python
battery = service.analyze_battery_storage(
    annual_production_kwh=12000.0, annual_consumption_kwh=4000.0,
    battery_capacity_kwh=10.0
)
```

## Grid Feed-In
```python
grid = service.analyze_grid_feed_in(
    annual_production_kwh=12000.0, annual_consumption_kwh=4000.0,
    annual_self_consumption_kwh=3000.0, system_size_kwp=10.0
)
```

## ROI/NPV
```python
roi = service.calculate_roi_npv(
    initial_investment_eur=15000.0, annual_production_kwh=12000.0,
    annual_self_consumption_kwh=3000.0, annual_feed_in_kwh=9000.0
)
```

## Key Results

### Standard/Premium/Custom
- `system_size_kwp`: System size in kWp
- `module_count`: Number of modules
- `annual_production_kwh`: Annual production
- `self_consumption_rate_percent`: Self-consumption rate

### Shading
- `overall_shading_level`: NONE/MINIMAL/MODERATE/HEAVY
- `annual_shading_loss_percent`: Annual loss percentage
- `recommendations`: List of recommendations

### Battery
- `optimal_capacity_kwh`: Optimal battery size
- `annual_cycles`: Annual charge/discharge cycles
- `self_consumption_increase_percent`: Increase in self-consumption
- `roi_years`: Battery ROI in years

### Grid
- `annual_feed_in_kwh`: Annual feed-in energy
- `annual_feed_in_revenue_eur`: Annual revenue
- `curtailment_losses_kwh`: Curtailment losses
- `grid_stability_score`: Stability score (0-100)

### ROI
- `payback_period_years`: Payback period
- `net_present_value_eur`: NPV
- `internal_rate_of_return_percent`: IRR
- `profitability_index`: Profitability index

## Enums

### CalculationVariant
- `STANDARD`: Basic calculation
- `PREMIUM`: With shading and battery
- `CUSTOM`: Fully customizable

### ShadingLevel
- `NONE`: < 5% loss
- `MINIMAL`: 5-15% loss
- `MODERATE`: 15-30% loss
- `HEAVY`: > 30% loss
