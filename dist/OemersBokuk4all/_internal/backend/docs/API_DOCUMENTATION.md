# Solar Calculator Pro API Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)
8. [Postman Collection](#postman-collection)

## Introduction

The Solar Calculator Pro API provides comprehensive functionality for:

- Solar energy system calculations
- Heat pump analysis
- Dynamic pricing with Excel-like formulas
- PDF report generation
- 3D visualization
- Customer relationship management
- Product catalog management

**Base URL**: `http://localhost:8000/api/v1`

**API Documentation**: `http://localhost:8000/api/docs` (Swagger UI)

**Alternative Documentation**: `http://localhost:8000/api/redoc` (ReDoc)

## Authentication

### Login

Obtain a JWT access token:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

Include the token in the Authorization header:

```http
GET /api/v1/solar/projects
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Refresh Token

```http
POST /api/v1/auth/refresh
Authorization: Bearer <current_token>
```

### Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/login` | Login and get access token | No |
| POST | `/api/v1/auth/logout` | Logout and invalidate token | Yes |
| POST | `/api/v1/auth/refresh` | Refresh access token | Yes |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

### Solar Calculator Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/solar/calculate` | Calculate solar system | Yes |
| GET | `/api/v1/solar/projects` | List all projects | Yes |
| POST | `/api/v1/solar/projects` | Create new project | Yes |
| GET | `/api/v1/solar/projects/{id}` | Get project details | Yes |
| PUT | `/api/v1/solar/projects/{id}` | Update project | Yes |
| DELETE | `/api/v1/solar/projects/{id}` | Delete project | Yes |
| POST | `/api/v1/solar/3d-visualization` | Generate 3D model | Yes |

### Price Matrix Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/pricing/matrix` | Get current price matrix | Yes |
| POST | `/api/v1/pricing/matrix/upload` | Upload new matrix | Yes |
| POST | `/api/v1/pricing/calculate` | Calculate price | Yes |
| POST | `/api/v1/pricing/validate` | Validate matrix | Yes |

### PDF Generation Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/pdf/generate` | Generate PDF report | Yes |
| GET | `/api/v1/pdf/templates` | List PDF templates | Yes |
| POST | `/api/v1/pdf/preview` | Preview PDF | Yes |

### Product Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/products` | List products | Yes |
| POST | `/api/v1/products` | Create product | Yes |
| GET | `/api/v1/products/{id}` | Get product details | Yes |
| PUT | `/api/v1/products/{id}` | Update product | Yes |
| DELETE | `/api/v1/products/{id}` | Delete product | Yes |
| GET | `/api/v1/products/search` | Search products | Yes |

### CRM Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/crm/customers` | List customers | Yes |
| POST | `/api/v1/crm/customers` | Create customer | Yes |
| GET | `/api/v1/crm/customers/{id}` | Get customer details | Yes |
| PUT | `/api/v1/crm/customers/{id}` | Update customer | Yes |
| DELETE | `/api/v1/crm/customers/{id}` | Delete customer | Yes |
| GET | `/api/v1/crm/offers` | List offers | Yes |
| POST | `/api/v1/crm/offers` | Create offer | Yes |
| GET | `/api/v1/crm/tasks` | List tasks | Yes |
| POST | `/api/v1/crm/tasks` | Create task | Yes |

### Data Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/data/records` | List all records | Yes |
| POST | `/api/v1/data/records` | Create record with dynamic keys | Yes |
| GET | `/api/v1/data/records/{id}` | Get record with PDF bytes | Yes |
| PUT | `/api/v1/data/records/{id}` | Update record | Yes |
| DELETE | `/api/v1/data/records/{id}` | Delete record | Yes |

## Request/Response Formats

### Solar Calculation Request

```json
{
  "roof_area": 50.0,
  "roof_type": "flat",
  "roof_angle": 30.0,
  "orientation": "south",
  "module_type": "standard",
  "annual_consumption": 4000.0,
  "location": "Berlin"
}
```

### Solar Calculation Response

```json
{
  "system_size": 10.5,
  "module_count": 30,
  "annual_production": 12000.0,
  "self_consumption_rate": 0.35,
  "payback_period": 12.5,
  "total_cost": 15000.0,
  "savings_25_years": 45000.0,
  "co2_savings": 150000.0,
  "formatted": {
    "system_size": "10,50 kWp",
    "total_cost": "15.000,00 €",
    "annual_production": "12.000,00 kWh"
  }
}
```

### Price Calculation Request

```json
{
  "module_count": 30,
  "battery_model": "Tesla Powerwall 2",
  "extras": ["monitoring", "insurance"],
  "discounts": {
    "early_bird": 0.05
  }
}
```

### Price Calculation Response

```json
{
  "base_price": 15000.0,
  "extras_cost": 1500.0,
  "discount_amount": 825.0,
  "total_price": 15675.0,
  "breakdown": {
    "modules": 9000.0,
    "inverter": 3000.0,
    "battery": 8000.0,
    "installation": 2000.0,
    "monitoring": 500.0,
    "insurance": 1000.0
  },
  "formatted": {
    "base_price": "15.000,00 €",
    "total_price": "15.675,00 €"
  }
}
```

### Product Response

```json
{
  "id": 1,
  "name": "Solar Module Premium 400W",
  "category": "solar_modules",
  "manufacturer": "SolarTech",
  "price": 250.0,
  "specifications": {
    "power": 400,
    "efficiency": 21.5,
    "dimensions": {
      "width": 1000,
      "height": 2000,
      "depth": 40
    },
    "weight": 22.5,
    "warranty_years": 25
  },
  "image_url": "https://example.com/images/module.jpg",
  "in_stock": true,
  "stock_quantity": 150,
  "formatted": {
    "price": "250,00 €",
    "efficiency": "21,50 %"
  },
  "dynamic_key": "product_1_20240118120000",
  "pdf_base64": "JVBERi0xLjQKJeLjz9MKMy..."
}
```

### Paginated Response

```json
{
  "items": [
    { "id": 1, "name": "Product 1" },
    { "id": 2, "name": "Product 2" }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "message": "Error description",
    "details": {},
    "path": "/api/v1/endpoint"
  }
}
```

### Common Error Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Field validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Validation Error Example

```json
{
  "error": {
    "message": "Validation error",
    "details": [
      {
        "loc": ["body", "roof_area"],
        "msg": "ensure this value is greater than 0",
        "type": "value_error.number.not_gt"
      }
    ],
    "path": "/api/v1/solar/calculate"
  }
}
```

## Rate Limiting

Rate limits are applied per IP address:

| Endpoint Category | Limit |
|-------------------|-------|
| Authentication | 5 requests/minute |
| Calculations | 10 requests/minute |
| General API | 60 requests/minute |

When rate limit is exceeded:

```json
{
  "error": {
    "message": "Rate limit exceeded",
    "details": {
      "retry_after": 60
    },
    "path": "/api/v1/solar/calculate"
  }
}
```

## Examples

### Example 1: Complete Solar Calculation Flow

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Calculate Solar System
curl -X POST "http://localhost:8000/api/v1/solar/calculate" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "roof_area": 50.0,
    "roof_type": "flat",
    "roof_angle": 30.0,
    "orientation": "south",
    "module_type": "standard",
    "annual_consumption": 4000.0,
    "location": "Berlin"
  }'

