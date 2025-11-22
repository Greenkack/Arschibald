# Heat Pump Advanced Service - Quick Reference

## Quick Start

```python
from backend.services.heatpump_advanced_service import (
    HeatPumpAdvancedService,
    HeatPumpType,
    HeatingSystem,
    TariffType
)

service = HeatPumpAdvancedService()
service.initialize()
```

## Heat Pump Types

| Type | Enum Value | Typical COP | Best For |
|------|-----------|-------------|----------|
| Air Source | `HeatPumpType.AIR_SOURCE` | 3.0-4.5 | Most installations |
| Ground Source | `HeatPumpType.GROUND_SOURCE` | 4.0-5.5 | High efficiency |
| Water Source | `HeatPumpType.WATER_SOURCE` | 4.0-5.5 | Near water bodies |
| Hybrid | `HeatPumpType.HYBRID` | Variable | Backup heating |

## Heating Systems

| System | Enum Value | Flow Temp | Best COP |
|--------|-----------|-----------|----------|
| Underfloor | `HeatingSystem.UNDERFLOOR` | 35-45°C | Highest |
| Fan Coil | `HeatingSystem.FAN_COIL` | 40-50°C | High |
| Radiators | `HeatingSystem.RADIATORS` | 50-70°C | Lower |
| Mixed | `HeatingSystem.MIXED` | 45-55°C | Medium |

## Insulation Quality

| Quality | U-Value (W/m²K) | Heat Loss |
|---------|----------------|-----------|
| `"poor"` | 1.5 | High |
| `"average"` | 1.0 | Medium |
| `"good"` | 0.6 | Low |
| `"excellent"` | 0.3 | Very Low |

## Common Calculations

### 1. Basic Heat Pump Sizing

```python
result = service.calculate_air_source_heat_pump(
    building_area_m2=150.0,
    insulation_quality="good",
    outdoor_temp_c=5.0,
    indoor_temp_c=20.0,
    heating_system=HeatingSystem.UNDERFLOOR
)
# Returns: heating_demand_kw, cop, annual_consumption_kwh
```

### 2. COP Calculation

```python
cop = service.calculate_cop(
    heat_pump_type=HeatPumpType.AIR_SOURCE,
    outdoor_temp_c=5.0,
    indoor_temp_c=20.0,
    flow_temp_c=40.0,
    return_temp_c=35.0
)
# Returns: cop_heating, scop_seasonal, efficiency_percent
```

### 3. Cost Comparison

```python
costs = service.compare_heating_costs(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=3.5,
    electricity_price_eur_kwh=0.30,
    gas_price_eur_kwh=0.08,
    oil_price_eur_l=1.20,
    heat_pump_investment_eur=15000.0
)
# Returns: annual costs, savings, payback_period
```

### 4. Tariff Optimization

```python
optimization = service.optimize_dynamic_tariff(
    annual_heating_demand_kwh=15000.0,
    tariff_type=TariffType.TIME_OF_USE,
    hourly_tariffs_eur_kwh=[0.20] * 24,
    thermal_storage_capacity_kwh=50.0
)
# Returns: optimal_schedule, cost_savings_percent
```

### 5. Seasonal Performance

```python
seasonal = service.analyze_seasonal_performance(
    heat_pump_type=HeatPumpType.AIR_SOURCE,
    latitude=51.0,
    building_area_m2=150.0,
    insulation_quality="good",
    heating_system=HeatingSystem.UNDERFLOOR
)
# Returns: monthly_cop, monthly_consumption_kwh
```

### 6. PV + Heat Pump

```python
combined = service.optimize_pv_heatpump_combination(
    pv_system_size_kwp=10.0,
    annual_pv_production_kwh=10000.0,
    heat_pump_capacity_kw=8.0,
    annual_hp_consumption_kwh=5000.0,
    annual_household_consumption_kwh=4000.0,
    electricity_price_eur_kwh=0.30,
    feed_in_tariff_eur_kwh=0.08
)
# Returns: self_consumption_rate, autarky_rate, savings
```

