# Troubleshooting Guide: German Formatting & Dynamic Keys

## Common Issues

### 1. Number Parsing Fails

**Problem**: `ValueError: Invalid German number format`

**Cause**: Input is not in valid German format

**Solution**:
```python
# Wrong - US format
parse_german("1,234.56")  # ❌ Fails

# Correct - German format
parse_german("1.234,56")  # ✅ Works
```

**Validation**:
```python
if validate_german(user_input):
    value = parse_german(user_input)
else:
    # Handle invalid input
    show_error("Bitte geben Sie eine gültige Zahl ein (z.B. 1.234,56)")
```

---

### 2. Incorrect Decimal Places

**Problem**: Number shows wrong decimal places

**Cause**: Default is 2 decimal places

**Solution**:
```python
# Specify decimal places
formatter.format(1234.5678, decimal_places=4)  # "1.234,5678"
formatter.format(1234.5, decimal_places=0)     # "1.234"
```

---

### 3. Currency Symbol Position

**Problem**: Currency symbol in wrong position

**Cause**: Default is suffix position

**Solution**:
```python
# Suffix (German default)
format_currency_german(1234.56)  # "1.234,56 €"

# Prefix (US style)
formatter.format_currency(1234.56, "$", "prefix")  # "$ 1.234,56"
```

---

### 4. Percentage Not Multiplied

**Problem**: 0.15 shows as "0,15 %" instead of "15,00 %"

**Cause**: `multiply_by_100` parameter

**Solution**:
```python
# Decimal input (0.15 = 15%)
format_percent_german(0.15)  # "15,00 %"

# Already percentage (15 = 15%)
format_percent_german(15, multiply_by_100=False)  # "15,00 %"
```

---

### 5. Dynamic Key Validation Fails

**Problem**: `Invalid key format`

**Cause**: Key doesn't match expected pattern

**Solution**:
```python
# Key must start with uppercase prefix (2-4 chars)
# Followed by underscore-separated components

# Valid keys
"SOL_20231116_a1b2c3d4"  # ✅
"PRJ_abc_123"            # ✅
"DAT_field_name"         # ✅

# Invalid keys
"sol_20231116_a1b2c3d4"  # ❌ Lowercase prefix
"S_20231116"             # ❌ Prefix too short
"SOLAR_123"              # ❌ Prefix too long (max 4)
```

---

### 6. Duplicate Keys Generated

**Problem**: Same key generated for different data

**Cause**: Using deterministic hash with same input

**Solution**:
```python
# Use unique identifiers in input
key1 = generate_hash_key("customer_1_name", KeyPrefix.DATA)
key2 = generate_hash_key("customer_2_name", KeyPrefix.DATA)

# Or use timestamp-based keys
mixin = DynamicKeyMixin()
key = mixin.generate_dynamic_key(KeyPrefix.DATA)  # Always unique
```

---

### 7. Key Index Lookup Returns None

**Problem**: `index.get(key)` returns None

**Cause**: Key not added or removed

**Solution**:
```python
# Check if key exists
if index.exists(key):
    obj = index.get(key)
else:
    # Key not found - add it or handle error
    print(f"Key not found: {key}")
```

---

### 8. Floating Point Precision Issues

**Problem**: Calculations produce unexpected results

**Cause**: Float precision errors

**Solution**:
```python
from decimal import Decimal

# Use Decimal for financial calculations
price1 = parse_german("1.234,56")  # Returns Decimal
price2 = parse_german("567,89")    # Returns Decimal

total = price1 + price2  # Decimal arithmetic
display = format_german(total)  # "1.802,45"
```

---

### 9. Unicode/Umlaut Issues

**Problem**: German characters (äöüß) not displaying correctly

**Cause**: Encoding issues

**Solution**:
```python
# Ensure UTF-8 encoding
text = "Größe: 10 m²"
pdf_bytes = generate_pdf_bytes_for_text(text)  # Handles UTF-8

# In API responses
return JSONResponse(
    content={"text": text},
    media_type="application/json; charset=utf-8"
)
```

---

### 10. Performance Issues with Large Datasets

**Problem**: Slow formatting of many numbers

**Cause**: Creating new formatter instances

**Solution**:
```python
# Bad - creates new instance each time
for num in numbers:
    result = GermanNumberFormatter().format(num)  # ❌ Slow

# Good - reuse instance
formatter = GermanNumberFormatter()
for num in numbers:
    result = formatter.format(num)  # ✅ Fast

# Best - use convenience functions (use singleton)
for num in numbers:
    result = format_german(num)  # ✅ Uses default_formatter
```

---

## Debug Checklist

1. ✅ Input is in correct format (German vs US)
2. ✅ Decimal places specified correctly
3. ✅ Currency symbol position is correct
4. ✅ Percentage multiplication setting is correct
5. ✅ Key prefix is uppercase (2-4 chars)
6. ✅ Key components are alphanumeric
7. ✅ Using Decimal for financial calculations
8. ✅ UTF-8 encoding for German characters
9. ✅ Reusing formatter instances for performance

## Getting Help

If issues persist:

1. Check the test files for usage examples:
   - `backend/tests/test_german_formatting_comprehensive.py`
   - `backend/tests/test_dynamic_keys_comprehensive.py`

2. Review the API documentation:
   - `backend/docs/GERMAN_FORMATTING_GUIDE.md`
   - `backend/docs/DYNAMIC_KEYS_ARCHITECTURE.md`

3. Run the test suite to verify installation:
   ```bash
   python -m pytest backend/tests/test_german_formatting_comprehensive.py -v
   python -m pytest backend/tests/test_dynamic_keys_comprehensive.py -v
   ```
