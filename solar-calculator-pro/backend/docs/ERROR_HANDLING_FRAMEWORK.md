# Error Handling Framework

Comprehensive error handling system for the Solar Calculator Pro backend.

## Overview

The error handling framework provides:

- **Custom Exception Classes**: Hierarchical exception classes for different error types
- **Error Codes System**: Standardized error codes for consistent error identification
- **Error Message Templates**: Pre-defined messages in German for user-friendly responses
- **Error Logging**: Automatic logging with appropriate severity levels
- **User-Friendly Responses**: Separate developer and user-facing messages

## Requirements

- **4.3**: Consistent error handling and HTTP status codes
- **4.4**: Request validation with Pydantic models
- **11.3**: Secure data handling and error responses

## Error Codes

Error codes follow the format `ERR_XXXX` where XXXX is a numeric code:

### Categories

- **1000-1999**: General errors
- **2000-2999**: Validation errors
- **3000-3999**: Authentication/Authorization errors
- **4000-4999**: Database errors
- **5000-5999**: Business logic errors
- **6000-6999**: File/Resource errors
- **7000-7999**: External service errors
- **8000-8999**: Solar calculator errors
- **9000-9999**: Heat pump errors
- **10000-10999**: Price matrix errors
- **11000-11999**: PDF generation errors

## Exception Classes

### Base Class: AppError

All custom exceptions inherit from `AppError`:

```python
from solar-calculator-pro.backend.core.errors import AppError, ErrorCode

error = AppError(
    error_code=ErrorCode.GENERAL_UNKNOWN,
    message="Developer-facing message",
    user_message="Benutzerfreundliche Nachricht",
    details={"key": "value"},
    status_code=500,
    context={"request_id": "123"}
)
```

### Specific Exception Classes

#### ValidationError
```python
from solar-calculator-pro.backend.core.errors import ValidationError, ErrorCode

raise ValidationError(
    error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
    details={"field": "email"}
)
```

#### AuthenticationError
```python
from solar-calculator-pro.backend.core.errors import AuthenticationError

raise AuthenticationError(
    error_code=ErrorCode.AUTH_INVALID_CREDENTIALS
)
```

#### DatabaseError
```python
from solar-calculator-pro.backend.core.errors import DatabaseError, ErrorCode

raise DatabaseError(
    error_code=ErrorCode.DB_CONNECTION_FAILED,
    details={"database": "main"}
)
```


#### NotFoundError
```python
from solar-calculator-pro.backend.core.errors import NotFoundError

raise NotFoundError(
    details={"resource": "Project", "id": 123}
)
```

#### Domain-Specific Errors

```python
from solar-calculator-pro.backend.core.errors import (
    SolarCalculatorError,
    HeatPumpError,
    PriceMatrixError,
    PDFGenerationError
)

# Solar calculator error
raise SolarCalculatorError(
    error_code=ErrorCode.SOLAR_INVALID_ROOF_AREA,
    details={"min": 10, "max": 1000}
)

# Heat pump error
raise HeatPumpError(
    error_code=ErrorCode.HEATPUMP_CALCULATION_FAILED
)

# Price matrix error
raise PriceMatrixError(
    error_code=ErrorCode.PRICE_MATRIX_NOT_FOUND
)

# PDF generation error
raise PDFGenerationError(
    error_code=ErrorCode.PDF_GENERATION_FAILED
)
```

## Error Handler Utilities

### ErrorHandler Class

The `ErrorHandler` class provides utility methods for error handling:

#### Handle Any Exception

```python
from solar-calculator-pro.backend.core.errors import ErrorHandler

try:
    # Some operation
    result = risky_operation()
except Exception as e:
    # Convert to AppError
    app_error = ErrorHandler.handle_exception(e)
    raise app_error
```

#### Create Validation Error

```python
error = ErrorHandler.create_validation_error(
    field="email",
    value="invalid-email",
    constraint="Must be valid email format",
    expected_format="user@example.com"
)
```

#### Create Not Found Error

```python
error = ErrorHandler.create_not_found_error(
    resource_type="Project",
    resource_id=123
)
```

#### Log Error with Context

```python
ErrorHandler.log_error_with_context(
    error=app_error,
    request_id="req-123",
    user_id="user-456",
    additional_context={"operation": "solar_calculation"}
)
```

## Decorator for Error Handling

Use the `@handle_errors` decorator to automatically handle errors in functions:

```python
from solar-calculator-pro.backend.core.errors import handle_errors, ErrorCode

@handle_errors(ErrorCode.SOLAR_CALCULATION_FAILED)
def calculate_solar_system(data):
    # Function implementation
    # Any exception will be converted to AppError with SOLAR_CALCULATION_FAILED code
    return result
```

## Context Manager for Error Handling

Use `ErrorContext` for automatic error logging with context:

```python
from solar-calculator-pro.backend.core.errors import ErrorContext

with ErrorContext("solar_calculation", user_id="123", request_id="req-456"):
    result = calculate_solar_system(data)
    # Automatically logs start, completion, and any errors
```

## Error Response Format

Errors are automatically converted to JSON responses:

