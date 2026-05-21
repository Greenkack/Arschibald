# API Quick Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
```bash
# Login
POST /auth/login
Body: {"username": "admin", "password": "password"}

# Use token in headers
Authorization: Bearer <token>
```

## Solar Calculator
```bash
# Calculate
POST /solar/calculate
Body: {
  "roof_area": 50.0,
  "roof_type": "flat",
  "roof_angle": 30.0,
  "orientation": "south",
  "module_type": "standard",
  "annual_consumption": 4000.0,
  "location": "Berlin"
}

# List projects
GET /solar/projects?page=1&page_size=20

# Create project
POST /solar/projects
Body: {
  "name": "Project Name",
  "customer_name": "Customer",
  "project_type": "solar",
  "data": {}
}

# Get project
GET /solar/projects/{id}

# Update project
PUT /solar/projects/{id}

# Delete project
DELETE /solar/projects/{id}

# 3D visualization
POST /solar/3d-visualization
Body: {
  "project_id": 1,
  "roof_type": "flat",
  "module_count": 30
}
```

## Price Matrix
```bash
# Get matrix
GET /pricing/matrix

# Upload matrix
POST /pricing/matrix/upload
Body: {
  "file_name": "matrix.xlsx",
  "file_content": "base64...",
  "matrix_type": "solar_pv"
}

# Calculate price
POST /pricing/calculate
Body: {
  "module_count": 30,
  "battery_model": "Tesla Powerwall 2",
  "extras": ["monitoring"]
}

# Validate matrix
POST /pricing/validate
```

## PDF Generation
```bash
# Generate PDF
POST /pdf/generate
Body: {
  "project_id": 1,
  "template": "standard",
  "options": {
    "include_charts": true,
    "include_3d": true
  }
}

# List templates
GET /pdf/templates

# Preview PDF
POST /pdf/preview
Body: {
  "project_id": 1,
  "template": "standard",
  "page": 1
}
```

## Products
```bash
# List products
GET /products?page=1&page_size=20&category=solar_modules

# Create product
POST /products
Body: {
  "name": "Solar Module 400W",
  "category": "solar_modules",
  "manufacturer": "SolarTech",
  "price": 250.0,
  "specifications": {}
}

# Get product
GET /products/{id}

# Update product
PUT /products/{id}

# Delete product
DELETE /products/{id}

# Search products
GET /products/search?q=solar&category=modules
```

## CRM
```bash
# List customers
GET /crm/customers?page=1&page_size=20

# Create customer
POST /crm/customers
Body: {
  "name": "Customer Name",
  "email": "email@example.com",
  "phone": "+49 123 456789",
  "address": {}
}

# Get customer
GET /crm/customers/{id}

# Update customer
PUT /crm/customers/{id}

# Delete customer
DELETE /crm/customers/{id}

# List offers
GET /crm/offers

# Create offer
POST /crm/offers
Body: {
  "customer_id": 1,
  "project_id": 1,
  "amount": 15000.0,
  "valid_until": "2024-12-31"
}

# List tasks
GET /crm/tasks

# Create task
POST /crm/tasks
Body: {
  "title": "Task Title",
  "description": "Description",
  "customer_id": 1,
  "due_date": "2024-12-31",
  "priority": "high"
}
```

## Data Management
```bash
# List records
GET /data/records?page=1&page_size=20

# Create record with dynamic keys
POST /data/records
Body: {
  "data_type": "calculation_result",
  "content": {},
  "metadata": {}
}

# Get record with PDF bytes
GET /data/records/{id}

# Update record
PUT /data/records/{id}

# Delete record
DELETE /data/records/{id}
```

## Common Query Parameters

### Pagination
```
?page=1&page_size=20
```

### Filtering
```
?category=solar_modules&manufacturer=SolarTech
```

### Sorting
```
?sort=price&order=asc
```

### Search
```
?q=search_term
```

## Response Formats

### Success Response
```json
{
  "id": 1,
  "name": "Item",
  "data": {},
  "formatted": {
    "price": "1.234,56 €"
  },
  "dynamic_key": "item_1_20240118120000"
}
```

### Paginated Response
```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

### Error Response
```json
{
  "error": {
    "message": "Error description",
    "details": {},
    "path": "/api/v1/endpoint"
  }
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Authentication | 5/min |
| Calculations | 10/min |
| General | 60/min |

## Number Formatting

All numbers use German formatting:
- Decimal: comma (,)
- Thousand: dot (.)
- Example: 1.234,56

## Date Format

ISO 8601: `YYYY-MM-DDTHH:MM:SS.sssZ`

## Documentation Links

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI Schema: http://localhost:8000/api/openapi.json
- Health Check: http://localhost:8000/health
