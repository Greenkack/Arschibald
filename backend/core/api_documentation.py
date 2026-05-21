"""
API Documentation Configuration

This module configures comprehensive OpenAPI/Swagger documentation
for the Solar Calculator Pro API.
"""

from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Generate custom OpenAPI schema with enhanced documentation
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Solar Calculator Pro API",
        version="1.0.0",
        description="""
# Solar Calculator Pro API

A comprehensive REST API for solar energy system calculations, heat pump analysis, 
price matrix management, PDF generation, CRM, and product management.

## Features

- **Solar Calculator**: Calculate solar system size, production, savings, and ROI
- **Heat Pump Calculator**: Analyze heat pump efficiency and cost savings
- **Price Matrix**: Dynamic pricing with Excel-like INDEX/MATCH formulas
- **PDF Generation**: Create professional PDF reports with charts and branding
- **3D Visualization**: Generate and export 3D models of solar installations
- **CRM**: Manage customers, offers, tasks, and communication
- **Product Management**: Comprehensive product catalog with pricing
- **Authentication**: Secure JWT-based authentication

## Authentication

Most endpoints require authentication using JWT tokens. To authenticate:

1. Call `POST /api/v1/auth/login` with username and password
2. Receive an access token in the response
3. Include the token in subsequent requests: `Authorization: Bearer <token>`

Example:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{"username": "admin", "password": "password"}'
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- Calculation endpoints: 10 requests per minute
- General endpoints: 60 requests per minute

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

Common HTTP status codes:
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Data Formats

### Numbers
All numeric values use German formatting in responses:
- Decimal separator: comma ()
- Thousand separator: dot (.)
- Example: `1.234,56` represents 1234.56

### Dates
All dates are in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS.sssZ`

### Currency
Currency values include the currency code:
```json
{
  "amount": 1234.56,
  "formatted": "1.234,56 €",
  "currency": "EUR"
}
```

## Pagination

List endpoints support pagination:
```
GET /api/v1/products?page=1&page_size=20
```

Response includes pagination metadata:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

## Filtering and Sorting

List endpoints support filtering and sorting:
```
GET /api/v1/products?category=solar&sort=price&order=asc
```

## Webhooks

Configure webhooks to receive real-time notifications:
- Calculation completed
- PDF generated
- Order status changed
- Customer created/updated

## Support

For API support, contact: support@solarcalculatorpro.com
        """,
        routes=app.routes,
        tags=[
            {
                "name": "Authentication",
                "description": "User authentication and session management"
            },
            {
                "name": "Solar Calculator",
                "description": "Solar energy system calculations and project management"
            },
            {
                "name": "Heat Pump",
                "description": "Heat pump sizing and efficiency calculations"
            },
            {
                "name": "Price Matrix",
                "description": "Dynamic pricing with Excel-like formulas"
            },
            {
                "name": "PDF Generation",
                "description": "Generate professional PDF reports"
            },
            {
                "name": "3D Visualization",
                "description": "3D model generation and export"
            },
            {
                "name": "Product Management",
                "description": "Product catalog and inventory management"
            },
            {
                "name": "CRM",
                "description": "Customer relationship management"
            },
            {
                "name": "Data Management",
                "description": "Universal data access with dynamic keys and PDF bytes"
            },
            {
                "name": "Admin",
                "description": "Administrative functions and system management"
            }
        ]
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer <token>"
        }
    }

    # Add common response schemas
    openapi_schema["components"]["schemas"]["Error"] = {
        "type": "object",
        "properties": {
            "error": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "details": {"type": "object"},
                    "path": {"type": "string"}
                }
            }
        }
    }

    openapi_schema["components"]["schemas"]["PaginatedResponse"] = {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {}},
            "total": {"type": "integer"},
            "page": {"type": "integer"},
            "page_size": {"type": "integer"},
            "pages": {"type": "integer"}
        }
    }

    # Add example responses
    openapi_schema["components"]["examples"] = {
        "ValidationError": {
            "value": {
                "error": {
                    "message": "Validation error",
                    "details": {
                        "field": "roof_area",
                        "error": "must be greater than 0"
                    },
                    "path": "/api/v1/solar/calculate"
                }
            }
        },
        "UnauthorizedError": {
            "value": {
                "error": {
                    "message": "Not authenticated",
                    "details": {},
                    "path": "/api/v1/solar/projects"
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def add_endpoint_examples(app: FastAPI):
    """
    Add comprehensive examples to all endpoints
    """
    # This will be called after all routes are registered
    pass


# Common response examples
COMMON_RESPONSES = {
    "400": {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Invalid request data",
                        "details": {"field": "value is required"},
                        "path": "/api/v1/endpoint"
                    }
                }
            }
        }
    },
    "401": {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Not authenticated",
                        "details": {},
                        "path": "/api/v1/endpoint"
                    }
                }
            }
        }
    },
    "403": {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Insufficient permissions",
                        "details": {},
                        "path": "/api/v1/endpoint"
                    }
                }
            }
        }
    },
    "404": {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Resource not found",
                        "details": {"id": 123},
                        "path": "/api/v1/endpoint/123"
                    }
                }
            }
        }
    },
    "422": {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Validation error",
                        "details": [
                            {
                                "loc": ["body", "field"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ],
                        "path": "/api/v1/endpoint"
                    }
                }
            }
        }
    },
    "429": {
        "description": "Too Many Requests",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Rate limit exceeded",
                        "details": {"retry_after": 60},
                        "path": "/api/v1/endpoint"
                    }
                }
            }
        }
    },
    "500": {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Internal server error",
                        "details": {},
                        "path": "/api/v1/endpoint"
                    }
                }
            }
        }
    }
}


def get_common_responses(include_auth: bool = True) -> Dict[str, Any]:
    """
    Get common response definitions for endpoints
    
    Args:
        include_auth: Whether to include 401/403 responses
    
    Returns:
        Dictionary of response definitions
    """
    responses = {
        "400": COMMON_RESPONSES["400"],
        "422": COMMON_RESPONSES["422"],
        "500": COMMON_RESPONSES["500"]
    }
    
    if include_auth:
        responses["401"] = COMMON_RESPONSES["401"]
        responses["403"] = COMMON_RESPONSES["403"]
    
    return responses
