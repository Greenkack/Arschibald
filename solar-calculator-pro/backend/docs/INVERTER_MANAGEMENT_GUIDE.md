# Solar Inverter Management System

## Overview

The Solar Inverter Management System provides comprehensive functionality for managing solar inverters including selection, sizing, compatibility checking, multi-inverter configurations, and monitoring integration.

## Features

### 1. Inverter Data Extraction
- Normalize inverter data from product database
- Extract technical specifications
- Identify inverter features and capabilities
- Handle missing or incomplete data gracefully

### 2. Intelligent Inverter Selection
- Automatic selection based on PV system power
- Scoring algorithm considering multiple factors:
  - Power sizing (DC/AC ratio)
  - Efficiency
  - Manufacturer preferences
  - Required features
  - Price
- Provides top alternatives with reasoning

### 3. Detailed Sizing Calculations
- Calculate required inverter specifications
- Determine optimal DC voltage and current
- Configure MPPT trackers
- Apply safety margins
- Provide sizing recommendations

### 4. Compatibility Checking
- Verify power compatibility
- Check voltage limits
- Validate current capacity
- Assess MPPT configuration
- Generate detailed compatibility reports

### 5. Multi-Inverter Configurations
- Design configurations for large systems
- Handle multiple roof orientations
- Optimize inverter distribution
- Calculate power allocation
- Provide configuration reasoning

### 6. Monitoring Integration
- Configure monitoring systems
- Define data points
- Setup alert thresholds
- Generate API endpoints
- Support multiple protocols

## API Endpoints

### List Inverters
```http
GET /api/v1/inverters
```

Query Parameters:
- `manufacturer` (optional): Filter by manufacturer
- `min_power_kw` (optional): Minimum power
- `max_power_kw` (optional): Maximum power

Response:
```json
[
  {
    "id": 1,
    "model_name": "Inverter 10kW",
    "manufacturer": "BrandA",
    "power_kw": 10.0,
    "efficiency_percent": 97.5,
    "max_dc_voltage": 1000.0,
    "mppt_count": 2,
    "max_dc_current": 30.0,
    "price_netto": 2500.0,
    "features": ["Smart Home Integration"]
  }
]
```

### Get Inverter Details
```http
GET /api/v1/inverters/{inverter_id}
```

Response: Single inverter object with full details

### Select Inverter
```http
POST /api/v1/inverters/select
```

Request Body:
```json
{
  "pv_power_kwp": 10.0,
  "system_voltage": 400.0,
  "preferences": {
    "manufacturer": "BrandA",
    "features": ["Smart Home Integration"],
    "max_price": 3000.0
  }
}
```

Response:
```json
{
  "selected_inverter": { /* inverter object */ },
  "selection_score": 85.5,
  "sizing_ratio": 1.0,
  "alternatives": [
    {
      "inverter": { /* inverter object */ },
      "score": 78.2
    }
  ],
  "selection_reasoning": "Wechselrichter ausgewählt: ..."
}
```

### Calculate Sizing
```http
POST /api/v1/inverters/sizing
```

Request Body:
```json
{
  "pv_power_kwp": 10.0,
  "module_voltage": 40.0,
  "module_current": 10.0,
  "string_configuration": {
    "modules_per_string": 10,
    "number_of_strings": 2
  }
}
```

Response:
```json
{
  "required_power_kw": 9.0,
  "recommended_power_range": {
    "min_kw": 8.0,
    "optimal_kw": 9.0,
    "max_kw": 10.0
  },
  "dc_specifications": {
    "string_voltage": 400.0,
    "required_max_voltage": 480.0,
    "total_current": 20.0,
    "required_max_current": 22.0
  },
  "mppt_configuration": {
    "recommended_mppt_count": 2,
    "strings_per_mppt": 1,
    "current_per_mppt": 10.0
  }
}
```

### Check Compatibility
```http
POST /api/v1/inverters/compatibility
```

Request Body:
```json
{
  "inverter_id": 1,
  "pv_system": {
    "pv_power_kwp": 10.0,
    "string_voltage": 400.0,
    "total_current": 20.0,
    "number_of_strings": 2
  }
}
```

