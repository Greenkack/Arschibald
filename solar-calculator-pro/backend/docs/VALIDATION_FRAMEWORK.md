# Validation Framework Documentation

## Overview

The Validation Framework provides a comprehensive, extensible system for validating data in the Solar Calculator Pro backend. It supports various data types, custom validation rules, and detailed error reporting.

## Features

- **Base validator classes** for extensibility
- **Number validation** with German format support
- **String validation** with pattern matching
- **Date/time validation** with range checking
- **Email and URL validation**
- **Custom validation rules**
- **Composite validators** for complex validation
- **Dictionary and list validation**
- **Detailed error handling** with error codes

## Requirements

- Requirements: 4.4 (Request Validation), 11.3 (Security - Input Validation)

## Installation

The validation framework is located at:
```
solar-calculator-pro/backend/core/validators.py
```

## Basic Usage

### Number Validation

```python
from core.validators import NumberValidator

# Basic number validation
validator = NumberValidator(field_name="age", min_value=18, max_value=100)
result = validator.validate(25)

if result.is_valid:
    print("Valid!")
else:
    for error in result.errors:
        print(f"Error: {error.message}")
```

### German Number Format

```python
# Validate German number format (1.234,56)
validator = NumberValidator(
    field_name="price",
    german_format=True,
    min_value=0,
    decimal_places=2
)
result = validator.validate("1.234,56")  # Valid: 1234.56
```

### String Validation

```python
from core.validators import StringValidator

# String with pattern
validator = StringValidator(
    field_name="username",
    min_length=3,
    max_length=20,
    pattern=r'^[a-zA-Z0-9_]+$'
)
result = validator.validate("john_doe")
```

### Email Validation

```python
from core.validators import EmailValidator

validator = EmailValidator(field_name="email", required=True)
result = validator.validate("user@example.com")
```

### Date/Time Validation

```python
from core.validators import DateTimeValidator
from datetime import date

validator = DateTimeValidator(
    field_name="birth_date",
    allow_future=False,
    min_date=date(1900, 1, 1)
)
result = validator.validate(date(1990, 5, 15))
```

## Advanced Usage

### Custom Validators

```python
validator = NumberValidator(field_name="even_number")
validator.add_custom_validator(
    lambda x: x % 2 == 0,
    "Number must be even"
)
result = validator.validate(4)  # Valid
result = validator.validate(5)  # Invalid
```

### Composite Validators

```python
from core.validators import CompositeValidator

validators = [
    NumberValidator(field_name="age", min_value=18),
    NumberValidator(field_name="age", max_value=100)
]
composite = CompositeValidator(validators)
result = composite.validate(25)
```

### Dictionary Validation

```python
from core.validators import DictValidator

schema = {
    "name": StringValidator(field_name="name", required=True),
    "age": NumberValidator(field_name="age", min_value=0),
    "email": EmailValidator(field_name="email")
}
validator = DictValidator(schema)

data = {
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com"
}
result = validator.validate(data)
```

### List Validation

```python
from core.validators import ListValidator

item_validator = NumberValidator(field_name="item", min_value=0)
validator = ListValidator(
    item_validator,
    field_name="scores",
    min_items=1,
    max_items=10,
    unique=True
)
result = validator.validate([85, 90, 95])
```

## Convenience Functions

For quick validation without creating validator instances:

```python
from core.validators import (
    validate_number,
    validate_string,
    validate_date,
    validate_email,
    validate_url
)

# Quick number validation
result = validate_number(42, field_name="age", min_value=18)

# Quick email validation
result = validate_email("user@example.com")

# Quick URL validation
result = validate_url("https://example.com", require_https=True)
```

## Error Handling

### ValidationError

```python
error = ValidationError(
    message="Value is too small",
    field="age",
    value=15,
    code="VALUE_TOO_SMALL"
)

# Convert to dictionary
error_dict = error.to_dict()
# {
#     "message": "Value is too small",
#     "field": "age",
#     "value": 15,
#     "code": "VALUE_TOO_SMALL"
# }
```

### ValidationResult

```python
result = validator.validate(value)

if result.is_valid:
    print("Validation passed")
else:
    print(f"Found {len(result.errors)} errors:")
    for error in result.errors:
        print(f"  - {error.field}: {error.message} ({error.code})")

# Convert to dictionary
result_dict = result.to_dict()
# {
#     "is_valid": False,
#     "errors": [...]
# }
```

## Error Codes

