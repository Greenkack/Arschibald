# Dynamic Key System Infrastructure

## Overview

The Dynamic Key System provides a comprehensive infrastructure for generating, managing, and validating unique keys for all data types in the application. It ensures data integrity, enables fast lookups, and supports flexible key-based access patterns.

## Features

- **Unique Key Generation**: Automatic generation of unique keys with timestamps and UUIDs
- **Type-Safe Prefixes**: Enumerated prefixes for different data types
- **Fast Indexing**: O(1) lookup performance with prefix-based queries
- **Validation**: Configurable validation rules for key formats
- **Metadata Support**: Attach metadata to keys for tracking and auditing
- **Global Index**: Singleton index for application-wide key management

## Architecture

### Components

1. **DynamicKeyMixin**: Mixin class for adding key generation to any model
2. **DynamicKeyIndex**: High-performance index for key-based lookups
3. **DynamicKeyValidator**: Configurable validator for key formats
4. **KeyPrefix**: Enumeration of standard key prefixes
5. **Global Functions**: Utility functions for common operations

## Usage

### Basic Key Generation

```python
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix

# Create an object with key generation capability
class SolarCalculation(DynamicKeyMixin):
    def __init__(self):
        super().__init__()
        self.power = 10.5
        self.modules = 30

# Generate a key
calc = SolarCalculation()
key = calc.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
print(key)  # Output: SOL_20231116_143052_a1b2c3d4
```

### Key Components

Generated keys have the following structure:
```
PREFIX_TIMESTAMP_UUID_ID_SUFFIX
```

- **PREFIX**: 2-4 letter code indicating data type (e.g., SOL, HP, PRJ)
- **TIMESTAMP**: Date and time in YYYYMMDD_HHMMSS format
- **UUID**: 8-character hexadecimal unique identifier
- **ID**: Optional entity ID from database
- **SUFFIX**: Optional custom suffix

### Using the Index

```python
from backend.core.dynamic_keys import DynamicKeyIndex, KeyPrefix

# Create an index
index = DynamicKeyIndex()

# Add objects
key1 = "SOL_20231116_143052_a1b2c3d4"
calc_data = {"power": 10.5, "modules": 30}
index.add(key1, calc_data, metadata={"user": "john"})

# Retrieve by key
data = index.get(key1)
print(data)  # {"power": 10.5, "modules": 30}

# Get all solar calculations
solar_calcs = index.get_by_prefix("SOL")
print(f"Found {len(solar_calcs)} solar calculations")

# Check existence
if index.exists(key1):
    print("Key exists in index")

# Get statistics
stats = index.get_statistics()
print(f"Total keys: {stats['total_keys']}")
print(f"Keys by prefix: {stats['keys_by_prefix']}")
```

### Validation

```python
from backend.core.dynamic_keys import DynamicKeyValidator

# Create validator
validator = DynamicKeyValidator()

# Validate a key
key = "SOL_20231116_143052_a1b2c3d4"
is_valid, error = validator.validate(key)

if is_valid:
    print("Key is valid")
else:
    print(f"Validation error: {error}")

# Configure validation rules
validator.set_rule('min_length', 15)
validator.set_rule('allow_custom_prefix', True)

# Validate with custom rules
is_valid, error = validator.validate(key, strict=True)
```

### Global Index

```python
from backend.core.dynamic_keys import get_global_key_index

# Get the global index (singleton)
index = get_global_key_index()

# Use it like any other index
index.add("SOL_001", {"data": "test"})
data = index.get("SOL_001")

# The same index is accessible from anywhere
from another_module import get_global_key_index
same_index = get_global_key_index()
same_data = same_index.get("SOL_001")  # Returns same data
```

### Hash-Based Keys

```python
from backend.core.dynamic_keys import generate_hash_key, KeyPrefix

# Generate deterministic key from data
data = "user@example.com"
key = generate_hash_key(data, KeyPrefix.USER)
print(key)  # USR_a1b2c3d4e5f6g7h8

# Same data always produces same key
key2 = generate_hash_key(data, KeyPrefix.USER)
assert key == key2
```

## Key Prefixes

The system includes predefined prefixes for common data types:

### Core Entities
- `USR` - User
- `PRJ` - Project
- `CUS` - Customer

### Solar Calculator
- `SOL` - Solar Calculation
- `MOD` - Solar Module
- `INV` - Solar Inverter
- `BAT` - Battery

### Heat Pump
- `HP` - Heat Pump Calculation
- `HPP` - Heat Pump Product

### Price Matrix
- `PMX` - Price Matrix
- `PRC` - Price Calculation
- `PRD` - Product

### PDF
- `PDF` - PDF Document
- `TPL` - PDF Template

### 3D Visualization
- `VIS` - 3D Visualization
- `PLC` - Module Placement

### CRM
- `OFF` - Offer
- `TSK` - Task
- `NOT` - Note
- `EML` - Email
- `CNT` - Contract

### Configuration
- `CFG` - Configuration
- `SET` - Setting

### Media
- `IMG` - Image
- `DOC` - Document
- `CHT` - Chart

### Generic
- `DAT` - Generic Data
- `TMP` - Temporary Data

## Advanced Usage

### Custom Key Generation

```python
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix

mixin = DynamicKeyMixin()

# Generate key with specific components
key = mixin.generate_dynamic_key(
    prefix=KeyPrefix.SOLAR_CALCULATION,
    include_timestamp=True,
    include_uuid=True,
    custom_suffix="premium"
)
print(key)  # SOL_20231116_143052_a1b2c3d4_premium

# Generate minimal key
key = mixin.generate_dynamic_key(
    prefix=KeyPrefix.DATA,
    include_timestamp=False,
    include_uuid=False
)
print(key)  # DAT
```

### Key Metadata

```python
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix

mixin = DynamicKeyMixin()
key = mixin.generate_dynamic_key(
    KeyPrefix.PROJECT,
    custom_suffix="important"
)

# Get metadata about the key
metadata = mixin.get_key_metadata()
print(f"Prefix: {metadata['prefix']}")
print(f"Created: {metadata['created_at']}")
print(f"Age: {metadata['key_age_seconds']} seconds")
print(f"Suffix: {metadata['custom_suffix']}")
```

### Key Parsing

```python
from backend.core.dynamic_keys import DynamicKeyMixin

key = "SOL_20231116_143052_a1b2c3d4_123"

# Extract prefix
prefix = DynamicKeyMixin.extract_prefix(key)
print(f"Prefix: {prefix}")  # SOL

# Extract all components
components = DynamicKeyMixin.extract_components(key)
print(f"Date: {components.get('date')}")  # 20231116
print(f"UUID: {components.get('uuid')}")  # a1b2c3d4
print(f"Parts: {components['parts']}")  # ['SOL', '20231116', '143052', 'a1b2c3d4', '123']
```

### Index with Metadata

```python
from backend.core.dynamic_keys import DynamicKeyIndex

index = DynamicKeyIndex()

# Add with rich metadata
key = "SOL_20231116_143052_a1b2c3d4"
data = {"power": 10.5}
metadata = {
    "created_by": "user123",
    "created_at": "2023-11-16T14:30:52",
    "version": 1,
    "tags": ["premium", "residential"]
}

index.add(key, data, metadata)

# Retrieve metadata
meta = index.get_metadata(key)
print(f"Created by: {meta['created_by']}")
print(f"Tags: {meta['tags']}")
```

### Prefix-Based Queries

```python
from backend.core.dynamic_keys import DynamicKeyIndex

index = DynamicKeyIndex()

# Add various objects
index.add("SOL_001", {"type": "solar", "power": 10})
index.add("SOL_002", {"type": "solar", "power": 15})
index.add("HP_001", {"type": "heatpump", "cop": 4.5})
index.add("PRJ_001", {"type": "project", "name": "House A"})

# Get all solar calculations
solar_data = index.get_by_prefix("SOL")
print(f"Found {len(solar_data)} solar calculations")

# Get just the keys
solar_keys = index.get_keys_by_prefix("SOL")
print(f"Solar keys: {solar_keys}")

# Count by prefix
solar_count = index.count_by_prefix("SOL")
hp_count = index.count_by_prefix("HP")
print(f"Solar: {solar_count}, Heat Pump: {hp_count}")

# Get all prefixes
all_prefixes = index.get_all_prefixes()
print(f"Available prefixes: {all_prefixes}")
```

