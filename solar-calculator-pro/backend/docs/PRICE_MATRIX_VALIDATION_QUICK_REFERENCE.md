# Price Matrix Validation - Quick Reference

## Quick Start

```python
from services.price_matrix_validation_service import PriceMatrixValidationService

validator = PriceMatrixValidationService()
result = validator.validate_matrix(matrix_data)

if result.valid:
    print("✓ Valid")
else:
    print("✗ Invalid:", result.errors)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/price-matrix/validate` | POST | Full validation |
| `/api/v1/price-matrix/validate/quick` | POST | Quick check |
| `/api/v1/price-matrix/validate/report` | POST | Text report |
| `/api/v1/price-matrix/validation/rules` | GET | Get rules |
| `/api/v1/price-matrix/validation/examples` | GET | Get examples |

## Validation Checks

### ✓ Structure
- Min 2 rows, 2 columns
- No duplicate positions
- No gaps in positions

### ✓ Data Types
- Column A: Numeric (module counts)
- Row 1: Text (storage models)
- Price cells: Numeric or empty

### ✓ Ranges
- Module count: 1-1,000
- Price: 0-1,000,000
- No negative prices

### ✓ Formulas
- Must start with `=`
- Balanced parentheses
- Valid functions: SUM, AVERAGE, MIN, MAX, IF, INDEX, MATCH, VLOOKUP, HLOOKUP

### ✓ Consistency
- "No Storage" column required
- Module counts should be ascending
- Minimize empty price cells

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Empty matrix | No rows/columns | Add data |
| Non-numeric module count | Text in Column A | Use numbers |
| Missing no-storage column | No "Kein Speicher" | Add column |
| Negative price | Price < 0 | Use positive values |
| Invalid formula | Bad syntax | Fix formula |

## Result Object

```python
{
    'valid': bool,           # Pass/fail
    'errors': List[str],     # Critical errors
    'warnings': List[str],   # Non-critical issues
    'info': Dict[str, Any],  # Statistics
    'timestamp': str         # When validated
}
```

## Example Matrix

```python
{
    'rows': [
        {'id': 1, 'position': 0, 'label': 'Header'},
        {'id': 2, 'position': 1, 'label': '10'},
    ],
    'columns': [
        {'id': 1, 'position': 0, 'label': 'Modulanzahl'},
        {'id': 2, 'position': 1, 'label': 'Kein Speicher'},
    ],
    'cells': {
        (1, 1): {'raw_input': 'Modulanzahl', 'value': None},
        (1, 2): {'raw_input': 'Kein Speicher', 'value': None},
        (2, 1): {'raw_input': '10', 'value': 10},
        (2, 2): {'raw_input': '12000', 'value': 12000},
    }
}
```

## Testing

```bash
# Run all tests
pytest tests/test_price_matrix_validation.py -v

# Run specific test
pytest tests/test_price_matrix_validation.py::TestStructureValidation -v

# With coverage
pytest tests/test_price_matrix_validation.py --cov=services.price_matrix_validation_service
```

## Performance

- Typical validation: < 100ms
- Large matrices (1000x100): < 500ms
- Memory usage: < 10MB

## Requirements

- Python 3.10+
- FastAPI (for API endpoints)
- pytest (for testing)

## See Also

- [Full Guide](PRICE_MATRIX_VALIDATION_GUIDE.md)
- [Price Matrix Structure](PRICE_MATRIX_STRUCTURE_GUIDE.md)
