# Solar Calculator Service Guide

## Overview

The Solar Calculator Service wraps the legacy `calculations.py` module and provides a modern, type-safe API for solar system calculations. It includes input validation, caching, error handling, and comprehensive logging.

## Features

- **Type-Safe API**: Uses Pydantic models for request/response validation
- **Intelligent Caching**: Caches calculation results for 5 minutes to improve performance
- **PVGIS Integration**: Automatically uses PVGIS for accurate yield calculations when coordinates are provided
- **Comprehensive Results**: Returns system sizing, energy production, economics, and environmental impact
- **Battery Storage Support**: Includes analysis for battery storage systems
- **Error Handling**: Robust error handling with detailed error messages
- **Health Checks**: Built-in health check endpoint for monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Endpoint                          │
│                  /api/v1/solar/calculate                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              SolarCalculatorService                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Input Validation (Pydantic)                         │ │
│  │  • Cache Check                                         │ │
│  │  • Transform Request → Legacy Format                   │ │
│  │  • Call Legacy calculations.py                         │ │
│  │  • Transform Results → Modern Format                   │ │
│  │  • Cache Result                                        │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Legacy calculations.py                          │
│  • perform_calculations()                                    │
│  • get_pvgis_data()                                         │
│  • All existing calculation logic                           │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### POST /api/v1/solar/calculate

Calculate solar system performance and economics.

**Request Body:**
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
  "include_storage": false
}
```

**Response:**
```json
{
  "calculation_timestamp": "2024-01-15T10:30:00",
  "calculation_duration_ms": 245.5,
  "system_sizing": {
    "system_size_kwp": 7.0,
    "module_count": 20,
    "module_capacity_w": 350.0,
    "specific_yield_kwh_kwp": 1000.0
  },
  "energy_production": {
    "annual_production_kwh": 7000.0,
    "monthly_production_kwh": {...},
    "pvgis_data_used": true,
    "pvgis_source": "PVGIS"
  },
  "self_consumption": {
    "annual_self_consumption_kwh": 3500.0,
    "self_consumption_rate_percent": 50.0,
    "autarky_degree_percent": 87.5,
    "annual_grid_feed_in_kwh": 3500.0,
    "annual_grid_purchase_kwh": 500.0
  },
  "economic_analysis": {
    "total_investment_cost_net": 10500.0,
    "total_investment_cost_gross": 12495.0,
    "annual_savings_year1": 1050.0,
    "payback_period_years": 10.0,
    "total_savings_20years": 25000.0,
    "total_savings_25years": 32000.0,
    "annual_feed_in_revenue": 280.0
  },
  "environmental_impact": {
    "annual_co2_savings_kg": 3318.0,
    "total_co2_savings_25years_kg": 82950.0,
    "equivalent_trees": 265,
    "equivalent_car_km": 27650.0
  },
  "warnings": [],
  "errors": []
}
```

### GET /api/v1/solar/health

Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "Service is healthy",
  "details": {
    "cache_size": 5,
    "cache_ttl_seconds": 300
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET /api/v1/solar/cache/stats

Get cache statistics (requires authentication).

**Response:**
```json
{
  "total_entries": 5,
  "cache_ttl_seconds": 300,
  "oldest_entry_age_seconds": 120.5
}
```

### DELETE /api/v1/solar/cache

Clear calculation cache (requires authentication).

**Response:**
```json
{
  "message": "Cleared 5 cache entries",
  "count": 5
}
```

## Usage Examples

### Python Client

```python
import requests

# Prepare calculation request
request_data = {
    "customer_name": "Max Mustermann",
    "latitude": 48.1351,
    "longitude": 11.5820,
    "roof_orientation": "Süd",
    "roof_inclination_deg": 30.0,
    "module_quantity": 20,
    "module_capacity_w": 350.0,
    "annual_consumption_kwh_yr": 4000.0,
    "electricity_price_kwh": 0.30
}

