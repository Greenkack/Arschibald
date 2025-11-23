# Heat Pump Dynamic Tariff Optimization Guide

## Overview

The Dynamic Tariff Optimization system helps heat pump owners minimize electricity costs by intelligently scheduling heating operations based on time-varying electricity rates. The system analyzes tariff structures, heating requirements, and comfort preferences to generate optimized schedules that balance cost savings with comfort.

## Features

### 1. Time-of-Use Tariff Analysis
- Analyzes tariff structures with different rates for different time periods
- Identifies peak, off-peak, and shoulder periods
- Calculates optimal heating times based on rate structure

### 2. Smart Heating Schedules
- Generates optimized 24-hour heating schedules
- Shifts flexible heating loads to cheaper periods
- Maintains comfort levels while minimizing costs
- Considers building thermal mass for load shifting

### 3. Cost Optimization Algorithms
- Advanced algorithms for minimizing electricity costs
- Balances cost savings with comfort requirements
- Accounts for heat pump COP (Coefficient of Performance)
- Provides detailed cost breakdowns and savings analysis

### 4. Demand Response Integration
- Evaluates demand response events
- Calculates participation feasibility
- Generates adjusted schedules for events
- Estimates incentive earnings

### 5. Tariff Comparison
- Compares multiple tariff options
- Provides pros and cons for each tariff
- Recommends best tariff for specific usage patterns
- Calculates potential savings for each option

### 6. Real-Time Tariff Monitoring
- Monitors current electricity rates
- Analyzes 24-hour rate forecasts
- Provides real-time recommendations
- Identifies optimal heating windows

## Tariff Types

### Flat Rate
- **Description**: Single rate for all hours
- **Best For**: Simple, predictable billing
- **Optimization Potential**: Limited (no time-based savings)

### Time of Use (TOU)
- **Description**: Different rates for peak and off-peak periods
- **Best For**: Flexible heating schedules
- **Optimization Potential**: High (10-30% savings typical)
- **Example Periods**:
  - Off-peak: 22:00-06:00 (€0.18/kWh)
  - Peak: 06:00-22:00 (€0.35/kWh)

### Dynamic Pricing
- **Description**: Rates vary based on market conditions
- **Best For**: Maximum savings with active management
- **Optimization Potential**: Very High (20-40% savings possible)
- **Requires**: Smart home integration and monitoring

### Real-Time Pricing
- **Description**: Rates change hourly based on grid conditions
- **Best For**: Advanced smart home systems
- **Optimization Potential**: Maximum (30-50% savings possible)
- **Requires**: Real-time monitoring and automated control

## API Endpoints

### 1. Optimize Heating Schedule

**Endpoint**: `POST /api/v1/tariff-optimization/optimize`

**Request**:
```json
{
  "tariff_structure": {
    "tariff_id": "tou_001",
    "name": "Standard TOU",
    "type": "time_of_use",
    "base_rate": 0.30,
    "periods": [
      {
        "start_time": "22:00:00",
        "end_time": "06:00:00",
        "rate": 0.18,
        "name": "off-peak"
      },
      {
        "start_time": "06:00:00",
        "end_time": "22:00:00",
        "rate": 0.35,
        "name": "peak"
      }
    ]
  },
  "heat_pump_cop": 3.5,
  "annual_heating_demand": 12000,
  "current_schedule": [
    {
      "hour": 0,
      "target_temperature": 19.0,
      "priority": 1,
      "flexible": true
    }
    // ... 23 more hours
  ],
  "comfort_priority": 0.7
}
```

**Response**:
```json
{
  "original_cost": 1200.50,
  "optimized_cost": 950.30,
  "savings": 250.20,
  "savings_percent": 20.8,
  "optimized_schedule": [
    {
      "hour": 0,
      "target_temperature": 19.0,
      "estimated_consumption": 1.2,
      "tariff_rate": 0.18,
      "cost": 0.216,
      "shifted_from": null
    }
    // ... 23 more hours
  ],
  "peak_load_reduction": 1.5,
  "comfort_score": 0.85
}
```

