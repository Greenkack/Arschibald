# Product Rotation System - Quick Reference

## Quick Start

```python
from backend.services.product_rotation_service import (
    get_product_rotation_service,
    RotationStrategy
)

# Get service
service = get_product_rotation_service()

# Reset state (start fresh)
service.reset_rotation_state()

# Select product with rotation
product = service.select_rotated_product(
    category="pv_module",
    strategy=RotationStrategy.AVOID_BOTH.value
)
```

## Rotation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `AVOID_BRANDS` | Avoid used brands | Brand diversity |
| `AVOID_PRODUCTS` | Avoid used products | Product diversity |
| `AVOID_BOTH` | Avoid both (recommended) | Maximum variety |
| `PRICE_SIMILAR` | Similar price (±tolerance) | Fair comparison |
| `PRICE_HIGHER` | Higher price | Premium options |
| `PRICE_LOWER` | Lower price | Budget options |

## Product Categories

- `pv_module` - Solar PV Modules
- `inverter` - Solar Inverters
- `battery` - Battery Storage
- `mounting` - Mounting Systems
- `cable` - Cables
- `accessory` - Accessories

## Common Operations

### Select Single Product
```python
product = service.select_rotated_product(
    category="pv_module",
    strategy=RotationStrategy.AVOID_BOTH.value,
    required_specs={"power_wp": {"min": 410}}
)
```

### Select Product Set
```python
product_set = service.select_product_set(
    categories=["pv_module", "inverter", "battery"],
    strategy=RotationStrategy.AVOID_BOTH.value
)
```

### Check Compatibility
```python
report = service.check_product_compatibility(product_set)
if report['is_compatible']:
    print("✓ Compatible")
else:
    print("✗ Issues:", report['issues'])
```

### Get/Reset State
```python
# Get current state
state = service.get_rotation_state()

# Reset state
service.reset_rotation_state()
```

## API Endpoints

```
GET  /api/v1/product-rotation/state
POST /api/v1/product-rotation/reset
POST /api/v1/product-rotation/select-product
POST /api/v1/product-rotation/select-product-set
POST /api/v1/product-rotation/check-compatibility
GET  /api/v1/product-rotation/strategies
GET  /api/v1/product-rotation/categories
```

## Multi-Offer Pattern

```python
# Reset for new batch
service.reset_rotation_state()

offers = []
for company in companies:
    # Select products (automatically rotated)
    product_set = service.select_product_set(
        categories=["pv_module", "inverter", "battery"],
        strategy=RotationStrategy.AVOID_BOTH.value
    )
    
    # Check compatibility
    compat = service.check_product_compatibility(product_set)
    
    # Create offer
    offers.append({
        "company": company,
        "products": product_set,
        "compatible": compat['is_compatible']
    })
```

## Specification Filters

```python
required_specs = {
    "power_wp": {"min": 400, "max": 500},  # Range
    "efficiency": {"min": 20.0},            # Minimum only
    "brand": "Brand A"                      # Exact match
}
```

## Compatibility Rules

### PV Module + Inverter
- ✓ Module Voc ≤ Inverter Max DC Voltage
- ⚠ Module Power ≤ Inverter Power × 1.2

### Battery + Inverter
- ✓ Inverter has battery support
- ✓ Battery Voltage = Inverter Battery Voltage

## Error Handling

```python
product = service.select_rotated_product(...)
if product is None:
    # No product available
    # - Check rotation state
    # - Reset if needed
    # - Relax filters
    pass
```

## Testing

```bash
# Run tests
pytest test_product_rotation_service.py -v

# Run demo
python demo_product_rotation.py
```

## Best Practices

1. ✓ Always reset state at start of multi-offer generation
2. ✓ Use `AVOID_BOTH` strategy for maximum variety
3. ✓ Check compatibility after selection
4. ✓ Handle None results gracefully
5. ✓ Use specifications to ensure quality

## Common Patterns

### Pattern 1: Simple Rotation
```python
service.reset_rotation_state()
for i in range(3):
    product = service.select_rotated_product(
        category="pv_module",
        strategy=RotationStrategy.AVOID_BOTH.value
    )
```

### Pattern 2: Price-Based
```python
main = service.select_rotated_product(category="pv_module")
similar = service.select_rotated_product(
    category="pv_module",
    strategy=RotationStrategy.PRICE_SIMILAR.value,
    reference_product_id=main['id'],
    price_tolerance=0.2
)
```

### Pattern 3: With Validation
```python
product_set = service.select_product_set(categories=[...])
report = service.check_product_compatibility(product_set)
if not report['is_compatible']:
    # Retry or handle error
    pass
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No products returned | Reset state, relax filters |
| Same brand appearing | Use `AVOID_BOTH` strategy |
| Incompatible products | Check compatibility report |
| Too few options | Increase price tolerance |

## Key Metrics

- **Rotation State**: Tracks used brands/products
- **Compatibility**: Validates product combinations
- **Strategies**: 6 different selection strategies
- **Categories**: 6 product categories supported

## Quick Tips

💡 **Tip 1**: Always reset state before new multi-offer batch
💡 **Tip 2**: Use `AVOID_BOTH` for best variety
💡 **Tip 3**: Check compatibility to avoid issues
💡 **Tip 4**: Handle None results gracefully
💡 **Tip 5**: Use specs to ensure quality products

## Example Output

```
Offer 1:
  PV Module: Brand A, Model A1, €200.00
  Inverter: Brand B, Model B1, €1,500.00
  Battery: Brand C, Model C1, €5,000.00
  Total: €6,700.00

Offer 2:
  PV Module: Brand D, Model D1, €220.00  ← Different brand!
  Inverter: Brand E, Model E1, €1,800.00  ← Different brand!
  Battery: Brand F, Model F1, €6,000.00  ← Different brand!
  Total: €8,020.00

Offer 3:
  PV Module: Brand G, Model G1, €240.00  ← Different brand!
  Inverter: Brand H, Model H1, €2,000.00  ← Different brand!
  Battery: Brand I, Model I1, €6,500.00  ← Different brand!
  Total: €8,740.00
```

## Summary

**Purpose**: Automatic product rotation for multi-PDF generation
**Key Feature**: Each offer gets DIFFERENT products/brands
**Strategy**: Use `AVOID_BOTH` for maximum variety
**Validation**: Always check compatibility
**Result**: Professional, varied, comparable offers

---

**For detailed documentation, see**: `PRODUCT_ROTATION_GUIDE.md`
