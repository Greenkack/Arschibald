# Dropdown Dynamic Keys - Cheat Sheet

## Quick Import

```python
from backend.services.dropdown_key_service import (
    DropdownKeyManager,
    DropdownType,
    get_dropdown_manager
)

manager = get_dropdown_manager()
```

## Create Dropdown

```python
dropdown = manager.register_dropdown(
    "dropdown_id",
    DropdownType.SINGLE_SELECT,
    "Label",
    [
        {"value": "v1", "label": "Option 1"},
        {"value": "v2", "label": "Option 2"}
    ]
)
```

## Get Dropdown/Option

```python
# By key
dropdown = manager.get_dropdown_by_key(key)
option = manager.get_option_by_key(key)

# By value
option = manager.get_option_by_value(dropdown_key, "v1")

# All options
options = manager.get_options_by_dropdown(dropdown_key)
```

## Cascading

```python
# Register relationship
parent_key, child_key = manager.register_cascading_dropdown(
    "parent_id",
    "child_id"
)

# Filter children
children = manager.filter_cascading_options(
    parent_key,
    parent_value,
    child_key
)
```

## Selection History

```python
# Record
manager.record_selection(
    dropdown_key,
    option_key,
    user_id="user123"
)

# Get history
history = manager.get_selection_history(
    dropdown_key=dropdown_key,
    limit=10
)

# Popular options
popular = manager.get_most_selected_options(
    dropdown_key,
    limit=5
)
```

## Dropdown Types

| Type | Use Case |
|------|----------|
| `SINGLE_SELECT` | One option |
| `MULTI_SELECT` | Multiple options |
| `CASCADING` | Parent-child |
| `SEARCHABLE` | Many options |
| `GROUPED` | Organized options |

## Option Properties

```python
option.key           # Unique key
option.value         # Value
option.label         # Display text
option.enabled       # Is enabled
option.visible       # Is visible
option.group         # Group name
option.sort_order    # Sort order
```

## Common Patterns

### Grouped Options
```python
options = [
    {"value": "v1", "label": "Opt 1", "group": "Group A"},
    {"value": "v2", "label": "Opt 2", "group": "Group B"}
]
```

### Nested Children
```python
options = [
    {
        "value": "parent",
        "label": "Parent",
        "children": [
            {"value": "child1", "label": "Child 1"}
        ]
    }
]
```

### Filter Options
```python
# Only enabled and visible
options = manager.get_options_by_dropdown(dropdown_key)

# Include disabled
options = manager.get_options_by_dropdown(
    dropdown_key,
    include_disabled=True
)

# Include hidden
options = manager.get_options_by_dropdown(
    dropdown_key,
    include_hidden=True
)
```

## Export/Stats

```python
# Export schema
schema = manager.export_dropdown_schema(dropdown_key)

# Get statistics
stats = manager.get_statistics()
print(stats['total_dropdowns'])
print(stats['total_options'])
```

## Tips

💡 Always use dynamic keys for tracking  
💡 Record selections for analytics  
💡 Use groups for organization  
💡 Enable search for 10+ options  
💡 Cache frequently accessed dropdowns  

## See Also

- Full Docs: `DROPDOWN_DYNAMIC_KEYS.md`
- Quick Ref: `DROPDOWN_KEYS_QUICK_REFERENCE.md`
- Tests: `test_dropdown_keys.py`
- Demo: `demo_dropdown_keys.py`
