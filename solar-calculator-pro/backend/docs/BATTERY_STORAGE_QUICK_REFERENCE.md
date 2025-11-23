# Battery Storage Service - Quick Reference

## Quick Start

```python
from services.battery_storage_service import BatteryStorageService, BatterySizingRequest

service = BatteryStorageService()

# Calculate battery sizing
request = BatterySizingRequest(
    daily_consumption_kwh=15.0,
    pv_system_size_kwp=10.0,
    annual_production_kwh=10000.0,
    self_consumption_rate=0.35,
    grid_feed_in_tariff=0.08,
    electricity_price=0.30
)

result = service.calculate_battery_sizing(request)
print(f"Recommended: {result['recommended_capacity_kwh']} kWh")
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/battery/sizing` | POST | Calculate optimal battery size |
| `/api/v1/battery/roi` | POST | Analyze return on investment |
| `/api/v1/battery/discharge-strategy` | POST | Simulate discharge strategies |
| `/api/v1/battery/grid-independence` | POST | Calculate grid independence |
| `/api/v1/battery/lifecycle` | POST | Analyze battery lifecycle |
| `/api/v1/battery/monitoring-integration` | POST | Get monitoring config |
| `/api/v1/battery/battery-specs` | GET | Get available battery specs |

## Key Features

### 1. Battery Sizing
- ✅ Optimal capacity calculation
- ✅ Backup power sizing
- ✅ Self-sufficiency targeting
- ✅ Performance predictions

### 2. ROI Analysis
- ✅ Payback period
- ✅ NPV calculation
- ✅ Lifetime savings
- ✅ Cash flow with degradation

### 3. Discharge Strategies
- ✅ Self-consumption
- ✅ Peak shaving
- ✅ Time-of-use optimization
- ✅ Backup mode

### 4. Grid Independence
- ✅ Self-sufficiency rate
- ✅ Monthly analysis
- ✅ Battery contribution
- ✅ Improvement metrics

### 5. Lifecycle Analysis
- ✅ Capacity degradation
- ✅ Replacement schedule
- ✅ Total cost of ownership
- ✅ Warranty tracking

### 6. Monitoring Integration
- ✅ Real-time data points
- ✅ Alert thresholds
- ✅ System-specific configs
- ✅ API endpoints

## Battery Specs

| Size | Capacity | Usable | Max Power | Cost/kWh |
|------|----------|--------|-----------|----------|
| Small | 5 kWh | 4.5 kWh | 2.5 kW | €800 |
| Medium | 10 kWh | 9.0 kWh | 5.0 kW | €750 |
| Large | 15 kWh | 13.5 kWh | 7.5 kW | €700 |

All batteries: 95% efficiency, 90% DoD, 10-year warranty, 6000 cycles

## Discharge Strategies

| Strategy | Use Case | Key Benefit |
|----------|----------|-------------|
| Self-Consumption | Maximize solar usage | Highest self-sufficiency |
| Peak Shaving | Reduce peak demand | Lower demand charges |
| Time-of-Use | Variable pricing | Arbitrage savings |
| Backup | Emergency power | Grid independence |

## Common Calculations

### Sizing for Backup
```python
backup_capacity = (daily_consumption_kwh / 24) * backup_hours / 0.9
```

### Sizing for Self-Sufficiency
```python
additional_storage = daily_deficit * target_self_sufficiency / 0.9
```

### Annual Savings
```python
annual_savings = daily_stored_energy * 365 * (electricity_price - feed_in_tariff)
```

### Payback Period
```python
payback_years = initial_cost / annual_savings
```

## Monitoring Data Points

### Real-Time (5s intervals)
- State of charge (%)
- Power flow (kW)
- Voltage (V)
- Current (A)
- Temperature (°C)

### Historical (15min intervals)
- Daily cycles
- Energy charged/discharged (kWh)
- Efficiency (%)
- Capacity remaining (%)

### Lifecycle (daily)
- Total cycles
- Total energy throughput (kWh)
- Capacity degradation (%)
- Warranty status (%)

