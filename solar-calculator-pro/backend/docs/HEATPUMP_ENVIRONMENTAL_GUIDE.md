# Heat Pump Environmental Analysis Guide

## Overview

The Heat Pump Environmental Analysis system provides comprehensive environmental impact assessment for heat pump installations, including CO2 savings calculations, carbon footprint tracking, sustainability ratings, and environmental certifications.

## Features

### 1. CO2 Savings Calculations

Calculate annual and lifetime CO2 savings compared to conventional heating systems:

```python
from backend.services.heatpump_advanced_service import HeatPumpAdvancedService, HeatPumpType

service = HeatPumpAdvancedService()
service.initialize()

impact = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.2,
    electricity_co2_g_kwh=400.0,
    gas_co2_g_kwh=200.0,
    oil_co2_g_kwh=266.0,
    renewable_energy_percent=40.0,
    lifetime_years=25,
    building_area_m2=150.0,
    heat_pump_type=HeatPumpType.AIR_SOURCE
)

print(f"Annual CO2 Savings: {impact.annual_co2_savings_kg:,.0f} kg")
print(f"Lifetime CO2 Savings: {impact.lifetime_co2_savings_kg:,.0f} kg")
print(f"vs. Gas: {impact.co2_savings_vs_gas_kg:,.0f} kg/year")
print(f"vs. Oil: {impact.co2_savings_vs_oil_kg:,.0f} kg/year")
```

### 2. Environmental Impact Analysis

Comprehensive environmental metrics:

- **Carbon Footprint**: Annual and lifetime carbon footprint
- **Renewable Energy**: Percentage and contribution
- **Air Quality**: Improvement score based on emission reduction
- **Water Conservation**: Estimated water savings
- **Noise Pollution**: Reduction in noise levels

```python
print(f"Environmental Score: {impact.environmental_score:.1f}/100")
print(f"Air Quality Score: {impact.air_quality_improvement_score:.1f}/100")
print(f"Water Conservation: {impact.water_conservation_liters_year:,.0f} L/year")
print(f"Noise Reduction: {impact.noise_pollution_reduction_db:.1f} dB")
```

### 3. Carbon Footprint Tracking

Track carbon footprint over the system lifetime with yearly breakdown:

```python
# Access yearly tracking data
for year_data in impact.carbon_footprint_tracking[:5]:
    print(f"Year {year_data['year']}:")
    print(f"  HP Emissions: {year_data['hp_emissions_kg']:,.0f} kg")
    print(f"  Gas Emissions: {year_data['gas_emissions_kg']:,.0f} kg")
    print(f"  Annual Savings: {year_data['annual_savings_kg']:,.0f} kg")
    print(f"  Cumulative Savings: {year_data['cumulative_savings_kg']:,.0f} kg")
```

Features:
- Yearly emissions tracking
- Cumulative savings calculation
- Grid decarbonization projection (2% improvement per year)
- Comparison with conventional systems

### 4. Sustainability Rating

Automatic sustainability rating (A+ to F) based on:
- Environmental score (50% weight)
- Carbon reduction percentage (30% weight)
- Renewable energy percentage (20% weight)

```python
print(f"Sustainability Rating: {impact.sustainability_rating}")
# Output: A+, A, B, C, D, E, or F
```

Rating Scale:
- **A+**: 90-100 points (Excellent)
- **A**: 80-89 points (Very Good)
- **B**: 70-79 points (Good)
- **C**: 60-69 points (Satisfactory)
- **D**: 50-59 points (Adequate)
- **E**: 40-49 points (Poor)
- **F**: 0-39 points (Very Poor)

### 5. Environmental Certifications

Automatic determination of applicable certifications:

```python
for cert in impact.environmental_certifications:
    print(f"✓ {cert}")
```

Available Certifications:
- **Energy Efficiency**: Energy Star, EU Energy Labels (A+++ to A+)
- **Renewable Energy**: 100% Renewable Ready, Renewable Energy Compatible
- **Carbon Reduction**: Carbon Neutral Certified, Low Carbon Technology
- **System Specific**: Geothermal Certified (for ground source)
- **Standards**: ISO 14001 Compatible, F-Gas Compliant, Low GWP Refrigerant

### 6. Renewable Energy Tracking

Track renewable energy contribution and fossil fuel replacement:

```python
print(f"Grid Renewable %: {impact.renewable_energy_percent:.1f}%")
print(f"Renewable Contribution: {impact.renewable_energy_contribution_kwh:,.0f} kWh/year")
print(f"Fossil Fuel Replacement: {impact.fossil_fuel_replacement_percent:.1f}%")
```

### 7. Sustainability Reporting

