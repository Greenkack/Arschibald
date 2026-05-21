# Solar Calculator Advanced Service - Complete Guide

## Overview

The Solar Calculator Advanced Service provides comprehensive solar system analysis with advanced features including multiple calculation variants, module placement optimization, shading analysis, weather integration, production forecasting, battery storage optimization, grid feed-in analysis, and detailed financial calculations (ROI, NPV, IRR).

## Features

### 1. Calculation Variants

#### Standard Calculation
Basic solar system sizing with essential calculations.

```python
from backend.services.solar_calculator_advanced_service import get_advanced_solar_service

service = get_advanced_solar_service()

result = service.calculate_standard(
    roof_area_m2=50.0,
    latitude=51.5,
    longitude=10.0,
    orientation=0.0,  # South
    tilt=30.0,
    module_power_w=400.0,
    annual_consumption_kwh=4000.0
)

print(f"System size: {result['system_size_kwp']} kWp")
print(f"Annual production: {result['annual_production_kwh']} kWh")
print(f"Self-consumption rate: {result['self_consumption_rate_percent']}%")
```

#### Premium Calculation
Includes shading analysis and battery optimization.

```python
result = service.calculate_premium(
    roof_area_m2=50.0,
    latitude=51.5,
    longitude=10.0,
    orientation=0.0,
    tilt=30.0,
    module_power_w=400.0,
    annual_consumption_kwh=4000.0,
    include_shading_analysis=True,
    include_battery=True,
    battery_capacity_kwh=None  # Auto-optimize
)

print(f"Shading loss: {result['shading_analysis'].annual_shading_loss_percent}%")
print(f"Optimal battery: {result['battery_analysis'].optimal_capacity_kwh} kWh")
```

#### Custom Calculation
Fully customizable parameters for advanced users.

```python
result = service.calculate_custom({
    "roof_area_m2": 50.0,
    "latitude": 51.5,
    "longitude": 10.0,
    "orientation": 0.0,
    "tilt": 30.0,
    "module_power_w": 400.0,
    "annual_consumption_kwh": 4000.0,
    "system_efficiency": 0.87,
    "degradation_rate_percent": 0.4,
    "temperature_coefficient": -0.35,
    "utilization_factor": 0.90
})
```

### 2. Module Placement Optimization

Automatically optimize module placement on roof considering obstacles and spacing requirements.

```python
placements = service.optimize_module_placement(
    roof_area_m2=50.0,
    roof_length_m=10.0,
    roof_width_m=5.0,
    module_length_m=1.7,
    module_width_m=1.0,
    orientation=0.0,
    tilt=30.0,
    obstacles=[
        {
            "x": 5.0,
            "y": 5.0,
            "width": 1.0,
            "length": 1.0,
            "height_m": 2.0,
            "type": "chimney"
        }
    ]
)

print(f"Optimized placement: {len(placements)} modules")
for placement in placements[:5]:
    print(f"  Row {placement.row}, Col {placement.column}: "
          f"({placement.x_position:.2f}, {placement.y_position:.2f})")
```

### 3. Shading Analysis

Comprehensive shading analysis with hourly resolution for entire year.

```python
shading_result = service.analyze_shading(
    latitude=51.5,
    longitude=10.0,
    orientation=0.0,
    tilt=30.0,
    roof_area_m2=50.0,
    obstacles=[
        {
            "height_m": 10.0,
            "distance_m": 15.0,
            "azimuth_deg": 180.0,  # South
            "width_m": 5.0,
            "type": "building"
        }
    ]
)

print(f"Shading level: {shading_result.overall_shading_level}")
print(f"Annual loss: {shading_result.annual_shading_loss_percent:.1f}%")
print(f"Monthly factors: {shading_result.monthly_shading_factors}")
print("Recommendations:")
for rec in shading_result.recommendations:
    print(f"  - {rec}")
```

### 4. Energy Production Forecasting

Forecast energy production over multiple years with degradation.

```python
forecast = service.forecast_energy_production(
    system_size_kwp=10.0,
    latitude=51.5,
    longitude=10.0,
    orientation=0.0,
    tilt=30.0,
    years=25,
    degradation_rate_percent=0.5
)

print(f"Year 1 production: {forecast['first_year_production_kwh']:.0f} kWh")
print(f"Year 25 production: {forecast['last_year_production_kwh']:.0f} kWh")
print(f"Total 25-year production: {forecast['total_production_kwh']:.0f} kWh")
print(f"Average annual: {forecast['average_annual_kwh']:.0f} kWh")
```

### 5. Battery Storage Analysis