## Alert Thresholds

### Critical
- SOC < 10%
- Temperature > 50°C
- Low voltage

### Warning
- SOC < 20%
- Temperature > 40°C
- Efficiency < 85%
- Capacity < 80%

### Info
- Daily cycles > 2
- Approaching warranty limit

## Example Requests

### Battery Sizing
```bash
curl -X POST http://localhost:8000/api/v1/battery/sizing \
  -H "Content-Type: application/json" \
  -d '{
    "daily_consumption_kwh": 15.0,
    "pv_system_size_kwp": 10.0,
    "annual_production_kwh": 10000.0,
    "self_consumption_rate": 0.35,
    "grid_feed_in_tariff": 0.08,
    "electricity_price": 0.30,
    "target_self_sufficiency": 0.8
  }'
```

### ROI Analysis
```bash
curl -X POST http://localhost:8000/api/v1/battery/roi \
  -H "Content-Type: application/json" \
  -d '{
    "battery_capacity_kwh": 10.0,
    "daily_consumption_kwh": 15.0,
    "pv_system_size_kwp": 10.0,
    "annual_production_kwh": 10000.0,
    "self_consumption_rate": 0.35,
    "grid_feed_in_tariff": 0.08,
    "electricity_price": 0.30,
    "analysis_years": 20
  }'
```

### Get Battery Specs
```bash
curl http://localhost:8000/api/v1/battery/battery-specs
```

## Performance Metrics

| Operation | Response Time |
|-----------|---------------|
| Battery Sizing | < 100ms |
| ROI Analysis | < 200ms |
| Discharge Strategy | < 150ms |
| Grid Independence | < 200ms |
| Lifecycle Analysis | < 250ms |

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid input |
| 500 | Server error |

## Testing

```bash
# Run all tests
pytest tests/test_battery_storage_service.py -v

# Run specific test
pytest tests/test_battery_storage_service.py::TestBatterySizing::test_basic_sizing -v

# Run with coverage
pytest tests/test_battery_storage_service.py --cov=services.battery_storage_service
```

## Integration Example

```python
# Complete workflow
from services.battery_storage_service import BatteryStorageService, BatterySizingRequest

service = BatteryStorageService()

# 1. Size battery
sizing_request = BatterySizingRequest(
    daily_consumption_kwh=15.0,
    pv_system_size_kwp=10.0,
    annual_production_kwh=10000.0,
    self_consumption_rate=0.35,
    grid_feed_in_tariff=0.08,
    electricity_price=0.30,
    target_self_sufficiency=0.8
)
sizing = service.calculate_battery_sizing(sizing_request)

# 2. Analyze ROI
battery_specs = service.default_battery_specs[sizing['selected_battery']]
roi = service.calculate_battery_roi(battery_specs, sizing_request, 20)

# 3. Simulate strategy
hourly_production = [0, 0, 0, 0, 0, 0.5, 2, 4, 6, 8, 9, 10, 9, 8, 6, 4, 2, 0.5, 0, 0, 0, 0, 0, 0]
hourly_consumption = [1, 1, 1, 1, 1, 2, 3, 2, 1.5, 1, 1, 1.5, 2, 1.5, 1, 1.5, 2, 3, 4, 3, 2, 1.5, 1, 1]

from services.battery_storage_service import DischargeStrategy
strategy = DischargeStrategy(strategy_type='self_consumption')
discharge = service.calculate_discharge_strategy(
    strategy, battery_specs, hourly_production, hourly_consumption
)

print(f"Battery: {sizing['recommended_capacity_kwh']} kWh")
print(f"Payback: {roi['simple_payback_years']} years")
print(f"Daily efficiency: {discharge['performance']['round_trip_efficiency_percent']}%")
```

## Requirements

- Requirements: 1.3, 6.1
- Python 3.10+
- FastAPI 0.100+
- Pydantic 2.0+

## Related Documentation

- [Battery Storage Guide](BATTERY_STORAGE_GUIDE.md)
- [Solar Calculator Service](SOLAR_CALCULATOR_ADVANCED_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
