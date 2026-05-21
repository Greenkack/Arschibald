# Product Rotation System - Complete Guide

## Overview

The Product Rotation System is a **critical component** for multi-PDF generation. It ensures that when generating multiple offers for different companies, each offer receives **DIFFERENT products and brands** than previous offers, providing variety and enabling meaningful comparison.

## Core Concept

### The Problem

When generating multiple PDF offers (e.g., for 8 different companies), using the same products in all offers would be:
- Boring and repetitive
- Not useful for comparison
- Unprofessional

### The Solution

**Automatic Product Rotation:**
- **Main Offer**: PV Module: Brand A, Inverter: Brand B, Battery: Brand A
- **Offer 2**: PV Module: Brand B (NOT Brand A!), Inverter: Brand C, Battery: Brand C
- **Offer 3**: PV Module: Brand D (NOT A or B!), Inverter: Brand A, Battery: Brand E

Each subsequent offer automatically avoids brands/products used in previous offers.

## Key Features

### 1. Brand Tracking
- Tracks which brands have been used in each category
- Prevents brand repetition across offers
- Category-specific tracking (PV modules, inverters, batteries, etc.)

### 2. Product Tracking
- Tracks which specific products have been used
- Prevents product repetition across offers
- Maintains variety even within the same brand

### 3. Rotation Strategies

#### AVOID_BRANDS
- Avoids previously used brands
- Same brand can appear with different products
- Good for brand diversity

#### AVOID_PRODUCTS
- Avoids previously used products
- Same brand can appear with different models
- Good for product diversity

#### AVOID_BOTH (Recommended)
- Avoids both brands AND products
- Maximum variety
- Best for multi-offer scenarios

#### PRICE_SIMILAR
- Selects products with similar price to reference
- Maintains price consistency
- Good for fair comparisons

#### PRICE_HIGHER
- Selects products with higher price
- Creates premium alternatives
- Good for upselling

#### PRICE_LOWER
- Selects products with lower price
- Creates budget alternatives
- Good for price-sensitive customers

### 4. Compatibility Checking
- Validates product combinations
- Checks voltage compatibility
- Verifies power ratings
- Ensures battery support
- Prevents incompatible configurations

### 5. Specification Requirements
- Filter by minimum/maximum values
- Ensure products meet requirements
- Support complex specifications
- Category-specific requirements

## Architecture

### Service Layer
```
ProductRotationService
├── Rotation State Management
│   ├── reset_rotation_state()
│   ├── get_rotation_state()
│   ├── mark_brand_used()
│   ├── mark_product_used()
│   ├── is_brand_used()
│   └── is_product_used()
├── Product Selection
│   ├── select_rotated_product()
│   └── select_product_set()
└── Compatibility
    └── check_product_compatibility()
```

### API Endpoints
```
GET  /api/v1/product-rotation/state
POST /api/v1/product-rotation/reset
POST /api/v1/product-rotation/select-product
POST /api/v1/product-rotation/select-product-set
POST /api/v1/product-rotation/check-compatibility
GET  /api/v1/product-rotation/strategies
GET  /api/v1/product-rotation/categories
```

## Usage Examples

### Example 1: Basic Rotation

```python
from backend.services.product_rotation_service import (
    get_product_rotation_service,
    RotationStrategy
)

# Get service instance
service = get_product_rotation_service()

# Reset state for new multi-offer generation
service.reset_rotation_state()

# Select first product
product1 = service.select_rotated_product(
    category="pv_module",
    strategy=RotationStrategy.AVOID_BOTH.value
)

# Select second product (will avoid first brand/product)
product2 = service.select_rotated_product(
    category="pv_module",
    strategy=RotationStrategy.AVOID_BOTH.value
)

# product2 will have different brand AND different product than product1
```

### Example 2: Complete Product Set

```python
# Select complete system for one offer
product_set = service.select_product_set(
    categories=["pv_module", "inverter", "battery"],
    strategy=RotationStrategy.AVOID_BOTH.value
)

# Result:
# {
#     "pv_module": {...},
#     "inverter": {...},
#     "battery": {...}
# }
```

### Example 3: Price-Based Selection

```python
# Main offer
main_product = service.select_rotated_product(
    category="pv_module",
    strategy=RotationStrategy.AVOID_BOTH.value
)

# Second offer with similar price (±20%)
similar_product = service.select_rotated_product(
    category="pv_module",
    strategy=RotationStrategy.PRICE_SIMILAR.value,
    reference_product_id=main_product['id'],
    price_tolerance=0.2
)
```

