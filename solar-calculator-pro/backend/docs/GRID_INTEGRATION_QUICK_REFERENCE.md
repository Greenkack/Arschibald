# Grid Integration Quick Reference

## Quick Start

```python
from backend.services.grid_integration_service import GridIntegrationService
from backend.models.grid_schemas import GridIntegrationAnalysisRequest

service = GridIntegrationService()

# Comprehensive analysis
request = GridIntegrationAnalysisRequest(
    system_size_kwp=10.0,
    annual_production_kwh=12000,
    annual_consumption_kwh=10000,
    location="Your Location",
    connection_type="three_phase",
    metering_type="net_metering",
    feed_in_tariff_per_kwh=0.10,
    electricity_price_per_kwh=0.30,
    grid_voltage=400,
    distance_to_grid_m=50
)

result = service.comprehensive_grid_analysis(request)
```

## Common Calculations

### Feed-in Tariff
```python
from backend.models.grid_schemas import FeedInTariffRequest

result = service.calculate_feed_in_tariff(FeedInTariffRequest(
    system_size_kwp=10.0,
    annual_production_kwh=12000,
    self_consumption_rate=0.3,
    feed_in_tariff_per_kwh=0.10,
    electricity_price_per_kwh=0.30,
    contract_duration_years=20
))
# Returns: annual/lifetime revenue, savings, payback period
```

### Net Metering
```python
from backend.models.grid_schemas import NetMeteringRequest

result = service.analyze_net_metering(NetMeteringRequest(
    system_size_kwp=10.0,
    annual_production_kwh=12000,
    annual_consumption_kwh=10000,
    electricity_price_per_kwh=0.30,
    net_metering_credit_per_kwh=0.27,
    monthly_production=[1000]*12,
    monthly_consumption=[833]*12
))
# Returns: monthly analysis, self-sufficiency, savings
```

### Grid Connection
```python
from backend.models.grid_schemas import GridConnectionRequest, GridConnectionType

result = service.calculate_grid_connection_requirements(GridConnectionRequest(
    system_size_kwp=10.0,
    connection_type=GridConnectionType.THREE_PHASE,
    voltage_level=400,
    distance_to_grid_m=50,
    inverter_power_kw=10.0,
    location="Your Location"
))
# Returns: cable size, cost, voltage drop, protection devices
```

### Power Quality
```python
from backend.models.grid_schemas import PowerQualityRequest, PowerQualityStandard

result = service.analyze_power_quality(PowerQualityRequest(
    system_size_kwp=10.0,
    inverter_specs={"rated_power_kw": 10.0, "power_factor": 0.99, "thd": 0.03},
    grid_voltage=400,
    standard=PowerQualityStandard.VDE_AR_N_4105
))
# Returns: compliance status, THD, power factor, issues
```

### Grid Stability
```python
from backend.models.grid_schemas import GridStabilityRequest

result = service.calculate_grid_stability(GridStabilityRequest(
    system_size_kwp=10.0,
    grid_short_circuit_power_mva=50.0,
    grid_impedance_ohm=0.1,
    inverter_response_time_ms=50
))
# Returns: stability index, SCR, grid services, concerns
```

### Smart Grid
```python
from backend.models.grid_schemas import SmartGridRequest

result = service.analyze_smart_grid_integration(SmartGridRequest(
    system_size_kwp=10.0,
    battery_capacity_kwh=10.0,
    enable_demand_response=True,
    enable_frequency_regulation=True
))
# Returns: services, revenue streams, payback period
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/grid/feed-in-tariff` | POST | Feed-in tariff calculations |
| `/api/v1/grid/net-metering` | POST | Net metering analysis |
| `/api/v1/grid/connection-requirements` | POST | Connection requirements |
| `/api/v1/grid/power-quality` | POST | Power quality analysis |
| `/api/v1/grid/grid-stability` | POST | Grid stability calculations |
| `/api/v1/grid/smart-grid` | POST | Smart grid integration |
| `/api/v1/grid/comprehensive-analysis` | POST | Complete analysis |

## Key Metrics

### Financial
- **Annual Feed-in Revenue**: Income from excess energy
- **Self-consumption Savings**: Savings from using own energy
- **Payback Period**: Years to recover investment
- **Lifetime Benefit**: Total 20-year benefit

### Technical
- **Cable Size**: Required cable cross-section (mm²)
- **Voltage Drop**: Percentage voltage drop
- **Power Factor**: Ratio of real to apparent power
- **THD**: Total Harmonic Distortion (%)
- **SCR**: Short Circuit Ratio (grid strength)

### Performance
- **Self-sufficiency Rate**: Production / Consumption
- **Grid Independence**: 1 - (Import / Consumption)
- **Stability Index**: Overall grid stability (0-1)
- **Feasibility Score**: Overall feasibility (0-100)

## Connection Types

- **SINGLE_PHASE**: Up to 10 kWp, 230V
- **THREE_PHASE**: 10+ kWp, 400V
- **MICRO_GRID**: Off-grid or islanded systems

## Metering Types

- **NET_METERING**: Credits for excess energy
- **FEED_IN_TARIFF**: Fixed payment for excess
- **GROSS_METERING**: All production metered
- **SELF_CONSUMPTION**: Maximize on-site use

## Power Quality Standards

- **IEEE_1547**: US standard
- **EN_50160**: European voltage characteristics
- **VDE_AR_N_4105**: German grid connection
- **IEC_61727**: PV utility interface

## Typical Values

### Feed-in Tariffs (Germany)
- Residential (<10 kWp): €0.08-0.12/kWh
- Commercial (10-40 kWp): €0.07-0.10/kWh
- Large (40+ kWp): €0.06-0.08/kWh

### Electricity Prices (Germany)
- Residential: €0.30-0.35/kWh
- Commercial: €0.20-0.25/kWh
- Industrial: €0.15-0.20/kWh

### System Degradation
- Standard: 0.5% per year
- Premium: 0.3% per year
- Budget: 0.7% per year

### Cable Sizing
- 5 kWp @ 50m: 6-10 mm²
- 10 kWp @ 50m: 10-16 mm²
- 15 kWp @ 100m: 25-35 mm²

### Grid Strength (SCR)
- Very Strong: SCR > 20
- Strong: SCR 10-20
- Medium: SCR 5-10
- Weak: SCR 3-5
- Very Weak: SCR < 3

## Error Handling

```python
try:
    result = service.calculate_feed_in_tariff(request)
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Calculation error: {e}")
```

## German Formatting

All outputs use German number formatting:
```python
# Currency
16.999,00 €  # Not 16,999.00 €

# Percentages
85,5%  # Not 85.5%

# Energy
12.500 kWh  # Not 12,500 kWh
```

## Common Issues

### Issue: High voltage drop
**Solution**: Increase cable size or reduce distance

### Issue: Power quality non-compliant
**Solution**: Check inverter specs, add filters

### Issue: Low stability index
**Solution**: Enable grid support services

### Issue: Low smart grid revenue
**Solution**: Add battery storage, enable more services

## Testing

```bash
# Run tests
pytest backend/tests/test_grid_integration_service.py -v

# Run specific test
pytest backend/tests/test_grid_integration_service.py::TestFeedInTariff -v

# Run with coverage
pytest backend/tests/test_grid_integration_service.py --cov=backend/services/grid_integration_service
```

## Support

For issues or questions:
1. Check the full guide: `GRID_INTEGRATION_GUIDE.md`
2. Review API documentation: `/api/v1/docs`
3. Check test examples: `test_grid_integration_service.py`
