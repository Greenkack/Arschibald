# Validation Reporter Reference

## Overview

The Validation Reporter module provides comprehensive validation reporting functionality for the Multi-PDF Positioning System. It generates detailed reports for individual firma/seite combinations as well as batch summaries across multiple combinations.

## Requirements Covered

- **6.4**: Validation reporting with comprehensive documentation
- **6.5**: Warning and error documentation with detailed listings

## Key Features

1. **Single Validation Reports**: Generate detailed reports for individual firma/seite combinations
2. **Batch Validation Reports**: Aggregate validation results across multiple combinations
3. **Multiple Output Formats**: Text and JSON formats for reports
4. **Error and Warning Lists**: Extract all errors and warnings across validations
5. **Summaries by Firma and Seite**: Group validation results by firma or seite
6. **File Export**: Save reports to disk in various formats

## Classes

### ValidationReporter

Main class for generating validation reports.

```python
from multi_pdf_positioning.validation_reporter import ValidationReporter

reporter = ValidationReporter()
```

#### Methods

##### generate_validation_report()

Generate a comprehensive validation report for a single combination.

```python
report = reporter.generate_validation_report(
    positions=[(50, 50, 200, 100), (250, 50, 400, 100)],
    elements=None,  # Optional YMLElement list
    firma=1,
    seite=1
)
```

**Parameters:**
- `positions`: List of position tuples (x1, y1, x2, y2)
- `elements`: Optional list of YMLElement objects for context
- `firma`: Optional firma number
- `seite`: Optional seite number

**Returns:** `ValidationReport` object

##### generate_batch_report()

Generate a batch validation report for multiple firma/seite combinations.

```python
validation_data = {
    (1, 1): ([(50, 50, 200, 100)], None),
    (1, 2): ([(250, 50, 400, 100)], None),
}

summary = reporter.generate_batch_report(validation_data)
```

**Parameters:**
- `validation_data`: Dictionary mapping (firma, seite) tuples to (positions, elements) tuples

**Returns:** `BatchValidationSummary` object

##### format_report_text()

Format a validation report as human-readable text.

```python
text = reporter.format_report_text(report, include_details=True)
print(text)
```

##### format_batch_summary_text()

Format a batch validation summary as human-readable text.

```python
text = reporter.format_batch_summary_text(
    summary,
    include_per_firma=True,
    include_per_seite=True
)
print(text)
```

##### format_report_json()

Format a validation report as JSON-serializable dictionary.

```python
data = reporter.format_report_json(report)
```

##### format_batch_summary_json()

Format a batch validation summary as JSON-serializable dictionary.

```python
data = reporter.format_batch_summary_json(summary)
```

##### save_report_text()

Save a validation report to a text file.

```python
from pathlib import Path

reporter.save_report_text(
    report,
    Path("reports/report_f1_s1.txt"),
    include_details=True
)
```

##### save_report_json()

Save a validation report to a JSON file.

```python
reporter.save_report_json(
    report,
    Path("reports/report_f1_s1.json")
)
```

##### save_batch_summary_text()

Save a batch validation summary to a text file.

```python
reporter.save_batch_summary_text(
    summary,
    Path("reports/batch_summary.txt"),
    include_per_firma=True,
    include_per_seite=True
)
```

##### save_batch_summary_json()

Save a batch validation summary to a JSON file.

```python
reporter.save_batch_summary_json(
    summary,
    Path("reports/batch_summary.json")
)
```

##### generate_error_list()

Generate a list of all errors across all reports.

```python
errors = reporter.generate_error_list(summary)

for error in errors:
    print(f"Firma {error['firma']}, Seite {error['seite']}: {error['message']}")
```

##### generate_warning_list()

Generate a list of all warnings across all reports.

```python
warnings = reporter.generate_warning_list(summary)

for warning in warnings:
    print(f"Firma {warning['firma']}, Seite {warning['seite']}: {warning['message']}")
```

##### generate_collision_list()

Generate a list of all collisions across all reports.

```python
collisions = reporter.generate_collision_list(summary)

for collision in collisions:
    print(f"Firma {collision['firma']}, Seite {collision['seite']}: "
          f"Elements {collision['element1_index']} and {collision['element2_index']}")
```

##### generate_summary_by_firma()

Generate summary statistics grouped by firma.

```python
firma_summaries = reporter.generate_summary_by_firma(summary)

for firma, stats in firma_summaries.items():
    print(f"Firma {firma}:")
    print(f"  Valid seiten: {stats['valid_seiten']}/{stats['total_seiten']}")
    print(f"  Errors: {stats['total_errors']}")
    print(f"  Warnings: {stats['total_warnings']}")
```

