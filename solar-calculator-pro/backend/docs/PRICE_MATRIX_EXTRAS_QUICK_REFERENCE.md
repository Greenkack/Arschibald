# Price Matrix Extras and Services - Quick Reference

## API Endpoints

### Special Products
```http
POST /api/v1/price-matrix-extras/special-products
```
Calculate costs for special products (extras).

### Services
```http
POST /api/v1/price-matrix-extras/services
GET  /api/v1/price-matrix-extras/services/all
GET  /api/v1/price-matrix-extras/services/standard
GET  /api/v1/price-matrix-extras/services/optional
```
Calculate service pricing and retrieve service lists.

### Bundle Pricing
```http
POST /api/v1/price-matrix-extras/bundle-pricing
```
Calculate bundle discounts.

### Conditional Pricing
```http
POST /api/v1/price-matrix-extras/conditional-pricing
```
Apply conditional pricing rules.

### Custom Rules
```http
POST /api/v1/price-matrix-extras/custom-rules
```
Apply custom pricing rules.

## Calculation Bases

| Basis | Code | Example |
|-------|------|---------|
| Per kWp | `kWp` | Installation: 100€/kWp |
| Per m² | `m²` | Roof prep: 50€/m² |
| Per Hour | `Stunde` | Consultation: 80€/hour |
| Per Piece | `Stück` | Device: 200€/piece |
| Flat Rate | `Pauschal` | Service: 150€ flat |

## Rule Types

### Bundle Rules
- `percentage`: Percentage discount
- `fixed`: Fixed amount discount

### Conditional Rules
- `percentage`: Percentage adjustment
- `fixed`: Fixed amount adjustment
- `multiplier`: Multiply base price

### Custom Rules
- `discount`: Apply discount
- `surcharge`: Apply surcharge

## Operators

| Operator | Description |
|----------|-------------|
| `equals` | Exact match |
| `not_equals` | Not equal |
| `greater_than` | Greater than |
| `less_than` | Less than |
| `greater_equal` | Greater or equal |
| `less_equal` | Less or equal |
| `in` | Value in list |
| `not_in` | Value not in list |

## Quick Examples

### Calculate Special Products
```python
service.calculate_special_products(
    {'anlage_kwp': 10.0},
    [{'id': 1, 'price': 150.0, 'quantity': 25}]
)
```

### Calculate Services
```python
service.calculate_services(
    {'anlage_kwp': 10.0},
    [2, 3],  # Optional service IDs
    include_standard=True
)
```

### Apply Bundle Discount
```python
service.calculate_bundle_pricing(
    items=[...],
    bundle_rules=[{
        'name': '10% Bundle',
        'type': 'percentage',
        'value': 10.0,
        'min_items': 3
    }]
)
```

### Apply Conditional Pricing
```python
service.apply_conditional_pricing(
    Decimal('10000.00'),
    {'system_size': 15.0},
    [{
        'name': 'Large System Discount',
        'condition': {
            'field': 'system_size',
            'operator': 'greater_than',
            'value': 10.0
        },
        'adjustment_type': 'percentage',
        'adjustment_value': -5.0
    }]
)
```

## German Currency Format

```python
# Input: Decimal('1234.56')
# Output: "1.234,56 €"

service._format_currency(Decimal('1234.56'))
```

## Common Project Details Fields

```python
project_details = {
    'anlage_kwp': 10.0,           # System size in kWp
    'pv_kwp': 10.0,               # Alternative kWp field
    'roof_area_m2': 70.0,         # Roof area in m²
    'module_quantity': 25,         # Number of modules
    'module_power_w': 400,         # Module power in watts
    'selected_module_name': '...',
    'selected_inverter_name': '...',
    'selected_storage_name': '...'
}
```

## Error Handling

```python
try:
    result = service.calculate_services(...)
except ValueError as e:
    # Handle validation errors
    logger.error(f"Validation error: {e}")
except Exception as e:
    # Handle other errors
    logger.error(f"Calculation error: {e}")
```

## Testing

```bash
# Run all tests
pytest tests/test_price_matrix_extras_service.py -v

# Run specific test class
pytest tests/test_price_matrix_extras_service.py::TestServicesCalculation -v

# Run with coverage
pytest tests/test_price_matrix_extras_service.py --cov=services.price_matrix_extras_service
```

## Performance Tips

1. **Cache service lists**: Services don't change frequently
2. **Use batch operations**: Calculate multiple items at once
3. **Pre-validate inputs**: Check before expensive calculations
4. **Use Decimal**: Avoid float precision issues
5. **Log calculations**: Track for debugging and auditing

## Common Patterns

### Full Pricing Calculation
```python
# 1. Calculate base price from matrix
base_price = get_matrix_price(...)

# 2. Add special products
extras = service.calculate_special_products(...)
base_price += extras['total']

# 3. Add services
services = service.calculate_services(...)
base_price += services['total_services']

# 4. Apply bundle discount
bundle = service.calculate_bundle_pricing(...)
base_price = bundle['final_total']

# 5. Apply conditional pricing
conditional = service.apply_conditional_pricing(...)
base_price = conditional['final_price']

# 6. Apply custom rules
final = service.apply_custom_pricing_rules(...)
final_price = final['total']
```

### Service Quantity Calculation
```python
# Automatic quantity calculation based on project details
quantity = service._calculate_quantity(
    'kWp',  # Calculation basis
    {'anlage_kwp': 10.0}  # Project details
)
# Returns: 10.0
```

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    model_name TEXT,
    category TEXT,
    price REAL,
    is_special_product INTEGER DEFAULT 0,
    calculate_per TEXT
);
```

### Services Table
```sql
CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    category TEXT,
    price REAL,
    calculate_per TEXT,
    is_standard INTEGER DEFAULT 0,
    pdf_order INTEGER DEFAULT 0
);
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 500 | Internal Server Error |

## Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log calculations
logger.info(f"Special products total: {result['total']}")
logger.debug(f"Applied rules: {result['applied_rules']}")
logger.error(f"Calculation failed: {error}")
```

## Support

- **Documentation**: See PRICE_MATRIX_EXTRAS_GUIDE.md
- **Tests**: See test_price_matrix_extras_service.py
- **API Docs**: http://localhost:8000/docs
