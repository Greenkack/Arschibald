# Heat Pump Analysis - Quick Reference

## Core Calculation Functions

### Building Heat Load
```python
calculate_building_heat_load(building_type, living_area_m2, insulation_quality) -> float
```
Returns heating load in kW based on building characteristics.

### Heat Pump Recommendation
```python
recommend_heat_pump(heat_load_kw, available_pumps) -> dict
```
Recommends smallest suitable heat pump from available models.

### Annual Energy Consumption
```python
calculate_annual_energy_consumption(heat_load_kw, scop, heating_hours=1800) -> float
```
Calculates annual electricity consumption in kWh.

### Economics Analysis
```python
calculate_heatpump_economics(heatpump_data, building_data) -> dict
```
Complete economic analysis including payback period and 20-year savings.

## Key Formulas

### Heat Load Calculation
```
heat_load_kw = (living_area_m2 * base_w_m2 * insulation_factor) / 1000
```

### Electricity Consumption
```
annual_electricity_kwh = annual_heat_demand_kwh / scop
```

### Payback Period
```
payback_years = investment_cost / annual_savings
```

### NPV (20 years)
```
NPV = -investment + Σ(operating_cost_i / (1 + discount_rate)^i)
```

## Product Database

### Structure
- **Manufacturers:** Viessmann, Buderus, Vaillant
- **Types:** Air-Water, Brine-Water, Water-Water, Hybrid
- **Power Range:** 4-16 kW typical
- **SCOP Range:** 3.5-5.5

### Access Functions
```python
get_heatpump_models(manufacturer, type, min_power, max_power)
find_suitable_model(required_power_kw, max_flow_temp, refrigerant)
```

## Configuration Options

### Building Types
- Neubau KFW40/55
- Altbau saniert/unsaniert

### Insulation Quality
- Sehr gut / Gut / Mittel / Schlecht

### Climate Zones
- Kalt (1.2x) / Gemäßigt (1.0x) / Mild (0.8x)

## BEG Subsidy

### Rates
- Base: 30%
- Speed Bonus: 20%
- Income Bonus: 30%
- Maximum: 70%

### Limits
- Max eligible: €60,000
- Income threshold: €40,000

## API Endpoints (Recommended)

```
POST /api/v1/heatpump/calculate-heat-load
POST /api/v1/heatpump/recommend-model
POST /api/v1/heatpump/check-radiator-compatibility
POST /api/v1/heatpump/calculate-economics
POST /api/v1/heatpump/calculate-subsidies
GET  /api/v1/heatpump/products
POST /api/v1/heatpump/dynamic-tariff/compare
```

## Migration Checklist

- [ ] Wrap calculation functions in service layer
- [ ] Migrate product database to RDBMS
- [ ] Create REST API endpoints
- [ ] Build React components
- [ ] Implement German number formatting
- [ ] Add comprehensive tests
- [ ] Optimize performance with caching
- [ ] Implement security measures

## Key Files

- `calculations_heatpump.py` - Core calculations
- `heatpump_pricing.py` - Pricing engine
- `heatpump_products_database.py` - Product data
- `heatpump_ui.py` - UI components
- `heatpump_dynamic_tariff.py` - Tariff calculations
- `heatpump_dynamic_tariff_charts.py` - Visualizations

## Contact

For detailed analysis, see: `HEAT_PUMP_DEEP_ANALYSIS.md`