Comprehensive battery storage analysis and optimization.

```python
battery_analysis = service.analyze_battery_storage(
    annual_production_kwh=12000.0,
    annual_consumption_kwh=4000.0,
    battery_capacity_kwh=10.0,
    battery_efficiency_percent=90.0,
    depth_of_discharge_percent=90.0
)

print(f"Optimal capacity: {battery_analysis.optimal_capacity_kwh} kWh")
print(f"Daily cycles: {battery_analysis.daily_cycles:.2f}")
print(f"Annual cycles: {battery_analysis.annual_cycles:.0f}")
print(f"Expected lifetime: {battery_analysis.expected_lifetime_years:.1f} years")
print(f"Self-consumption increase: {battery_analysis.self_consumption_increase_percent:.1f}%")
print(f"Autarky increase: {battery_analysis.autarky_increase_percent:.1f}%")
print(f"ROI: {battery_analysis.roi_years:.1f} years")
print(f"Cost-benefit ratio: {battery_analysis.cost_benefit_ratio:.2f}")
```

### 6. Grid Feed-In Analysis

Analyze grid feed-in characteristics and revenue.

```python
grid_analysis = service.analyze_grid_feed_in(
    annual_production_kwh=12000.0,
    annual_consumption_kwh=4000.0,
    annual_self_consumption_kwh=3000.0,
    system_size_kwp=10.0,
    feed_in_tariff_eur_kwh=0.082,
    grid_connection_capacity_kw=7.0
)

print(f"Annual feed-in: {grid_analysis.annual_feed_in_kwh:.0f} kWh")
print(f"Annual revenue: €{grid_analysis.annual_feed_in_revenue_eur:.2f}")
print(f"Peak feed-in power: {grid_analysis.peak_feed_in_power_kw:.1f} kW")
print(f"Grid capacity: {grid_analysis.grid_connection_capacity_kw:.1f} kW")
print(f"Curtailment losses: {grid_analysis.curtailment_losses_kwh:.0f} kWh")
print(f"Grid stability score: {grid_analysis.grid_stability_score:.0f}/100")
```

### 7. ROI and NPV Analysis

Comprehensive financial analysis with ROI, NPV, and IRR calculations.

```python
roi_analysis = service.calculate_roi_npv(
    initial_investment_eur=15000.0,
    annual_production_kwh=12000.0,
    annual_self_consumption_kwh=3000.0,
    annual_feed_in_kwh=9000.0,
    electricity_price_eur_kwh=0.30,
    feed_in_tariff_eur_kwh=0.082,
    electricity_price_increase_percent=3.0,
    discount_rate_percent=4.0,
    years=25,
    degradation_rate_percent=0.5,
    maintenance_cost_annual_eur=200.0
)

print(f"Initial investment: €{roi_analysis.initial_investment_eur:,.2f}")
print(f"Payback period: {roi_analysis.payback_period_years:.1f} years")
print(f"Net Present Value: €{roi_analysis.net_present_value_eur:,.2f}")
print(f"Internal Rate of Return: {roi_analysis.internal_rate_of_return_percent:.2f}%")
print(f"Profitability Index: {roi_analysis.profitability_index:.2f}")
print(f"Break-even year: {roi_analysis.break_even_year}")
```

## Data Models

### ModulePlacement
```python
@dataclass
class ModulePlacement:
    row: int
    column: int
    x_position: float
    y_position: float
    z_position: float
    orientation: float  # degrees
    tilt: float  # degrees
    shading_factor: float  # 0.0 to 1.0
    efficiency_factor: float  # 0.0 to 1.0
```

### WeatherData
```python
@dataclass
class WeatherData:
    latitude: float
    longitude: float
    annual_irradiation_kwh_m2: float
    monthly_irradiation: List[float]  # 12 months
    average_temperature_c: float
    monthly_temperatures: List[float]  # 12 months
    sunshine_hours_annual: float
    cloud_cover_percent: float
```

### ShadingAnalysisResult
```python
@dataclass
class ShadingAnalysisResult:
    overall_shading_level: ShadingLevel
    annual_shading_loss_percent: float
    monthly_shading_factors: List[float]  # 12 months
    hourly_shading_profile: List[List[float]]  # 365 days x 24 hours
    obstacles: List[Dict[str, Any]]
    recommendations: List[str]
```

### BatteryStorageAnalysis
```python
@dataclass
class BatteryStorageAnalysis:
    optimal_capacity_kwh: float
    actual_capacity_kwh: float
    daily_cycles: float
    annual_cycles: float
    efficiency_percent: float
    depth_of_discharge_percent: float
    expected_lifetime_years: float
    self_consumption_increase_percent: float
    autarky_increase_percent: float
    roi_years: float
    cost_benefit_ratio: float
```

