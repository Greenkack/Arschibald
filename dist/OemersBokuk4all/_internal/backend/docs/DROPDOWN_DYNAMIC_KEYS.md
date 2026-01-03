# Dropdown and Selection Dynamic Keys System

## Overview

The Dropdown and Selection Dynamic Keys System provides comprehensive management of dropdown options with unique dynamic keys, cascading relationships, and selection history tracking. This system ensures that all dropdown options are uniquely identifiable and trackable throughout the application.

**Requirements:** 14.7  
**Task:** 224

## Features

### Core Features

1. **Dynamic Key Generation**
   - Unique keys for all dropdown instances
   - Unique keys for all dropdown options
   - Hierarchical key structure for cascading dropdowns

2. **Dropdown Types**
   - Single Select
   - Multi Select
   - Cascading
   - Searchable
   - Grouped
   - Dynamic
   - Autocomplete

3. **Option Management**
   - Add/remove options dynamically
   - Enable/disable options
   - Show/hide options
   - Sort options
   - Group options

4. **Cascading Dropdowns**
   - Parent-child relationships
   - Automatic option filtering
   - Custom filter functions
   - Multi-level cascading

5. **Selection History**
   - Track all selections
   - User-specific history
   - Session-specific history
   - Popular options tracking
   - History export

## Architecture

### Key Components

```
DropdownKeyManager
├── Dropdown Registry
├── Option Registry
├── Selection History
└── Cascading Relationships

Dropdown
├── Options List
├── Selected Value
└── Cascading Filter

DropdownOption
├── Dynamic Key
├── Value & Label
├── Parent/Children Keys
└── Metadata

SelectionHistoryEntry
├── Dropdown Key
├── Option Key
├── User/Session Info
└── Timestamp
```

## Usage Examples

### 1. Basic Dropdown

```python
from backend.services.dropdown_key_service import (
    DropdownKeyManager,
    DropdownType
)

# Create manager
manager = DropdownKeyManager()

# Register dropdown
options = [
    {"value": "mono", "label": "Monocrystalline"},
    {"value": "poly", "label": "Polycrystalline"},
    {"value": "thin", "label": "Thin Film"}
]

dropdown = manager.register_dropdown(
    dropdown_id="module_type",
    dropdown_type=DropdownType.SINGLE_SELECT,
    label="Solar Module Type",
    options=options,
    form_id="solar_calculator_form"
)

print(f"Dropdown Key: {dropdown.key}")
print(f"Options: {len(dropdown.get_options())}")
```

### 2. Grouped Dropdown

```python
# Register dropdown with grouped options
product_options = [
    {
        "value": "trina_400",
        "label": "Trina Solar 400W",
        "group": "Premium"
    },
    {
        "value": "trina_350",
        "label": "Trina Solar 350W",
        "group": "Standard"
    },
    {
        "value": "jinko_420",
        "label": "JinkoSolar 420W",
        "group": "Premium"
    }
]

dropdown = manager.register_dropdown(
    dropdown_id="solar_module",
    dropdown_type=DropdownType.GROUPED,
    label="Solar Module Selection",
    options=product_options
)

# Get options by group
for option in dropdown.get_options():
    print(f"{option.group}: {option.label}")
```

### 3. Cascading Dropdown

```python
# Register parent dropdown (countries)
country_options = [
    {
        "value": "USA",
        "label": "United States",
        "children": [
            {"value": "CA", "label": "California"},
            {"value": "NY", "label": "New York"}
        ]
    },
    {
        "value": "Germany",
        "label": "Germany",
        "children": [
            {"value": "BY", "label": "Bavaria"},
            {"value": "BE", "label": "Berlin"}
        ]
    }
]

country_dropdown = manager.register_dropdown(
    dropdown_id="country",
    dropdown_type=DropdownType.CASCADING,
    label="Country",
    options=country_options
)

# Register cascading relationship
parent_key, child_key = manager.register_cascading_dropdown(
    "country",
    "state"
)

# Filter child options based on parent selection
usa_states = manager.filter_cascading_options(
    country_dropdown.key,
    "USA",
    child_key
)
```

