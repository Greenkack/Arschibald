# Validation Framework - Quick Reference

## Import

```python
from core.validators import (
    NumberValidator,
    StringValidator,
    DateTimeValidator,
    EmailValidator,
    URLValidator,
    CompositeValidator,
    DictValidator,
    ListValidator,
    validate_number,
    validate_string,
    validate_date,
    validate_email,
    validate_url
)
```

## Quick Validation

```python
# Number
result = validate_number(42, field_name="age", min_value=18)

# String
result = validate_string("hello", field_name="name", min_length=3)

# Email
result = validate_email("user@example.com")

# URL
result = validate_url("https://example.com")

# Date
result = validate_date(date.today())
```

## Number Validation

```python
# Basic
validator = NumberValidator(field_name="age", min_value=18, max_value=100)

# German format (1.234,56)
validator = NumberValidator(field_name="price", german_format=True)

# Integer only
validator = NumberValidator(field_name="count", allow_decimal=False)

# Positive only
validator = NumberValidator(field_name="amount", allow_negative=False)

# Decimal places
validator = NumberValidator(field_name="price", decimal_places=2)
```

## String Validation

```python
# Length
validator = StringValidator(field_name="name", min_length=3, max_length=50)

# Pattern
validator = StringValidator(field_name="code", pattern=r'^[A-Z]{3}\d{3}$')

# Allowed values
validator = StringValidator(
    field_name="status",
    allowed_values=["active", "inactive"]
)

# Transformations
validator = StringValidator(
    field_name="email",
    trim=True,
    lowercase=True
)
```

## Date/Time Validation

```python
# Basic
validator = DateTimeValidator(field_name="birth_date")

# No future dates
validator = DateTimeValidator(field_name="birth_date", allow_future=False)

# Date range
validator = DateTimeValidator(
    field_name="date",
    min_date=date(2020, 1, 1),
    max_date=date(2025, 12, 31)
)

# Custom format
validator = DateTimeValidator(
    field_name="date",
    date_format="%d.%m.%Y"
)
```

## Email & URL

```python
# Email
validator = EmailValidator(field_name="email", required=True)

# URL
validator = URLValidator(field_name="website")

# HTTPS only
validator = URLValidator(field_name="api_url", require_https=True)
```

## Dictionary Validation

```python
schema = {
    "name": StringValidator(field_name="name", required=True),
    "age": NumberValidator(field_name="age", min_value=0),
    "email": EmailValidator(field_name="email")
}
validator = DictValidator(schema)
result = validator.validate(data_dict)
```

## List Validation

```python
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

## Custom Validators

```python
validator = NumberValidator(field_name="even")
validator.add_custom_validator(
    lambda x: x % 2 == 0,
    "Must be even"
)
```

## Composite Validators

```python
validators = [
    NumberValidator(field_name="age", min_value=18),
    NumberValidator(field_name="age", max_value=100)
]
composite = CompositeValidator(validators)
```

## Error Handling

```python
result = validator.validate(value)

if result.is_valid:
    # Process value
    pass
else:
    # Handle errors
    for error in result.errors:
        print(f"{error.field}: {error.message} ({error.code})")
    
    # Or convert to dict
    error_dict = result.to_dict()
```

## Common Error Codes

| Code | Description |
|------|-------------|
| `REQUIRED_FIELD` | Required field missing |
| `INVALID_NUMBER_FORMAT` | Cannot parse number |
| `VALUE_TOO_SMALL` | Below minimum |
| `VALUE_TOO_LARGE` | Above maximum |
| `STRING_TOO_SHORT` | Below min length |
| `STRING_TOO_LONG` | Above max length |
| `PATTERN_MISMATCH` | Doesn't match pattern |
| `INVALID_EMAIL` | Invalid email format |
| `HTTPS_REQUIRED` | HTTPS required |
| `INVALID_DATE_FORMAT` | Cannot parse date |
| `FUTURE_DATE_NOT_ALLOWED` | Future date not allowed |
| `PAST_DATE_NOT_ALLOWED` | Past date not allowed |

## FastAPI Integration

```python
from fastapi import HTTPException
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    age: int
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        result = validate_number(v, field_name="age", min_value=18)
        if not result.is_valid:
            raise ValueError(result.errors[0].message)
        return v
```

## Solar Calculator Example

```python
solar_schema = {
    "roof_area": NumberValidator(
        field_name="roof_area",
        required=True,
        min_value=10,
        german_format=True
    ),
    "roof_angle": NumberValidator(
        field_name="roof_angle",
        min_value=0,
        max_value=90
    ),
    "orientation": StringValidator(
        field_name="orientation",
        allowed_values=["north", "south", "east", "west"]
    )
}

validator = DictValidator(solar_schema)
result = validator.validate(user_input)
```

## Testing

```bash
cd solar-calculator-pro/backend
python -m pytest tests/test_validators.py -v
```

## Tips

✅ Always specify `field_name` for better errors  
✅ Use `required=True` for mandatory fields  
✅ Use `german_format=True` for user inputs  
✅ Validate early, before processing  
✅ Return detailed errors to users  
✅ Combine validators for complex rules  
✅ Add custom validators for business logic  

## Requirements

- Requirements: 4.4 (Request Validation)
- Requirements: 11.3 (Security - Input Validation)
