# Error Handling Quick Reference

## Import

```python
from solar-calculator-pro.backend.core.errors import (
    AppError,
    ErrorCode,
    ValidationError,
    AuthenticationError,
    DatabaseError,
    NotFoundError,
    SolarCalculatorError,
    ErrorHandler,
    handle_errors,
    ErrorContext,
)
```

## Raise Errors

### Validation Error
```python
raise ValidationError(
    error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
    details={"field": "email"}
)
```

### Authentication Error
```python
raise AuthenticationError(
    error_code=ErrorCode.AUTH_INVALID_CREDENTIALS
)
```

### Database Error
```python
raise DatabaseError(
    error_code=ErrorCode.DB_RECORD_NOT_FOUND,
    details={"resource": "Project", "id": 123}
)
```

### Solar Calculator Error
```python
raise SolarCalculatorError(
    error_code=ErrorCode.SOLAR_CALCULATION_FAILED,
    details={"roof_area": 50, "reason": "Insufficient space"}
)
```

## Error Handler Utilities

### Convert Exception to AppError
```python
try:
    risky_operation()
except Exception as e:
    app_error = ErrorHandler.handle_exception(e)
    raise app_error
```

### Create Validation Error
```python
error = ErrorHandler.create_validation_error(
    field="email",
    value="invalid",
    constraint="Must be valid email"
)
```

### Create Not Found Error
```python
error = ErrorHandler.create_not_found_error(
    resource_type="Project",
    resource_id=123
)
```

## Decorator

```python
@handle_errors(ErrorCode.SOLAR_CALCULATION_FAILED)
def calculate_solar_system(data):
    # Any exception becomes AppError with specified code
    return result
```

## Context Manager

```python
with ErrorContext("operation_name", user_id="123"):
    # Automatic logging and error context
    result = perform_operation()
```

## Common Error Codes

| Code | Description |
|------|-------------|
| `ERR_2000` | Required field missing |
| `ERR_2001` | Invalid format |
| `ERR_2002` | Out of range |
| `ERR_3000` | Invalid credentials |
| `ERR_3001` | Token expired |
| `ERR_4002` | Record not found |
| `ERR_4003` | Duplicate record |
| `ERR_5001` | Calculation failed |
| `ERR_6000` | File not found |
| `ERR_8000` | Invalid roof area |
| `ERR_8002` | Solar calculation failed |
| `ERR_10000` | Price matrix not found |
| `ERR_11000` | PDF generation failed |

## Error Response Format

```json
{
  "error": {
    "code": "ERR_8000",
    "message": "Ungültige Dachfläche...",
    "details": {"field": "roof_area", "min": 10, "max": 1000},
    "severity": "low",
    "category": "validation",
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

## Best Practices

1. ✅ Use specific error classes
2. ✅ Provide detailed context in `details`
3. ✅ Use `ErrorHandler` for unknown exceptions
4. ✅ Use `ErrorContext` for operations
5. ✅ Test error handling in unit tests