Generate comprehensive sustainability reports:

```python
system_details = {
    "heat_pump_type": "Air Source Heat Pump",
    "capacity_kw": 10.0,
    "cop": 4.2,
    "heating_system": "Underfloor Heating",
    "installation_year": 2024,
    "building_type": "Residential",
    "building_area_m2": 150.0
}

report = service.generate_sustainability_report(impact, system_details)

# Access report sections
print(report["executive_summary"])
print(report["carbon_footprint"])
print(report["renewable_energy"])
print(report["environmental_benefits"])
print(report["certifications"])
print(report["recommendations"])
```

Report Sections:
- **Executive Summary**: Key metrics and ratings
- **Carbon Footprint**: Detailed emissions and tracking
- **Renewable Energy**: Grid and system renewable metrics
- **Environmental Benefits**: Air quality, water, noise, energy
- **Certifications**: List of applicable certifications
- **Recommendations**: Actionable improvement suggestions

## API Reference

### `analyze_environmental_impact()`

Comprehensive environmental impact analysis.

**Parameters:**
- `annual_heating_demand_kwh` (float): Annual heating demand in kWh
- `heat_pump_cop` (float): Heat pump Coefficient of Performance
- `electricity_co2_g_kwh` (float, optional): Grid electricity CO2 intensity (default: 400 g/kWh)
- `gas_co2_g_kwh` (float, optional): Gas CO2 intensity (default: 200 g/kWh)
- `oil_co2_g_kwh` (float, optional): Oil CO2 intensity (default: 266 g/kWh)
- `renewable_energy_percent` (float, optional): Grid renewable percentage (default: 0%)
- `lifetime_years` (int, optional): System lifetime for analysis (default: 25 years)
- `building_area_m2` (float, optional): Building area (default: 150 m²)
- `heat_pump_type` (HeatPumpType, optional): Type of heat pump (default: AIR_SOURCE)

**Returns:**
`EnvironmentalImpact` object with comprehensive environmental metrics.

### `generate_sustainability_report()`

Generate comprehensive sustainability report.

**Parameters:**
- `environmental_impact` (EnvironmentalImpact): Environmental impact analysis results
- `system_details` (Dict[str, Any]): Heat pump system details

**Returns:**
Dictionary with sustainability report sections.

## Environmental Metrics Explained

### CO2 Savings

**Annual CO2 Savings**: Yearly CO2 emission reduction compared to conventional heating
- Calculated by comparing heat pump emissions with gas/oil heating emissions
- Accounts for heat pump efficiency (COP) and grid electricity CO2 intensity
- Adjusted for renewable energy percentage in grid

**Lifetime CO2 Savings**: Total CO2 reduction over system lifetime (typically 25 years)
- Includes grid decarbonization projection (2% improvement per year)
- Cumulative savings accounting for improving grid mix
- Provides long-term environmental impact perspective

### Carbon Footprint

**Annual Carbon Footprint**: Yearly CO2 emissions from heat pump operation
- Based on electricity consumption and grid CO2 intensity
- Adjusted for renewable energy in grid mix
- Lower footprint indicates better environmental performance

**Carbon Footprint Reduction**: Percentage reduction compared to conventional heating
- Calculated as: (Gas Emissions - HP Emissions) / Gas Emissions × 100%
- Higher percentage indicates greater environmental benefit
- Typical range: 40-80% reduction

### Environmental Score

Composite score (0-100) based on:
- **CO2 Reduction** (50% weight): Emission reduction vs. conventional heating
- **Renewable Energy** (30% weight): Percentage of renewable energy used
- **Efficiency** (20% weight): Heat pump COP relative to theoretical maximum

Higher scores indicate better overall environmental performance.

### Air Quality Improvement

Score (0-100) based on:
- CO2 savings per square meter of building area
- Elimination of local combustion emissions
- Reduction in particulate matter and NOx emissions

Benefits:
- No local combustion = no indoor air pollution
- Reduced outdoor air pollution in urban areas
- Health benefits from cleaner air

### Primary Energy Factor

Ratio of primary energy consumption to useful energy:
- **Heat Pump**: Electricity × 1.8 (primary energy factor) / COP
- **Gas Heating**: Direct consumption × 1.1

Lower factor indicates more efficient use of primary energy resources.

## Use Cases

### 1. Residential Heat Pump Assessment

```python
# Standard residential installation
impact = service.analyze_environmental_impact(
    annual_heating_demand_kwh=12000.0,
    heat_pump_cop=4.0,
    renewable_energy_percent=30.0,
    building_area_m2=120.0,
    heat_pump_type=HeatPumpType.AIR_SOURCE
)
```

