# Heat Pump Environmental Analysis - Quick Reference

## Quick Start

```python
from backend.services.heatpump_advanced_service import HeatPumpAdvancedService, HeatPumpType

service = HeatPumpAdvancedService()
service.initialize()

impact = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.2,
    renewable_energy_percent=40.0
)

print(f"Annual CO2 Savings: {impact.annual_co2_savings_kg/1000:.2f} tons")
print(f"Sustainability Rating: {impact.sustainability_rating}")
```

## Key Metrics

| Metric | Description | Typical Range |
|--------|-------------|---------------|
| `annual_co2_savings_kg` | Yearly CO2 reduction | 2,000-8,000 kg |
| `lifetime_co2_savings_kg` | 25-year CO2 reduction | 50,000-200,000 kg |
| `carbon_footprint_reduction_percent` | % reduction vs. gas | 40-80% |
| `environmental_score` | Overall score (0-100) | 60-95 |
| `sustainability_rating` | Letter grade | A+ to F |
| `equivalent_trees_planted` | Tree equivalents | 100-400 trees |

## Sustainability Ratings

| Rating | Score Range | Description |
|--------|-------------|-------------|
| A+ | 90-100 | Excellent environmental performance |
| A | 80-89 | Very good environmental performance |
| B | 70-79 | Good environmental performance |
| C | 60-69 | Satisfactory performance |
| D | 50-59 | Adequate performance |
| E | 40-49 | Poor performance |
| F | 0-39 | Very poor performance |

## Environmental Certifications

### Energy Efficiency
- **COP ≥ 4.5**: Energy Star, EU A+++
- **COP ≥ 4.0**: EU A++
- **COP ≥ 3.5**: EU A+

### Renewable Energy
- **≥ 80% renewable**: 100% Renewable Ready
- **≥ 50% renewable**: Renewable Energy Compatible

### Carbon Reduction
- **≥ 70% reduction**: Carbon Neutral Certified
- **≥ 50% reduction**: Low Carbon Technology

### System Specific
- **Ground Source**: Geothermal Certified
- **All Types**: ISO 14001, F-Gas Compliant, Low GWP Refrigerant

## Common Scenarios

### Standard Residential
```python
impact = service.analyze_environmental_impact(
    annual_heating_demand_kwh=12000.0,
    heat_pump_cop=4.0,
    renewable_energy_percent=30.0,
    building_area_m2=120.0
)
```

### Green Tariff
```python
impact = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.2,
    renewable_energy_percent=100.0  # Green electricity
)
```

### Ground Source
```python
impact = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.8,  # Higher COP
    heat_pump_type=HeatPumpType.GROUND_SOURCE
)
```

## Sustainability Report

```python
system_details = {
    "heat_pump_type": "Air Source",
    "capacity_kw": 10.0,
    "cop": 4.2,
    "building_area_m2": 150.0
}

report = service.generate_sustainability_report(impact, system_details)

# Access sections
report["executive_summary"]      # Key metrics
report["carbon_footprint"]       # Emissions tracking
report["renewable_energy"]       # Renewable metrics
report["environmental_benefits"] # Air, water, noise
report["certifications"]         # Applicable certs
report["recommendations"]        # Improvement suggestions
```

## Carbon Footprint Tracking

```python
# Access yearly data
for year_data in impact.carbon_footprint_tracking:
    print(f"Year {year_data['year']}: "
          f"{year_data['cumulative_savings_kg']:,.0f} kg cumulative")
```

## Environmental Benefits

```python
# Air quality
print(f"Air Quality Score: {impact.air_quality_improvement_score:.1f}/100")

# Water conservation
print(f"Water Saved: {impact.water_conservation_liters_year:,.0f} L/year")

# Noise reduction
print(f"Noise Reduction: {impact.noise_pollution_reduction_db:.1f} dB")

# Primary energy
print(f"Primary Energy Factor: {impact.primary_energy_factor:.2f}")
```

## Comparison Example

```python
# Compare scenarios
scenarios = {
    "Standard Grid": {"renewable": 40.0, "cop": 4.0},
    "Green Tariff": {"renewable": 100.0, "cop": 4.0},
    "Ground Source": {"renewable": 40.0, "cop": 4.8}
}

for name, params in scenarios.items():
    impact = service.analyze_environmental_impact(
        annual_heating_demand_kwh=15000.0,
        heat_pump_cop=params["cop"],
        renewable_energy_percent=params["renewable"]
    )
    print(f"{name}: {impact.sustainability_rating} "
          f"({impact.annual_co2_savings_kg/1000:.2f} tons/year)")
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `electricity_co2_g_kwh` | 400 | Grid CO2 intensity (g/kWh) |
| `gas_co2_g_kwh` | 200 | Gas CO2 intensity (g/kWh) |
| `oil_co2_g_kwh` | 266 | Oil CO2 intensity (g/kWh) |
| `renewable_energy_percent` | 0 | Grid renewable % |
| `lifetime_years` | 25 | Analysis period |
| `building_area_m2` | 150 | Building area |

## Typical CO2 Intensities by Region

| Region | Grid CO2 (g/kWh) | Renewable % |
|--------|------------------|-------------|
| Germany | 400-450 | 40-50% |
| France | 50-100 | 70-80% |
| UK | 250-300 | 40-50% |
| Poland | 700-800 | 15-20% |
| Norway | 20-30 | 95-98% |

## Improvement Recommendations

### Low Score (< 60)
1. Switch to green electricity tariff
2. Upgrade to higher COP heat pump
3. Improve building insulation
4. Add solar PV system

### Medium Score (60-80)
1. Optimize operation schedule
2. Consider thermal storage
3. Regular maintenance
4. Monitor performance

### High Score (> 80)
1. Maintain current performance
2. Share best practices
3. Consider certification
4. Monitor grid improvements

## Performance Tips

- Cache results for repeated queries
- Use appropriate lifetime_years (typically 25)
- Verify regional CO2 intensities
- Update renewable % annually
- Include grid decarbonization trends

## Common Issues

### Low Environmental Score
- **Cause**: Low COP or high grid CO2
- **Fix**: Upgrade system or switch to green tariff

### Missing Certifications
- **Cause**: Incorrect parameters
- **Fix**: Verify COP and renewable %

### Unexpected Savings
- **Cause**: Wrong baseline comparison
- **Fix**: Check gas/oil CO2 values

## Demo File

Run the demo for examples:
```bash
python solar-calculator-pro/backend/demo_heatpump_environmental.py
```

## Documentation

- Full Guide: `HEATPUMP_ENVIRONMENTAL_GUIDE.md`
- API Reference: See guide for detailed API docs
- Examples: Check demo file for usage examples