##### generate_summary_by_seite()

Generate summary statistics grouped by seite.

```python
seite_summaries = reporter.generate_summary_by_seite(summary)

for seite, stats in seite_summaries.items():
    print(f"Seite {seite}:")
    print(f"  Valid firmen: {stats['valid_firmen']}/{stats['total_firmen']}")
    print(f"  Errors: {stats['total_errors']}")
    print(f"  Warnings: {stats['total_warnings']}")
```

### BatchValidationSummary

Data class containing aggregated validation results.

**Attributes:**
- `timestamp`: When the batch validation was performed
- `total_combinations`: Total number of combinations validated
- `valid_combinations`: Number of valid combinations
- `invalid_combinations`: Number of invalid combinations
- `total_errors`: Total errors across all combinations
- `total_warnings`: Total warnings across all combinations
- `total_collisions`: Total collisions across all combinations
- `reports_by_firma`: Reports grouped by firma
- `reports_by_seite`: Reports grouped by seite
- `all_reports`: All individual validation reports

## Convenience Functions

### generate_validation_report()

Convenience function to generate a validation report without creating a reporter instance.

```python
from multi_pdf_positioning.validation_reporter import generate_validation_report

report = generate_validation_report(
    positions=[(50, 50, 200, 100)],
    firma=1,
    seite=1
)
```

### generate_batch_report()

Convenience function to generate a batch validation report.

```python
from multi_pdf_positioning.validation_reporter import generate_batch_report

validation_data = {
    (1, 1): ([(50, 50, 200, 100)], None),
}

summary = generate_batch_report(validation_data)
```

## Usage Examples

### Example 1: Single Report

```python
from multi_pdf_positioning.validation_reporter import ValidationReporter

reporter = ValidationReporter()

# Validate positions
positions = [
    (50, 50, 200, 100),
    (250, 50, 400, 100),
]

report = reporter.generate_validation_report(
    positions, firma=1, seite=1
)

# Print report
print(reporter.format_report_text(report))

# Save report
reporter.save_report_text(report, Path("report.txt"))
reporter.save_report_json(report, Path("report.json"))
```

### Example 2: Batch Report

```python
from multi_pdf_positioning.validation_reporter import ValidationReporter

reporter = ValidationReporter()

# Prepare validation data
validation_data = {}

for firma in [1, 2, 3]:
    for seite in [1, 2, 3]:
        positions = [
            (50, 50, 200, 100),
            (250, 50, 400, 100),
        ]
        validation_data[(firma, seite)] = (positions, None)

# Generate batch report
summary = reporter.generate_batch_report(validation_data)

# Print summary
print(reporter.format_batch_summary_text(summary))

# Save summary
reporter.save_batch_summary_text(summary, Path("batch_summary.txt"))
reporter.save_batch_summary_json(summary, Path("batch_summary.json"))
```

### Example 3: Error and Warning Analysis

```python
from multi_pdf_positioning.validation_reporter import ValidationReporter

reporter = ValidationReporter()

# Generate batch report (with some invalid positions)
validation_data = {
    (1, 1): ([(400, 50, 600, 100)], None),  # Out of bounds
    (1, 2): ([(5, 50, 200, 100)], None),    # Too close to edge
    (2, 1): ([(50, 50, 200, 100), (100, 75, 250, 125)], None),  # Collision
}

summary = reporter.generate_batch_report(validation_data)

# Extract errors and warnings
errors = reporter.generate_error_list(summary)
warnings = reporter.generate_warning_list(summary)
collisions = reporter.generate_collision_list(summary)

print(f"Total errors: {len(errors)}")
print(f"Total warnings: {len(warnings)}")
print(f"Total collisions: {len(collisions)}")

# Print details
for error in errors:
    print(f"ERROR - Firma {error['firma']}, Seite {error['seite']}: {error['message']}")
```

### Example 4: Summaries by Firma and Seite

