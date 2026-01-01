# Calculation Results Dynamic Keys System

## Overview

The Calculation Results Dynamic Keys system provides comprehensive management of dynamic keys for all calculation results in the application. It enables versioning, comparison, history tracking, and export of calculation results with unique identifiers.

**Requirements:** 14.7  
**Task:** 225

## Features

### 1. Dynamic Key Generation
- Automatic generation of unique keys for all calculation results
- Support for multiple calculation types (Solar, Heat Pump, Combined, etc.)
- Customizable key prefixes based on calculation type
- Integration with project and user IDs

### 2. Result Versioning
- Automatic version creation on result registration
- Manual version creation for tracking changes
- Version history with change summaries
- Parent-child version relationships
- Access to specific versions or latest version

### 3. Result Comparison
- Compare two calculation results
- Calculate differences between results
- Compute similarity scores
- Track percentage changes for numeric values
- Identify added, removed, or changed fields

### 4. Result History
- Track all result operations (register, update, compare)
- Filter history by result key, calculation type, or user
- Timestamp tracking for all operations
- Comprehensive audit trail

### 5. Result Export
- Export results in multiple formats (JSON, Dict, CSV)
- Include or exclude version history
- Apply German number formatting
- Include or exclude metadata
- Export comparison results

## Architecture

### Core Components

```
CalculationResultKeyManager
├── Result Registry (key → CalculationResult)
├── Version Registry (key → List[CalculationResultVersion])
├── Comparison Registry (key → CalculationComparison)
└── History (List[operations])
```

### Key Classes

1. **CalculationResultKeyManager**: Main service class
2. **CalculationResult**: Represents a calculation result with dynamic key
3. **CalculationResultVersion**: Represents a versioned result
4. **CalculationComparison**: Represents a comparison between two results
5. **CalculationType**: Enum of calculation types

## Usage

### Basic Usage

```python
from backend.services.calculation_result_key_service import (
    get_calculation_result_manager,
    CalculationType
)

# Get manager instance
manager = get_calculation_result_manager()

# Register a calculation result
solar_data = {
    'system_size': 10.5,
    'annual_production': 12000,
    'payback_period': 8.5
}

result = manager.register_calculation_result(
    CalculationType.SOLAR,
    solar_data,
    project_id="PRJ_123",
    user_id="USER_456"
)

print(f"Result Key: {result.key}")
print(f"System Size: {result.get_value('system_size')} kWp")
```

### Versioning

```python
# Update result (creates new version)
updated_data = solar_data.copy()
updated_data['system_size'] = 12.0

manager.update_result(
    result.key,
    updated_data,
    user_id="USER_456",
    change_summary="Increased system size"
)

# Get all versions
versions = manager.get_versions(result.key)
print(f"Total versions: {len(versions)}")

# Get specific version
version_2 = manager.get_version(result.key, 2)
print(f"Version 2 system size: {version_2.data['system_size']}")

# Get latest version
latest = manager.get_latest_version(result.key)
print(f"Latest version: {latest.version_number}")
```

### Comparison

```python
# Compare two results
comparison = manager.compare_results(result_key_1, result_key_2)

print(f"Similarity: {comparison.similarity_score:.2%}")
print(f"Differences: {len(comparison.differences)}")

for key, diff in comparison.differences.items():
    print(f"{key}: {diff['value1']} → {diff['value2']}")
    print(f"  Change: {diff['change']}")
```

### History

```python
# Get all history
history = manager.get_result_history(limit=10)

# Filter by calculation type
solar_history = manager.get_result_history(
    calculation_type=CalculationType.SOLAR,
    limit=5
)

# Filter by result key
result_history = manager.get_result_history(
    result_key=result.key
)
```

### Export

```python
# Export as JSON
json_export = manager.export_result(
    result.key,
    format='json',
    include_versions=True
)

# Export as dictionary with German formatting
dict_export = manager.export_result(
    result.key,
    format='dict',
    apply_german_formatting=True
)

# Export comparison
comparison_export = manager.export_comparison(
    comparison.comparison_key,
    format='json'
)
```

## Calculation Types

The system supports the following calculation types:

- **SOLAR**: Solar PV calculations
- **HEATPUMP**: Heat pump calculations
- **COMBINED**: Combined solar + heat pump
- **PRICE**: Price calculations
- **FINANCIAL**: Financial analysis
- **ENVIRONMENTAL**: Environmental impact
- **TECHNICAL**: Technical calculations
- **CUSTOM**: Custom calculations

## Key Format

Dynamic keys follow this format:

```
{PREFIX}_{TIMESTAMP}_{UUID}_{PROJECT_ID}_{USER_ID}_{CUSTOM_SUFFIX}
```

Example:
```
SOL_20231116_143052_a1b2c3d4_PRJ_123_USER_456
```

### Key Prefixes by Type

- Solar: `SOL_`
- Heat Pump: `HP_`
- Price: `PRC_`
- Other: `DAT_`

## Version Format

Version keys extend the result key:

```
{RESULT_KEY}_V{VERSION_NUMBER}
```

Example:
```
SOL_20231116_143052_a1b2c3d4_PRJ_123_V2
```

## Data Structure

### CalculationResult

