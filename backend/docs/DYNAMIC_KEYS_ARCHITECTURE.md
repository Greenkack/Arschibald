# Dynamic Key System Architecture

## Overview

The Dynamic Key System provides unique, traceable identifiers for all data types in the application. It supports key generation, validation, indexing, and namespace management.

## Key Components

### 1. KeyPrefix Enum

Defines prefixes for different data types:

```python
from backend.core.dynamic_keys import KeyPrefix

# Core entities
KeyPrefix.USER          # "USR"
KeyPrefix.PROJECT       # "PRJ"
KeyPrefix.CUSTOMER      # "CUS"

# Solar calculator
KeyPrefix.SOLAR_CALCULATION  # "SOL"
KeyPrefix.SOLAR_MODULE       # "MOD"
KeyPrefix.SOLAR_INVERTER     # "INV"
KeyPrefix.SOLAR_BATTERY      # "BAT"

# Heat pump
KeyPrefix.HEATPUMP_CALCULATION  # "HP"
KeyPrefix.HEATPUMP_PRODUCT      # "HPP"

# Price matrix
KeyPrefix.PRICE_MATRIX      # "PMX"
KeyPrefix.PRICE_CALCULATION # "PRC"
KeyPrefix.PRODUCT           # "PRD"

# PDF
KeyPrefix.PDF_DOCUMENT  # "PDF"
KeyPrefix.PDF_TEMPLATE  # "TPL"

# 3D Visualization
KeyPrefix.VISUALIZATION_3D  # "VIS"
KeyPrefix.MODULE_PLACEMENT  # "PLC"

# CRM
KeyPrefix.OFFER     # "OFF"
KeyPrefix.TASK      # "TSK"
KeyPrefix.NOTE      # "NOT"
KeyPrefix.EMAIL     # "EML"
KeyPrefix.CONTRACT  # "CNT"

# Configuration
KeyPrefix.CONFIG   # "CFG"
KeyPrefix.SETTING  # "SET"

# Media
KeyPrefix.IMAGE     # "IMG"
KeyPrefix.DOCUMENT  # "DOC"
KeyPrefix.CHART     # "CHT"

# Generic
KeyPrefix.DATA  # "DAT"
KeyPrefix.TEMP  # "TMP"
```

### 2. DynamicKeyMixin

Add dynamic key capabilities to any model:

```python
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix

class SolarProject(DynamicKeyMixin):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        # Generate key on creation
        self.generate_dynamic_key(KeyPrefix.PROJECT)

# Usage
project = SolarProject("Roof Installation")
print(project.get_dynamic_key())  # "PRJ_20231116_143052_a1b2c3d4"
```

### 3. DynamicKeyIndex

Fast O(1) lookup for objects by key:

```python
from backend.core.dynamic_keys import DynamicKeyIndex, KeyPrefix

index = DynamicKeyIndex()

# Add objects
index.add("PRJ_20231116_143052_a1b2c3d4", project_obj)
index.add("SOL_20231116_143100_b2c3d4e5", calculation_obj)

# Lookup
project = index.get("PRJ_20231116_143052_a1b2c3d4")

# Get all by prefix
all_projects = index.get_by_prefix("PRJ")
all_calculations = index.get_by_prefix("SOL")

# Statistics
stats = index.get_statistics()
# {'total_keys': 2, 'total_prefixes': 2, 'keys_by_prefix': {'PRJ': 1, 'SOL': 1}}
```

### 4. DynamicKeyValidator

Validate keys against configurable rules:

```python
from backend.core.dynamic_keys import DynamicKeyValidator

validator = DynamicKeyValidator()

# Validate key
is_valid, error = validator.validate("PRJ_20231116_143052_a1b2c3d4")
# (True, None)

is_valid, error = validator.validate("invalid")
# (False, "Key too short (min: 5)")

# Configure rules
validator.set_rule('min_length', 10)
validator.set_rule('max_length', 50)
validator.set_rule('allow_custom_prefix', True)
```

## Key Generation Methods

### 1. Timestamp-based Keys (Default)

