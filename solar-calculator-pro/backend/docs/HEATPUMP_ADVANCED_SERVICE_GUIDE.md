# Heat Pump Advanced Service Guide

## Overview

The Heat Pump Advanced Service provides comprehensive heat pump analysis and optimization capabilities for the Solar Calculator Pro application. This service enables detailed calculations for all heat pump types, performance analysis, cost comparisons, and integration with PV systems and smart grids.

## Features

### 1. Heat Pump Calculation Types

#### Air Source Heat Pumps
- Calculate heating demand based on building characteristics
- Determine COP based on outdoor temperature
- Estimate annual energy consumption
- Optimize for different heating systems (radiators, underfloor, fan coil)

#### Ground Source Heat Pumps
- Calculate with stable ground temperatures
- Determine collector area requirements (horizontal/vertical)
- Higher COP than air source
- More consistent year-round performance

#### Water Source Heat Pumps
- Calculate using water body temperatures
- Similar performance to ground source
- Suitable for properties near water sources

### 2. COP (Coefficient of Performance) Calculations

The service calculates:
- **COP Heating**: Efficiency for heating mode
- **COP Cooling**: Efficiency for cooling mode (if applicable)
- **SCOP (Seasonal COP)**: Average efficiency across seasons
- **Efficiency Percentage**: Relative to theoretical Carnot efficiency

COP varies based on:
- Outdoor/source temperature
- Flow temperature (heating system dependent)
- Heat pump type
- Operating conditions

### 3. Dynamic Tariff Optimization

Optimize heat pump operation for time-of-use electricity tariffs:
- Identify optimal heating hours (low tariff periods)
- Avoid peak tariff hours
- Utilize thermal storage for load shifting
- Calculate cost savings vs. flat-rate operation
- Generate 24-hour optimal operation schedule

### 4. Heating Cost Comparison

Compare annual heating costs across systems:
- Heat pump (with COP consideration)
- Gas heating (90% efficiency)
- Oil heating (85% efficiency)
- Electric heating (100% efficiency)

Calculate:
- Annual costs for each system
- Savings vs. conventional systems
- Payback period for heat pump investment
- 25-year ROI

### 5. Seasonal Performance Analysis

Analyze heat pump performance across seasons:
- Calculate monthly COP values
- Estimate monthly consumption
- Determine seasonal averages (winter, spring, summer, autumn)
- Calculate efficiency variation
- Identify optimal operating conditions

### 6. PV + Heat Pump Optimization

Optimize combined PV and heat pump systems:
- Calculate self-consumption rate
- Determine autarky rate (energy independence)
- Optimize operation schedule for PV production
- Calculate synergy benefits from load shifting
- Estimate combined savings
- Generate hourly operation profile

### 7. Smart Grid Integration

Analyze potential for smart grid services:
- Demand response capability
- Load shifting capacity
- Peak shaving contribution
- Grid stabilization potential
- Renewable energy integration
- Flexibility value and revenue potential

### 8. Environmental Impact Analysis

Calculate environmental benefits:
- Annual CO2 savings vs. gas/oil heating
- Carbon footprint reduction percentage
- Primary energy factor
- Environmental score (0-100)
- Equivalent trees planted
- Impact of renewable energy in grid mix

## Usage Examples

### Basic Air Source Heat Pump Calculation

```python
from backend.services.heatpump_advanced_service import (
    HeatPumpAdvancedService,
    HeatingSystem
)

service = HeatPumpAdvancedService()
service.initialize()

result = service.calculate_air_source_heat_pump(
    building_area_m2=150.0,
    insulation_quality="good",
    outdoor_temp_c=5.0,
    indoor_temp_c=20.0,
    heating_system=HeatingSystem.UNDERFLOOR
)

print(f"Heating Demand: {result['heating_demand_kw']:.2f} kW")
print(f"COP: {result['cop']:.2f}")
print(f"Annual Consumption: {result['annual_consumption_kwh']:.0f} kWh")
```

### COP Calculation

```python
from backend.services.heatpump_advanced_service import HeatPumpType

cop_result = service.calculate_cop(
    heat_pump_type=HeatPumpType.AIR_SOURCE,
    outdoor_temp_c=5.0,
    indoor_temp_c=20.0,
    flow_temp_c=40.0,
    return_temp_c=35.0
)

print(f"COP Heating: {cop_result.cop_heating:.2f}")
print(f"SCOP Seasonal: {cop_result.scop_seasonal:.2f}")
print(f"Efficiency: {cop_result.efficiency_percent:.1f}%")
```

### Dynamic Tariff Optimization

```python
from backend.services.heatpump_advanced_service import TariffType

# Define hourly tariffs (24 hours)
hourly_tariffs = [0.20] * 24
hourly_tariffs[17:21] = [0.35] * 4  # Peak hours
hourly_tariffs[2:6] = [0.15] * 4    # Off-peak hours

result = service.optimize_dynamic_tariff(
    annual_heating_demand_kwh=15000.0,
    tariff_type=TariffType.TIME_OF_USE,
    hourly_tariffs_eur_kwh=hourly_tariffs,
    thermal_storage_capacity_kwh=50.0
)

print(f"Annual Cost: €{result.annual_cost_eur:.2f}")
print(f"Cost Savings: {result.cost_savings_percent:.1f}%")
print(f"Grid Friendly Score: {result.grid_friendly_score:.1f}/100")
```

### Heating Cost Comparison

