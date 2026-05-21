# Price Matrix Validation System

Comprehensive validation system for price matrices with structure, data type, range, formula, and consistency checks.

## Overview

The Price Matrix Validation System ensures that price matrices are correctly structured and contain valid data before being used in price calculations. It performs multiple levels of validation and provides detailed feedback on any issues found.

## Features

### 1. Structure Validation
- Validates minimum dimensions (2 rows, 2 columns)
- Checks for duplicate positions
- Detects gaps in row/column positions
- Ensures matrix is not empty

### 2. Data Type Validation
- Column A must contain numeric values (module counts)
- Row 1 must contain text values (storage model names)
- Price cells must be numeric or empty
- Validates data type consistency

### 3. Range Validation
- Module counts: 1 - 1,000
- Prices: 0 - 1,000,000
- Detects negative prices (error)
- Warns about values exceeding maximum

### 4. Formula Validation
- Validates Excel-like formula syntax
- Checks for balanced parentheses
- Validates function names
- Supports: SUM, AVERAGE, MIN, MAX, IF, INDEX, MATCH, VLOOKUP, HLOOKUP

### 5. Consistency Checks
- Requires "No Storage" column
- Checks for empty price cells
- Validates monotonic module count ordering
- Generates comprehensive statistics

## Usage

### Python API

```python
from services.price_matrix_validation_service import PriceMatrixValidationService

# Initialize validator
validator = PriceMatrixValidationService()

# Prepare matrix data
matrix_data = {
    'rows': [...],
    'columns': [...],
    'cells': {...}
}

# Validate
result = validator.validate_matrix(matrix_data)

# Check if valid
if result.valid:
    print("Matrix is valid!")
else:
    print("Validation errors:")
    for error in result.errors:
        print(f"  - {error}")

# Generate report
report = validator.get_validation_report(result)
print(report)
```

### REST API

#### Validate Matrix

```bash
POST /api/v1/price-matrix/validate
Content-Type: application/json

{
  "rows": [...],
  "columns": [...],
  "cells": {...}
}
```

Response:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "info": {
    "total_rows": 4,
    "total_columns": 4,
    "module_count_range": "10-20",
    "storage_model_count": 3
  },
  "timestamp": "2024-01-15T10:30:00",
  "report": "..."
}
```

#### Quick Validation

```bash
POST /api/v1/price-matrix/validate/quick
```

Returns only valid/invalid status for faster checks.

#### Get Validation Report

```bash
POST /api/v1/price-matrix/validate/report
```

Returns formatted text report.

#### Get Validation Rules

```bash
GET /api/v1/price-matrix/validation/rules
```

Returns documentation of all validation rules.

## Validation Rules

### Structure Rules

| Rule | Requirement | Severity |
|------|-------------|----------|
| Minimum rows | 2 (header + data) | Error |
| Minimum columns | 2 (module count + storage) | Error |
| No duplicate positions | Unique row/column positions | Error |
| No gaps | Continuous position sequence | Warning |

### Data Type Rules

| Rule | Requirement | Severity |
|------|-------------|----------|
| Column A | Numeric (module counts) | Error |
| Row 1 | Text (storage model names) | Error |
| Price cells | Numeric or empty | Error |

### Range Rules

| Rule | Minimum | Maximum | Severity |
|------|---------|---------|----------|
| Module count | 1 | 1,000 | Error |
| Price | 0 | 1,000,000 | Error (negative), Warning (too high) |

### Consistency Rules

| Rule | Requirement | Severity |
|------|-------------|----------|
| No Storage column | Must exist | Error |
| Module count ordering | Ascending order | Warning |
| Empty price cells | Should be filled | Warning |

## Validation Result

The validation result contains:

```python
{
    'valid': bool,              # Overall validation status
    'errors': List[str],        # Critical errors
    'warnings': List[str],      # Non-critical warnings
    'info': Dict[str, Any],     # Matrix information
    'timestamp': str            # Validation timestamp
}
```

### Information Fields

- `total_rows`: Number of rows
- `total_columns`: Number of columns
- `total_cells`: Number of cells with values
- `module_counts`: List of module counts
- `module_count_range`: Range of module counts
- `storage_models`: List of storage model names
- `storage_model_count`: Number of storage models
- `no_storage_column`: Name of no-storage column
- `price_statistics`: Min, max, average prices
- `empty_price_cell_count`: Number of empty price cells
- `formula_count`: Number of formula cells

## Examples

### Valid Matrix

```python
{
    'rows': [
        {'id': 1, 'position': 0, 'label': 'Header'},
        {'id': 2, 'position': 1, 'label': '10'},
        {'id': 3, 'position': 2, 'label': '15'},
    ],
    'columns': [
        {'id': 1, 'position': 0, 'label': 'Modulanzahl'},
        {'id': 2, 'position': 1, 'label': '10kWh'},
        {'id': 3, 'position': 2, 'label': 'Kein Speicher'},
    ],
    'cells': {
        (1, 1): {'raw_input': 'Modulanzahl', 'value': None},
        (1, 2): {'raw_input': '10kWh', 'value': None},
        (1, 3): {'raw_input': 'Kein Speicher', 'value': None},
        (2, 1): {'raw_input': '10', 'value': 10},
        (2, 2): {'raw_input': '15000', 'value': 15000},
        (2, 3): {'raw_input': '12000', 'value': 12000},
        (3, 1): {'raw_input': '15', 'value': 15},
        (3, 2): {'raw_input': '18000', 'value': 18000},
        (3, 3): {'raw_input': '15000', 'value': 15000},
    }
}
```

### Common Errors

#### Empty Matrix
```
Error: Matrix is empty - no rows or columns found
```

#### Non-numeric Module Count
```
Error: Column A must contain numeric module counts. Invalid rows: Row 2
```

#### Missing No Storage Column
```
Error: No "Kein Speicher" (No Storage) column found
```

#### Negative Price
```
Error: Negative prices found. Cells: B2: -1000
```

#### Non-numeric Price
```
Error: Price cells must contain numeric values. Invalid cells: B2 ('invalid')
```

## Validation Report

The validation report provides a formatted summary:

```
============================================================
PRICE MATRIX VALIDATION REPORT
============================================================
Timestamp: 2024-01-15T10:30:00

