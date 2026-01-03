# Form Input Dynamic Keys System

## Overview

The Form Input Dynamic Keys system provides comprehensive management of dynamic keys for all form inputs in the application. This system enables flexible data access, validation, persistence, and retrieval through unique keys attached to every form input.

**Requirements:** 14.7  
**Task:** 223

## Features

### Core Capabilities

1. **Dynamic Key Generation** - Automatic generation of unique keys for all form inputs
2. **Key Mapping** - Bidirectional mapping between field names and dynamic keys
3. **Key-Based Data Retrieval** - Fast lookup and retrieval using dynamic keys
4. **Key-Based Validation** - Validation rules attached to keys
5. **Key Persistence** - Save and load form inputs with their keys
6. **Value History** - Track all value changes with timestamps
7. **Form Submissions** - Store complete form submissions with keys

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           FormInputKeyManager                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │  • create_input_key()                              │ │
│  │  • register_form_input()                           │ │
│  │  • get_input_by_key()                              │ │
│  │  • get_form_key_mapping()                          │ │
│  │  • update_input_value()                            │ │
│  │  • validate_form()                                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              FormInput Objects                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  • Dynamic Key                                     │ │
│  │  • Current Value                                   │ │
│  │  • Validation Rules                                │ │
│  │  • Value History                                   │ │
│  │  • Metadata                                        │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           FormKeyPersistence                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │  • save_form_input()                               │ │
│  │  • load_form_input()                               │ │
│  │  • save_form_submission()                          │ │
│  │  • save_value_history()                            │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Usage Examples

### 1. Register Form Inputs

```python
from backend.services.form_input_key_service import (
    get_form_input_manager,
    FormInputType
)

# Get the global manager
manager = get_form_input_manager()

# Register a text input
text_input = manager.register_form_input(
    form_id="solar_calculator",
    field_name="customer_name",
    input_type=FormInputType.TEXT,
    label="Customer Name",
    default_value="",
    validation_rules={
        'required': True,
        'minLength': 2,
        'maxLength': 100
    }
)

# Register a number input
number_input = manager.register_form_input(
    form_id="solar_calculator",
    field_name="roof_area",
    input_type=FormInputType.NUMBER,
    label="Roof Area (m²)",
    default_value=50.0,
    validation_rules={
        'required': True,
        'min': 10,
        'max': 1000
    }
)

# Register a select input
select_input = manager.register_form_input(
    form_id="solar_calculator",
    field_name="roof_type",
    input_type=FormInputType.SELECT,
    label="Roof Type",
    default_value="flat",
    validation_rules={
        'required': True,
        'options': ['flat', 'gable', 'hip', 'shed']
    }
)

print(f"Text input key: {text_input.key}")
print(f"Number input key: {number_input.key}")
print(f"Select input key: {select_input.key}")
```

### 2. Update Input Values

```python
# Update by key
manager.update_input_value(text_input.key, "John Doe")
manager.update_input_value(number_input.key, 75.5)

# Update with validation
try:
    manager.update_input_value(number_input.key, 1500, validate=True)
except ValueError as e:
    print(f"Validation error: {e}")

# Get current value
value = manager.get_input_value(text_input.key)
print(f"Current value: {value}")
```

### 3. Get Form Data

```python
# Get all form data (field_name -> value)
data = manager.get_form_data("solar_calculator")
print(data)
# Output: {'customer_name': 'John Doe', 'roof_area': 75.5, 'roof_type': 'flat'}

# Get form data with keys included
data_with_keys = manager.get_form_data("solar_calculator", include_keys=True)
print(data_with_keys)
# Output: {
#     'customer_name': {
#         'value': 'John Doe',
#         'key': 'DAT_20231116_143052_a1b2c3d4_solar_calculator_customer_name',
#         'type': 'text'
#     },
#     ...
# }
```

### 4. Set Form Data

```python
# Set multiple values at once
form_data = {
    'customer_name': 'Jane Smith',
    'roof_area': 100.0,
    'roof_type': 'gable'
}

errors = manager.set_form_data("solar_calculator", form_data, validate=True)

if errors:
    print(f"Validation errors: {errors}")
else:
    print("Form data set successfully")
```

### 5. Validate Form

```python
# Validate all inputs in a form
is_valid, errors = manager.validate_form("solar_calculator")

if is_valid:
    print("Form is valid")
else:
    print(f"Validation errors: {errors}")
    # Output: {'customer_name': 'This field is required', ...}
```

### 6. Get Key Mapping

