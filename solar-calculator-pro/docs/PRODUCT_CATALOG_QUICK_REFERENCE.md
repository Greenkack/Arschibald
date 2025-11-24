# Product Catalog Management - Quick Reference

## Quick Start

### 1. Create a Category
```bash
curl -X POST http://localhost:8000/api/v1/catalog/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Solar Panels",
    "slug": "solar-panels",
    "is_active": true
  }'
```

### 2. Create a Product
```bash
curl -X POST http://localhost:8000/api/v1/catalog/products \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SP-500W-001",
    "name": "500W Solar Panel",
    "slug": "500w-solar-panel",
    "base_price": 299.99,
    "category_id": 1
  }'
```

### 3. Search Products
```bash
curl -X POST http://localhost:8000/api/v1/catalog/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "solar",
    "page": 1,
    "page_size": 20
  }'
```

## Key Concepts

### Hierarchical Categories
- **Parent-child relationships** for organization
- **Unlimited depth** for complex hierarchies
- **Path-based queries** for efficiency

### Product Attributes
- **Types**: text, number, boolean, select, multiselect
- **Validation**: min/max, required, custom rules
- **Filtering**: searchable, filterable attributes

### Product Variants
- **Multiple variants** per product
- **Price adjustments** from base price
- **Independent stock** tracking

### Product Bundles
- **Multiple products** in one package
- **Discount pricing** with savings calculation
- **Quantity control** per product

### Product Relationships
- **Related**: similar products
- **Cross-sell**: complementary products
- **Upsell**: premium alternatives
- **Accessory**: add-on products

### Tags
- **Flexible categorization** beyond categories
- **Color-coded** for visual distinction
- **Multi-tag** support per product

## API Endpoints Summary

| Resource | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| **Categories** |
| | POST | `/catalog/categories` | Create category |
| | GET | `/catalog/categories/{id}` | Get category |
| | GET | `/catalog/categories` | List categories |
| | GET | `/catalog/categories/tree/all` | Get tree |
| | PUT | `/catalog/categories/{id}` | Update category |
| | DELETE | `/catalog/categories/{id}` | Delete category |
| **Attributes** |
| | POST | `/catalog/attributes` | Create attribute |
| | GET | `/catalog/attributes/{id}` | Get attribute |
| | GET | `/catalog/attributes` | List attributes |
| | PUT | `/catalog/attributes/{id}` | Update attribute |
| | DELETE | `/catalog/attributes/{id}` | Delete attribute |
| **Products** |
| | POST | `/catalog/products` | Create product |
| | GET | `/catalog/products/{id}` | Get product |
| | POST | `/catalog/products/search` | Search products |
| | PUT | `/catalog/products/{id}` | Update product |
| | DELETE | `/catalog/products/{id}` | Delete product |
| **Variants** |
| | POST | `/catalog/products/{id}/variants` | Create variant |
| | GET | `/catalog/products/{id}/variants` | List variants |
| | GET | `/catalog/variants/{id}` | Get variant |
| | PUT | `/catalog/variants/{id}` | Update variant |
| | DELETE | `/catalog/variants/{id}` | Delete variant |
| **Bundles** |
| | POST | `/catalog/bundles` | Create bundle |
| | GET | `/catalog/bundles/{id}` | Get bundle |
| | GET | `/catalog/bundles` | List bundles |
| | PUT | `/catalog/bundles/{id}` | Update bundle |
| | DELETE | `/catalog/bundles/{id}` | Delete bundle |
| **Relationships** |
| | POST | `/catalog/products/{id}/relationships` | Create relationship |
| | GET | `/catalog/products/{id}/related` | Get related |
| | DELETE | `/catalog/relationships/{id}` | Delete relationship |
| **Tags** |
| | POST | `/catalog/tags` | Create tag |
| | GET | `/catalog/tags/{id}` | Get tag |
| | GET | `/catalog/tags` | List tags |
| | PUT | `/catalog/tags/{id}` | Update tag |
| | DELETE | `/catalog/tags/{id}` | Delete tag |

## Common Patterns

### Creating a Complete Product

```python
# 1. Create category
category = create_category({"name": "Solar Panels", "slug": "solar-panels"})

# 2. Create attributes
power_attr = create_attribute({"name": "Power", "type": "number", "unit": "W"})
color_attr = create_attribute({"name": "Color", "type": "select"})

# 3. Create attribute values
black_value = create_attribute_value({"attribute_id": color_attr.id, "value": "black", "label": "Black"})

# 4. Create product
product = create_product({
    "sku": "SP-500W-001",
    "name": "500W Solar Panel",
    "category_id": category.id,
    "base_price": 299.99,
    "attribute_value_ids": [black_value.id]
})

# 5. Create variants
variant = create_variant({
    "parent_product_id": product.id,
    "sku": "SP-500W-001-BLK",
    "name": "500W Solar Panel - Black",
    "price_adjustment": 0.00
})

# 6. Add tags
tag = create_tag({"name": "High Efficiency", "slug": "high-efficiency"})
update_product(product.id, {"tag_ids": [tag.id]})
```

