# Dynamic Keys System - Complete Guide

## Overview

The Dynamic Keys System provides a comprehensive infrastructure for generating, managing, and tracking unique keys throughout the application. It includes key-value configuration storage, type validation, namespacing, search capabilities, and usage tracking.

## Features

### 1. Dynamic Key Generation
- Unique key generation with customizable components
- Support for timestamps, UUIDs, and custom suffixes
- Hash-based key generation from data
- Prefix-based categorization

### 2. Key-Value Configuration Storage
- Typed key-value storage with validation
- Support for multiple data types (string, integer, float, boolean, date, JSON, etc.)
- Metadata attachment to keys
- Export/import functionality

### 3. Key Validation and Typing
- Automatic type validation
- Support for 12 different key types
- Custom validation rules
- Type safety enforcement

### 4. Key Namespacing
- Hierarchical namespace organization
- Parent-child namespace relationships
- Namespace-scoped operations
- Recursive key retrieval

### 5. Key Search and Filtering
- Pattern-based search (regex)
- Filter by prefix, type, namespace
- Metadata-based filtering
- Combined filter criteria

### 6. Usage Tracking
- Access count tracking
- First and last access timestamps
- Access history with configurable size
- Most/least accessed key analytics
- Unused key detection

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Dynamic Keys System                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Key          │  │ Key-Value    │  │ Usage        │      │
│  │ Generation   │  │ Store        │  │ Tracker      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │  Dynamic Key    │                        │
│                   │  Service        │                        │
│                   └────────┬────────┘                        │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │  REST API       │                        │
│                   │  Endpoints      │                        │
│                   └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Key Prefixes

The system supports the following key prefixes:

| Prefix | Description | Example |
|--------|-------------|---------|
| USR | User | USR_20231116_a1b2c3d4 |
| PRJ | Project | PRJ_20231116_e5f6g7h8 |
| CUS | Customer | CUS_20231116_i9j0k1l2 |
| SOL | Solar Calculation | SOL_20231116_m3n4o5p6 |
| MOD | Solar Module | MOD_20231116_q7r8s9t0 |
| INV | Solar Inverter | INV_20231116_u1v2w3x4 |
| BAT | Solar Battery | BAT_20231116_y5z6a7b8 |
| HP | Heat Pump Calculation | HP_20231116_c9d0e1f2 |
| HPP | Heat Pump Product | HPP_20231116_g3h4i5j6 |
| PMX | Price Matrix | PMX_20231116_k7l8m9n0 |
| PRC | Price Calculation | PRC_20231116_o1p2q3r4 |
| PRD | Product | PRD_20231116_s5t6u7v8 |
| PDF | PDF Document | PDF_20231116_w9x0y1z2 |
| TPL | PDF Template | TPL_20231116_a3b4c5d6 |
| VIS | 3D Visualization | VIS_20231116_e7f8g9h0 |
| PLC | Module Placement | PLC_20231116_i1j2k3l4 |
| OFF | Offer | OFF_20231116_m5n6o7p8 |
| TSK | Task | TSK_20231116_q9r0s1t2 |
| NOT | Note | NOT_20231116_u3v4w5x6 |
| EML | Email | EML_20231116_y7z8a9b0 |
| CNT | Contract | CNT_20231116_c1d2e3f4 |
| CFG | Configuration | CFG_20231116_g5h6i7j8 |
| SET | Setting | SET_20231116_k9l0m1n2 |
| IMG | Image | IMG_20231116_o3p4q5r6 |
| DOC | Document | DOC_20231116_s7t8u9v0 |
| CHT | Chart | CHT_20231116_w1x2y3z4 |
| DAT | Generic Data | DAT_20231116_a5b6c7d8 |
| TMP | Temporary | TMP_20231116_e9f0g1h2 |

## Key Types

The system supports the following key types for validation:

| Type | Description | Example |
|------|-------------|---------|
| STRING | Text string | "Hello World" |
| INTEGER | Whole number | 42 |
| FLOAT | Decimal number | 3.14159 |
| BOOLEAN | True/False | true |
| DATE | Date only | "2023-11-16" |
| DATETIME | Date and time | "2023-11-16T14:30:52" |
| JSON | JSON object/array | {"key": "value"} |
| BINARY | Binary data | b'\x00\x01\x02' |
| CURRENCY | Monetary value (≥0) | 99.99 |
| PERCENTAGE | Percentage (0-100) | 85.5 |
| EMAIL | Email address | "user@example.com" |
| URL | Web URL | "https://example.com" |

## Usage Examples

### Python Backend

#### 1. Generate a Dynamic Key

```python
from backend.services.dynamic_key_service import get_dynamic_key_service
from backend.core.dynamic_keys import KeyPrefix

service = get_dynamic_key_service()

# Generate a key with all components
key = service.generate_key(
    prefix=KeyPrefix.SOLAR_CALCULATION,
    include_timestamp=True,
    include_uuid=True,
    custom_suffix="test"
)
print(key)  # SOL_20231116_143052_a1b2c3d4_test

# Generate a hash-based key
hash_key = service.generate_hash_key_from_data(
    data="my_unique_data",
    prefix=KeyPrefix.DATA
)
print(hash_key)  # DAT_f4a3b2c1d0e9f8g7
```

