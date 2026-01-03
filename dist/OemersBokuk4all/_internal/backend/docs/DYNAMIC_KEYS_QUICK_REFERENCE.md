# Dynamic Keys Quick Reference

## Key Prefixes

| Prefix | Type | Example |
|--------|------|---------|
| `USR` | User | `USR_20231116_a1b2c3d4` |
| `PRJ` | Project | `PRJ_20231116_b2c3d4e5` |
| `CUS` | Customer | `CUS_20231116_c3d4e5f6` |
| `SOL` | Solar Calculation | `SOL_20231116_d4e5f6g7` |
| `HP` | Heat Pump | `HP_20231116_e5f6g7h8` |
| `PMX` | Price Matrix | `PMX_20231116_f6g7h8i9` |
| `PDF` | PDF Document | `PDF_20231116_g7h8i9j0` |
| `OFF` | Offer | `OFF_20231116_h8i9j0k1` |
| `DAT` | Generic Data | `DAT_20231116_i9j0k1l2` |

## Quick Generation

```python
from backend.core.dynamic_keys import (
    generate_hash_key,
    KeyPrefix,
    DynamicKeyMixin
)

# Hash-based (deterministic)
key = generate_hash_key("field_name", KeyPrefix.DATA)
# "DAT_a1b2c3d4e5f6g7h8"

# Timestamp-based (unique)
mixin = DynamicKeyMixin()
key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
# "SOL_20231116_143052_a1b2c3d4"
```

## Key Validation

```python
from backend.core.dynamic_keys import DynamicKeyMixin

# Validate format
DynamicKeyMixin.validate_key("SOL_20231116_a1b2c3d4")  # True
DynamicKeyMixin.validate_key("invalid")                # False

# Extract prefix
DynamicKeyMixin.extract_prefix("SOL_20231116_a1b2c3d4")  # "SOL"
```

## Key Index

```python
from backend.core.dynamic_keys import DynamicKeyIndex

index = DynamicKeyIndex()

# Add
index.add("PRJ_123", project_obj)

# Get
obj = index.get("PRJ_123")

# Get by prefix
projects = index.get_by_prefix("PRJ")

# Check existence
exists = index.exists("PRJ_123")  # True

# Remove
index.remove("PRJ_123")

# Statistics
stats = index.get_statistics()
```

## Common Patterns

### Form Keys
```python
def form_key(field):
    return generate_hash_key(f"form_{field}", KeyPrefix.DATA)
```

### Calculation Keys
```python
def calc_key(name):
    return generate_hash_key(f"calc_{name}", KeyPrefix.SOLAR_CALCULATION)
```

### PDF Keys
```python
def pdf_key(element):
    return generate_hash_key(f"pdf_{element}", KeyPrefix.PDF_DOCUMENT)
```

## Key Format

```
PREFIX_TIMESTAMP_UUID_[SUFFIX]
  │       │       │      │
  │       │       │      └── Optional custom suffix
  │       │       └── 8-char hex UUID
  │       └── YYYYMMDD_HHMMSS
  └── 2-4 uppercase letters
```

## Namespace Usage

```python
from backend.core.dynamic_keys import KeyNamespace

root = KeyNamespace("root")
solar = root.add_child("solar")
solar.add_key("SOL_123")

path = solar.get_full_path()  # "root.solar"
keys = solar.get_all_keys()   # ["SOL_123"]
```

## Key-Value Store

```python
from backend.core.dynamic_keys import KeyValueStore, KeyType

store = KeyValueStore()

# Set with type
store.set("price", 1234.56, key_type=KeyType.CURRENCY)

# Get
value = store.get("price")

# Search by type
keys = store.search(key_type=KeyType.CURRENCY)
```

## Performance

| Operation | Time |
|-----------|------|
| Generate key | < 0.1ms |
| Validate key | < 0.01ms |
| Index lookup | O(1) |
| 10,000 keys | < 5s |
