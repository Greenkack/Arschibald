"""
FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import API routers
from api.v1 import system_settings, database

# Load environment variables
load_dotenv()

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title=os.getenv("APP_NAME", "Solar Calculator Pro"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="""
# Solar Calculator Pro API

Backend API for Solar Calculator Pro Desktop Application.

## Features

* **Authentication**: JWT-based authentication with token refresh
* **User Management**: Complete user CRUD operations with role-based access
* **System Settings**: Configurable system-wide settings
* **Database Management**: Backup, restore, and optimization tools
* **Rate Limiting**: Built-in rate limiting for API protection
* **Error Handling**: Consistent error responses with detailed codes

## Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Authentication | 5 requests/minute |
| Read Operations | 100 requests/minute |
| Write Operations | 50 requests/minute |

## Error Codes

All errors follow a consistent format with specific error codes. See the [Error Codes](#error-codes) section for details.

## Additional Documentation

* [Complete API Documentation](./docs/API_DOCUMENTATION.md)
* [Authentication Guide](./docs/AUTHENTICATION_GUIDE.md)
* [Quick Reference](./docs/API_QUICK_REFERENCE.md)
* [Postman Collection](./docs/postman_collection.json)
    """,  # noqa
    contact={
        "name": "API Support",
        "email": "api-support@example.com",
        "url": "https://github.com/example/solar-calculator-pro"  # noqa
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Authentication and authorization operations"  # noqa
        },
        {
            "name": "users",
            "description": "User management operations"
        },
        {
            "name": "system-settings",
            "description": "System configuration and settings"
        },
        {
            "name": "database",
            "description": "Database backup, restore, and management"
        },
        {
            "name": "health",
            "description": "Health check and monitoring"
        }
    ]
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(system_settings.router, prefix="/api/v1")
app.include_router(database.router, prefix="/api/v1")


@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Check the health status of the API",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "app": "Solar Calculator Pro",
                        "version": "1.0.0",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Health check endpoint to verify API availability.

    Returns:
        dict: Health status information including app name, version,
              and timestamp
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "app": os.getenv("APP_NAME", "Solar Calculator Pro"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get(
    "/",
    tags=["health"],
    summary="API Root",
    description="Get basic API information and documentation links",
    responses={
        200: {
            "description": "API information",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Solar Calculator Pro API",
                        "version": "1.0.0",
                        "docs": "/docs",
                        "redoc": "/redoc",
                        "openapi": "/openapi.json"
                    }
                }
            }
        }
    }
)
async def root():
    """
    Root endpoint providing API information and documentation links.

    Returns:
        dict: API metadata and documentation URLs
    """
    return {
        "message": "Solar Calculator Pro API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "documentation": {
            "api_docs": "/docs/API_DOCUMENTATION.md",
            "auth_guide": "/docs/AUTHENTICATION_GUIDE.md",
            "quick_reference": "/docs/API_QUICK_REFERENCE.md",
            "postman_collection": "/docs/postman_collection.json"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True") == "True",
    )