### Number Validation
- `REQUIRED_FIELD` - Required field is missing
- `INVALID_NUMBER_FORMAT` - Cannot parse as number
- `NEGATIVE_NOT_ALLOWED` - Negative values not allowed
- `DECIMAL_NOT_ALLOWED` - Decimal values not allowed
- `TOO_MANY_DECIMAL_PLACES` - Too many decimal places
- `VALUE_TOO_SMALL` - Value below minimum
- `VALUE_TOO_LARGE` - Value above maximum

### String Validation
- `REQUIRED_FIELD` - Required field is missing
- `STRING_TOO_SHORT` - String below minimum length
- `STRING_TOO_LONG` - String above maximum length
- `PATTERN_MISMATCH` - String doesn't match pattern
- `INVALID_VALUE` - Value not in allowed values

### Date/Time Validation
- `REQUIRED_FIELD` - Required field is missing
- `INVALID_DATE_FORMAT` - Cannot parse as date
- `FUTURE_DATE_NOT_ALLOWED` - Future dates not allowed
- `PAST_DATE_NOT_ALLOWED` - Past dates not allowed
- `DATE_TOO_EARLY` - Date before minimum
- `DATE_TOO_LATE` - Date after maximum

### Email Validation
- `INVALID_EMAIL` - Invalid email format

### URL Validation
- `HTTPS_REQUIRED` - HTTPS protocol required

### List Validation
- `INVALID_TYPE` - Value is not a list
- `TOO_FEW_ITEMS` - List has too few items
- `TOO_MANY_ITEMS` - List has too many items
- `DUPLICATE_ITEMS` - List contains duplicates

### Custom Validation
- `CUSTOM_VALIDATION_FAILED` - Custom validator returned false
- `CUSTOM_VALIDATOR_ERROR` - Custom validator threw exception

## Validator Classes

### BaseValidator

Abstract base class for all validators.

**Parameters:**
- `field_name` (str, optional): Name of the field being validated
- `required` (bool): Whether the field is required

**Methods:**
- `validate(value)`: Validate the value
- `add_custom_validator(validator_func, error_message)`: Add custom validation

### NumberValidator

Validates numeric values with German format support.

**Parameters:**
- `field_name` (str, optional): Field name
- `required` (bool): Required field
- `min_value` (number, optional): Minimum value
- `max_value` (number, optional): Maximum value
- `allow_negative` (bool): Allow negative values (default: True)
- `allow_decimal` (bool): Allow decimal values (default: True)
- `decimal_places` (int, optional): Maximum decimal places
- `german_format` (bool): Parse German number format (default: False)

### StringValidator

Validates string values.

**Parameters:**
- `field_name` (str, optional): Field name
- `required` (bool): Required field
- `min_length` (int, optional): Minimum length
- `max_length` (int, optional): Maximum length
- `pattern` (str, optional): Regex pattern
- `allowed_values` (list, optional): List of allowed values
- `trim` (bool): Trim whitespace (default: True)
- `lowercase` (bool): Convert to lowercase (default: False)
- `uppercase` (bool): Convert to uppercase (default: False)

### DateTimeValidator

Validates date and time values.

**Parameters:**
- `field_name` (str, optional): Field name
- `required` (bool): Required field
- `min_date` (date/datetime, optional): Minimum date
- `max_date` (date/datetime, optional): Maximum date
- `date_format` (str): Date format string (default: "%Y-%m-%d")
- `allow_future` (bool): Allow future dates (default: True)
- `allow_past` (bool): Allow past dates (default: True)

### EmailValidator

Validates email addresses.

**Parameters:**
- `field_name` (str, optional): Field name
- `required` (bool): Required field

### URLValidator

Validates URLs.

**Parameters:**
- `field_name` (str, optional): Field name
- `required` (bool): Required field
- `require_https` (bool): Require HTTPS protocol (default: False)

### CompositeValidator

Combines multiple validators.

**Parameters:**
- `validators` (list): List of validators to run
- `field_name` (str, optional): Field name
- `stop_on_first_error` (bool): Stop after first error (default: False)

### DictValidator

Validates dictionary structures.

**Parameters:**
- `schema` (dict): Dictionary mapping field names to validators

### ListValidator

Validates list/array values.

**Parameters:**
- `item_validator` (BaseValidator): Validator for list items
- `field_name` (str, optional): Field name
- `required` (bool): Required field
- `min_items` (int, optional): Minimum number of items
- `max_items` (int, optional): Maximum number of items
- `unique` (bool): Require unique items (default: False)

## Integration with FastAPI

### Using with Pydantic Models