# 3. Create Project
curl -X POST "http://localhost:8000/api/v1/solar/projects" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Müller Residence",
    "customer_name": "Hans Müller",
    "customer_email": "hans@example.com",
    "project_type": "solar",
    "data": {
      "calculation_result": {...}
    }
  }'

# 4. Generate PDF
curl -X POST "http://localhost:8000/api/v1/pdf/generate" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "template": "standard",
    "options": {
      "include_charts": true,
      "include_3d": true
    }
  }'
```

### Example 2: Price Matrix Calculation

```bash
# 1. Get current price matrix
curl -X GET "http://localhost:8000/api/v1/pricing/matrix" \
  -H "Authorization: Bearer eyJ..."

# 2. Calculate price
curl -X POST "http://localhost:8000/api/v1/pricing/calculate" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "module_count": 30,
    "battery_model": "Tesla Powerwall 2",
    "extras": ["monitoring", "insurance"]
  }'
```

### Example 3: Product Search

```bash
# Search for solar modules
curl -X GET "http://localhost:8000/api/v1/products/search?q=solar&category=modules&min_power=400" \
  -H "Authorization: Bearer eyJ..."
```

### Example 4: CRM Customer Management

```bash
# Create customer
curl -X POST "http://localhost:8000/api/v1/crm/customers" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Schmidt",
    "email": "maria@example.com",
    "phone": "+49 123 456789",
    "address": {
      "street": "Hauptstraße 123",
      "city": "Berlin",
      "postal_code": "10115",
      "country": "Germany"
    }
  }'

# Create offer for customer
curl -X POST "http://localhost:8000/api/v1/crm/offers" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "project_id": 1,
    "amount": 15675.0,
    "valid_until": "2024-02-28",
    "status": "draft"
  }'
```

## Postman Collection

A Postman collection is available for easy API testing. Import the collection from:

`backend/docs/postman_collection.json`

The collection includes:
- Pre-configured authentication
- All API endpoints with examples
- Environment variables for easy switching between dev/prod
- Test scripts for common scenarios

### Using the Postman Collection

1. Import the collection into Postman
2. Set up environment variables:
   - `base_url`: `http://localhost:8000`
   - `username`: Your username
   - `password`: Your password
3. Run the "Login" request to get a token
4. The token will be automatically saved and used for subsequent requests

## Additional Resources

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json
- **Health Check**: http://localhost:8000/health

## Support

For API support or questions:
- Email: support@solarcalculatorpro.com
- Documentation: https://docs.solarcalculatorpro.com
- GitHub Issues: https://github.com/solarcalculatorpro/api/issues
