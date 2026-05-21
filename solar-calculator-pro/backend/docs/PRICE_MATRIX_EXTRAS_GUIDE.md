# Price Matrix Extras and Services Guide

Comprehensive guide for the Price Matrix Extras and Services system.

## Overview

The Price Matrix Extras and Services system provides comprehensive functionality for calculating:
- **Special Products (Extras)**: Products marked as special that are calculated in addition to the base matrix price
- **Services**: Standard and optional services with flexible calculation bases
- **Bundle Pricing**: Automatic discounts when purchasing multiple items together
- **Conditional Pricing**: Dynamic pricing based on conditions (system size, customer type, season, etc.)
- **Custom Pricing Rules**: User-defined discounts, surcharges, and adjustments

## Architecture

### Service Layer
- `PriceMatrixExtrasService`: Core service handling all calculations
- Database integration for products and services
- Decimal precision for accurate financial calculations
- German currency formatting (1.234,56 €)

### API Layer
- RESTful endpoints for all calculations
- Pydantic models for request/response validation
- Comprehensive error handling
- JSON serialization with Decimal support

## Special Products (Extras)

### What are Special Products?

Special products are items marked with `is_special_product = 1` in the database. These are calculated **in addition** to the base price matrix price.

**Standard Products (included in base price):**
- PV Modules
- Inverters
- Battery Storage
- Standard Mounting
- Standard Installation

**Special Products (calculated extra):**
- Premium modules with special features
- Advanced optimizers
- Monitoring systems
- Special mounting systems
- Additional accessories

### API Endpoint

```http
POST /api/v1/price-matrix-extras/special-products
```

**Request:**
```json
{
  "project_details": {
    "anlage_kwp": 10.0,
    "roof_area_m2": 70.0,
    "module_quantity": 25
  },
  "selected_products": [
    {
      "id": 123,
      "name": "Premium Optimizer",
      "category": "Optimizer",
      "price": 150.0,
      "quantity": 25
    }
  ]
}
```

**Response:**
```json
{
  "total": 3750.0,
  "items": [
    {
      "id": 123,
      "name": "Premium Optimizer",
      "category": "Optimizer",
      "unit_price": 150.0,
      "quantity": 25,
      "total_price": 3750.0,
      "formatted_unit_price": "150,00 €",
      "formatted_total": "3.750,00 €"
    }
  ],
  "count": 1,
  "formatted_total": "3.750,00 €"
}
```

## Services Calculation

### Service Types

**Standard Services** (always included):
- Basic installation
- System commissioning
- Standard warranty
- Basic documentation

**Optional Services** (user-selectable):
- Extended warranty
- Monitoring service
- Annual maintenance
- Premium support

### Calculation Bases

Services can be calculated based on different units:

| Basis | Description | Example |
|-------|-------------|---------|
| `kWp` | Per kilowatt-peak | Installation: 100€ per kWp |
| `m²` | Per square meter | Roof preparation: 50€ per m² |
| `Stunde` | Per hour | Consultation: 80€ per hour |
| `Stück` | Per piece | Commissioning: 200€ per piece |
| `Pauschal` | Flat rate | Documentation: 150€ flat |

### API Endpoint

```http
POST /api/v1/price-matrix-extras/services
```

**Request:**
```json
{
  "project_details": {
    "anlage_kwp": 10.0,
    "roof_area_m2": 70.0
  },
  "selected_service_ids": [2, 3],
  "include_standard": true
}
```

**Response:**
```json
{
  "standard_services": [
    {
      "id": 1,
      "name": "Installation",
      "unit_price": 100.0,
      "quantity": 10.0,
      "calculate_per": "kWp",
      "total_price": 1000.0,
      "formatted_total": "1.000,00 €"
    }
  ],
  "optional_services": [
    {
      "id": 2,
      "name": "Monitoring",
      "unit_price": 50.0,
      "quantity": 1.0,
      "calculate_per": "Pauschal",
      "total_price": 50.0,
      "formatted_total": "50,00 €"
    }
  ],
  "total_standard": 1000.0,
  "total_optional": 50.0,
  "total_services": 1050.0,
  "formatted_total_services": "1.050,00 €"
}
```

## Bundle Pricing

### Bundle Rules

Bundle pricing automatically applies discounts when certain conditions are met:

**Rule Types:**
- **Percentage Discount**: e.g., 10% off when buying 3+ items
- **Fixed Discount**: e.g., 200€ off for complete system bundle

**Conditions:**
- Minimum number of items
- Minimum total value
- Required specific items
- Required categories

### API Endpoint

```http
POST /api/v1/price-matrix-extras/bundle-pricing
```

**Request:**
```json
{
  "items": [
    {"id": 1, "total_price": 1000.0, "category": "Module"},
    {"id": 2, "total_price": 500.0, "category": "Inverter"},
    {"id": 3, "total_price": 300.0, "category": "Storage"}
  ],
  "bundle_rules": [
    {
      "name": "Complete System Bundle",
      "type": "percentage",
      "value": 10.0,
      "min_items": 3,
      "required_categories": ["Module", "Inverter", "Storage"]
    }
  ]
}
```

**Response:**
```json
{
  "original_total": 1800.0,
  "discount_amount": 180.0,
  "discount_percentage": 10.0,
  "final_total": 1620.0,
  "applied_rules": [
    {
      "name": "Complete System Bundle",
      "type": "percentage",
      "value": 10.0
    }
  ],
  "formatted_original": "1.800,00 €",
  "formatted_discount": "180,00 €",
  "formatted_final": "1.620,00 €"
}
```

## Conditional Pricing

### Condition Types

Conditional pricing applies adjustments based on various conditions:

**System-Based:**
- System size (kWp)
- Roof area
- Module count

**Customer-Based:**
- Customer type (residential, commercial, premium)
- Customer location
- Customer history

**Time-Based:**
- Season (summer/winter pricing)
- Day of week
- Time of day

**Market-Based:**
- Current demand
- Inventory levels
- Competitor pricing

### Operators

- `equals`: Exact match
- `not_equals`: Not equal
- `greater_than`: Greater than
- `less_than`: Less than
- `greater_equal`: Greater than or equal
- `less_equal`: Less than or equal
- `in`: Value in list
- `not_in`: Value not in list

### API Endpoint

```http
POST /api/v1/price-matrix-extras/conditional-pricing
```

**Request:**
```json
{
  "base_price": 10000.0,
  "conditions": {
    "system_size": 15.0,
    "customer_type": "commercial",
    "season": "summer"
  },
  "pricing_rules": [
    {
      "name": "Large System Discount",
      "condition": {
        "field": "system_size",
        "operator": "greater_than",
        "value": 10.0
      },
      "adjustment_type": "percentage",
      "adjustment_value": -5.0
    },
    {
      "name": "Commercial Customer Discount",
      "condition": {
        "field": "customer_type",
        "operator": "equals",
        "value": "commercial"
      },
      "adjustment_type": "fixed",
      "adjustment_value": -200.0
    }
  ]
}
```

**Response:**
```json
{
  "base_price": 10000.0,
  "adjustments": [
    {
      "rule_name": "Large System Discount",
      "rule_type": "percentage",
      "amount": -500.0,
      "formatted_amount": "-500,00 €"
    },
    {
      "rule_name": "Commercial Customer Discount",
      "rule_type": "fixed",
      "amount": -200.0,
      "formatted_amount": "-200,00 €"
    }
  ],
  "total_adjustment": -700.0,
  "final_price": 9300.0,
  "formatted_final": "9.300,00 €"
}
```

## Custom Pricing Rules

### Rule Types

**Discount Rules:**
- Fixed amount discount
- Percentage discount
- Tiered discounts

**Surcharge Rules:**
- Fixed amount surcharge
- Percentage surcharge
- Conditional surcharges

### API Endpoint

```http
POST /api/v1/price-matrix-extras/custom-rules
```

**Request:**
```json
{
  "pricing_data": {
    "total": 10000.0,
    "items": []
  },
  "custom_rules": [
    {
      "name": "Early Bird Discount",
      "type": "discount",
      "value": 5.0,
      "value_type": "percentage",
      "enabled": true
    },
    {
      "name": "Express Delivery",
      "type": "surcharge",
      "value": 100.0,
      "value_type": "fixed",
      "enabled": true
    }
  ]
}
```

**Response:**
```json
{
  "total": 9600.0,
  "discount_applied": 500.0,
  "surcharge_applied": 100.0,
  "applied_custom_rules": [
    {
      "applied": true,
      "rule_name": "Early Bird Discount"
    },
    {
      "applied": true,
      "rule_name": "Express Delivery"
    }
  ]
}
```

