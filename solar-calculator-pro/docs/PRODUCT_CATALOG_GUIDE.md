# Product Catalog Management System - Complete Guide

## Overview

The Product Catalog Management System provides comprehensive functionality for managing products, categories, attributes, variants, bundles, relationships, and tags in the Solar Calculator Pro application.

## Features

### 1. Hierarchical Categories
- **Multi-level category tree** with unlimited depth
- **Parent-child relationships** for organizing products
- **Path-based queries** for efficient hierarchy traversal
- **Sort ordering** for custom category arrangement
- **Active/inactive status** for visibility control
- **Category images** for visual representation
- **Flexible metadata** for additional category data

### 2. Product Attributes System
- **Multiple attribute types**: text, number, boolean, select, multiselect
- **Unit support** for measurements (W, kg, cm, etc.)
- **Validation rules** for data integrity
- **Filterable attributes** for product search
- **Searchable attributes** for full-text search
- **Required/optional** attribute configuration
- **Predefined values** for select/multiselect attributes

### 3. Product Variants
- **Multiple variants per product** (e.g., different colors, sizes)
- **Price adjustments** relative to base product price
- **Independent stock tracking** per variant
- **Variant-specific attributes** (color, size, etc.)
- **Variant-specific images**
- **Active/inactive status** per variant

### 4. Product Bundles
- **Multiple products in one bundle**
- **Bundle pricing** with automatic discount calculation
- **Quantity specification** for each product in bundle
- **Bundle-specific images**
- **Featured bundles** for promotions
- **Total savings calculation**

### 5. Product Relationships
- **Related products** for cross-selling
- **Upsell products** for higher-value alternatives
- **Cross-sell products** for complementary items
- **Accessory products** for add-ons
- **Sort ordering** for relationship priority

### 6. Product Tags
- **Flexible tagging system** for product categorization
- **Color-coded tags** for visual distinction
- **Tag-based filtering** in product search
- **Active/inactive status** for tag management
- **Tag descriptions** for clarity

## Database Schema

### Tables

1. **categories** - Hierarchical product categories
2. **attributes** - Product attribute definitions
3. **attribute_values** - Predefined values for select attributes
4. **products** - Base product information
5. **product_variants** - Product variants
6. **product_bundles** - Product bundles
7. **product_relationships** - Product relationships
8. **tags** - Product tags
9. **product_tags** - Many-to-many: products ↔ tags
10. **product_attributes** - Many-to-many: products ↔ attribute values
11. **bundle_products** - Many-to-many: bundles ↔ products

### Key Relationships

```
Category (1) ──→ (N) Product
Category (1) ──→ (N) Category (self-referencing)
Product (1) ──→ (N) ProductVariant
Product (N) ←──→ (N) Tag
Product (N) ←──→ (N) AttributeValue
Product (N) ←──→ (N) Product (relationships)
ProductBundle (N) ←──→ (N) Product
```

## API Endpoints

### Categories

```
POST   /api/v1/catalog/categories              - Create category
GET    /api/v1/catalog/categories/{id}         - Get category by ID
GET    /api/v1/catalog/categories              - List categories
GET    /api/v1/catalog/categories/tree/all     - Get category tree
PUT    /api/v1/catalog/categories/{id}         - Update category
DELETE /api/v1/catalog/categories/{id}         - Delete category
```

### Attributes

```
POST   /api/v1/catalog/attributes              - Create attribute
GET    /api/v1/catalog/attributes/{id}         - Get attribute by ID
GET    /api/v1/catalog/attributes              - List attributes
PUT    /api/v1/catalog/attributes/{id}         - Update attribute
DELETE /api/v1/catalog/attributes/{id}         - Delete attribute
```

### Products

```
POST   /api/v1/catalog/products                - Create product
GET    /api/v1/catalog/products/{id}           - Get product by ID
POST   /api/v1/catalog/products/search         - Search products
PUT    /api/v1/catalog/products/{id}           - Update product
DELETE /api/v1/catalog/products/{id}           - Delete product
```

### Product Variants

```
POST   /api/v1/catalog/products/{id}/variants  - Create variant
GET    /api/v1/catalog/products/{id}/variants  - List product variants
GET    /api/v1/catalog/variants/{id}           - Get variant by ID
PUT    /api/v1/catalog/variants/{id}           - Update variant
DELETE /api/v1/catalog/variants/{id}           - Delete variant
```

### Product Bundles

```
POST   /api/v1/catalog/bundles                 - Create bundle
GET    /api/v1/catalog/bundles/{id}            - Get bundle by ID
GET    /api/v1/catalog/bundles                 - List bundles
PUT    /api/v1/catalog/bundles/{id}            - Update bundle
DELETE /api/v1/catalog/bundles/{id}            - Delete bundle
```

### Product Relationships

```
POST   /api/v1/catalog/products/{id}/relationships  - Create relationship
GET    /api/v1/catalog/products/{id}/related        - Get related products
DELETE /api/v1/catalog/relationships/{id}           - Delete relationship
```

### Tags

