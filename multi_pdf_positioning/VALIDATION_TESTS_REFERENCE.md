# Validation Tests Quick Reference

## Overview

Comprehensive validation test suite for Multi-PDF Positioning System that validates all generated YML files.

## Quick Start

```bash
# Run all validation tests
python multi_pdf_positioning/test_validation_complete.py

# Specify custom directories
python multi_pdf_positioning/test_validation_complete.py \
    --coords-dir coords_multi \
    --backup-dir coords_multi_backup

# Don't save JSON report
python multi_pdf_positioning/test_validation_complete.py --no-save
```

## What Gets Validated

### 1. Positions Within Bounds ✓
- All X coordinates between 0 and 595 (page width)
- All Y coordinates between 0 and 842 (page height)
- Minimum margin of 10 points from edges
- Valid element dimensions (width > 0, height > 0)

### 2. No Overlapping Elements ✓
- Detects collisions between text elements
- Enforces minimum spacing of 5 points
- Reports overlap area in square points
- Lists all colliding element pairs

### 3. Attributes Preserved ✓
- Text content unchanged
- Font unchanged
- Font size unchanged
- Color unchanged
- Only positions modified

### 4. Valid YML Format ✓
- File can be parsed successfully
- All required attributes present
- No parsing errors
- Valid element structure

## Output Format

### Console Output

```
======================================================================
COMPREHENSIVE VALIDATION TEST SUITE
======================================================================

Found 64 YML files to validate

----------------------------------------------------------------------
Running validation tests...
----------------------------------------------------------------------

Validating: seite1_f1.yml
  ✗ FAILED
    - Found 30 collision(s)
    - Elements 0 and 1 overlap (1810.00 sq pts)

Validating: seite7_f1.yml
  ✓ PASSED

======================================================================
VALIDATION SUMMARY
======================================================================

Files Tested: 64
  ✓ Passed: 8
  ✗ Failed: 56

Elements Validated: 3,016
Total Errors: 480
Total Warnings: 272
Total Collisions: 3,696

Pass Rate: 12.5%
```

### JSON Report

Saved to `multi_pdf_positioning/validation_report.json`:

```json
{
  "summary": {
    "total_files": 64,
    "passed": 8,
    "failed": 56,
    "total_elements": 3016,
    "total_errors": 480,
    "total_warnings": 272,
    "total_collisions": 3696
  },
  "test_results": {
    "seite1_f1.yml": {
      "file": "seite1_f1.yml",
      "passed": false,
      "tests": {
        "bounds": true,
        "overlaps": false,
        "format_valid": true
      },
      "errors": [...],
      "warnings": [...],
      "element_count": 28,
      "collision_count": 30
    }
  }
}
```

## Python API

### Run All Tests

```python
from multi_pdf_positioning.test_validation_complete import run_validation_tests

# Run validation
success = run_validation_tests(
    coords_dir="coords_multi",
    backup_dir="coords_multi_backup",
    save_report=True
)

if success:
    print("✓ All tests passed!")
else:
    print("✗ Some tests failed")
```

### Use Test Suite Directly

```python
from multi_pdf_positioning.test_validation_complete import ValidationTestSuite
from pathlib import Path

# Create suite
suite = ValidationTestSuite(
    coords_dir="coords_multi",
    backup_dir="coords_multi_backup"
)

# Validate all files
report = suite.validate_all_files()

# Access results
print(f"Pass rate: {report['summary']['passed'] / report['summary']['total_files'] * 100:.1f}%")

# Get failed files
failed = [name for name, result in report['test_results'].items() if not result['passed']]
print(f"Failed files: {len(failed)}")
```

### Validate Single File

```python
# Validate specific file
yml_file = Path("coords_multi/seite7_f1.yml")
original_file = Path("coords_multi_backup/latest/seite7_f1.yml")

result = suite.validate_single_file(yml_file, original_file)

if result["passed"]:
    print(f"✓ {yml_file.name} passed")
else:
    print(f"✗ {yml_file.name} failed:")
    for error in result["errors"]:
        print(f"  - {error}")
```

## Test Categories

### Boundary Tests

```python
# Test positions within bounds
passed, errors = suite.test_positions_within_bounds(yml_file)

# Checks:
# - x1 >= 0, y1 >= 0
# - x2 <= 595, y2 <= 842
# - x1 >= 10, y1 >= 10 (margin warning)
# - x2 <= 585, y2 <= 832 (margin warning)
# - x2 > x1, y2 > y1 (valid dimensions)
```

### Collision Tests

```python
# Test for overlaps
passed, errors = suite.test_no_overlaps(yml_file)

# Checks:
# - No elements overlap (with 5pt spacing)
# - Reports overlap area
# - Lists all collision pairs
```

### Attribute Preservation Tests

```python
# Test only positions changed
passed, errors = suite.test_only_positions_changed(yml_file, original_file)

# Checks:
# - Text unchanged
# - Font unchanged
# - Font size unchanged
# - Color unchanged
# - Element count unchanged
```

### Format Tests

```python
# Test YML format valid
passed, errors = suite.test_yml_format_valid(yml_file)

# Checks:
# - File can be parsed
# - All attributes present
# - Valid structure
# - No parsing errors
```

## Common Issues

### Issue: Collisions Detected

**Problem**: Elements overlap or are too close together

**Solution**:
```python
# Use collision resolution
from multi_pdf_positioning.validation_system import ValidationSystem

validator = ValidationSystem()
collisions = validator.detect_collisions(positions)
adjusted = validator.resolve_collisions(positions, collisions)
```

### Issue: Positions Out of Bounds

**Problem**: Elements exceed page dimensions

**Solution**:
```python
# Use ensure_bounds
from multi_pdf_positioning.position_calculator import PositionCalculator

calculator = PositionCalculator()
adjusted_position = calculator.ensure_bounds(position)
```

### Issue: Attributes Changed

**Problem**: Non-position attributes were modified

**Solution**:
- Ensure YML generator only updates positions
- Verify format preservation is working
- Check that original elements are used as base

## Integration with Workflow

### After Generating YML Files

```bash
# 1. Generate YML files
python multi_pdf_positioning/main_workflow.py --generate

# 2. Run validation
python multi_pdf_positioning/test_validation_complete.py

# 3. Check report
cat multi_pdf_positioning/validation_report.json
```

### In CI/CD Pipeline

```bash
# Run validation and exit with error code if failed
python multi_pdf_positioning/test_validation_complete.py
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Validation failed!"
    exit 1
fi
```

### Automated Testing

```python
import pytest
from multi_pdf_positioning.test_validation_complete import run_validation_tests

def test_all_yml_files_valid():
    """Test that all generated YML files pass validation."""
    success = run_validation_tests(save_report=False)
    assert success, "Some YML files failed validation"
```

## Performance

- **Speed**: ~1-2 seconds per file
- **Total Time**: ~2-3 minutes for all 64 files
- **Memory**: Minimal (processes one file at a time)

## Exit Codes

- `0`: All tests passed
- `1`: Some tests failed

## Requirements Covered

✅ Task 11.3: Validierungs-Tests
- ✅ Validiere alle generierten YML-Dateien
- ✅ Prüfe, dass keine Positionen außerhalb der Grenzen liegen
- ✅ Prüfe, dass keine Überlappungen existieren
- ✅ Vergleiche generierte YML mit Original (nur Positionen geändert)

## See Also

- `validation_system.py` - Core validation logic
- `yml_parser.py` - YML file parsing
- `yml_generator.py` - YML file generation
- `position_calculator.py` - Position calculation
- `TASK_11_3_COMPLETE.md` - Detailed implementation documentation