# Make API call
response = requests.post(
    "http://localhost:8000/api/v1/solar/calculate",
    json=request_data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Process results
if response.status_code == 200:
    result = response.json()
    print(f"System Size: {result['system_sizing']['system_size_kwp']} kWp")
    print(f"Annual Production: {result['energy_production']['annual_production_kwh']} kWh")
    print(f"Payback Period: {result['economic_analysis']['payback_period_years']} years")
else:
    print(f"Error: {response.json()['detail']}")
```

### JavaScript/TypeScript Client

```typescript
interface SolarCalculationRequest {
  customer_name?: string;
  latitude?: number;
  longitude?: number;
  roof_orientation: string;
  roof_inclination_deg: number;
  module_quantity: number;
  module_capacity_w?: number;
  annual_consumption_kwh_yr: number;
  electricity_price_kwh: number;
  include_storage?: boolean;
}

async function calculateSolarSystem(request: SolarCalculationRequest) {
  const response = await fetch('http://localhost:8000/api/v1/solar/calculate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    throw new Error(`Calculation failed: ${response.statusText}`);
  }
  
  return await response.json();
}

// Usage
const result = await calculateSolarSystem({
  roof_orientation: "Süd",
  roof_inclination_deg: 30,
  module_quantity: 20,
  module_capacity_w: 350,
  annual_consumption_kwh_yr: 4000,
  electricity_price_kwh: 0.30
});

console.log(`System Size: ${result.system_sizing.system_size_kwp} kWp`);
```

## Input Parameters

### Required Parameters

- `module_quantity`: Number of PV modules (integer, >= 0)
- `annual_consumption_kwh_yr`: Annual household consumption in kWh/year (float, >= 0)

### Location Parameters

- `latitude`: Latitude coordinate (float, -90 to 90)
- `longitude`: Longitude coordinate (float, -180 to 180)
- `address`: Installation address (string, optional)

### Roof Configuration

- `roof_area_m2`: Available roof area in m² (float, > 0)
- `roof_orientation`: Roof orientation (enum: Süd, Südost, Südwest, Ost, West, Nord, Nordost, Nordwest, Flachdach, Sonstige)
- `roof_inclination_deg`: Roof inclination in degrees (float, 0-90, default: 30)
- `roof_type`: Type of roof (enum: Satteldach, Flachdach, Walmdach, Pultdach, Sonstige)

### Module Configuration

- `selected_module_id`: Selected PV module product ID (integer, optional)
- `module_capacity_w`: Module capacity in Watts (float, > 0)

### Economic Parameters

- `electricity_price_kwh`: Current electricity price in €/kWh (float, > 0, default: 0.30)
- `simulation_period_years`: Simulation period in years (integer, 1-50)
- `electricity_price_increase_annual_percent`: Annual electricity price increase in % (float, 0-20)

### Storage Configuration

- `include_storage`: Include battery storage (boolean, default: false)
- `selected_storage_id`: Selected storage product ID (integer, optional)
- `selected_storage_capacity_kwh`: Storage capacity in kWh (float, >= 0)

### Advanced Options

- `use_pvgis`: Use PVGIS for yield calculation (boolean, default: true)
- `global_yield_adjustment_percent`: Global yield adjustment in % (float, -50 to 50, default: 0)

## Caching

The service implements intelligent caching to improve performance:

- **Cache Key**: Generated from request parameters (MD5 hash)
- **Cache TTL**: 5 minutes (300 seconds)
- **Cache Size**: Maximum 100 entries (automatic cleanup)
- **Cache Invalidation**: Automatic on expiry or manual via API

### Cache Behavior

1. **Cache Hit**: If identical request is made within 5 minutes, cached result is returned immediately
2. **Cache Miss**: New calculation is performed and result is cached
3. **Cache Cleanup**: When cache exceeds 100 entries, expired entries are removed

## Error Handling

The service provides detailed error messages for common issues:

### Validation Errors (400)

```json
{
  "detail": "Invalid input: latitude must be between -90 and 90"
}
```

### Calculation Errors (500)

```json
{
  "detail": "Calculation failed: PVGIS service unavailable"
}
```

### Warnings

Non-critical issues are returned in the `warnings` array:

```json
{
  "warnings": [
    "PVGIS: Invalid default coordinates (0,0). Using manual calculation."
  ]
}
```

## Performance

- **Average Calculation Time**: 200-500ms (without cache)
- **Cached Response Time**: < 10ms
- **PVGIS API Call**: 100-300ms (when used)
- **Memory Usage**: ~50MB per service instance

## Testing

Run the test suite:

```bash
cd backend
pytest tests/test_solar_service.py -v
```

Test coverage includes:
- Service initialization
- Health checks
- Basic calculations
- Storage calculations
- Cache functionality
- Input validation
- Error handling

## Troubleshooting

### Service Not Initialized

**Error**: `RuntimeError: Service not initialized`

**Solution**: Ensure `initialize()` is called before using the service:

```python
service = SolarCalculatorService()
service.initialize()
```

### PVGIS Data Not Available

**Symptom**: `pvgis_data_used: false` in response

**Causes**:
1. Invalid coordinates (0,0)
2. PVGIS service unavailable
3. PVGIS disabled in settings

**Solution**: Service automatically falls back to manual calculation

### Cache Not Working

**Symptom**: Same request takes full calculation time

**Causes**:
1. Request parameters slightly different
2. Cache expired (> 5 minutes)
3. Cache was cleared

**Solution**: Verify request parameters are identical

## Future Enhancements

Planned improvements for future versions:

1. **Database Integration**: Store projects and calculation history
2. **Advanced Caching**: Redis-based distributed cache
3. **Batch Calculations**: Calculate multiple scenarios in parallel
4. **Real-time Updates**: WebSocket support for long-running calculations
5. **Export Formats**: PDF, Excel, CSV export of results
6. **Comparison Mode**: Compare multiple system configurations
7. **Optimization Engine**: Automatic system size optimization

## Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Legacy Wrapper Guide](./LEGACY_WRAPPER_GUIDE.md)
- [Authentication Guide](./AUTHENTICATION_GUIDE.md)
- [Error Handling Framework](./ERROR_HANDLING_FRAMEWORK.md)