```python
from multi_pdf_positioning.validation_reporter import ValidationReporter

reporter = ValidationReporter()

# Generate batch report
validation_data = {
    (1, 1): ([(50, 50, 200, 100)], None),
    (1, 2): ([(100, 75, 250, 125), (50, 50, 200, 100)], None),  # Collision
    (2, 1): ([(50, 50, 200, 100)], None),
    (2, 2): ([(50, 50, 200, 100)], None),
}

summary = reporter.generate_batch_report(validation_data)

# Get summaries
firma_summaries = reporter.generate_summary_by_firma(summary)
seite_summaries = reporter.generate_summary_by_seite(summary)

# Print firma summaries
for firma, stats in firma_summaries.items():
    print(f"Firma {firma}: {stats['valid_seiten']}/{stats['total_seiten']} valid")
    if stats['invalid_seite_numbers']:
        print(f"  Invalid seiten: {stats['invalid_seite_numbers']}")

# Print seite summaries
for seite, stats in seite_summaries.items():
    print(f"Seite {seite}: {stats['valid_firmen']}/{stats['total_firmen']} valid")
    if stats['invalid_firma_numbers']:
        print(f"  Invalid firmen: {stats['invalid_firma_numbers']}")
```

## Report Formats

### Text Report Format

```
======================================================================
VALIDATION REPORT
======================================================================
Firma: 1, Seite: 1
Timestamp: 2025-01-10T14:30:00.123456
Status: ✗ INVALID

SUMMARY
----------------------------------------------------------------------
  total_messages: 5
  errors: 2
  warnings: 1
  info: 2
  collisions: 1
  elements_validated: 3

ERRORS (2)
----------------------------------------------------------------------
  ✗ Element 1: x2 (600.00) exceeds page width (595)
  ✗ Collision between elements 0 and 1
    Details: Overlap area: 50.00 sq pts, Overlap rect: (100, 75, 200, 100)

WARNINGS (1)
----------------------------------------------------------------------
  ⚠ Element 2: x1 (5.00) is too close to left edge (min margin: 10)

COLLISIONS (1)
----------------------------------------------------------------------
  Elements 0 and 1
    Overlap area: 50.00 sq pts
    Overlap rect: (100, 75, 200, 100)

======================================================================
```

### Batch Summary Format

```
================================================================================
BATCH VALIDATION SUMMARY
================================================================================
Timestamp: 2025-01-10T14:30:00.123456

OVERALL STATISTICS
--------------------------------------------------------------------------------
  Total combinations validated: 12
  Valid combinations: 9 (75.0%)
  Invalid combinations: 3 (25.0%)
  Total errors: 5
  Total warnings: 2
  Total collisions: 2

BREAKDOWN BY FIRMA
--------------------------------------------------------------------------------

  Firma 1:
    Seiten validated: 4
    Valid: 3/4
    Errors: 2
    Warnings: 1
    Collisions: 1
    Invalid seiten: 2

  Firma 2:
    Seiten validated: 4
    Valid: 3/4
    Errors: 1
    Warnings: 0
    Collisions: 0
    Invalid seiten: 1

BREAKDOWN BY SEITE
--------------------------------------------------------------------------------

  Seite 1:
    Firmen validated: 3
    Valid: 2/3
    Errors: 1
    Warnings: 0
    Collisions: 1
    Invalid firmen: 1

INVALID COMBINATIONS
--------------------------------------------------------------------------------
  Firma 1, Seite 2:
    Errors: 2
    Warnings: 0
    Collisions: 1

================================================================================
```

## Integration with Other Modules

The Validation Reporter integrates with:

1. **ValidationSystem**: Uses the validation system to perform actual validation
2. **YMLParser**: Accepts YMLElement objects for better error context
3. **PositionCalculator**: Can validate calculated positions
4. **YMLGenerator**: Can validate generated positions before writing

## Best Practices

1. **Always validate before writing**: Validate positions before generating YML files
2. **Use batch reports for multiple combinations**: More efficient than individual reports
3. **Save reports for documentation**: Keep validation reports for audit trail
4. **Review warnings**: Warnings may indicate suboptimal positioning
5. **Use JSON format for programmatic access**: Easier to parse and analyze
6. **Include YMLElement context**: Provides better error messages with element text

## Performance Considerations

- Batch validation is more efficient than individual validations
- JSON format is faster to generate than text format
- File I/O is the main bottleneck for large batches
- Consider using parallel processing for very large batches (48+ combinations)

## Error Handling

The reporter handles errors gracefully:

- Invalid positions are reported but don't stop validation
- Missing firma/seite numbers are handled
- File I/O errors are propagated to caller
- Empty validation data is handled correctly

## Testing

Run tests with:

```bash
pytest multi_pdf_positioning/test_validation_reporter.py -v
```

Run demo with:

```bash
python multi_pdf_positioning/demo_validation_reporter.py
```

## See Also

- [Validation System Reference](VALIDATION_SYSTEM_REFERENCE.md)
- [YML Parser Reference](YML_PARSER_REFERENCE.md)
- [Position Calculator Reference](POSITION_CALCULATOR_REFERENCE.md)
