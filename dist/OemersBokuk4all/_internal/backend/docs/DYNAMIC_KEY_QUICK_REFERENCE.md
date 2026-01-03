# Dynamic Key System - Quick Reference

## Quick Start

```python
from backend.core.dynamic_keys import DynamicKeyMixin, DynamicKeyIndex, KeyPrefix

# Generate a key
mixin = DynamicKeyMixin()
key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)

# Index data
index = DynamicKeyIndex()
index.add(key, {"power": 10.5, "modules": 30})

# Retrieve data
data = index.get(key)
```

## Common Operations

### Generate Keys

```python
# Basic key
key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
# Result: SOL_20231116_143052_a1b2c3d4

# With custom suffix
key = mixin.generate_dynamic_key(KeyPrefix.PROJECT, custom_suffix="berlin")
# Result: PRJ_20231116_143052_a1b2c3d4_berlin

# Hash-based (deterministic)
key = generate_hash_key("user@example.com", KeyPrefix.USER)
# Result: USR_b4c9a289323b21a0
```

### Index Operations

```python
# Add
index.add(key, data, metadata={"user": "john"})

# Get
data = index.get(key)

# Check existence
if index.exists(key):
    print("Key exists")

# Remove
index.remove(key)

# Count
total = index.count()
solar_count = index.count_by_prefix("SOL")
```

### Query by Prefix

```python
# Get all solar calculations
solar_data = index.get_by_prefix("SOL")

# Get just the keys
solar_keys = index.get_keys_by_prefix("SOL")

# Get all prefixes
all_prefixes = index.get_all_prefixes()
```

### Validation

```python
validator = DynamicKeyValidator()

# Validate
is_valid, error = validator.validate(key)
if not is_valid:
    print(f"Error: {error}")

# Configure rules
validator.set_rule('min_length', 15)
validator.set_rule('allow_custom_prefix', True)
```

### Key Parsing

```python
# Extract prefix
prefix = DynamicKeyMixin.extract_prefix(key)

# Extract all components
components = DynamicKeyMixin.extract_components(key)
print(components['prefix'])  # SOL
print(components['date'])    # 20231116
print(components['uuid'])    # a1b2c3d4
```

## Key Prefixes

| Prefix | Type | Example |
|--------|------|---------|
| `SOL` | Solar Calculation | `SOL_20231116_143052_a1b2c3d4` |
| `HP` | Heat Pump | `HP_20231116_143052_a1b2c3d4` |
| `PRJ` | Project | `PRJ_20231116_143052_a1b2c3d4` |
| `USR` | User | `USR_20231116_143052_a1b2c3d4` |
| `CUS` | Customer | `CUS_20231116_143052_a1b2c3d4` |
| `PDF` | PDF Document | `PDF_20231116_143052_a1b2c3d4` |
| `OFF` | Offer | `OFF_20231116_143052_a1b2c3d4` |
| `DAT` | Generic Data | `DAT_20231116_143052_a1b2c3d4` |

See full list in documentation.

## Key Format

```
PREFIX_TIMESTAMP_UUID_ID_SUFFIX
```

- **PREFIX**: 2-4 letter code (e.g., SOL, HP, PRJ)
- **TIMESTAMP**: YYYYMMDD_HHMMSS format
- **UUID**: 8-character hexadecimal
- **ID**: Optional entity ID
- **SUFFIX**: Optional custom suffix

## Performance

- **Add**: ~250,000 ops/sec
- **Lookup**: O(1), < 0.0001 seconds
- **Prefix Query**: O(n) where n = keys with prefix
- **Memory**: ~100 bytes per key

## Best Practices

1. **Use appropriate prefixes** for easy identification
2. **Index strategically** - only what needs fast lookup
3. **Clean up** - remove objects when no longer needed
4. **Validate external keys** - always validate keys from outside
5. **Use metadata** - track creation time, user, version

## Common Patterns

### Service with Index

```python
class SolarService:
    def __init__(self):
        self.index = DynamicKeyIndex()
    
    def create_calculation(self, data):
        calc = SolarCalculation(data)
        self.index.add(calc.key, calc)
        return calc.key
    
    def get_calculation(self, key):
        return self.index.get(key)
```

### Model with Auto-Key

```python
class SolarCalculation(DynamicKeyMixin):
    def __init__(self, power, modules):
        super().__init__()
        self.power = power
        self.modules = modules
        self.key = self.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
```

### Caching

```python
cache = DynamicKeyIndex()

def get_or_calculate(params):
    cache_key = generate_hash_key(str(params), KeyPrefix.TEMP)
    
    if cache.exists(cache_key):
        return cache.get(cache_key)
    
    result = expensive_calculation(params)
    cache.add(cache_key, result)
    return result
```

## Error Handling

```python
# Handle invalid keys
try:
    mixin.set_dynamic_key("invalid", validate=True)
except ValueError as e:
    print(f"Invalid key: {e}")

# Handle missing keys
if not index.exists(key):
    print("Key not found")
else:
    data = index.get(key)

# Validate before use
is_valid, error = validator.validate(key)
if not is_valid:
    print(f"Validation failed: {error}")
```

## Testing

```bash
# Run standalone tests
python backend/test_dynamic_keys_standalone.py

# Run pytest tests
pytest backend/tests/test_dynamic_keys.py -v

# Run demo
python backend/demo_dynamic_keys.py
```

## Documentation

- **Full Guide**: `backend/docs/DYNAMIC_KEY_SYSTEM.md`
- **Examples**: `backend/examples/dynamic_key_examples.py`
- **Demo**: `backend/demo_dynamic_keys.py`
- **Tests**: `backend/tests/test_dynamic_keys.py`

## Support

For issues or questions:
1. Check full documentation
2. Review examples and demo
3. Run tests to verify setup
4. Contact development team