```python
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix

mixin = DynamicKeyMixin()
key = mixin.generate_dynamic_key(
    prefix=KeyPrefix.SOLAR_CALCULATION,
    include_timestamp=True,
    include_uuid=True
)
# "SOL_20231116_143052_a1b2c3d4"
```

### 2. Hash-based Keys (Deterministic)

```python
from backend.core.dynamic_keys import generate_hash_key, KeyPrefix

# Same input always produces same key
key1 = generate_hash_key("solar_panel_count", KeyPrefix.DATA)
key2 = generate_hash_key("solar_panel_count", KeyPrefix.DATA)
assert key1 == key2  # True

# Different input produces different key
key3 = generate_hash_key("battery_capacity", KeyPrefix.DATA)
assert key1 != key3  # True
```

### 3. Custom Suffix Keys

```python
from backend.core.dynamic_keys import DynamicKeyMixin, KeyPrefix

mixin = DynamicKeyMixin()
key = mixin.generate_dynamic_key(
    prefix=KeyPrefix.PDF_DOCUMENT,
    custom_suffix="offer_v2"
)
# "PDF_20231116_143052_a1b2c3d4_offer_v2"
```

## Namespace System

Organize keys hierarchically:

```python
from backend.core.dynamic_keys import KeyNamespace

# Create namespace hierarchy
root = KeyNamespace("root")
solar = root.add_child("solar")
calculations = solar.add_child("calculations")

# Add keys to namespace
calculations.add_key("SOL_20231116_143052_a1b2c3d4")
calculations.add_key("SOL_20231116_143100_b2c3d4e5")

# Get full path
print(calculations.get_full_path())  # "root.solar.calculations"

# Get all keys
all_keys = calculations.get_all_keys(recursive=True)
```

## Key-Value Store

Typed key-value storage with namespaces:

```python
from backend.core.dynamic_keys import KeyValueStore, KeyType

store = KeyValueStore()

# Set values with types
store.set("price_total", 1234.56, key_type=KeyType.CURRENCY)
store.set("efficiency", 0.95, key_type=KeyType.PERCENTAGE)
store.set("customer_email", "test@example.com", key_type=KeyType.EMAIL)

# Get values
price = store.get("price_total")  # 1234.56

# Search keys
currency_keys = store.search(key_type=KeyType.CURRENCY)
```

## Integration Examples

### Form Field Keys

```python
from backend.core.dynamic_keys import generate_hash_key, KeyPrefix

def generate_form_key(field_name: str) -> str:
    """Generate a unique key for a form field."""
    return generate_hash_key(f"form_{field_name}", KeyPrefix.DATA)

# Usage
customer_name_key = generate_form_key("customer_name")
customer_email_key = generate_form_key("customer_email")
```

### Calculation Result Keys

```python
from backend.core.dynamic_keys import generate_hash_key, KeyPrefix

def generate_calculation_key(calc_name: str) -> str:
    """Generate a unique key for a calculation result."""
    return generate_hash_key(f"calc_{calc_name}", KeyPrefix.SOLAR_CALCULATION)

# Usage
energy_key = generate_calculation_key("total_energy_production")
savings_key = generate_calculation_key("annual_savings")
```

### PDF Element Keys

```python
from backend.core.dynamic_keys import generate_hash_key, KeyPrefix

def generate_pdf_key(element_name: str) -> str:
    """Generate a unique key for a PDF element."""
    return generate_hash_key(f"pdf_{element_name}", KeyPrefix.PDF_DOCUMENT)

# Usage
header_key = generate_pdf_key("header_logo")
chart_key = generate_pdf_key("energy_chart")
```

## Best Practices

1. **Use appropriate prefixes** for data type identification
2. **Store keys with objects** for traceability
3. **Use hash-based keys** for deterministic lookups
4. **Use timestamp-based keys** for unique identifiers
5. **Validate keys** before storage or lookup
6. **Use namespaces** for logical organization
7. **Index frequently accessed objects** for O(1) lookup

## Performance

- Key generation: < 0.1ms per key
- Key validation: < 0.01ms per key
- Index lookup: O(1) constant time
- 10,000+ keys generated in < 5 seconds
