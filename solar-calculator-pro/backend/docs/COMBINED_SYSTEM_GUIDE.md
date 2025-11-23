# Combined Heat Pump + PV System Integration Guide

## Overview

The Combined System Integration provides comprehensive analysis and optimization for heat pump and PV systems working together. This integration maximizes synergies, optimizes self-consumption, and provides smart control strategies for optimal system performance.

## Key Features

### 1. System Optimization
- **Self-Consumption Maximization**: Automatically optimize energy flows to maximize PV self-consumption
- **Cost Optimization**: Minimize total energy costs through smart control
- **Grid Independence**: Maximize independence from the electrical grid
- **Comfort Priority**: Ensure heating comfort while optimizing energy use
- **Balanced Strategy**: Balance all factors for optimal overall performance

### 2. Synergy Analysis
- **Direct PV to Heat Pump**: Calculate PV energy directly used by heat pump
- **Battery-Mediated Energy**: Track PV energy used via battery storage
- **Heating Cost Reduction**: Quantify cost savings from PV integration
- **Effective COP Improvement**: Calculate improved heat pump efficiency
- **Grid Independence**: Measure heating independence from grid

### 3. Smart Control Strategies
- **Predictive Control**: Use weather and load forecasts for optimization
- **Time-of-Use Optimization**: Leverage variable electricity tariffs
- **Battery Management**: Intelligent charging/discharging strategies
- **Load Shifting**: Shift heat pump operation to PV production hours
- **Comfort Maintenance**: Ensure heating comfort while optimizing

### 4. Financial Analysis
- **Investment Breakdown**: Detailed cost analysis for all components
- **Annual Savings**: Calculate total annual cost savings
- **ROI Metrics**: Payback period, NPV, IRR, LCOE
- **Comparison Scenarios**: Compare with PV-only, HP-only, and conventional
- **Synergy Benefits**: Quantify additional benefits from combination

### 5. System Monitoring
- **Real-Time Data**: Current power, production, consumption
- **Performance Metrics**: Self-consumption rate, grid independence
- **System Status**: Operating modes, temperatures, battery SOC
- **Cost Tracking**: Daily, monthly, annual cost savings
- **Alerts**: Performance issues and optimization opportunities

## API Endpoints

### Analyze Combined System
```http
POST /api/v1/combined-system/analyze
```

**Request Body:**
```json
{
  "pv_system_size": 10.0,
  "pv_annual_production": 10000.0,
  "pv_module_count": 30,
  "pv_orientation": "south",
  "pv_tilt_angle": 30.0,
  "hp_model": "Viessmann Vitocal 200-S",
  "hp_cop": 4.2,
  "hp_heating_capacity": 8.0,
  "hp_power_consumption": 2.0,
  "annual_heating_demand": 12000.0,
  "building_insulation_quality": "good",
  "battery_capacity": 10.0,
  "battery_efficiency": 0.95,
  "electricity_price": 0.30,
  "feed_in_tariff": 0.08,
  "control_strategy": "self_consumption",
  "location": "Berlin",
  "latitude": 52.52,
  "longitude": 13.40
}
```

**Response:**
```json
{
  "system_configuration": {...},
  "optimized_control_strategy": "self_consumption",
  "annual_energy_flow": {
    "total_pv_production": 10000.0,
    "total_hp_consumption": 2857.14,
    "total_self_consumption": 7500.0,
    "total_grid_import": 1500.0,
    "total_grid_export": 2500.0
  },
  "synergy_analysis": {
    "pv_to_hp_direct": 2000.0,
    "pv_to_hp_via_battery": 500.0,
    "total_pv_for_heating": 2500.0,
    "heating_cost_reduction": 750.0,
    "heating_cost_reduction_percent": 87.5,
    "cop_improvement": 0.5,
    "grid_independence_heating": 87.5
  },
  "financial_analysis": {
    "total_investment": 28000.0,
    "annual_savings": 2500.0,
    "simple_payback_years": 11.2,
    "npv_20_years": 15000.0,
    "irr": 8.5
  },
  "self_consumption_rate": 0.75,
  "grid_independence_rate": 0.70,
  "annual_co2_savings": 4500.0
}
```

### Optimize System Operation
```http
POST /api/v1/combined-system/optimize
```

**Request Body:**
```json
{
  "system_id": 1,
  "optimization_goal": "minimize_cost",
  "time_horizon_days": 7
}
```

### Get Monitoring Data
```http
GET /api/v1/combined-system/monitoring/{system_id}
```

## Control Strategies

### 1. Self-Consumption Strategy
**Goal**: Maximize use of PV energy within the system

**Logic**:
- Prioritize direct PV consumption
- Charge battery with excess PV
- Discharge battery to cover consumption
- Minimize grid import/export

**Best For**: Systems with high electricity prices and low feed-in tariffs

### 2. Cost Optimization Strategy
**Goal**: Minimize total energy costs

**Logic**:
- Consider time-of-use tariffs
- Charge battery during low-price periods
- Discharge during high-price periods
- Balance self-consumption with grid interaction

**Best For**: Systems with variable electricity tariffs

### 3. Grid Independence Strategy
**Goal**: Maximize independence from electrical grid

**Logic**:
- Maximize battery utilization
- Prioritize self-consumption over feed-in
- Shift loads to PV production hours
- Minimize grid import

**Best For**: Areas with unreliable grid or high grid fees

### 4. Comfort Priority Strategy
**Goal**: Ensure optimal heating comfort

**Logic**:
- Maintain desired temperatures
- Use PV when available
- Don't compromise comfort for savings
- Flexible grid interaction

