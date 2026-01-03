# Form Input Dynamic Keys - Quick Reference

## Quick Start

```python
from backend.services.form_input_key_service import (
    get_form_input_manager,
    FormInputType
)

manager = get_form_input_manager()
```

## Register Input

```python
input_obj = manager.register_form_input(
    form_id="my_form",
    field_name="my_field",
    input_type=FormInputType.TEXT,
    label="My Field",
    default_value="",
    validation_rules={'required': True}
)
```

## Update Value

```python
# Update by key
manager.update_input_value(input_obj.key, "new value")

# Update with validation
manager.update_input_value(input_obj.key, "new value", validate=True)
```

## Get Value

```python
value = manager.get_input_value(input_obj.key)
```

## Get Form Data

```python
# Simple data
data = manager.get_form_data("my_form")

# With keys
data = manager.get_form_data("my_form", include_keys=True)
```

## Set Form Data

```python
errors = manager.set_form_data("my_form", {
    'field1': 'value1',
    'field2': 'value2'
}, validate=True)
```

## Validate Form

```python
is_valid, errors = manager.validate_form("my_form")
```

## Get Key Mapping

```python
mapping = manager.get_form_key_mapping("my_form")
# Returns: {'field_name': 'dynamic_key', ...}
```

## Get Input by Field

```python
input_obj = manager.get_input_by_field("my_form", "my_field")
```

## Export Schema

```python
schema = manager.export_form_schema("my_form")
```

## Clear Form

```python
manager.clear_form("my_form")
```

## Persistence

```python
from backend.services.form_key_persistence import get_form_key_persistence

persistence = get_form_key_persistence()

# Save input
persistence.save_form_input(input_obj.to_dict())

# Load input
loaded = persistence.load_form_input(key)

# Save submission
submission_id = persistence.save_form_submission(
    form_id="my_form",
    data={'field1': 'value1'}
)

# Load submissions
submissions = persistence.load_form_submissions("my_form")
```

## Input Types

```python
FormInputType.TEXT
FormInputType.NUMBER
FormInputType.EMAIL
FormInputType.PASSWORD
FormInputType.TEXTAREA
FormInputType.SELECT
FormInputType.MULTISELECT
FormInputType.CHECKBOX
FormInputType.RADIO
FormInputType.SLIDER
FormInputType.DATE
FormInputType.TIME
FormInputType.DATETIME
FormInputType.FILE
FormInputType.COLOR
FormInputType.RANGE
FormInputType.TOGGLE
```

## Validation Rules

```python
validation_rules = {
    'required': True,           # Field is required
    'min': 0,                   # Minimum value (numbers)
    'max': 100,                 # Maximum value (numbers)
    'minLength': 5,             # Minimum length (text)
    'maxLength': 100,           # Maximum length (text)
    'pattern': r'^[A-Z]+$',     # Regex pattern
    'options': ['a', 'b', 'c']  # Allowed options (select)
}
```

## Statistics

```python
# Manager stats
stats = manager.get_statistics()

# Persistence stats
stats = persistence.get_statistics()
```

## Common Patterns

### Solar Calculator Form

```python
# Register inputs
manager.register_form_input(
    form_id="solar_calc",
    field_name="roof_area",
    input_type=FormInputType.NUMBER,
    label="Roof Area (m²)",
    default_value=50.0,
    validation_rules={'required': True, 'min': 10, 'max': 1000}
)

manager.register_form_input(
    form_id="solar_calc",
    field_name="roof_type",
    input_type=FormInputType.SELECT,
    label="Roof Type",
    default_value="flat",
    validation_rules={
        'required': True,
        'options': ['flat', 'gable', 'hip', 'shed']
    }
)

# Set data
errors = manager.set_form_data("solar_calc", {
    'roof_area': 75.5,
    'roof_type': 'gable'
}, validate=True)

# Validate
is_valid, errors = manager.validate_form("solar_calc")

# Get data
data = manager.get_form_data("solar_calc")

# Save submission
persistence.save_form_submission(
    form_id="solar_calc",
    data=data,
    user_id="user123"
)
```

### Customer Form

```python
# Register inputs
manager.register_form_input(
    form_id="customer_form",
    field_name="name",
    input_type=FormInputType.TEXT,
    label="Name",
    validation_rules={'required': True, 'minLength': 2}
)

manager.register_form_input(
    form_id="customer_form",
    field_name="email",
    input_type=FormInputType.EMAIL,
    label="Email",
    validation_rules={'required': True}
)

manager.register_form_input(
    form_id="customer_form",
    field_name="phone",
    input_type=FormInputType.TEXT,
    label="Phone",
    validation_rules={'pattern': r'^\+?[0-9\s\-]+$'}
)
```

### Settings Form

```python
# Register inputs
manager.register_form_input(
    form_id="settings",
    field_name="theme",
    input_type=FormInputType.SELECT,
    label="Theme",
    default_value="light",
    validation_rules={'options': ['light', 'dark', 'auto']}
)

manager.register_form_input(
    form_id="settings",
    field_name="notifications",
    input_type=FormInputType.CHECKBOX,
    label="Enable Notifications",
    default_value=True
)

manager.register_form_input(
    form_id="settings",
    field_name="language",
    input_type=FormInputType.SELECT,
    label="Language",
    default_value="de",
    validation_rules={'options': ['de', 'en', 'fr', 'es']}
)
```

## Error Handling

```python
try:
    manager.update_input_value(key, value, validate=True)
except ValueError as e:
    print(f"Validation error: {e}")
except KeyError as e:
    print(f"Key not found: {e}")
```

## Testing

```bash
# Run tests
pytest backend/tests/test_form_input_keys.py -v

# Run specific test
pytest backend/tests/test_form_input_keys.py::TestFormInputKeyManager::test_register_form_input -v
```

## Requirements

✅ **14.7** - Dynamic keys for all form inputs

## Task

✅ **223** - Input Field Dynamic Keys
