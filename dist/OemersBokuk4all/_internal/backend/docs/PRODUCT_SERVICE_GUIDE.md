# Product Management Service Guide

## Overview

The Product Management Service provides a comprehensive API for managing products in the solar calculator application. It wraps the legacy `product_db.py` module and provides:

- **CRUD Operations**: Create, Read, Update, Delete products
- **Search and Filtering**: Advanced product search with multiple filters
- **Image Management**: Upload and manage product images
- **Import/Export**: Bulk import and export of product data
- **Category Management**: List and filter by product categories

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              FastAPI Product Endpoints                   │
│                 (api/v1/products.py)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ProductService                              │
│          (services/product_service.py)                   │
│                                                          │
│  • Input validation                                      │
│  • Error handling                                        │
│  • Logging                                               │
│  • Business logic                                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Legacy product_db.py                        │
│                                                          │
│  • Database operations                                   │
│  • Product CRUD                                          │
│  • Pricing calculations                                  │
└─────────────────────────────────────────────────────────┘
```

## Service Initialization

```python
from backend.services.product_service import get_product_service

# Get the singleton service instance
service = get_product_service()

# Service is automatically initialized
# Check health
health = service.health_check()
print(f"Service status: {health.status.value}")
```

## CRUD Operations

### Create Product

```python
# Create a new product
product_data = {
    'category': 'Modul',
    'model_name': 'SolarMax 450W',
    'brand': 'SolarMax',
    'price_euro': 220.0,
    'capacity_w': 450.0,
    'warranty_years': 25,
    'efficiency_percent': 21.5,
    'technology': 'Monokristallin',
    'feature': 'Bifazial'
}

created_product = service.create_product(product_data)
print(f"Created product ID: {created_product['id']}")
```

### Get Product

```python
# Get product by ID
product = service.get_product(product_id=1)
if product:
    print(f"Product: {product['model_name']}")

# Get product by model name
product = service.get_product_by_model_name('SolarMax 450W')
if product:
    print(f"Found product ID: {product['id']}")
```

### Update Product

```python
# Update product fields
update_data = {
    'price_euro': 210.0,
    'warranty_years': 30
}

updated_product = service.update_product(
    product_id=1,
    product_data=update_data
)
print(f"Updated product: {updated_product['model_name']}")
```

### Delete Product

```python
# Delete a product
success = service.delete_product(product_id=1)
if success:
    print("Product deleted successfully")
```

## Search and Filtering

### List Products

```python
# List all products
products = service.list_products()
print(f"Total products: {len(products)}")

# Filter by category
pv_modules = service.list_products(category='Modul')
print(f"PV Modules: {len(pv_modules)}")

# Filter by company
company_products = service.list_products(company_id=1)

# Search in model name, brand, or description
search_results = service.list_products(search_term='SolarMax')

# Pagination
page_1 = service.list_products(limit=10, offset=0)
page_2 = service.list_products(limit=10, offset=10)
```

### Advanced Search

```python
# Search with multiple filters
filters = {
    'category': 'Modul',
    'brand': 'SolarMax',
    'price_min': 150.0,
    'price_max': 300.0
}

results = service.search_products(
    query='450W',
    filters=filters,
    limit=50
)

for product in results:
    print(f"{product['model_name']}: €{product['price_euro']}")
```

### Get Categories

```python
# Get all product categories
categories = service.get_categories()
print(f"Categories: {', '.join(categories)}")
```

## Image Management

### Upload Product Image

```python
import base64

# Upload image from base64 data
with open('product_image.jpg', 'rb') as f:
    image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

updated_product = service.upload_product_image(
    product_id=1,
    image_data=image_base64,
    image_format='base64'
)

# Upload image from file path
updated_product = service.upload_product_image(
    product_id=1,
    image_data='/path/to/image.jpg',
    image_format='file_path'
)
```

### Delete Product Image

```python
# Remove image from product
updated_product = service.delete_product_image(product_id=1)
```

## Import/Export

### Export Products

```python
# Export to JSON
export_data = service.export_products(
    category='Modul',
    format='json'
)
print(f"Exported {export_data['product_count']} products")

# Save to file
import json
with open('products_export.json', 'w') as f:
    json.dump(export_data, f, indent=2)

# Export to CSV
csv_export = service.export_products(format='csv')
with open('products_export.csv', 'w') as f:
    f.write(csv_export['csv_data'])
```

### Import Products

```python
# Import from JSON
import_data = {
    'products': [
        {
            'category': 'Modul',
            'model_name': 'NewModule 500W',
            'brand': 'NewBrand',
            'price_euro': 250.0,
            'capacity_w': 500.0
        },
        # ... more products
    ]
}

results = service.import_products(
    import_data=import_data,
    format='json',
    update_existing=False  # Set to True to update existing products
)

print(f"Created: {results['created']}")
print(f"Updated: {results['updated']}")
print(f"Failed: {results['failed']}")

if results['errors']:
    print("Errors:")
    for error in results['errors']:
        print(f"  - {error}")
```

## API Endpoints

### Product CRUD

```
POST   /api/v1/products/                    Create product
GET    /api/v1/products/{product_id}        Get product by ID
GET    /api/v1/products/by-model/{name}     Get product by model name
PUT    /api/v1/products/{product_id}        Update product
DELETE /api/v1/products/{product_id}        Delete product
```

### Search and Filtering

```
GET    /api/v1/products/                    List products (with filters)
POST   /api/v1/products/search              Advanced search
GET    /api/v1/products/categories/list     Get categories
```

### Image Management

```
POST   /api/v1/products/{product_id}/image  Upload image
DELETE /api/v1/products/{product_id}/image  Delete image
```

### Import/Export

```
POST   /api/v1/products/export              Export products
POST   /api/v1/products/import              Import products
```

## Example API Requests

### Create Product

```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Modul",
    "model_name": "SolarMax 450W",
    "brand": "SolarMax",
    "price_euro": 220.0,
    "capacity_w": 450.0,
    "warranty_years": 25
  }'