Response:
```json
{
  "is_compatible": true,
  "compatibility_score": 100.0,
  "checks": [
    {
      "check": "Leistungsanpassung",
      "status": "OK",
      "details": "DC/AC-Verhältnis: 1.00 (optimal: 0.8-1.2)"
    }
  ],
  "warnings": [],
  "recommendation": "Wechselrichter ist vollständig kompatibel"
}
```

### Create Multi-Inverter Configuration
```http
POST /api/v1/inverters/multi-inverter
```

Request Body:
```json
{
  "pv_power_kwp": 40.0,
  "system_layout": {
    "roof_sections": [
      {
        "section_id": "1",
        "orientation": 180,
        "tilt": 30,
        "area_sqm": 100,
        "power_kwp": 20.0
      },
      {
        "section_id": "2",
        "orientation": 90,
        "tilt": 30,
        "area_sqm": 100,
        "power_kwp": 20.0
      }
    ]
  }
}
```

Response:
```json
{
  "configuration_type": "multi",
  "inverter_count": 2,
  "inverters": [ /* inverter objects */ ],
  "total_power_kw": 40.0,
  "power_distribution": [
    {
      "inverter_index": 0,
      "inverter": { /* inverter object */ },
      "assigned_power_kwp": 20.0,
      "roof_section": { /* roof section object */ }
    }
  ],
  "reasoning": "Multi-Wechselrichter-Konfiguration: ..."
}
```

### Configure Monitoring
```http
POST /api/v1/inverters/monitoring
```

Request Body:
```json
{
  "inverter_id": 1,
  "monitoring_config": {
    "protocol": "Modbus TCP",
    "update_interval": 60,
    "retention_days": 365
  }
}
```

Response:
```json
{
  "monitoring_supported": true,
  "inverter_id": 1,
  "communication_protocol": "Modbus TCP",
  "data_points": [
    "AC Power Output (kW)",
    "DC Power Input (kW)",
    "Efficiency (%)"
  ],
  "alerts": [
    {
      "type": "low_efficiency",
      "threshold": 90,
      "description": "Wirkungsgrad unter 90%"
    }
  ],
  "api_endpoints": {
    "real_time_data": "/api/v1/monitoring/inverter/1/realtime",
    "historical_data": "/api/v1/monitoring/inverter/1/history"
  }
}
```

## Usage Examples

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Select optimal inverter
response = requests.post(
    f"{BASE_URL}/inverters/select",
    json={
        "pv_power_kwp": 10.0,
        "preferences": {
            "manufacturer": "Huawei",
            "features": ["Smart Home Integration"]
        }
    }
)

selection = response.json()
print(f"Selected: {selection['selected_inverter']['model_name']}")
print(f"Score: {selection['selection_score']}")
print(f"Reasoning: {selection['selection_reasoning']}")

# Check compatibility
inverter_id = selection['selected_inverter']['id']
response = requests.post(
    f"{BASE_URL}/inverters/compatibility",
    json={
        "inverter_id": inverter_id,
        "pv_system": {
            "pv_power_kwp": 10.0,
            "string_voltage": 400.0,
            "total_current": 20.0,
            "number_of_strings": 2
        }
    }
)

compatibility = response.json()
print(f"Compatible: {compatibility['is_compatible']}")
print(f"Score: {compatibility['compatibility_score']}")
```

### JavaScript/TypeScript Example

```typescript
const BASE_URL = 'http://localhost:8000/api/v1';