```json
{
  "error": {
    "code": "ERR_8000",
    "message": "Ungültige Dachfläche. Bitte geben Sie einen Wert zwischen 10 und 1000 m² ein.",
    "details": {
      "field": "roof_area",
      "min": 10,
      "max": 1000
    },
    "severity": "low",
    "category": "validation",
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

## Error Severity Levels

- **LOW**: Minor issues, user can continue
- **MEDIUM**: Significant issues, operation failed
- **HIGH**: Serious issues, may affect system
- **CRITICAL**: Critical issues, requires immediate attention

## Error Categories

- **validation**: Input validation errors
- **authentication**: Authentication errors
- **authorization**: Authorization errors
- **database**: Database operation errors
- **business_logic**: Business rule violations
- **external_service**: External API errors
- **file_system**: File operation errors
- **network**: Network-related errors
- **configuration**: Configuration errors
- **system**: System-level errors

## Logging

Errors are automatically logged with appropriate levels:

- **CRITICAL** severity → `logger.critical()`
- **HIGH** severity → `logger.error()`
- **MEDIUM** severity → `logger.warning()`
- **LOW** severity → `logger.info()`

Log entries include:
- Error code
- Developer message
- User message
- Severity and category
- Details and context
- Timestamp
- Stack trace (for high/critical errors)

## Best Practices

### 1. Use Specific Error Classes

```python
# Good
raise ValidationError(
    error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
    details={"field": "email"}
)

# Avoid
raise Exception("Email is required")
```

### 2. Provide Detailed Context

```python
# Good
raise SolarCalculatorError(
    error_code=ErrorCode.SOLAR_CALCULATION_FAILED,
    details={
        "roof_area": 50,
        "module_type": "premium",
        "reason": "Insufficient space for modules"
    }
)

# Avoid
raise SolarCalculatorError()
```

### 3. Use Error Handler for Unknown Exceptions

```python
# Good
try:
    result = external_api_call()
except Exception as e:
    app_error = ErrorHandler.handle_exception(e)
    raise app_error

# Avoid
try:
    result = external_api_call()
except Exception:
    pass  # Silent failure
```

### 4. Use Context Manager for Operations

```python
# Good
with ErrorContext("pdf_generation", user_id=user.id):
    pdf = generate_pdf(data)

# Provides automatic logging and context
```

### 5. Add Custom Error Codes for New Features

When adding new features, define appropriate error codes:

```python
class ErrorCode(str, Enum):
    # ... existing codes ...
    
    # New feature errors (12000-12999)
    NEW_FEATURE_ERROR = "ERR_12000"
    NEW_FEATURE_VALIDATION = "ERR_12001"
```

## Integration with FastAPI

The error handling framework integrates with FastAPI middleware:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from solar-calculator-pro.backend.core.errors import AppError

app = FastAPI()

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )
```

## Testing

Test your error handling:

```python
import pytest
from solar-calculator-pro.backend.core.errors import ValidationError, ErrorCode

def test_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError(
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
            details={"field": "email"}
        )
    
    error = exc_info.value
    assert error.status_code == 422
    assert "email" in error.user_message
```

## Examples

### Example 1: Service Method with Error Handling

```python
from solar-calculator-pro.backend.core.errors import (
    SolarCalculatorError,
    ErrorCode,
    ErrorContext
)

class SolarService:
    def calculate_system(self, data: dict):
        with ErrorContext("solar_calculation", user_id=data.get("user_id")):
            # Validate input
            if data["roof_area"] < 10:
                raise SolarCalculatorError(
                    error_code=ErrorCode.SOLAR_INVALID_ROOF_AREA,
                    details={"min": 10, "max": 1000}
                )
            
            # Perform calculation
            result = self._perform_calculation(data)
            return result
```

### Example 2: API Endpoint with Error Handling

```python
from fastapi import APIRouter, HTTPException
from solar-calculator-pro.backend.core.errors import (
    AppError,
    ErrorHandler,
    ErrorCode
)

router = APIRouter()

@router.post("/calculate")
async def calculate_solar(data: dict):
    try:
        service = SolarService()
        result = service.calculate_system(data)
        return {"success": True, "data": result}
    except AppError as e:
        # AppError is automatically handled by FastAPI middleware
        raise
    except Exception as e:
        # Convert unknown exceptions to AppError
        app_error = ErrorHandler.handle_exception(e)
        raise app_error
```

### Example 3: Database Operation with Error Handling

```python
from sqlalchemy.exc import IntegrityError
from solar-calculator-pro.backend.core.errors import DatabaseError, ErrorCode

def create_project(db, project_data):
    try:
        project = Project(**project_data)
        db.add(project)
        db.commit()
        return project
    except IntegrityError:
        db.rollback()
        raise DatabaseError(
            error_code=ErrorCode.DB_DUPLICATE_RECORD,
            details={"resource": "Project", "field": "name"}
        )
    except Exception as e:
        db.rollback()
        raise DatabaseError(
            error_code=ErrorCode.DB_QUERY_FAILED,
            details={"operation": "create_project", "error": str(e)}
        )
```

## Summary

The error handling framework provides:

✅ Standardized error codes  
✅ Hierarchical exception classes  
✅ German user-friendly messages  
✅ Automatic logging with severity levels  
✅ Detailed error context and tracing  
✅ Easy integration with FastAPI  
✅ Comprehensive testing support  

For more information, see the source code at `solar-calculator-pro/backend/core/errors.py`.