### Example 4: With Specifications

```python
# Select only high-power modules
product = service.select_rotated_product(
    category="pv_module",
    strategy=RotationStrategy.AVOID_BOTH.value,
    required_specs={
        "power_wp": {"min": 410},
        "efficiency": {"min": 20.0}
    }
)
```

### Example 5: Compatibility Check

```python
# Check if products are compatible
report = service.check_product_compatibility({
    "pv_module": pv_module_product,
    "inverter": inverter_product,
    "battery": battery_product
})

if report['is_compatible']:
    print("✓ All products are compatible!")
else:
    print("✗ Compatibility issues:")
    for issue in report['issues']:
        print(f"  - {issue['message']}")
```

## Multi-Offer Workflow

### Complete Multi-PDF Generation Flow

```python
def generate_multi_pdf_offers(companies: List[str]):
    """Generate multiple PDF offers with product rotation"""
    
    service = get_product_rotation_service()
    service.reset_rotation_state()
    
    offers = []
    categories = ["pv_module", "inverter", "battery"]
    
    for company in companies:
        # Select rotated products for this company
        product_set = service.select_product_set(
            categories=categories,
            strategy=RotationStrategy.AVOID_BOTH.value
        )
        
        # Check compatibility
        compatibility = service.check_product_compatibility(product_set)
        
        if not compatibility['is_compatible']:
            # Handle incompatibility
            # Could retry with different strategy or log warning
            pass
        
        # Calculate total price
        total_price = sum(
            p.get('price_euro', 0) 
            for p in product_set.values() 
            if p
        )
        
        # Create offer
        offer = {
            "company": company,
            "products": product_set,
            "total_price": total_price,
            "compatibility": compatibility
        }
        
        offers.append(offer)
    
    return offers
```

## Product Categories

### Supported Categories

1. **pv_module** - Solar PV Modules
   - Power output (W)
   - Efficiency (%)
   - Voltage (V)
   - Dimensions

2. **inverter** - Solar Inverters
   - Max power (W)
   - Max DC voltage (V)
   - Battery support
   - Efficiency (%)

3. **battery** - Battery Storage
   - Capacity (kWh)
   - Voltage (V)
   - Cycle life
   - Warranty

4. **mounting** - Mounting Systems
   - Type (roof, ground, etc.)
   - Material
   - Load capacity

5. **cable** - Cables and Wiring
   - Type
   - Length
   - Cross-section

6. **accessory** - Accessories
   - Various accessories

## Rotation State Management

### State Structure

```python
{
    "used_brands": {
        "pv_module": ["Brand A", "Brand B"],
        "inverter": ["Inverter Brand A"],
        "battery": ["Battery Brand A", "Battery Brand B"]
    },
    "used_products": {
        "pv_module": [1, 2],
        "inverter": [10],
        "battery": [20, 21]
    },
    "total_used_brands": 5,
    "total_used_products": 5
}
```

### When to Reset State

- **Start of multi-offer generation**: Always reset before generating a new batch
- **Between different projects**: Reset when switching to a different customer/project
- **Manual reset**: Via API or admin interface when needed

### State Persistence

- State is maintained in memory during multi-offer generation
- State is NOT persisted to database (intentional)
- Each multi-offer batch starts fresh
- This ensures maximum variety across different batches

## Compatibility Rules

### PV Module + Inverter

1. **Voltage Compatibility**
   - Module Voc ≤ Inverter Max DC Voltage
   - Critical: Prevents damage to inverter

2. **Power Compatibility**
   - Module Power ≤ Inverter Power × 1.2
   - Warning: Allows 20% oversizing (common practice)

### Battery + Inverter

1. **Battery Support**
   - Inverter must have battery support
   - Critical: Prevents incompatible configuration

2. **Voltage Compatibility**
   - Battery Voltage = Inverter Battery Voltage
   - Critical: Ensures proper operation

## Performance Considerations

### Optimization Strategies

1. **Caching**: Product lists are cached per category
2. **Lazy Loading**: Products loaded only when needed
3. **Efficient Filtering**: Multiple filter passes to reduce dataset
4. **Random Selection**: Fast selection from filtered list

### Scalability

- Handles 100+ products per category efficiently
- Supports 10+ categories simultaneously
- Can generate 50+ offers in sequence
- Memory-efficient state tracking

## Error Handling

### Common Scenarios