### 7. Smart Grid Integration

```python
grid = service.analyze_smart_grid_integration(
    heat_pump_capacity_kw=8.0,
    thermal_storage_capacity_kwh=50.0,
    annual_consumption_kwh=5000.0
)
# Returns: demand_response_potential, flexibility_value
```

### 8. Environmental Impact

```python
env = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=3.5,
    renewable_energy_percent=30.0
)
# Returns: co2_savings_kg, environmental_score
```

## Typical Values

### COP by Temperature

| Outdoor Temp | Air Source COP | Ground Source COP |
|--------------|----------------|-------------------|
| -10°C | 2.5 | 4.5 |
| 0°C | 3.0 | 4.8 |
| 5°C | 3.5 | 5.0 |
| 10°C | 4.0 | 5.2 |
| 15°C | 4.5 | 5.5 |

### Annual Heating Hours by Climate

| Climate | Outdoor Temp | Heating Hours |
|---------|--------------|---------------|
| Cold | < 0°C | 2500 |
| Moderate | 0-5°C | 2200 |
| Mild | 5-10°C | 1800 |
| Warm | > 10°C | 1500 |

### Heating Demand by Building

| Building Type | Area (m²) | Insulation | Demand (kW) |
|---------------|-----------|------------|-------------|
| Old House | 150 | Poor | 15-20 |
| Renovated | 150 | Average | 10-12 |
| New Build | 150 | Good | 6-8 |
| Passive House | 150 | Excellent | 3-4 |

## Cost Estimates (Germany 2024)

| Item | Cost Range |
|------|-----------|
| Air Source HP (8 kW) | €8,000 - €15,000 |
| Ground Source HP (8 kW) | €15,000 - €25,000 |
| Installation | €2,000 - €5,000 |
| Thermal Storage (500L) | €1,500 - €3,000 |
| Electricity (Heat Pump Tariff) | €0.25 - €0.30/kWh |
| Gas | €0.07 - €0.10/kWh |
| Oil | €1.00 - €1.50/L |

## Performance Metrics

### Self-Consumption Rates (with PV)

| Configuration | Self-Consumption |
|---------------|------------------|
| No Storage | 30-40% |
| With HP Load Shifting | 50-60% |
| With Battery | 60-80% |
| With HP + Battery | 70-90% |

### Payback Periods

| Comparison | Typical Payback |
|------------|-----------------|
| HP vs Gas | 8-12 years |
| HP vs Oil | 6-10 years |
| HP vs Electric | 3-5 years |
| HP + PV vs Gas | 10-15 years |

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| Invalid COP | COP < 1.0 or > 6.0 | Check temperatures |
| Negative Demand | Heating demand < 0 | Check insulation quality |
| Invalid Tariff | Tariff array != 24 | Provide 24 hourly values |
| Storage Overflow | Storage > demand | Reduce storage size |

## Tips

1. **Underfloor heating** gives best COP (lowest flow temperature)
2. **Thermal storage** enables tariff optimization (10-20% savings)
3. **PV combination** increases self-consumption by 20-30%
4. **Ground source** has 20-30% higher COP than air source
5. **Good insulation** reduces heating demand by 40-60%
6. **Smart grid** participation can earn €200-500/year

## Common Mistakes

❌ Using radiator temperatures with underfloor heating  
✅ Match heating system to actual installation

❌ Ignoring thermal storage for tariff optimization  
✅ Include storage capacity for dynamic tariffs

❌ Comparing heat pump to 100% efficient gas  
✅ Use realistic efficiencies (gas 90%, oil 85%)

❌ Using summer COP for annual calculations  
✅ Use seasonal COP or monthly analysis

❌ Forgetting PV self-consumption benefits  
✅ Always analyze PV + HP combination

## See Also

- [Full Documentation](HEATPUMP_ADVANCED_SERVICE_GUIDE.md)
- [Test Examples](../tests/test_heatpump_advanced_service.py)
- [API Endpoints](API_DOCUMENTATION.md)