### GridFeedInAnalysis
```python
@dataclass
class GridFeedInAnalysis:
    annual_feed_in_kwh: float
    monthly_feed_in_kwh: List[float]
    feed_in_tariff_eur_kwh: float
    annual_feed_in_revenue_eur: float
    grid_connection_capacity_kw: float
    peak_feed_in_power_kw: float
    curtailment_losses_kwh: float
    grid_stability_score: float
```

### ROIAnalysis
```python
@dataclass
class ROIAnalysis:
    initial_investment_eur: float
    annual_savings_eur: float
    annual_revenue_eur: float
    payback_period_years: float
    net_present_value_eur: float
    internal_rate_of_return_percent: float
    profitability_index: float
    break_even_year: int
    cumulative_cash_flow_25years: List[float]
```

## Best Practices

### 1. Caching
The service automatically caches weather data and optimization results. Clear cache periodically:

```python
service._weather_cache.clear()
service._optimization_cache.clear()
```

### 2. Error Handling
All methods use error handling decorators. Catch exceptions appropriately:

```python
try:
    result = service.calculate_premium(...)
except RuntimeError as e:
    print(f"Calculation failed: {e}")
```

### 3. Performance
For batch calculations, reuse the service instance:

```python
service = get_advanced_solar_service()

for location in locations:
    result = service.calculate_standard(
        roof_area_m2=location['area'],
        latitude=location['lat'],
        longitude=location['lon'],
        ...
    )
```

### 4. Validation
Always validate input parameters before calling service methods:

```python
if roof_area_m2 <= 0:
    raise ValueError("Roof area must be positive")
if not -90 <= latitude <= 90:
    raise ValueError("Invalid latitude")
if not -180 <= longitude <= 180:
    raise ValueError("Invalid longitude")
```

## Integration Examples

### Complete Solar System Analysis

```python
def analyze_complete_solar_system(
    roof_area_m2: float,
    latitude: float,
    longitude: float,
    annual_consumption_kwh: float,
    initial_investment_eur: float
) -> Dict[str, Any]:
    """Complete solar system analysis"""
    
    service = get_advanced_solar_service()
    
    # 1. Premium calculation with shading and battery
    calc_result = service.calculate_premium(
        roof_area_m2=roof_area_m2,
        latitude=latitude,
        longitude=longitude,
        orientation=0.0,
        tilt=30.0,
        module_power_w=400.0,
        annual_consumption_kwh=annual_consumption_kwh,
        include_shading_analysis=True,
        include_battery=True
    )
    
    # 2. Production forecast
    forecast = service.forecast_energy_production(
        system_size_kwp=calc_result['system_size_kwp'],
        latitude=latitude,
        longitude=longitude,
        orientation=0.0,
        tilt=30.0,
        years=25
    )
    
    # 3. Grid feed-in analysis
    grid_analysis = service.analyze_grid_feed_in(
        annual_production_kwh=calc_result['annual_production_kwh'],
        annual_consumption_kwh=annual_consumption_kwh,
        annual_self_consumption_kwh=calc_result['annual_self_consumption_kwh'],
        system_size_kwp=calc_result['system_size_kwp']
    )
    
    # 4. Financial analysis
    roi_analysis = service.calculate_roi_npv(
        initial_investment_eur=initial_investment_eur,
        annual_production_kwh=calc_result['annual_production_kwh'],
        annual_self_consumption_kwh=calc_result['annual_self_consumption_kwh'],
        annual_feed_in_kwh=grid_analysis.annual_feed_in_kwh
    )
    
    return {
        "calculation": calc_result,
        "forecast": forecast,
        "grid_analysis": grid_analysis,
        "roi_analysis": roi_analysis
    }
```

## Requirements Validation

This implementation satisfies all requirements from Task 99:

✅ **Calculation Variants**: Standard, Premium, and Custom variants implemented
✅ **Module Placement Optimization**: Automatic placement with obstacle avoidance
✅ **Shading Analysis**: Hourly resolution for entire year with recommendations
✅ **Weather Data Integration**: Location-based weather data with caching
✅ **Energy Production Forecasting**: 25-year forecast with degradation
✅ **Battery Storage Calculations**: Comprehensive analysis with optimization
✅ **Grid Feed-In Calculations**: Revenue, curtailment, and stability analysis
✅ **ROI and NPV Calculations**: Complete financial analysis with IRR

## Requirements: 1.3, 6.1