### 2. Compare Tariffs

**Endpoint**: `POST /api/v1/tariff-optimization/compare-tariffs`

**Request**:
```json
{
  "tariffs": [
    {
      "tariff_id": "flat_001",
      "name": "Flat Rate",
      "type": "flat_rate",
      "base_rate": 0.30,
      "periods": []
    },
    {
      "tariff_id": "tou_001",
      "name": "Time of Use",
      "type": "time_of_use",
      "base_rate": 0.30,
      "periods": [...]
    }
  ],
  "annual_heating_demand": 12000,
  "heat_pump_cop": 3.5
}
```

**Response**:
```json
[
  {
    "tariff_name": "Time of Use",
    "tariff_type": "time_of_use",
    "annual_cost": 950.30,
    "potential_savings": 250.20,
    "recommended": true,
    "pros": [
      "Predictable rates with clear peak/off-peak periods",
      "Good savings potential with flexible heating schedule"
    ],
    "cons": [
      "Requires schedule adjustment"
    ]
  },
  {
    "tariff_name": "Flat Rate",
    "tariff_type": "flat_rate",
    "annual_cost": 1200.50,
    "potential_savings": 0.00,
    "recommended": false,
    "pros": [
      "Simple and predictable",
      "No schedule optimization needed"
    ],
    "cons": [
      "No savings from load shifting"
    ]
  }
]
```

### 3. Evaluate Demand Response Event

**Endpoint**: `POST /api/v1/tariff-optimization/demand-response/evaluate`

**Request**:
```json
{
  "event": {
    "event_id": "dr_20240115_001",
    "start_time": "2024-01-15T18:00:00",
    "end_time": "2024-01-15T20:00:00",
    "incentive_rate": 0.75,
    "required_reduction": 3.0
  },
  "current_schedule": [...]
}
```

**Response**:
```json
{
  "can_participate": true,
  "current_load": 4.5,
  "reduction_achieved": 3.0,
  "adjusted_schedule": [
    {
      "hour": 18,
      "target_temperature": 19.0,
      "reduced": true
    },
    {
      "hour": 19,
      "target_temperature": 19.0,
      "reduced": true
    }
  ],
  "incentive_earnings": 4.50,
  "recommendation": "participate"
}
```

### 4. Monitor Real-Time Tariff

**Endpoint**: `POST /api/v1/tariff-optimization/real-time/monitor`

**Request**:
```json
{
  "tariff_data": {
    "timestamp": "2024-01-15T14:30:00",
    "current_rate": 0.22,
    "forecast_next_hour": 0.28,
    "forecast_next_4_hours": [0.28, 0.32, 0.35, 0.30],
    "forecast_next_24_hours": [...],
    "grid_load_level": "medium"
  },
  "current_schedule": [...]
}
```

**Response**:
```json
{
  "current_rate": 0.22,
  "average_forecast": 0.30,
  "is_favorable": true,
  "recommendation": "Increase heating now - rates are favorable",
  "action": "increase_temperature",
  "optimal_hours_next_24h": [0, 1, 2, 3, 4, 5, 22, 23],
  "grid_load_level": "medium",
  "savings_opportunity": 0.80
}
```

## Optimization Strategies

### 1. Load Shifting
- Moves flexible heating loads to cheaper time periods
- Considers building thermal mass for pre-heating
- Maintains comfort during occupied hours
- Reduces heating during expensive peak periods

### 2. Peak Shaving
- Reduces peak electricity demand
- Spreads heating load more evenly
- Can reduce demand charges
- Improves grid stability

### 3. Thermal Mass Utilization
- Pre-heats building during cheap periods
- Allows coasting through expensive periods
- Maintains comfort with stored heat
- Maximizes savings potential

