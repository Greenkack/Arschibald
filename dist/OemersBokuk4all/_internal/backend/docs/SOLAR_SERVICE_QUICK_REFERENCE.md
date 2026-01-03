# Solar Calculator Service - Quick Reference

## Quick Start

```python
from backend.services.solar_service import get_solar_service
from backend.models.solar_schemas import SolarCalculationRequest

# Get service instance
service = get_solar_service()

# Create request
request = SolarCalculationRequest(
    latitude=48.1351,
    longitude=11.5820,
    roof_orientation="Süd",
    roof_inclination_deg=30.0,
    module_quantity=20,
    module_capacity_w=350.0,
    annual_consumption_kwh_yr=4000.0,
    electricity_price_kwh=0.30
)

# Calculate
result = service.calculate_solar_system(request)

# Access results
print(f"System Size: {result.system_sizing.system_size_kwp} kWp")
print(f"Annual Production: {result.energy_production.annual_production_kwh} kWh")
print(f"Payback: {result.economic_analysis.payback_period_years} years")
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/solar/calculate` | Calculate solar system | Yes |
| GET | `/api/v1/solar/health` | Health check | No |
| GET | `/api/v1/solar/cache/stats` | Cache statistics | Yes |
| DELETE | `/api/v1/solar/cache` | Clear cache | Yes |

## Request Parameters

### Minimal Request
```json
{
  "module_quantity": 20,
  "annual_consumption_kwh_yr": 4000.0
}
```

### Complete Request
```json
{
  "customer_name": "Max Mustermann",
  "latitude": 48.1351,
  "longitude": 11.5820,
  "roof_area_m2": 50.0,
  "roof_orientation": "Süd",
  "roof_inclination_deg": 30.0,
  "module_quantity": 20,
  "module_capacity_w": 350.0,
  "annual_consumption_kwh_yr": 4000.0,
  "electricity_price_kwh": 0.30,
  "include_storage": true,
  "selected_storage_capacity_kwh": 10.0
}
```

## Response Structure

```json
{
  "system_sizing": {
    "system_size_kwp": 7.0,
    "module_count": 20,
    "specific_yield_kwh_kwp": 1000.0
  },
  "energy_production": {
    "annual_production_kwh": 7000.0,
    "pvgis_data_used": true
  },
  "self_consumption": {
    "annual_self_consumption_kwh": 3500.0,
    "self_consumption_rate_percent": 50.0,
    "autarky_degree_percent": 87.5
  },
  "economic_analysis": {
    "total_investment_cost_net": 10500.0,
    "payback_period_years": 10.0,
    "total_savings_20years": 25000.0
  },
  "environmental_impact": {
    "annual_co2_savings_kg": 3318.0,
    "equivalent_trees": 265
  }
}
```

## Roof Orientations

- `Süd` - South
- `Südost` - Southeast
- `Südwest` - Southwest
- `Ost` - East
- `West` - West
- `Nord` - North
- `Nordost` - Northeast
- `Nordwest` - Northwest
- `Flachdach` - Flat roof
- `Sonstige` - Other

## Common Use Cases

### Basic Calculation
```python
request = SolarCalculationRequest(
    module_quantity=20,
    annual_consumption_kwh_yr=4000.0
)
result = service.calculate_solar_system(request)
```

### With PVGIS
```python
request = SolarCalculationRequest(
    latitude=48.1351,
    longitude=11.5820,
    module_quantity=20,
    annual_consumption_kwh_yr=4000.0,
    use_pvgis=True
)
result = service.calculate_solar_system(request)
```

### With Battery Storage
```python
request = SolarCalculationRequest(
    module_quantity=20,
    annual_consumption_kwh_yr=4000.0,
    include_storage=True,
    selected_storage_capacity_kwh=10.0
)
result = service.calculate_solar_system(request)
```

### Custom Economic Parameters
```python
request = SolarCalculationRequest(
    module_quantity=20,
    annual_consumption_kwh_yr=4000.0,
    simulation_period_years=25,
    electricity_price_increase_annual_percent=5.0
)
result = service.calculate_solar_system(request)
```

## Error Handling

```python
try:
    result = service.calculate_solar_system(request)
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Calculation failed: {e}")
```

## Cache Management

```python
# Get cache stats
stats = service.get_cache_stats()
print(f"Cache entries: {stats['total_entries']}")

# Clear cache
count = service.clear_cache()
print(f"Cleared {count} entries")
```

## Health Check

```python
health = service.health_check()
if health.is_healthy():
    print("Service is healthy")
else:
    print(f"Service unhealthy: {health.message}")
```

## Testing

```bash
# Run all tests
pytest backend/tests/test_solar_service.py -v

# Run specific test
pytest backend/tests/test_solar_service.py::TestSolarCalculatorService::test_calculate_solar_system_basic -v

# Run with coverage
pytest backend/tests/test_solar_service.py --cov=backend/services/solar_service --cov-report=html
```

## Performance Tips

1. **Use Caching**: Identical requests are cached for 5 minutes
2. **Provide Coordinates**: PVGIS is faster than manual calculation
3. **Batch Requests**: Group similar calculations together
4. **Monitor Cache**: Check cache stats regularly

## Common Issues

| Issue | Solution |
|-------|----------|
| Service not initialized | Call `service.initialize()` |
| PVGIS not working | Check coordinates, falls back to manual |
| Slow calculations | Check if caching is enabled |
| Invalid coordinates | Provide valid lat/lon or use manual mode |

## Environment Variables

```bash
# Backend configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000
DEBUG=true

# Database
DATABASE_URL=sqlite:///./solar_calculator.db

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## Related Files

- Service: `backend/services/solar_service.py`
- Models: `backend/models/solar_schemas.py`
- API: `backend/api/v1/solar.py`
- Tests: `backend/tests/test_solar_service.py`
- Legacy: `calculations.py`