```python
from pydantic import BaseModel, field_validator
from core.validators import validate_number, validate_email

class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        result = validate_number(v, field_name="age", min_value=18, max_value=100)
        if not result.is_valid:
            raise ValueError(result.errors[0].message)
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email_field(cls, v):
        result = validate_email(v, field_name="email", required=True)
        if not result.is_valid:
            raise ValueError(result.errors[0].message)
        return v
```

### Custom Validation Endpoint

```python
from fastapi import APIRouter, HTTPException
from core.validators import DictValidator, StringValidator, NumberValidator

router = APIRouter()

@router.post("/validate")
async def validate_data(data: dict):
    schema = {
        "name": StringValidator(field_name="name", required=True, min_length=2),
        "age": NumberValidator(field_name="age", min_value=0, max_value=150)
    }
    validator = DictValidator(schema)
    result = validator.validate(data)
    
    if not result.is_valid:
        raise HTTPException(
            status_code=422,
            detail=result.to_dict()
        )
    
    return {"message": "Validation passed"}
```

## Testing

Run the test suite:

```bash
cd solar-calculator-pro/backend
python -m pytest tests/test_validators.py -v
```

Test coverage: 94%

## Best Practices

1. **Always specify field names** for better error messages
2. **Use required=True** for mandatory fields
3. **Combine validators** using CompositeValidator for complex rules
4. **Add custom validators** for business-specific logic
5. **Handle validation errors** gracefully in API endpoints
6. **Use German format** for user-facing number inputs
7. **Validate early** to catch errors before processing
8. **Return detailed errors** to help users fix issues

## Examples

### Solar Calculator Input Validation

```python
from core.validators import DictValidator, NumberValidator, StringValidator

# Define validation schema for solar calculator input
solar_input_schema = {
    "roof_area": NumberValidator(
        field_name="roof_area",
        required=True,
        min_value=10,
        max_value=1000,
        german_format=True
    ),
    "roof_angle": NumberValidator(
        field_name="roof_angle",
        required=True,
        min_value=0,
        max_value=90,
        allow_decimal=True,
        decimal_places=1
    ),
    "orientation": StringValidator(
        field_name="orientation",
        required=True,
        allowed_values=["north", "south", "east", "west"]
    ),
    "annual_consumption": NumberValidator(
        field_name="annual_consumption",
        required=True,
        min_value=0,
        german_format=True
    )
}

validator = DictValidator(solar_input_schema)

# Validate user input
user_input = {
    "roof_area": "50,5",  # German format
    "roof_angle": 30.0,
    "orientation": "south",
    "annual_consumption": "4.500"  # German format
}

result = validator.validate(user_input)
if result.is_valid:
    # Process the input
    pass
else:
    # Return errors to user
    errors = result.to_dict()
```

### Price Matrix Validation

```python
# Validate price matrix entry
price_validator = NumberValidator(
    field_name="price",
    required=True,
    min_value=0,
    german_format=True,
    decimal_places=2
)

result = price_validator.validate("1.234,56")
```

### User Registration Validation

```python
registration_schema = {
    "username": StringValidator(
        field_name="username",
        required=True,
        min_length=3,
        max_length=20,
        pattern=r'^[a-zA-Z0-9_]+$'
    ),
    "email": EmailValidator(
        field_name="email",
        required=True
    ),
    "password": StringValidator(
        field_name="password",
        required=True,
        min_length=8
    ),
    "age": NumberValidator(
        field_name="age",
        required=True,
        min_value=18,
        allow_decimal=False
    )
}

validator = DictValidator(registration_schema)
```

## Security Considerations

The validation framework helps prevent:

1. **SQL Injection**: By validating input types and formats
2. **XSS Attacks**: By validating string patterns and lengths
3. **Buffer Overflow**: By enforcing maximum lengths
4. **Invalid Data**: By type checking and range validation
5. **Malicious Input**: By pattern matching and allowed values

Always validate user input before:
- Database operations
- File operations
- External API calls
- Business logic processing

## Performance

- Validators are lightweight and fast
- German format parsing uses efficient string operations
- Regex patterns are compiled once and reused
- Custom validators can be optimized as needed

## Future Enhancements

Potential future additions:
- Phone number validation
- Credit card validation
- IBAN validation
- Postal code validation
- IP address validation
- JSON schema validation
- XML validation

## Support

For issues or questions:
- Check the test file: `tests/test_validators.py`
- Review error codes above
- See examples in this documentation

## License

Part of Solar Calculator Pro Backend
Requirements: 4.4, 11.3
