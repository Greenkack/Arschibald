# German Formatting Quick Reference

## Format Examples

| Input | Output |
|-------|--------|
| `1234.56` | `1.234,56` |
| `1234567.89` | `1.234.567,89` |
| `0.5` | `0,50` |
| `-999.99` | `-999,99` |
| `1234.56 €` | `1.234,56 €` |
| `15%` | `15,00 %` |

## Quick Functions

```python
from backend.core.german_formatter import (
    format_german,
    parse_german,
    format_currency_german,
    format_percent_german,
    validate_german
)

# Format
format_german(1234.56)           # "1.234,56"
format_german(1234.5678, 4)      # "1.234,5678"

# Parse
parse_german("1.234,56")         # Decimal('1234.56')

# Currency
format_currency_german(1234.56)  # "1.234,56 €"

# Percentage
format_percent_german(0.15)      # "15,00 %"

# Validate
validate_german("1.234,56")      # True
```

## Class Usage

```python
from backend.core.german_formatter import GermanNumberFormatter

formatter = GermanNumberFormatter()

# Format
formatter.format(1234.56)                    # "1.234,56"
formatter.format(1234.56, decimal_places=4)  # "1.234,5600"

# Parse
formatter.parse("1.234,56")                  # Decimal('1234.56')

# Currency
formatter.format_currency(1234.56)           # "1.234,56 €"
formatter.format_currency(1234.56, "$")      # "1.234,56 $"

# Percentage
formatter.format_percent(0.15)               # "15,00 %"

# Validate
formatter.validate("1.234,56")               # True
```

## Conversion Helpers

```python
formatter = GermanNumberFormatter()

# To float
formatter.to_float("1.234,56")  # 1234.56

# To int
formatter.to_int("1.234,56")    # 1235 (rounded)
```

## Common Patterns

### Price Display
```python
def display_price(amount):
    return format_currency_german(amount)
```

### Form Processing
```python
def process_input(german_value):
    if not validate_german(german_value):
        raise ValueError("Invalid format")
    return parse_german(german_value)
```

### Calculation Workflow
```python
# Input -> Calculate -> Display
value = parse_german("1.234,56")
result = value * 2
display = format_german(result)  # "2.469,12"
```

## Error Handling

```python
try:
    value = parse_german("invalid")
except ValueError as e:
    print(f"Error: {e}")
```

## Separators

| Type | Character |
|------|-----------|
| Thousand | `.` (dot) |
| Decimal | `,` (comma) |
| Currency | ` €` (space + symbol) |
| Percent | ` %` (space + symbol) |
