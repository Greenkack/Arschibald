# German Number Formatting Guide

## Overview

This guide covers the German number formatting system used throughout the application. German format uses:
- **Dot (.)** as thousand separator
- **Comma (,)** as decimal separator
- **2 decimal places** for currency and percentages

## Quick Reference

| Standard Format | German Format |
|-----------------|---------------|
| 1234.56 | 1.234,56 |
| 1234567.89 | 1.234.567,89 |
| 0.5 | 0,50 |
| -999.99 | -999,99 |

## GermanNumberFormatter API

### Basic Usage

```python
from backend.core.german_formatter import GermanNumberFormatter

# Create formatter instance
formatter = GermanNumberFormatter()

# Format numbers
formatter.format(1234.56)        # "1.234,56"
formatter.format(1234567.89)     # "1.234.567,89"
formatter.format(0.5)            # "0,50"
formatter.format(-999.99)        # "-999,99"
```

### Parsing German Numbers

```python
from backend.core.german_formatter import GermanNumberFormatter

formatter = GermanNumberFormatter()

# Parse German format to Decimal
formatter.parse("1.234,56")      # Decimal('1234.56')
formatter.parse("1.234.567,89")  # Decimal('1234567.89')
formatter.parse("-999,99")       # Decimal('-999.99')
```

### Currency Formatting

```python
from backend.core.german_formatter import GermanNumberFormatter

formatter = GermanNumberFormatter()

# Format as Euro (default)
formatter.format_currency(1234.56)                    # "1.234,56 €"

# Format with different currency
formatter.format_currency(1234.56, "$", "prefix")     # "$ 1.234,56"
formatter.format_currency(1234.56, "CHF")             # "1.234,56 CHF"
```

### Percentage Formatting

```python
from backend.core.german_formatter import GermanNumberFormatter

formatter = GermanNumberFormatter()

# Format decimal as percentage (multiplies by 100)
formatter.format_percent(0.15)                        # "15,00 %"
formatter.format_percent(0.5)                         # "50,00 %"

# Format without multiplication
formatter.format_percent(15, multiply_by_100=False)   # "15,00 %"
```

### Custom Decimal Places

```python
from backend.core.german_formatter import GermanNumberFormatter

formatter = GermanNumberFormatter()

# Specify decimal places
formatter.format(1234.5678, decimal_places=4)  # "1.234,5678"
formatter.format(1234.5, decimal_places=0)     # "1.234"
formatter.format(1234.5, decimal_places=3)     # "1.234,500"
```

### Validation

```python
from backend.core.german_formatter import GermanNumberFormatter

formatter = GermanNumberFormatter()

# Validate German number format
formatter.validate("1.234,56")     # True
formatter.validate("1,234.56")     # False (US format)
formatter.validate("abc")          # False
```

## Convenience Functions

For quick one-off operations, use the convenience functions:

```python
from backend.core.german_formatter import (
    format_german,
    parse_german,
    format_currency_german,
    format_percent_german,
    validate_german
)

# Quick formatting
format_german(1234.56)              # "1.234,56"
format_german(1234.5678, 4)         # "1.234,5678"

# Quick parsing
parse_german("1.234,56")            # Decimal('1234.56')

# Quick currency
format_currency_german(1234.56)     # "1.234,56 €"

# Quick percentage
format_percent_german(0.15)         # "15,00 %"

# Quick validation
validate_german("1.234,56")         # True
```

## Bidirectional Conversion

The formatter supports seamless conversion between display format and calculation values:

```python
from backend.core.german_formatter import GermanNumberFormatter

formatter = GermanNumberFormatter()

# Display -> Calculation
user_input = "1.234,56"
calculation_value = formatter.parse(user_input)  # Decimal('1234.56')

# Perform calculation
result = calculation_value * 2  # Decimal('2469.12')

# Calculation -> Display
display_value = formatter.format(result)  # "2.469,12"
```

## Integration with Forms

### React/TypeScript Frontend

```typescript
// Use GermanNumberInput component
import { GermanNumberInput } from '@/components/GermanNumberInput';

<GermanNumberInput
  value={price}
  onChange={(value) => setPrice(value)}
  decimalPlaces={2}
  suffix=" €"
/>
```

### Backend API

```python
from fastapi import APIRouter
from backend.core.german_formatter import format_german, parse_german

router = APIRouter()

@router.post("/calculate")
async def calculate(data: CalculationRequest):
    # Parse German input
    amount = parse_german(data.amount_german)
    
    # Perform calculation
    result = amount * data.factor
    
    # Return German formatted result
    return {
        "result": float(result),
        "result_formatted": format_german(result)
    }
```

## Error Handling

```python
from backend.core.german_formatter import GermanNumberFormatter

formatter = GermanNumberFormatter()

try:
    value = formatter.parse("invalid")
except ValueError as e:
    print(f"Invalid format: {e}")
    # Handle error appropriately
```

## Performance Considerations

- The formatter is optimized for high-volume operations
- 10,000+ format/parse operations complete in under 2 seconds
- Use the singleton `default_formatter` for best performance
- Avoid creating new formatter instances in loops

## Best Practices

1. **Always validate user input** before parsing
2. **Use Decimal** for financial calculations to avoid floating-point errors
3. **Store values in standard format** in the database
4. **Format for display only** at the presentation layer
5. **Use consistent decimal places** throughout the application

## Common Patterns

### Price Display

```python
def display_price(amount: float) -> str:
    return format_currency_german(amount)

# Usage
display_price(1234.56)  # "1.234,56 €"
```

### Percentage Display

```python
def display_percentage(value: float) -> str:
    return format_percent_german(value)

# Usage (value is 0.15 for 15%)
display_percentage(0.15)  # "15,00 %"
```

### Form Input Processing

```python
def process_form_input(german_value: str) -> Decimal:
    if not validate_german(german_value):
        raise ValueError("Invalid number format")
    return parse_german(german_value)
```