### 2. Green Tariff Comparison

```python
# Compare standard vs. green electricity tariff
impact_standard = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.2,
    renewable_energy_percent=40.0
)

impact_green = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.2,
    renewable_energy_percent=100.0
)

improvement = impact_green.annual_co2_savings_kg - impact_standard.annual_co2_savings_kg
print(f"Additional CO2 savings with green tariff: {improvement:,.0f} kg/year")
```

### 3. System Type Comparison

```python
# Compare air source vs. ground source
impact_air = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.0,
    heat_pump_type=HeatPumpType.AIR_SOURCE
)

impact_ground = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.8,
    heat_pump_type=HeatPumpType.GROUND_SOURCE
)
```

### 4. Long-term Environmental Planning

```python
# Analyze 25-year environmental impact
impact = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.2,
    lifetime_years=25
)

# Access yearly tracking
for year in [1, 5, 10, 15, 20, 25]:
    year_data = impact.carbon_footprint_tracking[year-1]
    print(f"Year {year}: {year_data['cumulative_savings_kg']:,.0f} kg cumulative savings")
```

## Best Practices

### 1. Accurate Input Data

- Use actual building heating demand (from energy audit or bills)
- Use manufacturer-specified COP values
- Check local grid CO2 intensity (varies by region)
- Verify renewable energy percentage in grid mix

### 2. Scenario Analysis

- Compare multiple scenarios (standard grid, green tariff, different heat pump types)
- Analyze sensitivity to key parameters (COP, renewable %, grid CO2)
- Consider future grid decarbonization in long-term planning

### 3. Reporting

- Include sustainability report in customer proposals
- Highlight key environmental benefits (CO2 savings, trees equivalent)
- Show certification eligibility
- Provide actionable recommendations

### 4. Continuous Monitoring

- Track actual performance vs. projections
- Update analysis with actual consumption data
- Monitor grid renewable percentage changes
- Reassess certifications periodically

## Integration Examples

### With Solar PV System

```python
# Combined PV + Heat Pump environmental analysis
pv_production_kwh = 8000.0
hp_consumption_kwh = 3571.0  # 15000 kWh demand / 4.2 COP

# Calculate self-consumption
self_consumption_rate = 0.50  # 50% of HP consumption from PV
renewable_from_pv = (hp_consumption_kwh * self_consumption_rate / hp_consumption_kwh) * 100
total_renewable = 40.0 + renewable_from_pv  # Grid + PV

impact = service.analyze_environmental_impact(
    annual_heating_demand_kwh=15000.0,
    heat_pump_cop=4.2,
    renewable_energy_percent=min(100.0, total_renewable)
)
```

### With Dynamic Tariff

```python
# Optimize for renewable energy hours
from backend.services.heatpump_advanced_service import TariffType

tariff_optimization = service.optimize_dynamic_tariff(
    annual_heating_demand_kwh=15000.0,
    tariff_type=TariffType.TIME_OF_USE,
    hourly_tariffs_eur_kwh=[0.20] * 24,  # Simplified
    thermal_storage_capacity_kwh=50.0
)

# Use optimized schedule for environmental analysis
# Higher renewable usage during optimal hours
```

## Troubleshooting

### Low Environmental Score

**Possible causes:**
- Low heat pump COP
- High grid CO2 intensity
- Low renewable energy percentage

**Solutions:**
- Upgrade to more efficient heat pump
- Switch to green electricity tariff
- Combine with solar PV system
- Improve building insulation

### Unexpected Certification Results

**Check:**
- COP value is correct
- Renewable percentage is accurate
- Heat pump type is correctly specified
- All input parameters are realistic

### Carbon Footprint Tracking Issues

**Verify:**
- Lifetime years parameter is set correctly
- Grid decarbonization assumption is appropriate for region
- Baseline comparison system (gas/oil) is correct

## Performance Considerations

- Environmental analysis is computationally lightweight
- Carbon footprint tracking generates 25 data points (one per year)
- Sustainability report generation is fast (<100ms)
- Results can be cached for repeated queries with same parameters

## Future Enhancements

Planned features:
- Regional CO2 intensity databases
- Real-time grid carbon intensity integration
- Advanced certification tracking
- Lifecycle assessment (LCA) integration
- Circular economy metrics
- Biodiversity impact assessment

## Support

For questions or issues:
- Check demo file: `demo_heatpump_environmental.py`
- Review API documentation
- Contact development team

## Version History

- **v1.0.0** (2024): Initial release with comprehensive environmental analysis
  - CO2 savings calculations
  - Carbon footprint tracking
  - Sustainability ratings
  - Environmental certifications
  - Sustainability reporting
