# Error Handling Quick Reference

## Common Exceptions

```python
from backend.core.exceptions import *

# Authentication (401)
raise InvalidCredentialsError()
raise TokenExpiredError()
raise InvalidTokenError()

# Authorization (403)
raise AuthorizationError(required_permission="admin")

# Not Found (404)
raise ResourceNotFoundError("Project", project_id)

# Conflict (409)
raise ResourceAlreadyExistsError("User", email)

# Validation (422)
raise InvalidInputError("field", "message", value)
raise MissingRequiredFieldError("field")
raise InvalidFormatError("field", "expected_format", value)

# Business Logic (400)
raise CalculationError("solar", "reason")
raise InvalidStateError("current", "required")

# Database (500)
raise DatabaseError("message")
raise DatabaseIntegrityError("constraint")

# Files (400)
raise InvalidFileTypeError("file.txt", [".pdf"])
raise FileSizeExceededError("file.pdf", 10MB, 5MB)

# Rate Limiting (429)
raise RateLimitExceededError(100, 60, 30)

# Pricing (400)
raise MatrixLookupError(50, "Tesla Powerwall")
```

## Validation

```python
from backend.core.validation import Validator

# Required field
Validator.validate_required(value, "field")

# Email
Validator.validate_email(email, "email")

# Password
Validator.validate_password(password, "password")

# Range
Validator.validate_range(age, "age", min_val=0, max_val=120)

# Length
Validator.validate_length(text, "field", min_length=3, max_length=20)

# Enum
Validator.validate_enum(status, "status", ["active", "inactive"])

# Positive
Validator.validate_positive(quantity, "quantity")

# German number
price = Validator.validate_german_number_format("1.234,56", "price")

# File
Validator.validate_file_extension(filename, [".pdf"], "file")
Validator.validate_file_size(size, max_size, "file")
```

## Pydantic Models

```python
from backend.core.validation import *

# Pagination
pagination = PaginationParams(page=2, page_size=50)
offset = pagination.offset
limit = pagination.limit

# Sorting
sort = SortParams(sort_by="name", sort_order="desc")

# Date range
dates = DateRangeParams(start_date=start, end_date=end)

# Search
search = SearchParams(query="text", fields=["name"])
```

## Error Logging

```python
from backend.core.error_logging import get_error_logger

logger = get_error_logger()

# General error
logger.log_error(error, context={}, user_id=1, request_path="/api")

# Validation error
logger.log_validation_error("field", "message", value, "/api")

# Security event
logger.log_security_event("type", "message", user_id=1, ip="1.2.3.4")

# API access
logger.log_access("POST", "/api", 200, 45.2, user_id=1)

# Database error
logger.log_database_error("insert", "users", error, "query")

# External service
logger.log_external_service_error("API", "/endpoint", error)

# Performance
logger.log_performance_issue("operation", 5000, 1000)
```

## Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "timestamp": "2024-01-15T10:30:00Z",
    "details": {},
    "path": "/api/v1/endpoint",
    "hint": "Helpful suggestion"
  }
}
```

## Status Codes

- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **409**: Conflict
- **422**: Validation Error
- **429**: Rate Limit
- **500**: Server Error
- **502**: Bad Gateway
- **503**: Service Unavailable

## Setup

```python
from fastapi import FastAPI
from backend.middleware.error_handler import setup_error_handlers

app = FastAPI()
setup_error_handlers(app)
```

## Testing

```bash
pytest backend/tests/test_error_handling.py -v
```