✓ VALIDATION PASSED
Matrix is valid and ready for use in price calculations.

MATRIX INFORMATION:
------------------------------------------------------------
Rows: 4
Columns: 4
Cells with values: 12
Module count range: 10-20
Storage models: 3
  - 10kWh, 15kWh, Kein Speicher
No storage column: Kein Speicher
Price range: 12000.00 - 23500.00
Average price: 17333.33
Price cells: 9

============================================================
```

## Integration

### With Price Matrix Store

```python
from price_matrix_store import get_matrix_full
from services.price_matrix_validation_service import PriceMatrixValidationService

# Load matrix
matrix_data = get_matrix_full(matrix_id)

# Validate
validator = PriceMatrixValidationService()
result = validator.validate_matrix(matrix_data)

if not result.valid:
    raise ValueError(f"Invalid matrix: {result.errors}")
```

### With Price Calculation

```python
# Validate before calculation
result = validator.validate_matrix(matrix_data)

if result.valid:
    # Proceed with price calculation
    price = calculate_price(module_count, storage_model)
else:
    # Handle validation errors
    return {'error': result.errors}
```

## Testing

Run tests:
```bash
pytest tests/test_price_matrix_validation.py -v
```

Test coverage includes:
- Structure validation
- Data type validation
- Range validation
- Formula validation
- Consistency checks
- Statistics generation
- Report generation

## Performance

- Validation time: < 100ms for typical matrices (100 rows x 20 columns)
- Memory usage: < 10MB for large matrices
- Supports matrices up to 1,000 rows x 100 columns

## Error Handling

All validation errors are non-fatal and return detailed error messages. The validation service never throws exceptions during validation - all errors are captured in the result object.

## Requirements

- Python 3.10+
- No external dependencies (uses only standard library)

## See Also

- [Price Matrix Structure Guide](PRICE_MATRIX_STRUCTURE_GUIDE.md)
- [Price Matrix Lookup](PRICE_MATRIX_LOOKUP_GUIDE.md)
- [Price Matrix Error Handling](PRICE_MATRIX_ERROR_HANDLING_GUIDE.md)