1. **No Products Available**
   - Returns None
   - Logs warning
   - Fallback: Relaxes filters if too strict

2. **All Brands/Products Used**
   - Fallback: Returns any available product
   - Logs info about fallback
   - Ensures generation continues

3. **Incompatible Products**
   - Returns compatibility report
   - Lists all issues and warnings
   - Allows manual override if needed

4. **Invalid Category**
   - Raises ValueError
   - Clear error message
   - Lists valid categories

## Testing

### Unit Tests

```bash
# Run all tests
pytest solar-calculator-pro/backend/tests/test_product_rotation_service.py -v

# Run specific test
pytest solar-calculator-pro/backend/tests/test_product_rotation_service.py::TestProductRotationService::test_select_rotated_product_avoid_brands -v
```

### Demo Script

```bash
# Run demonstration
python solar-calculator-pro/backend/demo_product_rotation.py
```

## API Integration

### REST API Examples

#### Get Rotation State
```http
GET /api/v1/product-rotation/state
```

Response:
```json
{
    "used_brands": {
        "pv_module": ["Brand A", "Brand B"]
    },
    "used_products": {
        "pv_module": [1, 2]
    },
    "total_used_brands": 2,
    "total_used_products": 2
}
```

#### Reset State
```http
POST /api/v1/product-rotation/reset
```

#### Select Product
```http
POST /api/v1/product-rotation/select-product
Content-Type: application/json

{
    "category": "pv_module",
    "strategy": "avoid_both",
    "price_tolerance": 0.2,
    "required_specs": {
        "power_wp": {"min": 410}
    }
}
```

#### Select Product Set
```http
POST /api/v1/product-rotation/select-product-set
Content-Type: application/json

{
    "categories": ["pv_module", "inverter", "battery"],
    "strategy": "avoid_both",
    "price_tolerance": 0.2
}
```

#### Check Compatibility
```http
POST /api/v1/product-rotation/check-compatibility
Content-Type: application/json

{
    "product_set": {
        "pv_module": {...},
        "inverter": {...},
        "battery": {...}
    }
}
```

## Best Practices

### 1. Always Reset State
```python
# At start of multi-offer generation
service.reset_rotation_state()
```

### 2. Use AVOID_BOTH Strategy
```python
# For maximum variety
strategy=RotationStrategy.AVOID_BOTH.value
```

### 3. Check Compatibility
```python
# Always verify product combinations
report = service.check_product_compatibility(product_set)
if not report['is_compatible']:
    # Handle incompatibility
    pass
```

### 4. Handle None Results
```python
product = service.select_rotated_product(...)
if product is None:
    # Handle no product available
    # Could retry with different strategy
    pass
```

### 5. Use Specifications
```python
# Ensure products meet requirements
required_specs = {
    "power_wp": {"min": 400},
    "efficiency": {"min": 20.0}
}
```

## Troubleshooting

### Issue: No Products Returned

**Cause**: Filters too strict or all products used

**Solution**:
1. Check rotation state
2. Reset state if needed
3. Relax specifications
4. Use less strict strategy

### Issue: Same Brand Appearing

**Cause**: Using AVOID_PRODUCTS instead of AVOID_BOTH

**Solution**: Use `RotationStrategy.AVOID_BOTH.value`

### Issue: Incompatible Products

**Cause**: Products don't meet compatibility rules

**Solution**:
1. Check compatibility report
2. Review product specifications
3. Select different products
4. Update product database

## Future Enhancements

### Planned Features

1. **Smart Selection**: ML-based product selection
2. **Price Optimization**: Automatic price balancing
3. **Customer Preferences**: Remember customer preferences
4. **Historical Data**: Learn from past selections
5. **Advanced Compatibility**: More compatibility rules
6. **Performance Metrics**: Track selection performance

## Support

For issues or questions:
- Check logs: `backend/logs/product_rotation.log`
- Run demo: `python demo_product_rotation.py`
- Run tests: `pytest test_product_rotation_service.py -v`
- Review API docs: `/docs` endpoint

## Summary

The Product Rotation System is **essential** for professional multi-PDF generation. It ensures:

✓ **Variety**: Each offer has different products
✓ **Comparison**: Customers can compare different options
✓ **Professionalism**: No repetitive offers
✓ **Compatibility**: Products work together
✓ **Flexibility**: Multiple strategies available
✓ **Reliability**: Robust error handling

**Key Takeaway**: Always use `AVOID_BOTH` strategy and check compatibility for best results!
