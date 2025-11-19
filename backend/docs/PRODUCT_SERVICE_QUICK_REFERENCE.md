# Product Management Service - Quick Reference

## Service Initialization

```python
from backend.services.product_service import get_product_service

service = get_product_service()
```

## CRUD Operations

### Create
```python
product = service.create_product({
    'category': 'Modul',
    'model_name': 'SolarMax 450W',
    'brand': 'SolarMax',
    'price_euro': 220.0
})
```

### Read
```python
# By ID
product = service.get_product(1)

# By model name
product = service.get_product_by_model_name('SolarMax 450W')
```

### Update
```python
updated = service.update_product(1, {'price_euro': 210.0})
```

### Delete
```python
success = service.delete_product(1)
```

## Search & Filter

### List Products
```python
# All products
products = service.list_products()

# By category
modules = service.list_products(category='Modul')

# With search
results = service.list_products(search_term='SolarMax')

# With pagination
page = service.list_products(limit=10, offset=0)
```

### Advanced Search
```python
results = service.search_products(
    query='450W',
    filters={
        'category': 'Modul',
        'price_min': 150.0,
        'price_max': 300.0
    },
    limit=50
)
```

### Categories
```python
categories = service.get_categories()
```

## Image Management

### Upload
```python
# Base64
updated = service.upload_product_image(
    product_id=1,
    image_data='base64string',
    image_format='base64'
)

# File path
updated = service.upload_product_image(
    product_id=1,
    image_data='/path/to/image.jpg',
    image_format='file_path'
)
```

### Delete
```python
updated = service.delete_product_image(1)
```

## Import/Export

### Export
```python
# JSON
data = service.export_products(format='json')

# CSV
data = service.export_products(format='csv')
```

### Import
```python
results = service.import_products(
    import_data={'products': [...]},
    format='json',
    update_existing=False
)
```

## API Endpoints

### CRUD
```
POST   /api/v1/products/
GET    /api/v1/products/{id}
GET    /api/v1/products/by-model/{name}
PUT    /api/v1/products/{id}
DELETE /api/v1/products/{id}
```

### Search
```
GET    /api/v1/products/
POST   /api/v1/products/search
GET    /api/v1/products/categories/list
```

### Images
```
POST   /api/v1/products/{id}/image
DELETE /api/v1/products/{id}/image
```

### Import/Export
```
POST   /api/v1/products/export
POST   /api/v1/products/import
```

## Required Fields

- **category**: Product category
- **model_name**: Unique model name

## Common Filters

- **category**: Filter by category
- **company_id**: Filter by company
- **search_term**: Search in name/brand/description
- **price_min/max**: Price range
- **brand**: Filter by brand
- **limit/offset**: Pagination

## Error Handling

```python
try:
    product = service.create_product(data)
except ValueError as e:
    # Validation error
    pass
except RuntimeError as e:
    # Operation error
    pass
```

## Health Check

```python
health = service.health_check()
print(health.status.value)  # healthy, degraded, unhealthy
```

## Product Fields

### Core
- id, category, model_name, brand, price_euro

### Technical
- capacity_w, power_kw, storage_power_kw
- efficiency_percent, warranty_years
- length_m, width_m, weight_kg

### Pricing
- calculate_per, purchase_price_net
- margin_type, margin_value

### Attributes
- technology, feature, design, upgrade
- outdoor_opt, self_supply_feature
- shadow_fading, smart_home

### Module Details
- cell_technology, module_structure
- cell_type, version, module_warranty_text

### Other
- image_base64, description, pros, cons
- rating, labor_hours, datasheet_link_db_path
- company_id, created_at, updated_at
