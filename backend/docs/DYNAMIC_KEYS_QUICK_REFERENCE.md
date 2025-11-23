# Dynamic Keys System - Quick Reference

## Quick Start

```python
from backend.services.dynamic_key_service import get_dynamic_key_service
from backend.core.dynamic_keys import KeyPrefix, KeyType

service = get_dynamic_key_service()
```

## Key Generation

```python
# Generate standard key
key = service.generate_key(KeyPrefix.SOLAR_CALCULATION)
# Result: SOL_20231116_143052_a1b2c3d4

# Generate hash key
hash_key = service.generate_hash_key_from_data("data", KeyPrefix.DATA)
# Result: DAT_f4a3b2c1d0e9f8g7
```

## Store & Retrieve

```python
# Set value
service.set_value("key", "value", key_type=KeyType.STRING)

# Get value
value = service.get_value("key")

# Delete value
service.delete_value("key")

# Check existence
exists = service.value_exists("key")
```

## Namespaces

```python
# Create namespace
service.create_namespace("root.solar.calculations")

# Set value in namespace
service.set_value("key", "value", namespace="root.solar")

# Get keys from namespace
keys = service.get_namespace_keys("root.solar", recursive=True)
```

## Search & Filter

```python
# Search by pattern
keys = service.search_keys(pattern="solar_.*")

# Filter by prefix
keys = service.filter_by_prefix(KeyPrefix.SOLAR_CALCULATION)

# Filter by type
keys = service.filter_by_type(KeyType.FLOAT)

# Filter by namespace
keys = service.filter_by_namespace("root.solar")
```

## Usage Tracking

```python
# Get statistics
stats = service.get_usage_statistics("key")

# Most accessed
most = service.get_most_accessed_keys(limit=10)

# Recently accessed
recent = service.get_recently_accessed_keys(limit=10)

# Unused keys
unused = service.get_unused_keys()
```

## Bulk Operations

```python
# Bulk set
service.bulk_set({"key1": "val1", "key2": "val2"})

# Bulk get
values = service.bulk_get(["key1", "key2"])

# Bulk delete
count = service.bulk_delete(["key1", "key2"])
```

## Export & Import

```python
# Export
data = service.export_configuration()

# Import
service.import_configuration(data)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/dynamic-keys/generate` | Generate key |
| POST | `/dynamic-keys/set` | Store value |
| GET | `/dynamic-keys/get/{key}` | Retrieve value |
| DELETE | `/dynamic-keys/delete/{key}` | Delete value |
| POST | `/dynamic-keys/search` | Search keys |
| GET | `/dynamic-keys/filter/prefix/{prefix}` | Filter by prefix |
| GET | `/dynamic-keys/usage/statistics` | Get usage stats |
| POST | `/dynamic-keys/bulk/set` | Bulk set |
| GET | `/dynamic-keys/export` | Export config |
| POST | `/dynamic-keys/import` | Import config |

## Key Prefixes

| Prefix | Type | Example |
|--------|------|---------|
| SOL | Solar Calculation | SOL_20231116_a1b2c3d4 |
| HP | Heat Pump | HP_20231116_e5f6g7h8 |
| PMX | Price Matrix | PMX_20231116_i9j0k1l2 |
| PDF | PDF Document | PDF_20231116_m3n4o5p6 |
| PRJ | Project | PRJ_20231116_q7r8s9t0 |
| CUS | Customer | CUS_20231116_u1v2w3x4 |

## Key Types

| Type | Validation | Example |
|------|------------|---------|
| STRING | Text | "Hello" |
| INTEGER | Whole number | 42 |
| FLOAT | Decimal | 3.14 |
| BOOLEAN | True/False | true |
| CURRENCY | Money (≥0) | 99.99 |
| PERCENTAGE | 0-100 | 85.5 |
| JSON | Object/Array | {"key": "value"} |
| EMAIL | Email address | "user@example.com" |

## Common Patterns

### Store Calculation Result

```python
key = service.generate_key(KeyPrefix.SOLAR_CALCULATION)
service.set_value(
    key=f"{key}_result",
    value={"size": 10.5, "modules": 30},
    key_type=KeyType.JSON,
    namespace="root.solar.calculations",
    metadata={"date": "2023-11-16"}
)
```

### Search Recent Calculations

```python
keys = service.search_keys(
    pattern="SOL_.*_result",
    namespace="root.solar.calculations",
    key_type=KeyType.JSON
)
```

### Track Most Used Features

```python
most_accessed = service.get_most_accessed_keys(limit=10)
for key, count in most_accessed:
    print(f"{key}: {count} accesses")
```

### Clean Up Old Data

```python
# Get unused keys
unused = service.get_unused_keys()

# Delete them
service.bulk_delete(unused)
```

## Error Handling

```python
try:
    service.set_value("key", "value", key_type=KeyType.INTEGER)
except ValueError as e:
    print(f"Type validation failed: {e}")

try:
    value = service.get_value("nonexistent_key")
    if value is None:
        print("Key not found")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. **Use bulk operations** for multiple keys
2. **Enable caching** for frequently accessed values
3. **Use namespaces** to organize related keys
4. **Clean up unused keys** periodically
5. **Use appropriate types** for validation
6. **Track usage** to identify optimization opportunities

## Requirements

- **4.1**: API-First design
- **6.1**: Modular code extraction
- **14.4**: Dynamic key generation
- **14.7**: Key-value storage