### 4. Comfort Balancing
- Adjustable comfort priority (0-1 scale)
- 0 = Maximum cost savings
- 1 = Maximum comfort
- 0.7 = Balanced (recommended default)

## Best Practices

### 1. Schedule Optimization
- Review and adjust schedule monthly
- Consider seasonal heating patterns
- Update for lifestyle changes
- Monitor actual vs. predicted savings

### 2. Tariff Selection
- Compare all available tariffs annually
- Consider switching during low-rate periods
- Factor in contract terms and fees
- Monitor for new tariff offerings

### 3. Demand Response
- Participate when comfortable
- Pre-heat before events when possible
- Monitor incentive earnings
- Adjust participation based on weather

### 4. Real-Time Monitoring
- Check rates during high-cost periods
- Adjust heating based on forecasts
- Use automation when available
- Track savings over time

## Example Use Cases

### Use Case 1: Standard TOU Optimization
**Scenario**: Home with flexible heating schedule
**Tariff**: Time-of-use with night discount
**Strategy**: Shift heating to night hours
**Expected Savings**: 15-25%

### Use Case 2: Demand Response Participation
**Scenario**: Grid stress event on cold day
**Event**: 2-hour reduction request with incentive
**Strategy**: Pre-heat before event, reduce during
**Expected Earnings**: €5-10 per event

### Use Case 3: Dynamic Pricing
**Scenario**: Smart home with automated control
**Tariff**: Hourly dynamic pricing
**Strategy**: Continuous optimization based on forecasts
**Expected Savings**: 25-35%

## Integration Examples

### Python Integration
```python
from services.tariff_optimization_service import TariffOptimizationService
from models.tariff_schemas import *

# Create service
service = TariffOptimizationService()

# Define tariff
tariff = TariffStructure(
    tariff_id="tou_001",
    name="Standard TOU",
    type=TariffType.TIME_OF_USE,
    base_rate=0.30,
    periods=[...]
)

# Create schedule
schedule = [
    HeatingSchedule(hour=h, target_temperature=20.0, flexible=True)
    for h in range(24)
]

# Optimize
request = OptimizationRequest(
    tariff_structure=tariff,
    heat_pump_cop=3.5,
    annual_heating_demand=12000,
    current_schedule=schedule,
    comfort_priority=0.7
)

result = service.optimize_schedule(request)
print(f"Annual savings: €{result.savings:.2f}")
```

### REST API Integration
```javascript
// Optimize schedule
const response = await fetch('/api/v1/tariff-optimization/optimize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tariff_structure: {...},
    heat_pump_cop: 3.5,
    annual_heating_demand: 12000,
    current_schedule: [...],
    comfort_priority: 0.7
  })
});

const result = await response.json();
console.log(`Savings: €${result.savings.toFixed(2)}`);
```

## Troubleshooting

### Issue: Low Savings
**Possible Causes**:
- High comfort priority setting
- Limited flexible hours in schedule
- Tariff structure not suitable for optimization
- Building has low thermal mass

**Solutions**:
- Reduce comfort priority to 0.5-0.6
- Mark more hours as flexible
- Consider switching to TOU or dynamic tariff
- Improve building insulation

### Issue: Comfort Complaints
**Possible Causes**:
- Comfort priority too low
- Too much load shifting
- Insufficient pre-heating

**Solutions**:
- Increase comfort priority to 0.8-0.9
- Mark critical hours as non-flexible
- Enable pre-heating during cheap periods

### Issue: Unexpected Costs
**Possible Causes**:
- Tariff rates changed
- Actual consumption higher than estimated
- COP lower than specified

**Solutions**:
- Update tariff structure in system
- Recalibrate consumption estimates
- Verify heat pump COP rating

## Support

For questions or issues:
- Email: support@solar-calculator-pro.com
- Documentation: https://docs.solar-calculator-pro.com
- API Reference: https://api.solar-calculator-pro.com/docs