## Integration Examples

### Python Backend Integration

```python
from services.price_matrix_extras_service import PriceMatrixExtrasService

# Initialize service
service = PriceMatrixExtrasService(db_connection)

# Calculate special products
special_products_result = service.calculate_special_products(
    project_details={'anlage_kwp': 10.0},
    selected_products=[
        {'id': 1, 'price': 150.0, 'quantity': 25}
    ]
)

# Calculate services
services_result = service.calculate_services(
    project_details={'anlage_kwp': 10.0},
    selected_service_ids=[2, 3],
    include_standard=True
)

# Apply bundle pricing
bundle_result = service.calculate_bundle_pricing(
    items=[...],
    bundle_rules=[...]
)
```

### Frontend Integration

```typescript
import axios from 'axios';

// Calculate special products
const calculateSpecialProducts = async (projectDetails, products) => {
  const response = await axios.post(
    '/api/v1/price-matrix-extras/special-products',
    {
      project_details: projectDetails,
      selected_products: products
    }
  );
  return response.data;
};

// Calculate services
const calculateServices = async (projectDetails, serviceIds) => {
  const response = await axios.post(
    '/api/v1/price-matrix-extras/services',
    {
      project_details: projectDetails,
      selected_service_ids: serviceIds,
      include_standard: true
    }
  );
  return response.data;
};
```

## Best Practices

### 1. Always Use Decimal for Money

```python
from decimal import Decimal

# Good
price = Decimal('10.50')

# Bad
price = 10.50  # Float precision issues
```

### 2. Validate Input Data

```python
# Validate project details
if 'anlage_kwp' not in project_details:
    raise ValueError("Missing required field: anlage_kwp")

# Validate positive values
if price < 0:
    raise ValueError("Price cannot be negative")
```

### 3. Handle Database Errors

```python
try:
    result = service.calculate_services(...)
except Exception as e:
    logger.error(f"Service calculation failed: {e}")
    # Return default/fallback values
```

### 4. Cache Frequently Used Data

```python
# Cache service list
@lru_cache(maxsize=1)
def get_all_services():
    return service._get_services_from_db()
```

### 5. Log Important Calculations

```python
logger.info(f"Calculated special products: {result['total']}")
logger.info(f"Applied bundle discount: {result['discount_amount']}")
```

## Troubleshooting

### Issue: Services not calculating correctly

**Solution:** Check that `calculate_per` field is set correctly and project_details contains required fields.

```python
# Ensure project details has required fields
required_fields = ['anlage_kwp', 'roof_area_m2', 'module_quantity']
for field in required_fields:
    if field not in project_details:
        logger.warning(f"Missing field: {field}")
```

### Issue: Bundle rules not applying

**Solution:** Verify that all conditions are met (min_items, min_total, required_items, required_categories).

```python
# Debug bundle rule application
logger.debug(f"Items count: {len(items)}")
logger.debug(f"Total: {sum(item['total_price'] for item in items)}")
logger.debug(f"Categories: {[item['category'] for item in items]}")
```

### Issue: Decimal serialization errors

**Solution:** Convert Decimal to float before JSON serialization.

```python
# Convert Decimal to float
result['total'] = float(result['total'])
```

## Performance Considerations

### Database Queries

- Use connection pooling
- Cache service and product lists
- Use indexes on frequently queried fields

### Calculation Optimization

- Pre-calculate common values
- Use batch operations when possible
- Implement result caching for identical requests

### API Response Time

- Target: < 200ms for simple calculations
- Target: < 500ms for complex bundle/conditional pricing
- Use async operations for multiple calculations

## Security

### Input Validation

- Validate all numeric inputs
- Sanitize string inputs
- Check for SQL injection attempts
- Validate price ranges

### Authorization

- Verify user permissions for custom rules
- Audit log for pricing changes
- Restrict access to sensitive pricing data

## Future Enhancements

- [ ] Machine learning for dynamic pricing
- [ ] A/B testing for pricing strategies
- [ ] Real-time competitor price monitoring
- [ ] Advanced forecasting and analytics
- [ ] Multi-currency support
- [ ] Tax calculation integration
- [ ] Payment gateway integration

## Support

For questions or issues:
- Check the API documentation
- Review test cases for examples
- Contact the development team
