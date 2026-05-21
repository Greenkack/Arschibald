# Product Advanced Service Guide

## Overview

The Product Advanced Service provides comprehensive advanced product management features including lifecycle management, versioning, comparison, recommendations, availability tracking, supplier integration, pricing history, and performance analytics.

## Features

### 1. Product Lifecycle Management

Track and manage the complete lifecycle of products from draft to archived status.

**Lifecycle Statuses:**
- `draft` - Product in development
- `active` - Product available for sale
- `discontinued` - Product no longer sold
- `archived` - Product removed from active catalog
- `pending_approval` - Awaiting approval

**API Endpoints:**
```
GET  /api/v1/product-advanced/{product_id}/lifecycle
PUT  /api/v1/product-advanced/{product_id}/lifecycle
```

**Example:**
```python
from backend.services.product_advanced_service import get_product_advanced_service

service = get_product_advanced_service()

# Get lifecycle information
lifecycle = service.get_product_lifecycle(product_id=1)

# Update lifecycle status
updated = service.update_product_lifecycle(
    product_id=1,
    status="discontinued",
    notes="End of life - replaced by newer model"
)
```

### 2. Product Versioning

Create and track versions of products as they evolve over time.

**API Endpoints:**
```
POST /api/v1/product-advanced/{product_id}/versions
GET  /api/v1/product-advanced/{product_id}/versions
```

**Example:**
```python
# Create new version
version = service.create_product_version(
    product_id=1,
    changes={
        "price_euro": 260.0,
        "efficiency": 21.0
    },
    version_notes="Price increase and efficiency improvement"
)

# Get version history
history = service.get_product_version_history(product_id=1, limit=50)
```

### 3. Product Comparison Engine

Compare multiple products across specified attributes.

**API Endpoint:**
```
POST /api/v1/product-advanced/compare
```

**Example:**
```python
# Compare products
comparison = service.compare_products(
    product_ids=[1, 2, 3],
    comparison_attributes=["power_wp", "efficiency", "price_euro"]
)

# Results include:
# - Product details
# - Attribute values for each product
# - Differences highlighted
```

### 4. Product Recommendations

Get intelligent product recommendations based on calculation context.

**API Endpoint:**
```
POST /api/v1/product-advanced/recommendations
```

**Example:**
```python
# Get recommendations
recommendations = service.get_product_recommendations(
    calculation_context={
        "required_power": 420,
        "budget": 270.0,
        "preferred_brands": ["Brand A", "Brand B"]
    },
    category="Solar Modules",
    limit=5
)

# Each recommendation includes:
# - Product details
# - Recommendation score
# - Reasons for recommendation
```

**Scoring Factors:**
- Lifecycle status (active products preferred)
- Power output match
- Efficiency rating
- Price vs budget
- Brand preferences

### 5. Product Availability Tracking

Track stock levels and availability status.

**Availability Statuses:**
- `in_stock` - Product available
- `low_stock` - Below reorder point
- `out_of_stock` - No stock available
- `backordered` - On order from supplier
- `discontinued` - No longer available

**API Endpoints:**
```
GET /api/v1/product-advanced/{product_id}/availability
PUT /api/v1/product-advanced/{product_id}/availability
```

**Example:**
```python
# Get availability
availability = service.get_product_availability(product_id=1)

# Update availability
updated = service.update_product_availability(
    product_id=1,
    stock_quantity=50,
    reorder_point=15,
    estimated_restock_date="2024-02-01"
)
```

### 6. Supplier Integration

Manage supplier relationships and pricing.

**API Endpoints:**
```
GET  /api/v1/product-advanced/{product_id}/suppliers
POST /api/v1/product-advanced/{product_id}/suppliers
```

**Example:**
```python
# Get suppliers
suppliers = service.get_product_suppliers(product_id=1)

# Add supplier
supplier = service.add_product_supplier(
    product_id=1,
    supplier_data={
        "supplier_name": "Solar Supplier Inc",
        "supplier_sku": "SUP-12345",
        "unit_price": 200.0,
        "minimum_order_quantity": 10,
        "lead_time_days": 14,
        "is_preferred": True
    }
)
```

### 7. Pricing History

Track and analyze pricing changes over time.

**API Endpoints:**
```
GET /api/v1/product-advanced/{product_id}/pricing-history
GET /api/v1/product-advanced/{product_id}/pricing-trends
```

**Example:**
```python
# Get pricing history
history = service.get_pricing_history(
    product_id=1,
    start_date="2024-01-01",
    end_date="2024-03-31",
    limit=50
)

# Analyze pricing trends
trends = service.analyze_pricing_trends(
    product_id=1,
    period_days=90
)

# Trends include:
# - Current, min, max, average prices
# - Price change and percentage
# - Trend direction (increasing/decreasing/stable)
# - Volatility
```

### 8. Performance Analytics

Analyze product performance metrics.

**API Endpoints:**
```
GET /api/v1/product-advanced/{product_id}/performance
GET /api/v1/product-advanced/category/{category}/performance
```

