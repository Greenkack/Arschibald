# Error Handling and Validation Guide

## Overview

This guide covers the comprehensive error handling and validation system implemented for the FastAPI backend. The system provides:

- **Custom Exception Classes**: Specific exceptions for different error scenarios
- **Request Validation**: Pydantic-based validation with user-friendly error messages
- **Global Error Handlers**: Centralized error handling middleware
- **Error Logging**: Comprehensive logging with rotation and monitoring
- **User-Friendly Responses**: Consistent, helpful error responses

## Table of Contents

1. [Custom Exceptions](#custom-exceptions)
2. [Validation System](#validation-system)
3. [Error Handlers](#error-handlers)
4. [Error Logging](#error-logging)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

## Custom Exceptions

### Base Exception

All custom exceptions inherit from `BaseAPIException`:

```python
from backend.core.exceptions import BaseAPIException

class MyCustomError(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code="MY_CUSTOM_ERROR"
        )
```

### Authentication & Authorization

```python
from backend.core.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    TokenExpiredError,
    InvalidTokenError,
    AuthorizationError
)

# Usage examples
raise InvalidCredentialsError()  # 401
raise TokenExpiredError()  # 401
raise AuthorizationError(required_permission="admin")  # 403
```

### Resource Exceptions

```python
from backend.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    ResourceConflictError
)

# Usage examples
raise ResourceNotFoundError("Project", project_id)  # 404
raise ResourceAlreadyExistsError("User", email)  # 409
```

### Validation Exceptions

```python
from backend.core.exceptions import (
    ValidationError,
    InvalidInputError,
    MissingRequiredFieldError,
    InvalidFormatError
)

# Usage examples
raise InvalidInputError("age", "Must be positive", value=-5)  # 422
raise MissingRequiredFieldError("username")  # 422
raise InvalidFormatError("email", "valid email address", "invalid")  # 422
```

### Business Logic Exceptions

```python
from backend.core.exceptions import (
    BusinessLogicError,
    CalculationError,
    InvalidStateError
)

# Usage examples
raise CalculationError("solar", "Invalid roof area")  # 400
raise InvalidStateError(current_state="draft", required_state="active")  # 400
```

### Database Exceptions

```python
from backend.core.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseIntegrityError
)

# Usage examples
raise DatabaseConnectionError()  # 500
raise DatabaseIntegrityError("unique_email")  # 500
```

### File Exceptions

```python
from backend.core.exceptions import (
    FileError,
    InvalidFileTypeError,
    FileSizeExceededError
)

# Usage examples
raise InvalidFileTypeError("doc.txt", [".pdf", ".docx"])  # 400
raise FileSizeExceededError("large.pdf", 10_000_000, 5_000_000)  # 400
```

### Rate Limiting

```python
from backend.core.exceptions import RateLimitExceededError

# Usage example
raise RateLimitExceededError(limit=100, window=60, retry_after=30)  # 429
```

### Pricing Exceptions

```python
from backend.core.exceptions import (
    PricingError,
    MatrixLookupError
)

# Usage examples
raise MatrixLookupError(module_count=50, battery_model="Tesla")  # 400
```

## Validation System

### Validation Rules

```python
from backend.core.validation import ValidationRules

# Email validation
if not ValidationRules.validate_email(email):
    raise InvalidFormatError("email", "valid email address", email)

# Phone validation
if not ValidationRules.validate_phone(phone):
    raise InvalidFormatError("phone", "international format", phone)

# Password strength
if not ValidationRules.validate_password_strength(password):
    raise InvalidInputError("password", "Must meet strength requirements")

# Range validation
if not ValidationRules.validate_range(age, min_val=0, max_val=120):
    raise InvalidInputError("age", "Must be between 0 and 120", age)

# Length validation
if not ValidationRules.validate_length(username, min_length=3, max_length=20):
    raise InvalidInputError("username", "Must be 3-20 characters")

# Enum validation
if not ValidationRules.validate_enum(status, ["active", "inactive"]):
    raise InvalidInputError("status", "Must be active or inactive")
```

### Validator Helper Class

```python
from backend.core.validation import Validator

# Validate required field
Validator.validate_required(value, "field_name")

# Validate email
Validator.validate_email(email, "email")

# Validate password
Validator.validate_password(password, "password")

# Validate range
Validator.validate_range(age, "age", min_val=0, max_val=120)

# Validate length
Validator.validate_length(username, "username", min_length=3, max_length=20)

# Validate enum
Validator.validate_enum(status, "status", ["active", "inactive"])

# Validate positive number
Validator.validate_positive(quantity, "quantity")

# Validate German number format
price = Validator.validate_german_number_format("1.234,56", "price")
# Returns: 1234.56

# Validate file extension
Validator.validate_file_extension(filename, [".pdf", ".docx"], "file")

# Validate file size
Validator.validate_file_size(size_bytes, max_size_bytes, "file")
```

### Pydantic Models

```python
from backend.core.validation import (
    ValidatedBaseModel,
    PaginationParams,
    SortParams,
    DateRangeParams,
    SearchParams
)

# Pagination
pagination = PaginationParams(page=2, page_size=50)
offset = pagination.offset  # 50
limit = pagination.limit  # 50

# Sorting
sort = SortParams(sort_by="name", sort_order="desc")

# Date range
date_range = DateRangeParams(start_date=start, end_date=end)

# Search
search = SearchParams(query="solar", fields=["name", "description"])
```

### Custom Pydantic Models

```python
from pydantic import Field, validator
from backend.core.validation import ValidatedBaseModel

class UserCreateRequest(ValidatedBaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=0, le=120)
    
    @validator('email')
    def validate_email(cls, v):
        from backend.core.validation import Validator
        Validator.validate_email(v, "email")
        return v
    
    @validator('password')
    def validate_password(cls, v):
        from backend.core.validation import Validator
        Validator.validate_password(v, "password")
        return v
```

## Error Handlers

### Setup

Error handlers are automatically configured in `main.py`:

```python
from fastapi import FastAPI
from backend.middleware.error_handler import setup_error_handlers

app = FastAPI()
setup_error_handlers(app)
```

### Error Response Format

All errors return a consistent JSON format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "details": {
      "field": "email",
      "value": "invalid"
    },
    "path": "/api/v1/users",
    "hint": "Helpful suggestion for fixing the error"
  }
}
```

### Status Codes

- **400**: Bad Request (validation, business logic errors)
- **401**: Unauthorized (authentication failures)
- **403**: Forbidden (authorization failures)
- **404**: Not Found (resource not found)
- **409**: Conflict (resource already exists, state conflicts)
- **422**: Unprocessable Entity (validation errors)
- **429**: Too Many Requests (rate limiting)
- **500**: Internal Server Error (unexpected errors)
- **502**: Bad Gateway (external service errors)
- **503**: Service Unavailable (temporary unavailability)

## Error Logging

### Error Logger

```python
from backend.core.error_logging import get_error_logger

error_logger = get_error_logger()

# Log general error
error_logger.log_error(
    error=exception,
    context={"operation": "calculation"},
    user_id=user_id,
    request_path="/api/v1/calculate"
)

# Log validation error
error_logger.log_validation_error(
    field="email",
    message="Invalid format",
    value="invalid-email",
    request_path="/api/v1/users"
)

# Log security event
error_logger.log_security_event(
    event_type="failed_login",
    message="Multiple failed login attempts",
    user_id=user_id,
    ip_address="192.168.1.1",
    details={"attempts": 5}
)

# Log API access
error_logger.log_access(
    method="POST",
    path="/api/v1/projects",
    status_code=201,
    duration_ms=45.2,
    user_id=user_id,
    ip_address="192.168.1.1"
)

# Log database error
error_logger.log_database_error(
    operation="insert",
    table="users",
    error=exception,
    query="INSERT INTO users..."
)

# Log external service error
error_logger.log_external_service_error(
    service_name="WeatherAPI",
    endpoint="/forecast",
    error=exception,
    request_data={"location": "Berlin"},
    response_data={"error": "timeout"}
)

# Log performance issue
error_logger.log_performance_issue(
    operation="calculate_solar",
    duration_ms=5000,
    threshold_ms=1000,
    details={"module_count": 100}
)
```

### Log Files

Logs are stored in `backend/logs/`:

- `app.log`: General application logs
- `errors.log`: Error logs only
- `access.log`: API access logs
- `security.log`: Security-related events

Logs are automatically rotated when they reach 10MB, keeping 5 backup files.

## Best Practices

### 1. Use Specific Exceptions

```python
# Good
raise ResourceNotFoundError("Project", project_id)

# Avoid
raise Exception("Project not found")
```

### 2. Provide Context

```python
# Good
raise CalculationError(
    "solar",
    "Roof area must be positive",
)

# Avoid
raise Exception("Invalid input")
```

### 3. Validate Early

```python
# Good
def create_user(data: UserCreateRequest):
    # Validation happens automatically via Pydantic
    Validator.validate_email(data.email, "email")
    # ... rest of logic

# Avoid
def create_user(data: dict):
    # No validation until later
    user = User(**data)  # Might fail here
```

### 4. Log Appropriately

```python
# Good
try:
    result = expensive_calculation()
except Exception as e:
    error_logger.log_error(e, context={"operation": "calculation"})
    raise CalculationError("solar", str(e))

# Avoid
try:
    result = expensive_calculation()
except Exception:
    pass  # Silent failure
```

### 5. Return User-Friendly Messages

```python
# Good
raise InvalidInputError(
    "roof_area",
    "Roof area must be between 10 and 1000 square meters",
    value=roof_area
)

# Avoid
raise Exception(f"Invalid value: {roof_area}")
```

## Examples

### Example 1: API Endpoint with Validation

```python
from fastapi import APIRouter, Depends
from backend.core.validation import Validator
from backend.core.exceptions import ResourceNotFoundError, InvalidInputError

router = APIRouter()

@router.post("/projects")
async def create_project(data: ProjectCreateRequest):
    # Validation happens automatically via Pydantic
    
    # Additional business logic validation
    if data.roof_area <= 0:
        raise InvalidInputError(
            "roof_area",
            "Roof area must be positive",
            value=data.roof_area
        )
    
    # Check if project already exists
    existing = db.query(Project).filter_by(name=data.name).first()
    if existing:
        raise ResourceAlreadyExistsError("Project", data.name)
    
    # Create project
    project = Project(**data.dict())
    db.add(project)
    db.commit()
    
    return {"id": project.id, "message": "Project created successfully"}

@router.get("/projects/{project_id}")
async def get_project(project_id: int):
    project = db.query(Project).filter_by(id=project_id).first()
    
    if not project:
        raise ResourceNotFoundError("Project", project_id)
    
    return project
```

### Example 2: Service with Error Handling

```python
from backend.core.exceptions import CalculationError, DatabaseError
from backend.core.error_logging import get_error_logger

error_logger = get_error_logger()

class SolarService:
    def calculate(self, request: SolarCalculationRequest):
        try:
            # Validate inputs
            Validator.validate_positive(request.roof_area, "roof_area")
            Validator.validate_range(
                request.roof_angle,
                "roof_angle",
                min_val=0,
                max_val=90
            )
            
            # Perform calculation
            result = self._perform_calculation(request)
            
            # Log success
            error_logger.log_access(
                method="CALCULATE",
                path="/solar/calculate",
                status_code=200,
                duration_ms=45.2
            )
            
            return result
            
        except InvalidInputError as e:
            # Re-raise validation errors
            raise
            
        except Exception as e:
            # Log unexpected errors
            error_logger.log_error(
                error=e,
                context={"operation": "solar_calculation"},
                request_path="/solar/calculate"
            )
            
            # Raise as calculation error
            raise CalculationError("solar", str(e))
```

### Example 3: File Upload with Validation

```python
from fastapi import UploadFile
from backend.core.exceptions import InvalidFileTypeError, FileSizeExceededError
from backend.core.validation import Validator

@router.post("/upload")
async def upload_file(file: UploadFile):
    # Validate file type
    allowed_types = [".pdf", ".xlsx", ".csv"]
    Validator.validate_file_extension(file.filename, allowed_types, "file")
    
    # Read file
    content = await file.read()
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024
    Validator.validate_file_size(len(content), max_size, "file")
    
    # Process file
    # ...
    
    return {"message": "File uploaded successfully"}
```

## Testing

Run the error handling tests:

```bash
cd backend
pytest tests/test_error_handling.py -v
```

## Summary

The error handling and validation system provides:

✅ **Comprehensive exception classes** for all error scenarios  
✅ **Robust validation** with Pydantic and custom validators  
✅ **Consistent error responses** with helpful hints  
✅ **Detailed logging** with rotation and monitoring  
✅ **User-friendly messages** in German and English  
✅ **Full test coverage** for all components  

This system ensures that all errors are handled gracefully, logged appropriately, and communicated clearly to users.