### Searching with Filters

```python
search_params = {
    "query": "solar panel",           # Text search
    "category_id": 1,                 # Filter by category
    "manufacturer": "SolarTech",      # Filter by manufacturer
    "min_price": 200.00,              # Price range
    "max_price": 500.00,
    "tags": [1, 2],                   # Filter by tags
    "is_active": True,                # Only active products
    "in_stock": True,                 # Only in-stock products
    "sort_by": "price",               # Sort by price
    "sort_order": "asc",              # Ascending order
    "page": 1,                        # Page number
    "page_size": 20                   # Items per page
}

results = search_products(search_params)
```

### Creating a Bundle

```python
bundle = create_bundle({
    "name": "Complete Solar System",
    "slug": "complete-solar-system",
    "bundle_price": 4999.99,
    "discount_percentage": 15.0,
    "product_items": [
        {"product_id": 1, "quantity": 10},  # 10x Solar panels
        {"product_id": 5, "quantity": 1},   # 1x Inverter
        {"product_id": 8, "quantity": 1}    # 1x Mounting system
    ]
})
```

### Adding Product Relationships

```python
# Add related products
create_relationship({
    "product_id": 1,
    "related_product_id": 2,
    "relationship_type": "related",
    "sort_order": 1
})

# Add upsell product
create_relationship({
    "product_id": 1,
    "related_product_id": 3,
    "relationship_type": "upsell",
    "sort_order": 1
})

# Add accessory
create_relationship({
    "product_id": 1,
    "related_product_id": 10,
    "relationship_type": "accessory",
    "sort_order": 1
})
```

## Data Models

### Category
```json
{
  "id": 1,
  "name": "Solar Panels",
  "slug": "solar-panels",
  "description": "High-efficiency solar panels",
  "parent_id": null,
  "level": 0,
  "path": "",
  "sort_order": 1,
  "is_active": true,
  "image_url": "/images/categories/solar-panels.jpg",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Product
```json
{
  "id": 1,
  "sku": "SP-500W-001",
  "name": "500W Monocrystalline Solar Panel",
  "slug": "500w-mono-solar-panel",
  "description": "High-efficiency 500W solar panel",
  "short_description": "500W solar panel with 21% efficiency",
  "category_id": 1,
  "manufacturer": "SolarTech",
  "model": "ST-500M",
  "base_price": 299.99,
  "currency": "EUR",
  "is_active": true,
  "is_featured": false,
  "stock_quantity": 100,
  "weight": 25.5,
  "dimensions": {"length": 200, "width": 100, "height": 4},
  "images": ["/images/products/sp-500w-001-1.jpg"],
  "specifications": {"power": 500, "efficiency": 21, "warranty": 25},
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Product Variant
```json
{
  "id": 1,
  "parent_product_id": 1,
  "sku": "SP-500W-001-BLK",
  "name": "500W Solar Panel - Black Frame",
  "description": "Black aluminum frame variant",
  "price_adjustment": 20.00,
  "stock_quantity": 50,
  "is_active": true,
  "variant_attributes": {"color": "black", "frame_type": "aluminum"},
  "images": ["/images/variants/sp-500w-001-blk-1.jpg"],
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Product Bundle
```json
{
  "id": 1,
  "name": "Complete Solar System Bundle",
  "slug": "complete-solar-bundle",
  "description": "Everything you need for a 5kW system",
  "bundle_price": 4999.99,
  "discount_percentage": 15.0,
  "is_active": true,
  "is_featured": true,
  "images": ["/images/bundles/complete-solar-1.jpg"],
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "products": [...]
}
```

## Tips & Tricks

### Performance
- Use pagination for large product lists
- Filter by category to reduce result sets
- Cache category trees for faster access
- Use eager loading for relationships

### Data Integrity
- Always use unique SKUs
- Validate parent_id references for categories
- Check stock quantities before orders
- Verify price adjustments are reasonable

### Search Optimization
- Use specific queries for better results
- Combine multiple filters for precision
- Sort by relevance for text searches
- Use tags for flexible categorization

### Maintenance
- Regularly update stock quantities
- Archive inactive products
- Clean up unused tags
- Optimize category hierarchy

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Category tree not loading | Check parent_id references |
| Product search returns nothing | Verify is_active = true |
| Variant price incorrect | Check price_adjustment value |
| Bundle savings wrong | Verify discount_percentage |
| Duplicate SKU error | Use unique SKUs for all products |
| Relationship not showing | Check relationship_type value |

## Next Steps

1. **Set up categories** for your product hierarchy
2. **Define attributes** for product specifications
3. **Import products** with all details
4. **Create variants** for product options
5. **Build bundles** for promotions
6. **Add relationships** for cross-selling
7. **Tag products** for flexible categorization

## Resources

- Full Guide: `PRODUCT_CATALOG_GUIDE.md`
- API Documentation: `http://localhost:8000/docs`
- Database Schema: See migration files
- Code Examples: See service and API files