### 4. Selection History

```python
# Record a selection
option = manager.get_option_by_value(dropdown.key, "mono")
entry = manager.record_selection(
    dropdown.key,
    option.key,
    user_id="user123",
    session_id="session456"
)

# Get selection history
history = manager.get_selection_history(
    dropdown_key=dropdown.key,
    limit=10
)

for entry in history:
    print(f"{entry.option_label} selected at {entry.timestamp}")

# Get most popular options
popular = manager.get_most_selected_options(
    dropdown.key,
    limit=5
)

for option, count in popular:
    print(f"{option.label}: {count} selections")
```

### 5. Multi-Select Dropdown

```python
# Register multi-select dropdown
feature_options = [
    {"value": "monitoring", "label": "Real-time Monitoring"},
    {"value": "optimizer", "label": "Power Optimizers"},
    {"value": "battery", "label": "Battery Storage"}
]

dropdown = manager.register_dropdown(
    dropdown_id="system_features",
    dropdown_type=DropdownType.MULTI_SELECT,
    label="System Features",
    options=feature_options,
    multiple=True
)

# Set multiple selected values
dropdown.set_selected_value(["monitoring", "battery"])
```

### 6. Searchable Dropdown

```python
# Register searchable dropdown
city_options = [
    {"value": "berlin", "label": "Berlin"},
    {"value": "munich", "label": "Munich"},
    {"value": "hamburg", "label": "Hamburg"},
    # ... many more cities
]

dropdown = manager.register_dropdown(
    dropdown_id="city",
    dropdown_type=DropdownType.SEARCHABLE,
    label="City Selection",
    options=city_options,
    searchable=True
)
```

### 7. Dynamic Options

```python
# Get dropdown
dropdown = manager.get_dropdown_by_key(dropdown_key)

# Add option dynamically
from backend.services.dropdown_key_service import DropdownOption

new_option = DropdownOption(
    key=manager.create_option_key(
        dropdown.key,
        "new_value",
        "New Option"
    ),
    value="new_value",
    label="New Option"
)

dropdown.add_option(new_option)

# Remove option
dropdown.remove_option(option_key)

# Disable option
option = dropdown.get_option_by_value("some_value")
option.enabled = False

# Hide option
option.visible = False
```

### 8. Export Schema

```python
# Export complete dropdown schema
schema = manager.export_dropdown_schema(dropdown.key)

print(f"Dropdown ID: {schema['dropdown_id']}")
print(f"Label: {schema['label']}")
print(f"Type: {schema['dropdown_type']}")
print(f"Total Options: {schema['total_options']}")

for opt in schema['options']:
    print(f"  - {opt['label']} (key: {opt['key']})")
```

## API Reference

### DropdownKeyManager

#### Methods

**`create_dropdown_key(dropdown_id, dropdown_type, form_id=None, custom_suffix=None)`**
- Creates a unique dynamic key for a dropdown
- Returns: `str` - Generated key

**`create_option_key(dropdown_key, option_value, option_label, parent_key=None)`**
- Creates a unique dynamic key for an option
- Returns: `str` - Generated key

**`register_dropdown(dropdown_id, dropdown_type, label, options, ...)`**
- Registers a new dropdown with options
- Returns: `Dropdown` object

**`get_dropdown_by_key(key)`**
- Retrieves a dropdown by its key
- Returns: `Dropdown` or `None`

**`get_option_by_key(key)`**
- Retrieves an option by its key
- Returns: `DropdownOption` or `None`

**`get_options_by_dropdown(dropdown_key, include_disabled=False, include_hidden=False)`**
- Gets all options for a dropdown
- Returns: `List[DropdownOption]`

