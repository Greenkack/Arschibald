# Pricing Service Guide

## Overview

The Pricing Service provides a FastAPI backend for price matrix operations with Excel INDEX/MATCH logic implementation.

## Features

### 1. Excel INDEX/MATCH Logic

The service implements the Excel INDEX/MATCH formula logic for price lookups:

```
=INDEX(A2:A200, MATCH(C37, A2:XX200, 0), MATCH(C65, B2:XX2, 0))
```

**Components:**
- **Column A (A2:A200)**: PV Module Count (Anzahl der PV-Module)
- **Row 1 (B2:XX2)**: Battery Storage Models (Batteriespeichermodelle)
- **Last Column**: "kein Speicher" (No Storage) option
- **Cells**: Turnkey PV system prices (schlüsselfertige Preise)

**Lookup Logic:**
1. Input 1: Module count from Solar Calculator
2. Input 2: Battery storage model from Solar Calculator
3. Special case: "kein Speicher" selection uses last column
4. Result: Intersection cell value = turnkey system price

### 2. Price Includes Everything

The base price from the matrix includes:
- PV modules
- Inverter
- Battery storage (if selected)
- Mounting system (Unterkonstruktion)
- All cables and materials
- Installation and commissioning
- Permits and approvals (Genehmigungen)
- Commissions and margins (Provisionen)

### 3. Additional Costs (Only if Selected)

- Extra costs (Extrakosten)
- Surcharges (Aufpreise)
- Discounts (Rabatte)
- Deductions (Nachlässe)
- Accessories (Zubehör)
- Special products (Extras)

## API Endpoints

### Price Calculation

```http
POST /api/v1/pricing/calculate
Content-Type: application/json

{
  "module_count": 20,
  "storage_model": "15kWh",
  "matrix_id": null,
  "enable_fallback": true
}
```

**Response:**
```json
{
  "success": true,
  "base_price": 18500.00,
  "row_used": "20",
  "row_id": 5,
  "column_used": "15kWh",
  "column_id": 3,
  "matrix_id": 1,
  "matrix_name": "Preismatrix 2024",
  "fallback_used": false
}
```

### Matrix Management

#### Create Matrix
```http
POST /api/v1/pricing/matrix
Content-Type: application/json

{
  "name": "Preismatrix 2024",
  "description": "Aktuelle Preise für PV-Anlagen",
  "pricing_mode": "pauschal",
  "include_accessories": true,
  "include_misc": true
}
```

#### List Matrices
```http
GET /api/v1/pricing/matrix
```

#### Get Matrix
```http
GET /api/v1/pricing/matrix/{matrix_id}
```

#### Activate Matrix
```http
PUT /api/v1/pricing/matrix/{matrix_id}/activate
```

#### Delete Matrix
```http
DELETE /api/v1/pricing/matrix/{matrix_id}
```

### Matrix Upload

```http
POST /api/v1/pricing/matrix/upload/csv
Content-Type: application/json

{
  "name": "Imported Matrix",
  "csv_content": "ROW_LABEL;10kWh;15kWh;Kein Speicher\n10;15000;17500;12000\n15;18000;20500;15000",
  "delimiter": ";"
}
```

### Matrix Validation

```http
GET /api/v1/pricing/matrix/{matrix_id}/validate
```

### Matrix Export

```http
POST /api/v1/pricing/matrix/export/csv
Content-Type: application/json

{
  "matrix_id": 1,
  "delimiter": ";"
}
```

### CRUD Operations

#### Add Row
```http
POST /api/v1/pricing/matrix/row
Content-Type: application/json

{
  "matrix_id": 1,
  "label": "25",
  "position": null
}
```

#### Add Column
```http
POST /api/v1/pricing/matrix/column
Content-Type: application/json

{
  "matrix_id": 1,
  "label": "20kWh",
  "position": null
}
```

#### Set Cell Value
```http
PUT /api/v1/pricing/matrix/cell
Content-Type: application/json

{
  "matrix_id": 1,
  "row_id": 5,
  "column_id": 3,
  "value": 18500.00,
  "data_type": "number"
}
```

#### Remove Row
```http
DELETE /api/v1/pricing/matrix/row/{row_id}
```

#### Remove Column
```http
DELETE /api/v1/pricing/matrix/column/{column_id}
```

### Cache Management

#### Clear Cache
```http
DELETE /api/v1/pricing/cache
```

#### Get Cache Stats
```http
GET /api/v1/pricing/cache/stats
```

## Error Handling

The service provides comprehensive error handling with:

- **User-friendly error messages** in German
- **Fallback strategies** for missing data
- **Admin notifications** for critical errors
- **Detailed error information** for debugging

### Error Types

- `matrix_not_found`: No active matrix found
- `no_row`: Module count not in matrix
- `no_column`: Storage model not in matrix
- `no_price`: Price cell is empty
- `invalid_price`: Cell contains invalid value
- `invalid_input`: Invalid input parameters

### Fallback Strategies

1. **Floor Module Count**: Use next-smaller module count
2. **No Storage**: Fall back to "kein Speicher" column
3. **Standard Calculation**: Use standard calculation if matrix unavailable

## German Number Formatting

All prices are formatted according to German locale:
- Decimal separator: `,` (comma)
- Thousand separator: `.` (dot)
- Decimal places: 2

Example: `18.500,00 €`

## Dynamic Keys and PDF Bytes

The service supports:
- **Dynamic keys** for all matrix cells
- **PDF bytes generation** for matrix data
- **Real-time sync** with Solar Calculator

## Requirements

- Python 3.10+
- FastAPI 0.100+
- Pydantic 2.0+
- SQLAlchemy (for database)
- Pandas (for matrix operations)

## Usage Example

```python
from backend.services.pricing_service import get_pricing_service

# Get service instance
service = get_pricing_service()

# Calculate price
result = service.calculate_price(
    module_count=20,
    storage_model="15kWh",
    enable_fallback=True
)

if result['success']:
    print(f"Price: {result['base_price']} EUR")
    print(f"Row: {result['row_used']}, Column: {result['column_used']}")
else:
    print(f"Error: {result['user_message']}")
```

## Testing

Run tests with:
```bash
pytest backend/tests/test_pricing_service.py -v
```

## Related Documentation

- [Price Matrix INDEX/MATCH Logic](PRICE_MATRIX_INDEX_MATCH_LOGIC.md)
- [Price Matrix Error Handling](../../docs/PRICE_MATRIX_ERROR_HANDLING_GUIDE.md)
- [Price Matrix Validation](../../docs/PRICE_MATRIX_STRUCTURE_GUIDE.md)
