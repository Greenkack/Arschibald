# Pricing Service Quick Reference

## Quick Start

```python
from backend.services.pricing_service import get_pricing_service

service = get_pricing_service()

# Calculate price
result = service.calculate_price(
    module_count=20,
    storage_model="15kWh"
)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/pricing/calculate` | Calculate price |
| POST | `/api/v1/pricing/matrix` | Create matrix |
| GET | `/api/v1/pricing/matrix` | List matrices |
| GET | `/api/v1/pricing/matrix/{id}` | Get matrix |
| PUT | `/api/v1/pricing/matrix/{id}/activate` | Activate matrix |
| DELETE | `/api/v1/pricing/matrix/{id}` | Delete matrix |
| POST | `/api/v1/pricing/matrix/upload/csv` | Upload CSV |
| GET | `/api/v1/pricing/matrix/{id}/validate` | Validate matrix |
| POST | `/api/v1/pricing/matrix/export/csv` | Export CSV |
| POST | `/api/v1/pricing/matrix/row` | Add row |
| POST | `/api/v1/pricing/matrix/column` | Add column |
| DELETE | `/api/v1/pricing/matrix/row/{id}` | Remove row |
| DELETE | `/api/v1/pricing/matrix/column/{id}` | Remove column |
| PUT | `/api/v1/pricing/matrix/cell` | Set cell value |
| DELETE | `/api/v1/pricing/cache` | Clear cache |
| GET | `/api/v1/pricing/cache/stats` | Cache stats |

## Excel INDEX/MATCH Logic

```
=INDEX(A2:A200, MATCH(module_count, A2:XX200, 0), MATCH(storage_model, B2:XX2, 0))
```

- **Column A**: Module counts
- **Row 1**: Storage models
- **Last Column**: "kein Speicher"
- **Cells**: Turnkey prices

## Price Calculation Example

```bash
curl -X POST http://localhost:8000/api/v1/pricing/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "module_count": 20,
    "storage_model": "15kWh",
    "enable_fallback": true
  }'
```

## Matrix Upload Example

```bash
curl -X POST http://localhost:8000/api/v1/pricing/matrix/upload/csv \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Matrix",
    "csv_content": "ROW_LABEL;10kWh;15kWh;Kein Speicher\n10;15000;17500;12000",
    "delimiter": ";"
  }'
```

## Error Handling

| Error Type | Description | Fallback |
|------------|-------------|----------|
| `matrix_not_found` | No active matrix | Standard calc |
| `no_row` | Module count missing | Floor logic |
| `no_column` | Storage model missing | "kein Speicher" |
| `no_price` | Empty cell | None |
| `invalid_price` | Invalid value | None |

## Fallback Strategies

1. **Floor Module Count**: Use next-smaller count
2. **No Storage**: Fall back to "kein Speicher"
3. **Standard Calculation**: Use default calculation

## German Number Formatting

- Decimal: `,` (comma)
- Thousand: `.` (dot)
- Example: `18.500,00 €`

## Common Tasks

### Create and Activate Matrix
```python
# Create
result = service.create_matrix(name="Matrix 2024")
matrix_id = result['matrix_id']

# Activate
service.set_active_matrix(matrix_id)
```

### Add Data to Matrix
```python
# Add row
service.add_row(matrix_id=1, label="25")

# Add column
service.add_column(matrix_id=1, label="20kWh")

# Set cell value
service.set_cell_value(
    matrix_id=1,
    row_id=5,
    column_id=3,
    value=18500.00
)
```

### Validate Matrix
```python
result = service.validate_matrix(matrix_id=1)
if result['valid']:
    print("Matrix is valid")
else:
    print(result['user_message'])
```

## Requirements

- Requirements: 1.3, 4.5, 14.1, 14.2
- Python 3.10+
- FastAPI 0.100+