```
POST   /api/v1/catalog/tags                    - Create tag
GET    /api/v1/catalog/tags/{id}               - Get tag by ID
GET    /api/v1/catalog/tags                    - List tags
PUT    /api/v1/catalog/tags/{id}               - Update tag
DELETE /api/v1/catalog/tags/{id}               - Delete tag
```

## Usage Examples

### Creating a Category

```python
import requests

category_data = {
    "name": "Solar Panels",
    "slug": "solar-panels",
    "description": "High-efficiency solar panels",
    "parent_id": None,
    "sort_order": 1,
    "is_active": True
}

response = requests.post(
    "http://localhost:8000/api/v1/catalog/categories",
    json=category_data
)
category = response.json()
```

### Creating a Product with Attributes

```python
product_data = {
    "sku": "SP-500W-001",
    "name": "500W Monocrystalline Solar Panel",
    "slug": "500w-mono-solar-panel",
    "description": "High-efficiency 500W solar panel",
    "category_id": 1,
    "manufacturer": "SolarTech",
    "model": "ST-500M",
    "base_price": 299.99,
    "currency": "EUR",
    "is_active": True,
    "stock_quantity": 100,
    "tag_ids": [1, 2],
    "attribute_value_ids": [5, 8, 12]
}

response = requests.post(
    "http://localhost:8000/api/v1/catalog/products",
    json=product_data
)
product = response.json()
```

### Creating Product Variants

```python
variant_data = {
    "sku": "SP-500W-001-BLK",
    "name": "500W Solar Panel - Black Frame",
    "price_adjustment": 20.00,
    "stock_quantity": 50,
    "variant_attributes": {
        "color": "black",
        "frame_type": "aluminum"
    }
}

response = requests.post(
    f"http://localhost:8000/api/v1/catalog/products/{product_id}/variants",
    json=variant_data
)
variant = response.json()
```

### Creating a Product Bundle

```python
bundle_data = {
    "name": "Complete Solar System Bundle",
    "slug": "complete-solar-bundle",
    "description": "Everything you need for a 5kW system",
    "bundle_price": 4999.99,
    "discount_percentage": 15.0,
    "product_items": [
        {"product_id": 1, "quantity": 10},  # Solar panels
        {"product_id": 5, "quantity": 1},   # Inverter
        {"product_id": 8, "quantity": 1}    # Mounting system
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/catalog/bundles",
    json=bundle_data
)
bundle = response.json()
```

### Searching Products

```python
search_params = {
    "query": "solar panel",
    "category_id": 1,
    "min_price": 200.00,
    "max_price": 500.00,
    "tags": [1, 2],
    "is_active": True,
    "in_stock": True,
    "sort_by": "price",
    "sort_order": "asc",
    "page": 1,
    "page_size": 20
}

response = requests.post(
    "http://localhost:8000/api/v1/catalog/products/search",
    json=search_params
)
results = response.json()
```

## Best Practices

### Category Organization
1. **Keep hierarchy shallow** (3-4 levels maximum)
2. **Use descriptive names** for clarity
3. **Set appropriate sort orders** for logical arrangement
4. **Use slugs consistently** for URL-friendly paths

### Product Management
1. **Use unique SKUs** for all products and variants
2. **Provide detailed descriptions** for better search
3. **Add multiple images** for better visualization
4. **Set accurate stock quantities** for inventory management
5. **Use tags liberally** for flexible categorization

### Attribute System
1. **Define attributes before products** for consistency
2. **Use appropriate types** for data validation
3. **Set validation rules** for data integrity
4. **Make critical attributes required**
5. **Use units consistently** for measurements

### Performance Optimization
1. **Use pagination** for large product lists
2. **Filter by category** to reduce result sets
3. **Index frequently searched fields**
4. **Cache category trees** for faster access
5. **Use eager loading** for relationships

## Integration with Other Systems

### Price Matrix Integration
- Products can be linked to price matrix entries
- Dynamic pricing based on product attributes
- Bulk pricing for product bundles

### PDF Generation Integration
- Product data included in PDF quotes
- Product images embedded in PDFs
- Product specifications in technical sheets

### CRM Integration
- Products linked to customer quotes
- Product recommendations based on customer history
- Product availability tracking for sales

## Troubleshooting

### Common Issues

**Issue**: Category tree not loading
- **Solution**: Check parent_id references are valid
- **Solution**: Verify is_active status is set correctly

**Issue**: Product search returns no results
- **Solution**: Check search filters are not too restrictive
- **Solution**: Verify products have is_active = True

**Issue**: Variant price calculation incorrect
- **Solution**: Ensure price_adjustment is set correctly
- **Solution**: Check base_price on parent product

**Issue**: Bundle total savings not calculating
- **Solution**: Verify all products in bundle have valid prices
- **Solution**: Check discount_percentage is set

## Future Enhancements

- **Product reviews and ratings**
- **Product comparison tool**
- **Advanced inventory management**
- **Product import/export (CSV, Excel)**
- **Product image optimization**
- **Product recommendations engine**
- **Multi-language product descriptions**
- **Product availability notifications**

## Support

For issues or questions:
- Check the API documentation at `/docs`
- Review the code examples above
- Contact the development team