```python
{
    'key': 'SOL_20231116_143052_a1b2c3d4',
    'calculation_type': 'solar',
    'data': {
        'system_size': 10.5,
        'annual_production': 12000,
        # ... more fields
    },
    'project_id': 'PRJ_123',
    'user_id': 'USER_456',
    'session_id': 'SESSION_789',
    'created_at': '2023-11-16T14:30:52',
    'updated_at': '2023-11-16T14:30:52',
    'metadata': {}
}
```

### CalculationResultVersion

```python
{
    'version_key': 'SOL_..._V2',
    'version_number': 2,
    'result_key': 'SOL_...',
    'calculation_type': 'solar',
    'data': { ... },
    'timestamp': '2023-11-16T14:35:00',
    'user_id': 'USER_456',
    'parent_version_key': 'SOL_..._V1',
    'change_summary': 'Increased system size',
    'metadata': {}
}
```

### CalculationComparison

```python
{
    'comparison_key': 'CMP_SOL_..._SOL_...',
    'result_key_1': 'SOL_...',
    'result_key_2': 'SOL_...',
    'differences': {
        'system_size': {
            'value1': 10.5,
            'value2': 12.0,
            'change': 14.29  # Percentage
        }
    },
    'similarity_score': 0.875,
    'timestamp': '2023-11-16T14:40:00',
    'metadata': {}
}
```

## German Number Formatting

When exporting with German formatting enabled:

- Decimal separator: `,` (comma)
- Thousand separator: `.` (dot)
- Decimal places: 2

Example:
```python
# Original: 15000.50
# Formatted: "15.000,50"
```

## Statistics

Get comprehensive statistics:

```python
stats = manager.get_statistics()

# Returns:
{
    'total_results': 42,
    'total_versions': 156,
    'total_comparisons': 8,
    'results_by_type': {
        'solar': 30,
        'heatpump': 12
    },
    'average_versions_per_result': 3.71,
    'history_entries': 200
}
```

## Best Practices

### 1. Always Use Manager Instance

```python
# Good
manager = get_calculation_result_manager()

# Avoid creating new instances
# manager = CalculationResultKeyManager()  # Don't do this
```

### 2. Provide Meaningful Change Summaries

```python
# Good
manager.update_result(
    key,
    data,
    change_summary="Optimized module placement for better production"
)

# Less useful
manager.update_result(key, data, change_summary="Updated")
```

### 3. Use Appropriate Calculation Types

```python
# Good - specific type
manager.register_calculation_result(
    CalculationType.SOLAR,
    data
)

# Less specific
manager.register_calculation_result(
    CalculationType.CUSTOM,
    data
)
```

### 4. Include Context in Metadata

```python
result = manager.register_calculation_result(
    CalculationType.SOLAR,
    data,
    metadata={
        'source': 'web_ui',
        'optimization_level': 'high',
        'weather_data_source': 'pvgis'
    }
)
```

### 5. Export with Versions for Audit Trail

```python
# For audit purposes
exported = manager.export_result(
    key,
    format='json',
    include_versions=True,
    include_metadata=True
)
```

## Integration Examples

### With Solar Calculator

```python
# After solar calculation
result = manager.register_calculation_result(
    CalculationType.SOLAR,
    calculation_results,
    project_id=project_id,
    user_id=current_user_id,
    session_id=session_id
)

# Store key in session
st.session_state['calculation_result_key'] = result.key
```

### With Heat Pump Calculator

```python
# After heat pump calculation
result = manager.register_calculation_result(
    CalculationType.HEATPUMP,
    heatpump_results,
    project_id=project_id
)

# Compare with previous calculation
if previous_result_key:
    comparison = manager.compare_results(
        previous_result_key,
        result.key
    )
    show_comparison_ui(comparison)
```

### With PDF Generation

```python
# Get result for PDF
result = manager.get_result_by_key(result_key)

# Export with German formatting for PDF
pdf_data = manager.export_result(
    result_key,
    format='dict',
    apply_german_formatting=True
)

# Generate PDF with formatted data
generate_pdf(pdf_data)
```

## Error Handling

```python
try:
    result = manager.get_result_by_key(key)
    if not result:
        print("Result not found")
except ValueError as e:
    print(f"Error: {e}")
```

## Performance Considerations

- Results are stored in memory (use database for persistence)
- Version history grows with updates (consider cleanup strategies)
- Comparison operations are O(n) where n is number of fields
- Export operations create copies of data

## Future Enhancements

- Database persistence for results and versions
- Automatic cleanup of old versions
- Advanced comparison algorithms
- Result templates
- Batch operations
- Result search and filtering
- Result tags and categories

## Related Documentation

- [Dynamic Keys System](DYNAMIC_KEY_SYSTEM.md)
- [German Number Formatting](GERMAN_FORMATTER.md)
- [Form Input Keys](FORM_INPUT_DYNAMIC_KEYS.md)
- [Dropdown Keys](DROPDOWN_DYNAMIC_KEYS.md)

## Support

For issues or questions:
- Check the demo file: `backend/demo_calculation_result_keys.py`
- Run tests: `pytest backend/tests/test_calculation_result_keys.py`
- Review examples in this documentation
