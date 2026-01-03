# Dropdown Dynamic Keys - Quick Reference

## Quick Start

```python
from backend.services.dropdown_key_service import (
    DropdownKeyManager,
    DropdownType
)

manager = DropdownKeyManager()
```

## Common Operations

### Create Basic Dropdown

```python
options = [
    {"value": "opt1", "label": "Option 1"},
    {"value": "opt2", "label": "Option 2"}
]

dropdown = manager.register_dropdown(
    "my_dropdown",
    DropdownType.SINGLE_SELECT,
    "My Dropdown",
    options
)
```

### Get Option by Value

```python
option = manager.get_option_by_value(dropdown.key, "opt1")
print(option.label)  # "Option 1"
```

### Record Selection

```python
manager.record_selection(
    dropdown.key,
    option.key,
    user_id="user123"
)
```

### Get Selection History

```python
history = manager.get_selection_history(
    dropdown_key=dropdown.key,
    limit=10
)
```

### Cascading Dropdown

```python
country_options = [
    {
        "value": "USA",
        "label": "United States",
        "children": [
            {"value": "CA", "label": "California"},
            {"value": "NY", "label": "New York"}
        ]
    }
]

country_dropdown = manager.register_dropdown(
    "country",
    DropdownType.CASCADING,
    "Country",
    country_options
)
```

### Multi-Select

```python
dropdown = manager.register_dropdown(
    "features",
    DropdownType.MULTI_SELECT,
    "Features",
    options,
    multiple=True
)
```

### Grouped Options

```python
options = [
    {"value": "opt1", "label": "Option 1", "group": "Group A"},
    {"value": "opt2", "label": "Option 2", "group": "Group B"}
]
```

### Most Popular Options

```python
popular = manager.get_most_selected_options(
    dropdown.key,
    limit=5
)

for option, count in popular:
    print(f"{option.label}: {count} times")
```

### Export Schema

```python
schema = manager.export_dropdown_schema(dropdown.key)
print(schema['total_options'])
```

### Statistics

```python
stats = manager.get_statistics()
print(f"Total dropdowns: {stats['total_dropdowns']}")
print(f"Total options: {stats['total_options']}")
```

## Dropdown Types

- `SINGLE_SELECT` - Single selection
- `MULTI_SELECT` - Multiple selections
- `CASCADING` - Parent-child relationship
- `SEARCHABLE` - With search functionality
- `GROUPED` - Options in groups
- `DYNAMIC` - Dynamically loaded options
- `AUTOCOMPLETE` - With autocomplete

## Key Methods

| Method | Description |
|--------|-------------|
| `register_dropdown()` | Create new dropdown |
| `get_dropdown_by_key()` | Get dropdown by key |
| `get_option_by_key()` | Get option by key |
| `get_option_by_value()` | Get option by value |
| `record_selection()` | Record selection |
| `get_selection_history()` | Get history |
| `get_most_selected_options()` | Get popular options |
| `export_dropdown_schema()` | Export schema |

## Option Properties

```python
option.key           # Dynamic key
option.value         # Option value
option.label         # Display label
option.group         # Group name
option.enabled       # Is enabled
option.visible       # Is visible
option.sort_order    # Sort order
option.parent_key    # Parent key (cascading)
option.children_keys # Child keys (cascading)
option.metadata      # Additional data
```

## Selection History

```python
entry.dropdown_key   # Dropdown key
entry.option_key     # Option key
entry.option_value   # Selected value
entry.option_label   # Selected label
entry.timestamp      # When selected
entry.user_id        # Who selected
entry.session_id     # Session ID
```

## Tips

1. **Always use dynamic keys** for tracking
2. **Record selections** for analytics
3. **Use groups** for organization
4. **Enable search** for many options
5. **Cache dropdowns** for performance
6. **Export schemas** for documentation

## Examples

See `backend/demo_dropdown_keys.py` for comprehensive examples.

## Tests

```bash
pytest backend/tests/test_dropdown_keys.py -v
```

## Documentation

Full documentation: `backend/docs/DROPDOWN_DYNAMIC_KEYS.md`