```

### Search Products

```bash
curl -X POST "http://localhost:8000/api/v1/products/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "450W",
    "category": "Modul",
    "price_min": 150.0,
    "price_max": 300.0,
    "limit": 50
  }'
```

### Export Products

```bash
curl -X POST "http://localhost:8000/api/v1/products/export" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Modul",
    "format": "json"
  }'
```

## Product Data Model

### Core Fields

- **id**: Product ID (auto-generated)
- **category**: Product category (required)
- **model_name**: Unique model name (required)
- **brand**: Manufacturer/brand
- **price_euro**: Price in euros

### Technical Specifications

- **capacity_w**: Capacity in watts (PV modules)
- **storage_power_kw**: Storage power in kW (batteries)
- **power_kw**: Power in kW (inverters)
- **max_cycles**: Maximum charge cycles (batteries)
- **warranty_years**: Warranty period
- **length_m**, **width_m**, **weight_kg**: Physical dimensions
- **efficiency_percent**: Efficiency percentage

### Enhanced Pricing Fields

- **calculate_per**: Calculation method (Stück, Meter, pauschal, kWp)
- **purchase_price_net**: Purchase price (net)
- **margin_type**: Margin type (percentage or fixed)
- **margin_value**: Margin value
- **pricing_category**: Pricing category

### Technical Attributes

- **technology**: Technology type (e.g., Monokristallin, HJT)
- **feature**: Special features (e.g., Bifazial)
- **design**: Design variant (e.g., All-Black)
- **upgrade**: Upgrade options
- **outdoor_opt**: Outdoor optimization (0/1)
- **self_supply_feature**: Self supply feature (0/1)
- **shadow_fading**: Shadow fading feature (0/1)
- **smart_home**: Smart home integration (0/1)

### Module Details

- **cell_technology**: Cell technology (e.g., N-Type, TOPCon)
- **module_structure**: Module structure (e.g., Glas-Glas)
- **cell_type**: Cell type (e.g., 108 Halbzellen)
- **version**: Version (e.g., All-Black)
- **module_warranty_text**: Warranty text

### Other Fields

- **image_base64**: Product image (base64 encoded)
- **description**: Product description
- **pros**: Product advantages
- **cons**: Product disadvantages
- **rating**: Product rating (0-5)
- **labor_hours**: Labor hours for installation
- **datasheet_link_db_path**: Datasheet file path
- **company_id**: Company ID
- **created_at**: Creation timestamp
- **updated_at**: Last update timestamp

## Error Handling

The service provides comprehensive error handling:

```python
try:
    product = service.create_product(product_data)
except ValueError as e:
    # Validation error (e.g., missing required fields)
    print(f"Validation error: {e}")
except RuntimeError as e:
    # Operation error (e.g., database error)
    print(f"Operation error: {e}")
except Exception as e:
    # Unexpected error
    print(f"Unexpected error: {e}")
```

## Health Checks

```python
# Check service health
health = service.health_check()

print(f"Status: {health.status.value}")
print(f"Message: {health.message}")

if health.details:
    print(f"Product count: {health.details.get('product_count')}")
    print(f"DB available: {health.details.get('db_available')}")
```

## Best Practices

1. **Always validate input data** before creating or updating products
2. **Use search and filtering** instead of loading all products
3. **Implement pagination** for large product lists
4. **Handle errors gracefully** with try-except blocks
5. **Use transactions** for bulk operations (import/export)
6. **Optimize images** before uploading (compress, resize)
7. **Cache frequently accessed products** in your application
8. **Use model_name** as a unique identifier for products
9. **Validate pricing data** before updating prices
10. **Test import/export** with small datasets first

## Performance Considerations

- **Pagination**: Use `limit` and `offset` for large product lists
- **Filtering**: Apply filters at the database level when possible
- **Caching**: Cache frequently accessed products
- **Batch Operations**: Use import/export for bulk operations
- **Image Optimization**: Compress images before uploading
- **Search Optimization**: Use indexed fields for search

## Integration with Other Services

The Product Management Service integrates with:

- **Pricing Service**: For price calculations and matrix lookups
- **Solar Calculator Service**: For system component selection
- **PDF Generation Service**: For product datasheets
- **Database Service**: For data persistence

## Troubleshooting

### Service Not Initialized

```python
# Ensure service is initialized
service = get_product_service()
if not service.is_initialized:
    service.initialize()
```

### Database Not Available

```python
# Check database availability
health = service.health_check()
if not health.details.get('db_available'):
    print("Database is not available")
    # Check database connection
```

### Product Not Found

```python
# Always check if product exists
product = service.get_product(product_id)
if not product:
    print(f"Product {product_id} not found")
```

### Import Errors

```python
# Check import results for errors
results = service.import_products(import_data)
if results['failed'] > 0:
    print("Import errors:")
    for error in results['errors']:
        print(f"  - {error}")
```

## See Also

- [Product Service Quick Reference](PRODUCT_SERVICE_QUICK_REFERENCE.md)
- [Pricing Service Guide](PRICING_SERVICE_GUIDE.md)
- [Database Service Guide](DATABASE_SERVICE_GUIDE.md)
- [API Documentation](../api/v1/products.py)
