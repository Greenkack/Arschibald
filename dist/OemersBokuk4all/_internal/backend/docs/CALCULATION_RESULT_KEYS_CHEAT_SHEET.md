# Calculation Results Dynamic Keys - Cheat Sheet

## Import

```python
from backend.services.calculation_result_key_service import (
    get_calculation_result_manager,
    CalculationType
)

manager = get_calculation_result_manager()
```

## Register Result

```python
result = manager.register_calculation_result(
    CalculationType.SOLAR,
    {'system_size': 10.5},
    project_id="PRJ_123"
)
```

## Get Result

```python
result = manager.get_result_by_key(key)
```

## Update Result

```python
manager.update_result(key, new_data, change_summary="Updated")
```

## Versions

```python
# All versions
versions = manager.get_versions(key)

# Specific version
v2 = manager.get_version(key, 2)

# Latest version
latest = manager.get_latest_version(key)
```

## Compare

```python
comparison = manager.compare_results(key1, key2)
print(comparison.similarity_score)
print(comparison.differences)
```

## History

```python
# All history
history = manager.get_result_history(limit=10)

# By type
solar = manager.get_result_history(
    calculation_type=CalculationType.SOLAR
)
```

## Export

```python
# JSON
json_data = manager.export_result(key, format='json')

# Dict with versions
dict_data = manager.export_result(
    key,
    format='dict',
    include_versions=True
)

# German formatting
german = manager.export_result(
    key,
    format='dict',
    apply_german_formatting=True
)
```

## Statistics

```python
stats = manager.get_statistics()
```

## Calculation Types

- `CalculationType.SOLAR`
- `CalculationType.HEATPUMP`
- `CalculationType.COMBINED`
- `CalculationType.PRICE`
- `CalculationType.FINANCIAL`
- `CalculationType.ENVIRONMENTAL`
- `CalculationType.TECHNICAL`
- `CalculationType.CUSTOM`

## Key Format

`{PREFIX}_{TIMESTAMP}_{UUID}_{PROJECT_ID}`

Example: `SOL_20231116_143052_a1b2c3d4_PRJ_123`

## Version Format

`{RESULT_KEY}_V{NUMBER}`

Example: `SOL_20231116_143052_a1b2c3d4_V2`

## Common Patterns

### Track Iterations
```python
result = manager.register_calculation_result(
    CalculationType.SOLAR, initial_data
)
for i in range(5):
    manager.update_result(
        result.key, iteration_data,
        change_summary=f"Iteration {i+1}"
    )
```

### Compare Before/After
```python
before = manager.register_calculation_result(
    CalculationType.SOLAR, before_data
)
after = manager.register_calculation_result(
    CalculationType.SOLAR, after_data
)
comparison = manager.compare_results(before.key, after.key)
```

### Export for PDF
```python
pdf_data = manager.export_result(
    key, format='dict',
    apply_german_formatting=True
)
```

## Files

- **Service:** `backend/services/calculation_result_key_service.py`
- **Tests:** `backend/tests/test_calculation_result_keys.py`
- **Docs:** `backend/docs/CALCULATION_RESULT_KEYS.md`
- **Demo:** `backend/demo_calculation_result_keys.py`

## Run

```bash
# Demo
python backend/demo_calculation_result_keys.py

# Tests
pytest backend/tests/test_calculation_result_keys.py -v
```