**`get_option_by_value(dropdown_key, value)`**
- Gets an option by its value
- Returns: `DropdownOption` or `None`

**`register_cascading_dropdown(parent_dropdown_id, child_dropdown_id, ...)`**
- Registers a cascading relationship
- Returns: `tuple[str, str]` - (parent_key, child_key)

**`filter_cascading_options(parent_key, parent_value, child_key)`**
- Filters child options based on parent selection
- Returns: `List[DropdownOption]`

**`record_selection(dropdown_key, option_key, user_id=None, session_id=None, metadata=None)`**
- Records a selection in history
- Returns: `SelectionHistoryEntry`

**`get_selection_history(dropdown_key=None, user_id=None, session_id=None, limit=None)`**
- Gets selection history with filters
- Returns: `List[SelectionHistoryEntry]`

**`get_most_selected_options(dropdown_key, limit=5)`**
- Gets most frequently selected options
- Returns: `List[tuple[DropdownOption, int]]`

**`clear_selection_history(dropdown_key=None, user_id=None)`**
- Clears selection history
- Returns: `int` - Number of entries cleared

**`export_dropdown_schema(dropdown_key)`**
- Exports complete dropdown schema
- Returns: `Dict[str, Any]`

**`get_statistics()`**
- Gets statistics about dropdowns
- Returns: `Dict[str, Any]`

### Dropdown

#### Properties
- `key`: Dynamic key
- `dropdown_id`: Identifier
- `dropdown_type`: Type enum
- `label`: Display label
- `form_id`: Optional form ID
- `multiple`: Allow multiple selection
- `searchable`: Enable search
- `selected_value`: Current selection

#### Methods

**`add_option(option)`**
- Adds an option to the dropdown

**`remove_option(option_key)`**
- Removes an option by key
- Returns: `bool`

**`get_options()`**
- Gets all options sorted by sort_order
- Returns: `List[DropdownOption]`

**`get_option_by_value(value)`**
- Gets option by value
- Returns: `DropdownOption` or `None`

**`set_selected_value(value)`**
- Sets the selected value

**`get_selected_value()`**
- Gets the selected value
- Returns: `Any`

**`get_selected_option()`**
- Gets the selected option object
- Returns: `DropdownOption` or `None`

**`to_dict()`**
- Converts to dictionary
- Returns: `Dict[str, Any]`

### DropdownOption

#### Properties
- `key`: Dynamic key
- `value`: Option value
- `label`: Display label
- `group`: Optional group name
- `metadata`: Additional data
- `parent_key`: Parent option key (for cascading)
- `children_keys`: List of child option keys
- `enabled`: Whether option is enabled
- `visible`: Whether option is visible
- `sort_order`: Sort order

#### Methods

**`to_dict()`**
- Converts to dictionary
- Returns: `Dict[str, Any]`

### SelectionHistoryEntry

#### Properties
- `dropdown_key`: Dropdown key
- `option_key`: Selected option key
- `option_value`: Selected value
- `option_label`: Selected label
- `timestamp`: Selection timestamp
- `user_id`: Optional user ID
- `session_id`: Optional session ID
- `metadata`: Additional data

#### Methods

**`to_dict()`**
- Converts to dictionary
- Returns: `Dict[str, Any]`

## Integration Examples

### With Forms

```python
from backend.services.form_input_key_service import get_form_input_manager
from backend.services.dropdown_key_service import get_dropdown_manager

form_manager = get_form_input_manager()
dropdown_manager = get_dropdown_manager()

# Register dropdown
dropdown = dropdown_manager.register_dropdown(
    "module_type",
    DropdownType.SINGLE_SELECT,
    "Module Type",
    options,
    form_id="solar_form"
)

# Register as form input
form_input = form_manager.register_form_input(
    form_id="solar_form",
    field_name="module_type",
    input_type=FormInputType.SELECT,
    label="Module Type"
)

# Link dropdown to form input
form_input.metadata['dropdown_key'] = dropdown.key
```