```python
result = service.compare_heating_costs(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=3.5,
    electricity_price_eur_kwh=0.30,
    gas_price_eur_kwh=0.08,
    oil_price_eur_l=1.20,
    heat_pump_investment_eur=15000.0
)

print(f"Heat Pump: €{result.heat_pump_annual_cost_eur:.2f}/year")
print(f"Gas: €{result.gas_annual_cost_eur:.2f}/year")
print(f"Savings vs Gas: €{result.savings_vs_gas_eur:.2f}/year")
print(f"Payback Period: {result.payback_period_years:.1f} years")
```

### Seasonal Performance Analysis

```python
result = service.analyze_seasonal_performance(
    heat_pump_type=HeatPumpType.AIR_SOURCE,
    latitude=51.0,
    building_area_m2=150.0,
    insulation_quality="good",
    heating_system=HeatingSystem.UNDERFLOOR
)

print(f"Winter COP: {result.winter_cop:.2f}")
print(f"Summer COP: {result.summer_cop:.2f}")
print(f"Annual Average COP: {result.annual_average_cop:.2f}")
print(f"Efficiency Variation: {result.efficiency_variation_percent:.1f}%")
```

### PV + Heat Pump Optimization

```python
result = service.optimize_pv_heatpump_combination(
    pv_system_size_kwp=10.0,
    annual_pv_production_kwh=10000.0,
    heat_pump_capacity_kw=8.0,
    annual_hp_consumption_kwh=5000.0,
    annual_household_consumption_kwh=4000.0,
    electricity_price_eur_kwh=0.30,
    feed_in_tariff_eur_kwh=0.08
)

print(f"Self-Consumption Rate: {result.self_consumption_rate_percent:.1f}%")
print(f"Autarky Rate: {result.autarky_rate_percent:.1f}%")
print(f"Combined Savings: €{result.combined_savings_eur:.2f}/year")
print(f"Synergy Benefit: €{result.synergy_benefit_eur:.2f}/year")
```

### Smart Grid Integration

```python
result = service.analyze_smart_grid_integration(
    heat_pump_capacity_kw=8.0,
    thermal_storage_capacity_kwh=50.0,
    annual_consumption_kwh=5000.0,
    grid_signal_response_time_min=15.0
)

print(f"Demand Response Potential: {result.demand_response_potential_kw:.1f} kW")
print(f"Load Shifting Capacity: {result.load_shifting_capacity_kwh:.1f} kWh")
print(f"Grid Stabilization Score: {result.grid_stabilization_score:.1f}/100")
print(f"Flexibility Value: €{result.flexibility_value_eur_year:.2f}/year")
```

### Environmental Impact Analysis

```python
result = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=3.5,
    electricity_co2_g_kwh=400.0,
    gas_co2_g_kwh=200.0,
    oil_co2_g_kwh=266.0,
    renewable_energy_percent=30.0
)

print(f"Annual CO2 Savings: {result.annual_co2_savings_kg:.0f} kg")
print(f"CO2 Savings vs Gas: {result.co2_savings_vs_gas_kg:.0f} kg")
print(f"Environmental Score: {result.environmental_score:.1f}/100")
print(f"Equivalent Trees: {result.equivalent_trees_planted} trees")
```

## API Integration

### FastAPI Endpoint Example

```python
from fastapi import APIRouter, Depends
from backend.services.heatpump_advanced_service import HeatPumpAdvancedService

router = APIRouter(prefix="/api/v1/heatpump", tags=["heatpump"])

@router.post("/calculate/air-source")
async def calculate_air_source(
    building_area_m2: float,
    insulation_quality: str,
    outdoor_temp_c: float,
    indoor_temp_c: float,
    heating_system: str
):
    service = HeatPumpAdvancedService()
    service.initialize()
    
    result = service.calculate_air_source_heat_pump(
        building_area_m2=building_area_m2,
        insulation_quality=insulation_quality,
        outdoor_temp_c=outdoor_temp_c,
        indoor_temp_c=indoor_temp_c,
        heating_system=HeatingSystem(heating_system)
    )
    
    return result
```

## Best Practices

1. **Initialize Once**: Create and initialize the service once, reuse for multiple calculations
2. **Cache Results**: The service includes internal caching for COP and tariff calculations
3. **Validate Inputs**: Always validate building parameters and temperatures before calculation
4. **Consider Climate**: Use appropriate outdoor temperatures for your location
5. **Thermal Storage**: Include thermal storage capacity for better tariff optimization
6. **Combine with PV**: Always analyze PV + heat pump combination for maximum savings
7. **Monitor Performance**: Use seasonal analysis to track actual vs. predicted performance

## Performance Considerations

- COP calculations are cached based on temperature conditions
- Tariff optimizations are cached for repeated queries
- Seasonal analysis calculates 12 months of data
- PV + HP optimization generates 24-hour profiles
- All calculations are optimized for sub-second response times

## Error Handling

The service includes comprehensive error handling:
- Invalid input parameters are caught and logged
- Service errors are wrapped with context
- Health checks monitor service status
- All methods include error recovery

## Requirements

- Python 3.10+
- NumPy for numerical calculations
- Backend core services (BaseService, error handling, logging)

## Related Services

- **Solar Calculator Advanced Service**: For PV system calculations
- **Visualization Advanced Service**: For 3D heat pump visualization
- **Pricing Service**: For cost calculations and comparisons

## Support

For issues or questions:
- Check the test file for usage examples
- Review the API documentation
- Contact the development team