## Integration with Database Models

### SQLAlchemy Integration

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix

Base = declarative_base()

class SolarCalculation(Base, DynamicKeyMixin):
    __tablename__ = 'solar_calculations'
    
    id = Column(Integer, primary_key=True)
    dynamic_key = Column(String(100), unique=True, index=True)
    power = Column(Integer)
    modules = Column(Integer)
    created_at = Column(DateTime)
    
    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        DynamicKeyMixin.__init__(self)
        
        # Generate key on creation
        if not self.dynamic_key:
            self.dynamic_key = self.generate_dynamic_key(
                KeyPrefix.SOLAR_CALCULATION
            )

# Usage
calc = SolarCalculation(power=10, modules=30)
print(f"Generated key: {calc.dynamic_key}")
```

### Pydantic Integration

```python
from pydantic import BaseModel, Field
from typing import Optional
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix

class SolarCalculationModel(BaseModel, DynamicKeyMixin):
    id: Optional[int] = None
    dynamic_key: Optional[str] = None
    power: float
    modules: int
    
    def __init__(self, **data):
        BaseModel.__init__(self, **data)
        DynamicKeyMixin.__init__(self)
        
        # Generate key if not provided
        if not self.dynamic_key:
            self.dynamic_key = self.generate_dynamic_key(
                KeyPrefix.SOLAR_CALCULATION
            )
    
    class Config:
        arbitrary_types_allowed = True

# Usage
calc = SolarCalculationModel(power=10.5, modules=30)
print(f"Key: {calc.dynamic_key}")
print(f"Data: {calc.dict()}")
```

## Performance Considerations

### Index Performance

The `DynamicKeyIndex` provides:
- **O(1)** lookup by key
- **O(1)** insertion
- **O(1)** deletion
- **O(n)** prefix-based queries (where n = number of keys with that prefix)

### Memory Usage

Each indexed object stores:
- Key string (~50-100 bytes)
- Object reference (8 bytes)
- Optional metadata (variable)

For 1 million objects: ~50-100 MB memory overhead

### Best Practices

1. **Use appropriate prefixes**: Choose descriptive prefixes for easy identification
2. **Index strategically**: Only index objects that need fast lookup
3. **Clean up**: Remove objects from index when no longer needed
4. **Use global index sparingly**: For application-wide data only
5. **Validate keys**: Always validate keys from external sources

## Error Handling

```python
from backend.core.dynamic_keys import DynamicKeyMixin, DynamicKeyIndex

# Handle invalid keys
try:
    mixin = DynamicKeyMixin()
    mixin.set_dynamic_key("invalid_key", validate=True)
except ValueError as e:
    print(f"Invalid key: {e}")

# Handle missing keys
index = DynamicKeyIndex()
key = "SOL_nonexistent"

if not index.exists(key):
    print(f"Key not found: {key}")
else:
    data = index.get(key)

# Handle validation errors
from backend.core.dynamic_keys import DynamicKeyValidator

validator = DynamicKeyValidator()
is_valid, error = validator.validate("bad_key")

if not is_valid:
    print(f"Validation failed: {error}")
```

## Testing

The system includes comprehensive tests covering:
- Key generation and uniqueness
- Validation rules
- Index operations
- Prefix-based queries
- Metadata management
- Integration scenarios

Run tests with:
```bash
pytest backend/tests/test_dynamic_keys.py -v
```

## Requirements

This implementation satisfies:
- **Requirement 14.4**: Dynamic key generation for all data types
- **Requirement 14.7**: Key indexing for fast lookup

## Future Enhancements

Potential improvements:
1. Distributed key generation for multi-instance deployments
2. Key expiration and TTL support
3. Hierarchical key namespaces
4. Key migration tools
5. Performance monitoring and analytics
6. Redis-backed index for persistence
7. Key compression for storage optimization

## Support

For questions or issues with the Dynamic Key System:
1. Check this documentation
2. Review test cases in `test_dynamic_keys.py`
3. Examine example usage in integration tests
4. Contact the development team
