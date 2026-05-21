# Product Advanced Service - Quick Reference

## Service Initialization

```python
from backend.services.product_advanced_service import get_product_advanced_service

service = get_product_advanced_service()
```

## Lifecycle Management

```python
# Get lifecycle
lifecycle = service.get_product_lifecycle(product_id)

# Update lifecycle
service.update_product_lifecycle(product_id, "discontinued", "notes")
```

**Statuses:** `draft`, `active`, `discontinued`, `archived`, `pending_approval`

## Versioning

```python
# Create version
version = service.create_product_version(
    product_id, 
    changes={"price_euro": 260.0},
    version_notes="Price update"
)

# Get history
history = service.get_product_version_history(product_id, limit=50)
```

## Product Comparison

```python
comparison = service.compare_products(
    product_ids=[1, 2, 3],
    comparison_attributes=["power_wp", "efficiency", "price_euro"]
)
```

## Recommendations

```python
recommendations = service.get_product_recommendations(
    calculation_context={
        "required_power": 420,
        "budget": 270.0,
        "preferred_brands": ["Brand A"]
    },
    category="Solar Modules",
    limit=5
)
```

## Availability Tracking

```python
# Get availability
availability = service.get_product_availability(product_id)

# Update availability
service.update_product_availability(
    product_id,
    stock_quantity=50,
    reorder_point=15
)
```

**Statuses:** `in_stock`, `low_stock`, `out_of_stock`, `backordered`, `discontinued`

## Supplier Management

```python
# Get suppliers
suppliers = service.get_product_suppliers(product_id)

# Add supplier
supplier = service.add_product_supplier(
    product_id,
    supplier_data={
        "supplier_name": "Supplier Inc",
        "unit_price": 200.0,
        "minimum_order_quantity": 10
    }
)
```

## Pricing History

```python
# Get history
history = service.get_pricing_history(
    product_id,
    start_date="2024-01-01",
    end_date="2024-03-31",
    limit=50
)

# Analyze trends
trends = service.analyze_pricing_trends(product_id, period_days=90)
```

## Performance Analytics

```python
# Product performance
performance = service.get_product_performance(product_id, period_days=30)

# Category performance
category_perf = service.get_category_performance(
    "Solar Modules",
    period_days=30,
    limit=10
)
```

## Price Matrix Integration

```python
# Single product pricing
pricing = service.get_product_pricing_from_matrix(
    product_id,
    quantity=10,
    context={"discount_code": "BULK10"}
)

# Bulk pricing
bulk_pricing = service.get_bulk_pricing(
    product_ids=[1, 2, 3],
    quantities=[10, 5, 8],
    context={"customer_type": "wholesale"}
)
```

**Bulk Discounts:**
- 5-9 products: 3%
- 10+ products: 5%

## API Endpoints

### Lifecycle
- `GET /api/v1/product-advanced/{id}/lifecycle`
- `PUT /api/v1/product-advanced/{id}/lifecycle`

### Versioning
- `POST /api/v1/product-advanced/{id}/versions`
- `GET /api/v1/product-advanced/{id}/versions`

### Comparison & Recommendations
- `POST /api/v1/product-advanced/compare`
- `POST /api/v1/product-advanced/recommendations`

### Availability
- `GET /api/v1/product-advanced/{id}/availability`
- `PUT /api/v1/product-advanced/{id}/availability`

### Suppliers
- `GET /api/v1/product-advanced/{id}/suppliers`
- `POST /api/v1/product-advanced/{id}/suppliers`

### Pricing
- `GET /api/v1/product-advanced/{id}/pricing-history`
- `GET /api/v1/product-advanced/{id}/pricing-trends`
- `GET /api/v1/product-advanced/{id}/matrix-pricing`
- `POST /api/v1/product-advanced/bulk-pricing`

### Performance
- `GET /api/v1/product-advanced/{id}/performance`
- `GET /api/v1/product-advanced/category/{category}/performance`

## Error Handling

```python
try:
    result = service.get_product_lifecycle(product_id)
except ValueError as e:
    # Validation error or not found
    pass
except RuntimeError as e:
    # Operation failed
    pass
```

## Health Check

```python
health = service.health_check()
# Returns: HealthCheckResult with status and message
```

## Common Use Cases

### 1. Product Lifecycle Workflow
```python
# New product
service.update_product_lifecycle(id, "draft")
# Ready for sale
service.update_product_lifecycle(id, "active")
# End of life
service.update_product_lifecycle(id, "discontinued")
# Archive
service.update_product_lifecycle(id, "archived")
```

### 2. Smart Recommendations
```python
context = {
    "required_power": 5000,
    "budget": 12000.0,
    "roof_area": 30,
    "preferred_brands": ["Trina", "JA Solar"]
}
recs = service.get_product_recommendations(context, "Solar Modules", 5)
```

### 3. Stock Management
```python
avail = service.get_product_availability(id)
if avail["status"] == "low_stock":
    # Trigger reorder
    service.update_product_availability(
        id,
        estimated_restock_date="2024-02-01"
    )
```

### 4. Price Analysis
```python
trends = service.analyze_pricing_trends(id, 90)
if trends["trend"] == "increasing":
    print(f"Price up {trends['price_change_percent']:.1f}%")
```

### 5. Performance Monitoring
```python
perf = service.get_product_performance(id, 30)
if perf["metrics"]["return_rate"] > 0.05:
    # High return rate - investigate
    pass
```

## Tips

- Use lifecycle management for product catalog organization
- Create versions for significant changes
- Provide rich context for better recommendations
- Monitor availability to prevent stockouts
- Analyze pricing trends for competitive positioning
- Track performance metrics for inventory decisions
- Use bulk pricing for system quotes

## See Also

- [Full Service Guide](./PRODUCT_ADVANCED_SERVICE_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