// Select inverter
const selectInverter = async (pvPowerKwp: number) => {
  const response = await fetch(`${BASE_URL}/inverters/select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      pv_power_kwp: pvPowerKwp,
      preferences: {
        manufacturer: 'Huawei',
        features: ['Smart Home Integration']
      }
    })
  });
  
  return await response.json();
};

// Calculate sizing
const calculateSizing = async (config: any) => {
  const response = await fetch(`${BASE_URL}/inverters/sizing`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
  
  return await response.json();
};

// Usage
const selection = await selectInverter(10.0);
console.log('Selected:', selection.selected_inverter.model_name);

const sizing = await calculateSizing({
  pv_power_kwp: 10.0,
  module_voltage: 40.0,
  module_current: 10.0,
  string_configuration: {
    modules_per_string: 10,
    number_of_strings: 2
  }
});
console.log('Required power:', sizing.required_power_kw);
```

## Inverter Selection Algorithm

The selection algorithm scores inverters based on multiple criteria:

### 1. Power Sizing (40 points max)
- Optimal range: 0.8-1.0 × PV power
- Perfect match at 0.9 × PV power
- Penalty for out-of-range inverters

### 2. Efficiency (20 points max)
- Linear scoring from 90% to 100%
- 95% efficiency = 20 points
- 90% efficiency = 0 points

### 3. Manufacturer Preference (15 points max)
- Full points if matches preferred manufacturer
- Zero points otherwise

### 4. Feature Matching (15 points max)
- Proportional to number of matching features
- All features match = 15 points

### 5. Price (10 points max)
- Lower price = higher score
- Normalized to typical range (500-5000 EUR)

**Total Score: 0-100 points**

## Sizing Guidelines

### DC/AC Ratio
- **Optimal**: 0.9-1.0 (90-100% of inverter power)
- **Acceptable**: 0.8-1.2
- **Oversizing**: > 1.0 (more PV than inverter can handle)
- **Undersizing**: < 0.8 (inverter too large)

### Safety Margins
- **Voltage**: 20% margin above string voltage
- **Current**: 10% margin above total current

### MPPT Configuration
- **1-2 strings**: 1 MPPT
- **3-4 strings**: 2 MPPTs
- **5-6 strings**: 3 MPPTs
- **7+ strings**: 4 MPPTs

## Multi-Inverter Scenarios

### When to Use Multiple Inverters

1. **Large Systems** (> 30 kWp)
   - Better efficiency at partial load
   - Improved system availability
   - Easier maintenance

2. **Multiple Roof Orientations**
   - Separate MPPT tracking per orientation
   - Optimized energy harvest
   - Independent operation

3. **Phased Installation**
   - Start with smaller system
   - Expand later without replacing inverter

### Configuration Strategy

- **Same Orientation**: Distribute power evenly
- **Different Orientations**: One inverter per orientation
- **Large System**: Use 10-15kW inverters for optimal efficiency

## Monitoring Integration

### Supported Protocols
- Modbus TCP/RTU
- SunSpec
- Manufacturer-specific APIs

### Data Points
- Real-time power (AC/DC)
- Energy production (daily/total)
- Efficiency
- Voltage and current
- Temperature
- Status and errors

### Alert Types
- Low efficiency
- High temperature
- Error states
- Communication loss
- Production anomalies

## Best Practices

### Selection
1. Always check compatibility after selection
2. Consider future expansion needs
3. Verify warranty and support
4. Check monitoring capabilities

### Sizing
1. Use 0.9 DC/AC ratio as starting point
2. Apply appropriate safety margins
3. Consider local regulations
4. Account for temperature derating

### Installation
1. Follow manufacturer guidelines
2. Ensure proper ventilation
3. Use appropriate cable sizing
4. Install surge protection

### Monitoring
1. Enable all available data points
2. Set appropriate alert thresholds
3. Regular performance checks
4. Maintain historical data

## Troubleshooting

### Selection Issues
- **No inverters found**: Check database connection
- **Low scores**: Adjust preferences or expand inverter database
- **No alternatives**: Add more inverter models

### Compatibility Issues
- **Voltage too high**: Reduce modules per string
- **Current too high**: Reduce number of strings or add MPPTs
- **Power mismatch**: Select different inverter size

### Monitoring Issues
- **Not supported**: Check inverter features
- **Connection failed**: Verify protocol and settings
- **Missing data**: Check data point configuration

## Requirements Mapping

This implementation satisfies the following requirements:

- **1.3**: Solar calculator functionality with inverter management
- **6.1**: Legacy code wrapper infrastructure for existing inverter logic

## Related Documentation

- [Solar Calculator Advanced Service Guide](SOLAR_CALCULATOR_ADVANCED_GUIDE.md)
- [Product Management Guide](PRODUCT_MANAGEMENT_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Monitoring Integration Guide](MONITORING_INTEGRATION_GUIDE.md)