#### 2. Store and Retrieve Values

```python
from backend.core.dynamic_keys import KeyType

# Store a value with type validation
service.set_value(
    key="solar_system_size",
    value=10.5,
    key_type=KeyType.FLOAT,
    namespace="root.solar.calculations",
    metadata={"unit": "kWp", "description": "System size"}
)

# Retrieve the value
value = service.get_value("solar_system_size")
print(value)  # 10.5

# Get metadata
metadata = service.get_key_metadata("solar_system_size")
print(metadata)  # {"unit": "kWp", "description": "System size"}
```

#### 3. Use Namespaces

```python
# Create a namespace hierarchy
service.create_namespace("root.solar.calculations.residential")

# Add keys to namespace
service.set_value(
    key="system_1",
    value={"size": 10.5, "modules": 30},
    namespace="root.solar.calculations.residential"
)

# Get all keys in namespace
keys = service.get_namespace_keys("root.solar.calculations", recursive=True)
print(keys)  # ['system_1', ...]

# List all namespaces
namespaces = service.list_namespaces()
print(namespaces)
```

#### 4. Search and Filter Keys

```python
# Search by pattern
keys = service.search_keys(pattern="solar_.*")

# Filter by prefix
keys = service.filter_by_prefix(KeyPrefix.SOLAR_CALCULATION)

# Filter by type
keys = service.filter_by_type(KeyType.FLOAT)

# Filter by namespace
keys = service.filter_by_namespace("root.solar", recursive=True)

# Combined search
keys = service.search_keys(
    pattern="system_.*",
    namespace="root.solar",
    key_type=KeyType.JSON,
    metadata_filter={"unit": "kWp"}
)
```

#### 5. Track Usage

```python
# Access tracking is automatic when track_usage=True (default)
service.get_value("solar_system_size", track_usage=True)

# Get usage statistics for a specific key
stats = service.get_usage_statistics("solar_system_size")
print(stats)
# {
#     'key': 'solar_system_size',
#     'accessed': True,
#     'access_count': 5,
#     'first_access': '2023-11-16T14:30:52',
#     'last_access': '2023-11-16T15:45:30',
#     'duration_seconds': 4478,
#     'average_frequency': 4.02
# }

# Get most accessed keys
most_accessed = service.get_most_accessed_keys(limit=10)
print(most_accessed)  # [('key1', 100), ('key2', 75), ...]

# Get recently accessed keys
recent = service.get_recently_accessed_keys(limit=10)
print(recent)  # [('key3', datetime(...)), ...]

# Get unused keys
unused = service.get_unused_keys()
print(unused)  # ['key4', 'key5', ...]
```

#### 6. Bulk Operations

```python
# Bulk set
items = {
    "key1": "value1",
    "key2": 42,
    "key3": 3.14
}
service.bulk_set(items, namespace="root.test")

# Bulk get
values = service.bulk_get(["key1", "key2", "key3"])
print(values)  # {'key1': 'value1', 'key2': 42, 'key3': 3.14}

# Bulk delete
deleted_count = service.bulk_delete(["key1", "key2"])
print(deleted_count)  # 2
```

#### 7. Export and Import

```python
# Export configuration
data = service.export_configuration(namespace="root.solar")

# Save to file
import json
with open("config.json", "w") as f:
    json.dump(data, f, indent=2)

# Import configuration
with open("config.json", "r") as f:
    data = json.load(f)

service.import_configuration(data, namespace="root.solar")
```

### REST API

#### 1. Generate a Key

```bash
# POST /api/v1/dynamic-keys/generate
curl -X POST http://localhost:8000/api/v1/dynamic-keys/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prefix": "SOL",
    "include_timestamp": true,
    "include_uuid": true,
    "custom_suffix": "test"
  }'

# Response:
# {
#   "key": "SOL_20231116_143052_a1b2c3d4_test",
#   "prefix": "SOL",
#   "created_at": "2023-11-16T14:30:52"
# }
```

#### 2. Store a Value

```bash
# POST /api/v1/dynamic-keys/set
curl -X POST http://localhost:8000/api/v1/dynamic-keys/set \
  -H "Content-Type: application/json" \
  -d '{
    "key": "solar_system_size",
    "value": 10.5,
    "key_type": "float",
    "namespace": "root.solar.calculations",
    "metadata": {"unit": "kWp"}
  }'

# Response:
# {
#   "success": true,
#   "key": "solar_system_size"
# }
```

#### 3. Retrieve a Value

