# Calculation Results Dynamic Keys - Quick Reference

## Quick Start

```python
from backend.services.calculation_result_key_service import (
    get_calculation_result_manager,
    CalculationType
)

manager = get_calculation_result_manager()
```

## Common Operations

### Register Result

```python
result = manager.register_calculation_result(
    CalculationType.SOLAR,
    {'system_size': 10.5, 'annual_production': 12000},
    project_id="PRJ_123"
)
```

### Get Result

```python
result = manager.get_result_by_key(key)
value = result.get_value('system_size')
```

### Update Result

```python
manager.update_result(
    key,
    updated_data,
    change_summary="Increased system size"
)
```

### Create Version

```python
version = manager.create_version(
    result_key,
    new_data,
    change_summary="Optimization iteration"
)
```

### Get Versions

```python
# All versions
versions = manager.get_versions(result_key)

# Specific version
version = manager.get_version(result_key, 2)

# Latest version
latest = manager.get_latest_version(result_key)
```

### Compare Results

```python
comparison = manager.compare_results(key1, key2)
print(f"Similarity: {comparison.similarity_score:.2%}")
print(f"Differences: {comparison.differences}")
```

### Get History

```python
# All history
history = manager.get_result_history(limit=10)

# By type
solar_history = manager.get_result_history(
    calculation_type=CalculationType.SOLAR
)

# By result
result_history = manager.get_result_history(
    result_key=key
)
```

### Export Result

```python
# As JSON
json_data = manager.export_result(key, format='json')

# As dict with versions
dict_data = manager.export_result(
    key,
    format='dict',
    include_versions=True
)

# With German formatting
german_data = manager.export_result(
    key,
    format='dict',
    apply_german_formatting=True
)
```

### Export Comparison

```python
exported = manager.export_comparison(
    comparison.comparison_key,
    format='json'
)
```

### Get Statistics

```python
stats = manager.get_statistics()
print(f"Total Results: {stats['total_results']}")
print(f"Total Versions: {stats['total_versions']}")
```

## Calculation Types

```python
CalculationType.SOLAR          # Solar PV
CalculationType.HEATPUMP       # Heat pump
CalculationType.COMBINED       # Solar + Heat pump
CalculationType.PRICE          # Price calculations
CalculationType.FINANCIAL      # Financial analysis
CalculationType.ENVIRONMENTAL  # Environmental impact
CalculationType.TECHNICAL      # Technical calculations
CalculationType.CUSTOM         # Custom calculations
```

## Key Format

```
{PREFIX}_{TIMESTAMP}_{UUID}_{PROJECT_ID}_{USER_ID}
```

Example: `SOL_20231116_143052_a1b2c3d4_PRJ_123`

## Version Format

```
{RESULT_KEY}_V{VERSION_NUMBER}
```

Example: `SOL_20231116_143052_a1b2c3d4_V2`

## Export Formats

- `'json'` - JSON string
- `'dict'` - Python dictionary
- `'csv'` - CSV string (flattened data)

## Common Patterns

### Track Optimization Iterations

```python
result = manager.register_calculation_result(
    CalculationType.SOLAR,
    initial_data,
    project_id=project_id
)

for iteration in optimizations:
    manager.update_result(
        result.key,
        iteration_data,
        change_summary=f"Iteration {iteration}"
    )

versions = manager.get_versions(result.key)
print(f"Total iterations: {len(versions)}")
```

### Compare Before/After

```python
before = manager.register_calculation_result(
    CalculationType.SOLAR,
    before_data
)

after = manager.register_calculation_result(
    CalculationType.SOLAR,
    after_data
)

comparison = manager.compare_results(before.key, after.key)
for key, diff in comparison.differences.items():
    print(f"{key}: {diff['change']:+.1f}%")
```

### Export for PDF

```python
pdf_data = manager.export_result(
    result_key,
    format='dict',
    apply_german_formatting=True,
    include_metadata=False
)

generate_pdf(pdf_data['data'])
```

### Audit Trail

```python
# Get all operations for a result
history = manager.get_result_history(result_key=key)

for entry in history:
    print(f"{entry['timestamp']}: {entry['action']}")
```

## Tips

1. **Always use the global manager**: `get_calculation_result_manager()`
2. **Provide change summaries**: Makes version history meaningful
3. **Use appropriate types**: Choose the right CalculationType
4. **Include metadata**: Add context for better tracking
5. **Export with versions**: For complete audit trail

## Error Handling

```python
result = manager.get_result_by_key(key)
if not result:
    print("Result not found")

try:
    comparison = manager.compare_results(key1, key2)
except ValueError as e:
    print(f"Comparison failed: {e}")
```

## Demo & Tests

- **Demo**: `python backend/demo_calculation_result_keys.py`
- **Tests**: `pytest backend/tests/test_calculation_result_keys.py -v`

## Full Documentation

See [CALCULATION_RESULT_KEYS.md](CALCULATION_RESULT_KEYS.md) for complete documentation.