**Best For**: Users prioritizing comfort over cost savings

### 5. Balanced Strategy
**Goal**: Balance all factors

**Logic**:
- Optimize self-consumption
- Consider costs
- Maintain comfort
- Reasonable grid independence

**Best For**: Most users seeking overall optimization

## Integration Examples

### Example 1: Basic Analysis
```python
from backend.services.combined_system_service import CombinedSystemService
from backend.models.combined_system_schemas import CombinedSystemRequest, ControlStrategy

service = CombinedSystemService()

request = CombinedSystemRequest(
    pv_system_size=10.0,
    pv_annual_production=10000.0,
    pv_module_count=30,
    pv_orientation="south",
    pv_tilt_angle=30.0,
    hp_model="Viessmann Vitocal 200-S",
    hp_cop=4.2,
    hp_heating_capacity=8.0,
    hp_power_consumption=2.0,
    annual_heating_demand=12000.0,
    building_insulation_quality="good",
    battery_capacity=10.0,
    electricity_price=0.30,
    feed_in_tariff=0.08,
    control_strategy=ControlStrategy.SELF_CONSUMPTION,
    location="Berlin",
    latitude=52.52,
    longitude=13.40
)

result = service.analyze_combined_system(request)

print(f"Annual Savings: €{result.financial_analysis.annual_savings:.2f}")
print(f"Self-Consumption Rate: {result.self_consumption_rate * 100:.1f}%")
print(f"Payback Period: {result.financial_analysis.simple_payback_years:.1f} years")
```

### Example 2: Time-of-Use Tariff
```python
from backend.models.combined_system_schemas import TimeOfUseProfile

# Define time-of-use tariff
tariff = [
    TimeOfUseProfile(hour=h, price_per_kwh=0.40, is_peak=True) 
    for h in range(17, 21)  # Peak hours 17-21
] + [
    TimeOfUseProfile(hour=h, price_per_kwh=0.20, is_peak=False) 
    for h in range(0, 6)  # Off-peak hours 0-6
] + [
    TimeOfUseProfile(hour=h, price_per_kwh=0.30, is_peak=False) 
    for h in range(6, 17)  # Standard hours
] + [
    TimeOfUseProfile(hour=h, price_per_kwh=0.30, is_peak=False) 
    for h in range(21, 24)  # Standard hours
]

request.time_of_use_tariff = tariff
request.control_strategy = ControlStrategy.COST_OPTIMIZATION

result = service.analyze_combined_system(request)
```

## Performance Metrics

### Self-Consumption Rate
```
Self-Consumption Rate = PV Energy Used Locally / Total PV Production
```
- **Target**: > 70% for combined systems
- **Excellent**: > 80%
- **Factors**: Battery size, load profile, control strategy

### Grid Independence Rate
```
Grid Independence = 1 - (Grid Import / Total Consumption)
```
- **Target**: > 60% for combined systems
- **Excellent**: > 75%
- **Factors**: PV size, battery size, heating demand

### Heating Grid Independence
```
Heating Independence = PV Energy for Heating / Total HP Consumption
```
- **Target**: > 50%
- **Excellent**: > 70%
- **Key Metric**: Shows PV contribution to heating

## Optimization Tips

### 1. System Sizing
- **PV System**: Size for 100-120% of annual consumption
- **Battery**: 0.5-1.0 kWh per kWp of PV
- **Heat Pump**: Size for peak heating load

### 2. Control Settings
- Enable smart control for automatic optimization
- Use self-consumption strategy for best results
- Consider time-of-use tariffs if available
- Monitor and adjust based on performance

### 3. Operational Best Practices
- Shift heat pump operation to PV production hours
- Use battery for evening/morning peaks
- Maintain comfortable indoor temperatures
- Regular system monitoring and maintenance

### 4. Financial Optimization
- Maximize self-consumption to reduce grid costs
- Leverage feed-in tariff for excess production
- Consider battery size for optimal ROI
- Monitor payback period and adjust strategy

## Troubleshooting

### Low Self-Consumption Rate
**Symptoms**: < 60% self-consumption
**Causes**:
- PV production not aligned with consumption
- Battery too small or not utilized
- Heat pump not optimized for PV hours

**Solutions**:
- Adjust heat pump schedule
- Increase battery capacity
- Enable smart control
- Shift other loads to PV hours

### High Grid Import
**Symptoms**: > 40% grid import
**Causes**:
- Insufficient PV capacity
- Battery undersized
- High evening/night consumption

**Solutions**:
- Increase PV system size
- Add or upgrade battery
- Optimize load profile
- Use time-of-use tariff

### Poor Financial Performance
**Symptoms**: Payback > 15 years
**Causes**:
- High investment costs
- Low electricity prices
- Poor system utilization

**Solutions**:
- Optimize system sizing
- Improve self-consumption
- Consider financing options
- Review component costs

## Best Practices

1. **System Design**
   - Size PV for annual consumption
   - Choose heat pump with good COP
   - Add battery for flexibility
   - Consider future expansion

2. **Control Strategy**
   - Start with balanced strategy
   - Monitor performance
   - Adjust based on results
   - Enable smart features

3. **Monitoring**
   - Check daily performance
   - Review monthly trends
   - Track cost savings
   - Identify optimization opportunities

4. **Maintenance**
   - Regular system checks
   - Clean PV modules
   - Service heat pump annually
   - Update control software

## Support

For technical support or questions:
- Email: support@solar-calculator-pro.com
- Documentation: https://docs.solar-calculator-pro.com
- API Reference: https://api.solar-calculator-pro.com/docs