**Example:**
```python
# Get product performance
performance = service.get_product_performance(
    product_id=1,
    period_days=30
)

# Metrics include:
# - Total sales and revenue
# - Average order value
# - Return rate
# - Customer satisfaction
# - Repeat purchase rate

# Get category performance
category_perf = service.get_category_performance(
    category="Solar Modules",
    period_days=30,
    limit=10
)
```

### 9. Price Matrix Integration

Integrate with the price matrix system for advanced pricing.

**API Endpoints:**
```
GET  /api/v1/product-advanced/{product_id}/matrix-pricing
POST /api/v1/product-advanced/bulk-pricing
```

**Example:**
```python
# Get pricing from matrix
pricing = service.get_product_pricing_from_matrix(
    product_id=1,
    quantity=10,
    context={"discount_code": "BULK10"}
)

# Get bulk pricing
bulk_pricing = service.get_bulk_pricing(
    product_ids=[1, 2, 3, 4, 5],
    quantities=[10, 5, 8, 12, 6],
    context={"customer_type": "wholesale"}
)

# Bulk discounts:
# - 5-9 products: 3% discount
# - 10+ products: 5% discount
```

## Error Handling

All service methods include comprehensive error handling:

```python
try:
    result = service.get_product_lifecycle(product_id=1)
except ValueError as e:
    # Product not found or validation error
    print(f"Validation error: {e}")
except RuntimeError as e:
    # Service operation failed
    print(f"Operation failed: {e}")
except Exception as e:
    # Unexpected error
    print(f"Unexpected error: {e}")
```

## Logging

All operations are logged with timing information:

```
INFO: Product Advanced Service initialized successfully
INFO: Updated product 1 lifecycle to discontinued
INFO: Created version 2 for product 1
INFO: Compared 3 products across 5 attributes
INFO: Generated 5 product recommendations
```

## Health Checks

Monitor service health:

```python
health = service.health_check()

if health.status == "healthy":
    print("Service is operational")
else:
    print(f"Service issue: {health.message}")
```

## Best Practices

1. **Lifecycle Management**
   - Always provide notes when changing lifecycle status
   - Archive discontinued products after grace period
   - Use pending_approval for new products

2. **Versioning**
   - Create versions for significant changes
   - Include detailed version notes
   - Track breaking changes separately

3. **Recommendations**
   - Provide comprehensive calculation context
   - Include budget and preferences
   - Review recommendation scores

4. **Availability**
   - Set appropriate reorder points
   - Update stock regularly
   - Provide restock dates when known

5. **Performance Analytics**
   - Analyze trends over consistent periods
   - Compare products within same category
   - Monitor key metrics regularly

## Integration Examples

### Solar Calculator Integration

```python
# Get recommendations for solar project
recommendations = service.get_product_recommendations(
    calculation_context={
        "required_power": 5000,  # 5kW system
        "budget": 12000.0,
        "roof_area": 30,
        "preferred_brands": ["Trina", "JA Solar"]
    },
    category="Solar Modules",
    limit=5
)

# Check availability
for rec in recommendations:
    availability = service.get_product_availability(rec["id"])
    if availability["is_available"]:
        print(f"{rec['model_name']}: {availability['stock_quantity']} in stock")
```

### Price Matrix Integration

```python
# Calculate system pricing
module_ids = [1, 1, 1, 1, 1]  # 5 modules
inverter_id = 10
battery_id = 20

bulk_pricing = service.get_bulk_pricing(
    product_ids=module_ids + [inverter_id, battery_id],
    quantities=[1] * len(module_ids) + [1, 1],
    context={
        "system_type": "residential",
        "installation_included": True
    }
)

print(f"Total system price: €{bulk_pricing['total_price']:.2f}")
```

## API Response Examples

### Lifecycle Response
```json
{
  "success": true,
  "data": {
    "product_id": 1,
    "status": "active",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-15T10:30:00",
    "version": 2,
    "is_active": true
  }
}
```

### Comparison Response
```json
{
  "success": true,
  "data": {
    "products": [
      {"id": 1, "model_name": "Module A", "brand": "Brand A"},
      {"id": 2, "model_name": "Module B", "brand": "Brand B"}
    ],
    "attributes": {
      "power_wp": {
        "values": [
          {"product_id": 1, "value": 400, "formatted_value": "400W"},
          {"product_id": 2, "value": 450, "formatted_value": "450W"}
        ],
        "has_differences": true
      }
    },
    "summary": {
      "total_products": 2,
      "total_attributes": 3
    }
  }
}
```

### Recommendation Response
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "model_name": "Module 400W",
      "brand": "TestBrand",
      "power_wp": 400,
      "efficiency": 20.5,
      "price_euro": 250.0,
      "recommendation_score": 55.0,
      "recommendation_reasons": [
        "Currently available",
        "Power output: 400W",
        "High efficiency: 20.5%",
        "Preferred brand: TestBrand"
      ]
    }
  ]
}
```

## See Also

- [Product Service Guide](./PRODUCT_SERVICE_GUIDE.md)
- [Pricing Service Guide](./PRICING_SERVICE_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