### With Database

```python
from backend.services.universal_data_service import UniversalDataService

data_service = UniversalDataService()

# Store dropdown with dynamic key
dropdown_data = dropdown.to_dict()
data_service.store_with_key(
    data=dropdown_data,
    dynamic_key=dropdown.key,
    data_type="dropdown"
)

# Store selection history
for entry in selection_history:
    data_service.store_with_key(
        data=entry.to_dict(),
        dynamic_key=f"SEL_{entry.dropdown_key}_{entry.timestamp.isoformat()}",
        data_type="selection"
    )
```

## Best Practices

### 1. Key Naming

```python
# Use descriptive dropdown IDs
dropdown_id = "solar_module_type"  # Good
dropdown_id = "dd1"  # Bad

# Use form_id for context
form_id = "solar_calculator_form"
```

### 2. Option Organization

```python
# Use sort_order for custom ordering
options = [
    {"value": "premium", "label": "Premium", "sort_order": 1},
    {"value": "standard", "label": "Standard", "sort_order": 2},
    {"value": "basic", "label": "Basic", "sort_order": 3}
]

# Use groups for logical organization
options = [
    {"value": "opt1", "label": "Option 1", "group": "Category A"},
    {"value": "opt2", "label": "Option 2", "group": "Category A"},
    {"value": "opt3", "label": "Option 3", "group": "Category B"}
]
```

### 3. Cascading Dropdowns

```python
# Define clear parent-child relationships
country_options = [
    {
        "value": "USA",
        "label": "United States",
        "children": [...]  # Nested children
    }
]

# Or use filter functions for complex logic
def filter_states(parent_option, child_option):
    return child_option.metadata.get('country') == parent_option.value

manager.register_cascading_dropdown(
    "country",
    "state",
    filter_function=filter_states
)
```

### 4. Selection History

```python
# Always include user_id and session_id
manager.record_selection(
    dropdown_key,
    option_key,
    user_id=current_user.id,
    session_id=current_session.id
)

# Periodically clean old history
manager.clear_selection_history(
    dropdown_key=dropdown_key,
    # Keep only recent selections
)
```

### 5. Performance

```python
# Cache frequently accessed dropdowns
dropdown_cache = {}

def get_cached_dropdown(dropdown_id):
    if dropdown_id not in dropdown_cache:
        dropdown_cache[dropdown_id] = manager.get_dropdown_by_key(
            dropdown_id
        )
    return dropdown_cache[dropdown_id]

# Use include_disabled and include_hidden wisely
active_options = manager.get_options_by_dropdown(
    dropdown_key,
    include_disabled=False,  # Exclude disabled
    include_hidden=False  # Exclude hidden
)
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest backend/tests/test_dropdown_keys.py -v

# Run specific test
pytest backend/tests/test_dropdown_keys.py::TestDropdownKeyManager::test_create_dropdown_key -v

# Run with coverage
pytest backend/tests/test_dropdown_keys.py --cov=backend.services.dropdown_key_service
```

## Demo

Run the comprehensive demo:

```bash
python backend/demo_dropdown_keys.py
```

## Related Documentation

- [Dynamic Keys System](DYNAMIC_KEY_SYSTEM.md)
- [Form Input Keys](FORM_INPUT_DYNAMIC_KEYS.md)
- [Universal Data Model](UNIVERSAL_DATA_MODEL.md)
- [Database Integration](DATABASE_INTEGRATION.md)

## Support

For issues or questions:
1. Check the demo file for examples
2. Review the test suite for usage patterns
3. Consult the API reference above
4. Check related documentation

## Changelog

### Version 1.0.0 (2024-11-16)
- Initial implementation
- Basic dropdown with dynamic keys
- Grouped dropdowns
- Cascading dropdowns
- Selection history tracking
- Multi-select support
- Searchable dropdowns
- Schema export
- Comprehensive tests
- Full documentation
