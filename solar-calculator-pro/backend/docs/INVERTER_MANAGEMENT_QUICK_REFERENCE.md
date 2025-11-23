# Inverter Management Quick Reference

## Quick Start

```python
from services.inverter_service import InverterService

# Initialize service
service = InverterService()

# Select inverter
result = service.select_inverter(pv_power_kwp=10.0)
print(f"Selected: {result['selected_inverter']['model_name']}")

# Check compatibility
compatibility = service.check_inverter_compatibility(
    inverter=result['selected_inverter'],
    pv_system={'pv_power_kwp': 10.0, 'string_voltage': 400.0, 'total_current': 20.0, 'number_of_strings': 2}
)
print(f"Compatible: {compatibility['is_compatible']}")
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/inverters` | GET | List all inverters |
| `/api/v1/inverters/{id}` | GET | Get inverter details |
| `/api/v1/inverters/select` | POST | Select optimal inverter |
| `/api/v1/inverters/sizing` | POST | Calculate sizing |
| `/api/v1/inverters/compatibility` | POST | Check compatibility |
| `/api/v1/inverters/multi-inverter` | POST | Multi-inverter config |
| `/api/v1/inverters/monitoring` | POST | Configure monitoring |
| `/api/v1/inverters/manufacturers` | GET | List manufacturers |

## Key Functions

### InverterService Methods

```python
# Extract inverter data
extract_inverter_data(product_data: Dict) -> Dict

# Select optimal inverter
select_inverter(
    pv_power_kwp: float,
    system_voltage: float = 400.0,
    available_inverters: Optional[List] = None,
    preferences: Optional[Dict] = None
) -> Dict

# Calculate sizing
calculate_inverter_sizing(
    pv_power_kwp: float,
    module_voltage: float,
    module_current: float,
    string_configuration: Dict
) -> Dict

# Check compatibility
check_inverter_compatibility(
    inverter: Dict,
    pv_system: Dict
) -> Dict

# Multi-inverter configuration
create_multi_inverter_configuration(
    pv_power_kwp: float,
    system_layout: Dict,
    available_inverters: Optional[List] = None
) -> Dict

# Monitoring integration
integrate_monitoring(
    inverter: Dict,
    monitoring_config: Dict
) -> Dict
```

## Sizing Guidelines

### DC/AC Ratio
- **Optimal**: 0.9-1.0
- **Acceptable**: 0.8-1.2
- **Oversizing**: > 1.0
- **Undersizing**: < 0.8

### Safety Margins
- **Voltage**: +20%
- **Current**: +10%

### MPPT Count
- 1-2 strings → 1 MPPT
- 3-4 strings → 2 MPPTs
- 5-6 strings → 3 MPPTs
- 7+ strings → 4 MPPTs

## Selection Scoring

| Criterion | Max Points | Description |
|-----------|------------|-------------|
| Power Sizing | 40 | Optimal DC/AC ratio |
| Efficiency | 20 | Higher is better |
| Manufacturer | 15 | Preference match |
| Features | 15 | Required features |
| Price | 10 | Lower is better |
| **Total** | **100** | |

## Compatibility Checks

1. **Power**: 0.8 ≤ DC/AC ≤ 1.2
2. **Voltage**: String voltage ≤ 90% of max
3. **Current**: Current per MPPT ≤ 90% of max
4. **MPPT**: Strings ≤ 2 × MPPT count

## Multi-Inverter Triggers

- System > 30 kWp
- Multiple roof orientations
- Phased installation

## Monitoring Data Points

- AC Power Output (kW)
- DC Power Input (kW)
- Efficiency (%)
- Daily Energy (kWh)
- Total Energy (kWh)
- DC Voltage (V)
- DC Current (A)
- AC Voltage (V)
- AC Current (A)
- Temperature (°C)
- Status
- Error Codes

## Common Patterns

### Select and Validate
```python
# Select
selection = service.select_inverter(pv_power_kwp=10.0)
inverter = selection['selected_inverter']

# Validate
compatibility = service.check_inverter_compatibility(
    inverter=inverter,
    pv_system={...}
)

if compatibility['is_compatible']:
    print("✓ Compatible")
else:
    print("✗ Not compatible")
    print(compatibility['recommendation'])
```

### Calculate Complete Sizing
```python
sizing = service.calculate_inverter_sizing(
    pv_power_kwp=10.0,
    module_voltage=40.0,
    module_current=10.0,
    string_configuration={
        'modules_per_string': 10,
        'number_of_strings': 2
    }
)

print(f"Required: {sizing['required_power_kw']}kW")
print(f"Range: {sizing['recommended_power_range']}")
print(f"MPPT: {sizing['mppt_configuration']}")
```

### Multi-Inverter Setup
```python
config = service.create_multi_inverter_configuration(
    pv_power_kwp=40.0,
    system_layout={
        'roof_sections': [
            {'section_id': '1', 'power_kwp': 20.0, 'orientation': 180},
            {'section_id': '2', 'power_kwp': 20.0, 'orientation': 90}
        ]
    }
)

print(f"Type: {config['configuration_type']}")
print(f"Count: {config['inverter_count']}")
print(f"Total: {config['total_power_kw']}kW")
```

## Error Handling

```python
try:
    result = service.select_inverter(pv_power_kwp=10.0)
except ValueError as e:
    print(f"Selection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

```bash
# Run all tests
pytest backend/tests/test_inverter_service.py -v

# Run specific test class
pytest backend/tests/test_inverter_service.py::TestInverterSelection -v

# Run with coverage
pytest backend/tests/test_inverter_service.py --cov=services.inverter_service
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 404 | Inverter not found |
| 422 | Validation error |
| 500 | Server error |

## Requirements

- Python 3.10+
- FastAPI
- Pydantic
- SQLite (for product database)

## Related Files

- `services/inverter_service.py` - Core service
- `api/v1/inverters.py` - API endpoints
- `models/inverter_schemas.py` - Data schemas
- `tests/test_inverter_service.py` - Tests
- `docs/INVERTER_MANAGEMENT_GUIDE.md` - Full guide