```python
# Get the mapping of field names to dynamic keys
key_mapping = manager.get_form_key_mapping("solar_calculator")
print(key_mapping)
# Output: {
#     'customer_name': 'DAT_20231116_143052_a1b2c3d4_solar_calculator_customer_name',
#     'roof_area': 'DAT_20231116_143053_b2c3d4e5_solar_calculator_roof_area',
#     'roof_type': 'DAT_20231116_143054_c3d4e5f6_solar_calculator_roof_type'
# }
```

### 7. Retrieve Input by Field Name

```python
# Get input by form ID and field name
input_obj = manager.get_input_by_field("solar_calculator", "roof_area")

if input_obj:
    print(f"Key: {input_obj.key}")
    print(f"Value: {input_obj.get_value()}")
    print(f"Type: {input_obj.input_type}")
```

### 8. Export Form Schema

```python
# Export complete form schema
schema = manager.export_form_schema("solar_calculator")
print(schema)
# Output: {
#     'form_id': 'solar_calculator',
#     'inputs': [...],
#     'key_mapping': {...},
#     'total_inputs': 3
# }
```

### 9. Persist Form Inputs

```python
from backend.services.form_key_persistence import get_form_key_persistence

# Get persistence instance
persistence = get_form_key_persistence()

# Save a form input
form_input_dict = text_input.to_dict()
persistence.save_form_input(form_input_dict)

# Load a form input
loaded = persistence.load_form_input(text_input.key)
print(loaded)

# Load all inputs for a form
all_inputs = persistence.load_form_inputs("solar_calculator")
print(f"Loaded {len(all_inputs)} inputs")
```

### 10. Save Form Submissions

```python
# Save a complete form submission
submission_id = persistence.save_form_submission(
    form_id="solar_calculator",
    data={
        'customer_name': 'John Doe',
        'roof_area': 75.5,
        'roof_type': 'flat'
    },
    user_id="user123",
    session_id="session456"
)

print(f"Submission saved with ID: {submission_id}")

# Load form submissions
submissions = persistence.load_form_submissions("solar_calculator", limit=10)
for submission in submissions:
    print(f"Submitted at: {submission['submitted_at']}")
    print(f"Data: {submission['data']}")
```

### 11. Track Value History

```python
# Value history is automatically tracked
input_obj = manager.get_input_by_field("solar_calculator", "roof_area")

# Set multiple values
input_obj.set_value(50.0)
input_obj.set_value(75.0)
input_obj.set_value(100.0)

# Get value history
history = input_obj.get_value_history()
for entry in history:
    print(f"Value: {entry['value']} at {entry['timestamp']}")

# Save history to database
for entry in history:
    persistence.save_value_history(
        input_key=input_obj.key,
        value=entry['value'],
        changed_at=entry['timestamp']
    )
```

### 12. Clear Form

```python
# Reset all inputs to their default values
manager.clear_form("solar_calculator")

# Verify values are reset
data = manager.get_form_data("solar_calculator")
print(data)
# Output: {'customer_name': '', 'roof_area': 50.0, 'roof_type': 'flat'}
```

## Supported Input Types

The system supports all common form input types:

- **TEXT** - Single-line text input
- **NUMBER** - Numeric input with min/max validation
- **EMAIL** - Email input with format validation
- **PASSWORD** - Password input
- **TEXTAREA** - Multi-line text input
- **SELECT** - Dropdown selection
- **MULTISELECT** - Multiple selection dropdown
- **CHECKBOX** - Boolean checkbox
- **RADIO** - Radio button group
- **SLIDER** - Range slider
- **DATE** - Date picker
- **TIME** - Time picker
- **DATETIME** - Date and time picker
- **FILE** - File upload
- **COLOR** - Color picker
- **RANGE** - Numeric range
- **TOGGLE** - Toggle switch

## Validation Rules

### Common Rules

- **required** - Field must have a value
- **min** - Minimum value (for numbers)
- **max** - Maximum value (for numbers)
- **minLength** - Minimum text length
- **maxLength** - Maximum text length
- **pattern** - Regular expression pattern
- **options** - Allowed values for select inputs

### Example Validation Rules

```python
validation_rules = {
    # Required field
    'required': True,
    
    # Number constraints
    'min': 0,
    'max': 1000,
    
    # Text constraints
    'minLength': 5,
    'maxLength': 100,
    
    # Pattern matching
    'pattern': r'^[A-Z][a-z]+$',
    
    # Select options
    'options': ['option1', 'option2', 'option3']
}
```

## Database Schema

### form_inputs Table

