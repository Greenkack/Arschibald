# Combined Heat Pump + PV System - Quick Reference

## Quick Start

```python
from backend.services.combined_system_service import CombinedSystemService
from backend.models.combined_system_schemas import CombinedSystemRequest, ControlStrategy

service = CombinedSystemService()

# Analyze combined system
result = service.analyze_combined_system(CombinedSystemRequest(
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
))

print(f"Annual Savings: €{result.financial_analysis.annual_savings:.2f}")
print(f"Self-Consumption: {result.self_consumption_rate * 100:.1f}%")
print(f"Payback: {result.financial_analysis.simple_payback_years:.1f} years")
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/combined-system/analyze` | POST | Analyze combined system |
| `/api/v1/combined-system/optimize` | POST | Optimize operation |
| `/api/v1/combined-system/monitoring/{id}` | GET | Get monitoring data |

## Control Strategies

| Strategy | Goal | Best For |
|----------|------|----------|
| `SELF_CONSUMPTION` | Maximize PV use | High electricity prices |
| `COST_OPTIMIZATION` | Minimize costs | Variable tariffs |
| `GRID_INDEPENDENCE` | Minimize grid use | Unreliable grid |
| `COMFORT_PRIORITY` | Ensure comfort | Comfort-focused users |
| `BALANCED` | Balance all | Most users |

## Key Metrics

### Self-Consumption Rate
```
= PV Energy Used Locally / Total PV Production
Target: > 70%
```

### Grid Independence
```
= 1 - (Grid Import / Total Consumption)
Target: > 60%
```

### Heating Independence
```
= PV Energy for Heating / HP Consumption
Target: > 50%
```

## Synergy Benefits

1. **Direct PV to Heat Pump**: PV energy directly powering heat pump
2. **Battery-Mediated**: PV energy stored and used later for heating
3. **Cost Reduction**: Lower heating costs through PV integration
4. **COP Improvement**: Effective heat pump efficiency increase
5. **Grid Independence**: Reduced reliance on electrical grid

## Financial Metrics

- **Total Investment**: PV + HP + Battery + Installation
- **Annual Savings**: Baseline costs - Combined system costs
- **Payback Period**: Investment / Annual Savings
- **NPV**: Net Present Value over 20 years
- **IRR**: Internal Rate of Return
- **LCOE**: Levelized Cost of Energy

## Optimization Tips

### System Sizing
- **PV**: 100-120% of annual consumption
- **Battery**: 0.5-1.0 kWh per kWp PV
- **Heat Pump**: Size for peak load

### Control Settings
- Enable smart control
- Use self-consumption strategy
- Monitor performance
- Adjust based on results

### Operational
- Shift HP to PV hours
- Use battery for peaks
- Maintain comfort
- Regular monitoring

## Common Issues

### Low Self-Consumption (< 60%)
**Fix**: Adjust HP schedule, increase battery, enable smart control

### High Grid Import (> 40%)
**Fix**: Increase PV size, add battery, optimize load profile

### Poor ROI (> 15 years)
**Fix**: Optimize sizing, improve self-consumption, review costs

## Performance Targets

| Metric | Good | Excellent |
|--------|------|-----------|
| Self-Consumption | 70% | 80% |
| Grid Independence | 60% | 75% |
| Heating Independence | 50% | 70% |
| Payback Period | < 12 years | < 10 years |
| Annual Savings | > €2000 | > €3000 |

## Example Results

### Typical 10 kWp PV + 8 kW Heat Pump System
- **Investment**: €28,000
- **Annual Savings**: €2,500
- **Payback**: 11.2 years
- **Self-Consumption**: 75%
- **Grid Independence**: 70%
- **CO2 Savings**: 4,500 kg/year

## Integration Checklist

- [ ] Size PV system appropriately
- [ ] Select heat pump with good COP
- [ ] Add battery storage (recommended)
- [ ] Configure control strategy
- [ ] Set up monitoring
- [ ] Enable smart control
- [ ] Review performance monthly
- [ ] Adjust settings as needed

## Quick Commands

```bash
# Analyze system
curl -X POST http://localhost:8000/api/v1/combined-system/analyze \
  -H "Content-Type: application/json" \
  -d @system_config.json

# Get monitoring data
curl http://localhost:8000/api/v1/combined-system/monitoring/1

# Optimize operation
curl -X POST http://localhost:8000/api/v1/combined-system/optimize \
  -H "Content-Type: application/json" \
  -d '{"system_id": 1, "optimization_goal": "minimize_cost"}'
```

## Support Resources

- **Full Guide**: COMBINED_SYSTEM_GUIDE.md
- **API Docs**: http://localhost:8000/docs
- **Examples**: backend/demo_combined_system.py
- **Tests**: backend/tests/test_combined_system_service.py