```bash
# GET /api/v1/dynamic-keys/get/{key}
curl http://localhost:8000/api/v1/dynamic-keys/get/solar_system_size

# Response:
# {
#   "key": "solar_system_size",
#   "value": 10.5,
#   "key_type": "float",
#   "metadata": {"unit": "kWp"},
#   "exists": true
# }
```

#### 4. Search Keys

```bash
# POST /api/v1/dynamic-keys/search
curl -X POST http://localhost:8000/api/v1/dynamic-keys/search \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "solar_.*",
    "namespace": "root.solar",
    "key_type": "float"
  }'

# Response:
# {
#   "keys": ["solar_system_size", "solar_module_count"],
#   "count": 2
# }
```

#### 5. Get Usage Statistics

```bash
# GET /api/v1/dynamic-keys/usage/statistics?key=solar_system_size
curl http://localhost:8000/api/v1/dynamic-keys/usage/statistics?key=solar_system_size

# Response:
# {
#   "statistics": {
#     "key": "solar_system_size",
#     "accessed": true,
#     "access_count": 5,
#     "first_access": "2023-11-16T14:30:52",
#     "last_access": "2023-11-16T15:45:30",
#     "duration_seconds": 4478,
#     "average_frequency": 4.02
#   }
# }
```

## Best Practices

### 1. Key Naming Conventions

- Use descriptive names: `solar_system_size` instead of `size`
- Use snake_case for consistency
- Include context in the name: `residential_solar_system_size`
- Avoid special characters except underscore

### 2. Namespace Organization

- Create logical hierarchies: `root.solar.calculations.residential`
- Keep namespace depth reasonable (3-5 levels)
- Use consistent naming across namespaces
- Document namespace structure

### 3. Type Validation

- Always specify key_type for important data
- Use appropriate types (CURRENCY for money, PERCENTAGE for percentages)
- Validate data before storing
- Handle type validation errors gracefully

### 4. Metadata Usage

- Store relevant context in metadata
- Include units, descriptions, versions
- Use metadata for filtering and search
- Keep metadata lightweight

### 5. Usage Tracking

- Enable tracking for important keys
- Regularly review usage statistics
- Identify and remove unused keys
- Monitor access patterns for optimization

### 6. Performance

- Use bulk operations for multiple keys
- Cache frequently accessed values
- Use namespaces to organize related keys
- Clean up unused keys periodically

## Integration with Other Systems

### Solar Calculator Integration

```python
# Generate key for solar calculation
calc_key = service.generate_key(KeyPrefix.SOLAR_CALCULATION)

# Store calculation results
service.set_value(
    key=f"{calc_key}_results",
    value={
        "system_size": 10.5,
        "module_count": 30,
        "annual_production": 12000
    },
    key_type=KeyType.JSON,
    namespace="root.solar.calculations",
    metadata={
        "calculation_date": "2023-11-16",
        "customer_id": "CUS_123"
    }
)
```

### PDF Generation Integration

```python
# Generate key for PDF document
pdf_key = service.generate_key(KeyPrefix.PDF_DOCUMENT)

# Store PDF metadata
service.set_value(
    key=f"{pdf_key}_metadata",
    value={
        "template": "solar_offer",
        "pages": 8,
        "size_bytes": 1024000
    },
    key_type=KeyType.JSON,
    namespace="root.pdf.documents"
)
```

### Price Matrix Integration

```python
# Generate key for price calculation
price_key = service.generate_key(KeyPrefix.PRICE_CALCULATION)

# Store price data
service.set_value(
    key=f"{price_key}_price",
    value=16999.00,
    key_type=KeyType.CURRENCY,
    namespace="root.pricing.calculations",
    metadata={
        "module_count": 30,
        "battery_model": "Battery_10kWh",
        "calculation_date": "2023-11-16"
    }
)
```

## Troubleshooting

### Common Issues

1. **Key validation fails**
   - Check key format matches pattern: `PREFIX_[components]`
   - Ensure prefix is valid (2-4 uppercase letters)
   - Verify components are alphanumeric

2. **Type validation errors**
   - Verify value matches specified type
   - Check type constraints (e.g., CURRENCY ≥ 0, PERCENTAGE 0-100)
   - Use correct type for data

3. **Namespace not found**
   - Ensure namespace path is correct
   - Create namespace before adding keys
   - Check for typos in namespace path

4. **Usage tracking not working**
   - Verify `track_usage=True` in get/set operations
   - Check if key exists before tracking
   - Ensure tracker is initialized

## Requirements Satisfied

- **Requirement 4.1**: API-First design with RESTful endpoints
- **Requirement 6.1**: Modular code extraction with service layer
- **Requirement 14.4**: Dynamic key generation for all data types
- **Requirement 14.7**: Key-value configuration storage with typing

## Related Documentation

- [Universal Data System](./UNIVERSAL_DATA_MODEL.md)
- [PDF Bytes Generation](./PDF_BYTE_GENERATION.md)
- [German Number Formatting](./GERMAN_FORMATTING.md)
- [API Documentation](./API_DOCUMENTATION.md)