```sql
CREATE TABLE form_inputs (
    key TEXT PRIMARY KEY,
    form_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    input_type TEXT NOT NULL,
    label TEXT NOT NULL,
    current_value TEXT,
    default_value TEXT,
    validation_rules TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(form_id, field_name)
);
```

### form_data Table

```sql
CREATE TABLE form_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id TEXT NOT NULL,
    submission_data TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    user_id TEXT,
    session_id TEXT
);
```

### value_history Table

```sql
CREATE TABLE value_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_key TEXT NOT NULL,
    value TEXT,
    changed_at TEXT NOT NULL,
    FOREIGN KEY (input_key) REFERENCES form_inputs(key)
);
```

## API Integration

### FastAPI Endpoints (Example)

```python
from fastapi import APIRouter, HTTPException
from backend.services.form_input_key_service import get_form_input_manager

router = APIRouter(prefix="/api/v1/forms")

@router.get("/{form_id}/schema")
async def get_form_schema(form_id: str):
    """Get form schema with all inputs and keys"""
    manager = get_form_input_manager()
    return manager.export_form_schema(form_id)

@router.get("/{form_id}/data")
async def get_form_data(form_id: str, include_keys: bool = False):
    """Get current form data"""
    manager = get_form_input_manager()
    return manager.get_form_data(form_id, include_keys)

@router.post("/{form_id}/data")
async def set_form_data(form_id: str, data: dict):
    """Set form data with validation"""
    manager = get_form_input_manager()
    errors = manager.set_form_data(form_id, data, validate=True)
    
    if errors:
        raise HTTPException(status_code=422, detail=errors)
    
    return {"success": True}

@router.post("/{form_id}/validate")
async def validate_form(form_id: str):
    """Validate all form inputs"""
    manager = get_form_input_manager()
    is_valid, errors = manager.validate_form(form_id)
    
    return {
        "is_valid": is_valid,
        "errors": errors
    }

@router.get("/input/{key}")
async def get_input_by_key(key: str):
    """Get input details by dynamic key"""
    manager = get_form_input_manager()
    input_obj = manager.get_input_by_key(key)
    
    if not input_obj:
        raise HTTPException(status_code=404, detail="Input not found")
    
    return input_obj.to_dict()
```

## Best Practices

### 1. Form Registration

- Register all form inputs at application startup
- Use consistent form_id naming conventions
- Provide clear, descriptive labels
- Set appropriate default values
- Define comprehensive validation rules

### 2. Key Management

- Never hardcode dynamic keys
- Always use the key mapping to retrieve keys
- Store keys in the database for persistence
- Use keys for all data operations

### 3. Validation

- Always validate before saving
- Provide clear error messages
- Validate on both client and server
- Use appropriate validation rules for each input type

### 4. Persistence

- Save form inputs after registration
- Persist form submissions for audit trail
- Track value history for important fields
- Implement regular database backups

### 5. Performance

- Use key-based lookups for fast access
- Cache frequently accessed forms
- Batch operations when possible
- Index database tables appropriately

## Statistics and Monitoring

```python
# Get manager statistics
manager_stats = manager.get_statistics()
print(f"Total inputs: {manager_stats['total_inputs']}")
print(f"Total forms: {manager_stats['total_forms']}")
print(f"Inputs by type: {manager_stats['inputs_by_type']}")

# Get persistence statistics
persistence_stats = persistence.get_statistics()
print(f"Total submissions: {persistence_stats['total_submissions']}")
print(f"Total history entries: {persistence_stats['total_history_entries']}")
```

## Error Handling

```python
from backend.services.form_input_key_service import get_form_input_manager

manager = get_form_input_manager()

try:
    # Attempt to update with validation
    manager.update_input_value(key, value, validate=True)
except ValueError as e:
    print(f"Validation error: {e}")
except KeyError as e:
    print(f"Key not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

Run the comprehensive test suite:

```bash
pytest backend/tests/test_form_input_keys.py -v
```

## Related Documentation

- [Dynamic Keys System](DYNAMIC_KEY_SYSTEM.md)
- [Universal Data Model](UNIVERSAL_DATA_MODEL.md)
- [German Number Formatting](../docs/GERMAN_FORMATTING.md)

## Requirements Fulfilled

✅ **14.7** - Attach dynamic keys to all database records, form inputs, dropdown options, slider values, and calculation results

## Task Completion

✅ **Task 223: Input Field Dynamic Keys**
- ✅ Attach dynamic keys to all form inputs
- ✅ Create key mapping for form data
- ✅ Implement key-based data retrieval
- ✅ Build key-based validation
- ✅ Create key persistence system
