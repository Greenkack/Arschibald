# Enhanced Pricing System

A comprehensive pricing calculation system for PV and heat pump applications with dynamic key generation for PDF integration, profit margin management, and support for all existing product database fields.

## Features

### Core Functionality

- **Dynamic Key Generation**: All pricing values automatically get unique PDF keys
- **Comprehensive Product Support**: Leverages all existing product fields (id, category, model_name, brand, price_euro, calculate_per, capacity_w, storage_power_kw, power_kw, max_cycles, warranty_years, technology, feature, design, upgrade, max_kwh_capacity, outdoor_opt, self_supply_feature, shadow_fading, smart_home, length_m, width_m, weight_kg, efficiency_percent, origin_country, description, pros, cons, rating, image_base64, created_at, updated_at)
- **Multiple Calculation Methods**: Support for "per piece", "per meter", "lump sum", and "per kWp" pricing
- **Advanced Pricing Formula**: (Matrix Price + Accessories) × (1 - Discount%) × (1 + Surcharge%) - Fixed Discounts + Fixed Surcharges
- **System Type Support**: Separate engines for PV, heat pump, and combined systems
- **Input Validation**: Comprehensive validation of all pricing data

### Calculate Per Methods

- **Stück (Per Piece)**: Standard per-unit pricing for modules, inverters, batteries
- **Meter**: Per-meter pricing for cables and mounting rails
- **Pauschal (Lump Sum)**: Fixed pricing for services and packages
- **kWp**: System-dependent pricing based on capacity

## Architecture

```
pricing/
├── __init__.py                    # Package initialization
├── enhanced_pricing_engine.py     # Core pricing engine
├── dynamic_key_manager.py         # Dynamic key generation
├── demo_enhanced_pricing.py       # Demonstration script
└── README.md                      # This file

tests/
└── test_enhanced_pricing_engine.py # Comprehensive unit tests
```

## Quick Start

### Basic Usage

```python
from pricing import PricingEngine, DynamicKeyManager

# Create a PV pricing engine
engine = PricingEngine("pv")

# Define components with product data
components = [
    {
        "product_id": 1,
        "quantity": 20,  # 20 PV modules
    },
    {
        "model_name": "PowerMax 5K",
        "quantity": 1,   # 1 inverter
    }
]

# Calculate base price
result = engine.calculate_base_price(components)
print(f"Base price: {result.base_price}€")
print(f"Dynamic keys: {len(result.dynamic_keys)}")
```

### Complete Pricing Calculation

```python
# Define complete calculation data
calculation_data = {
    "components": [
        {"product_id": 1, "quantity": 20},  # PV modules
        {"product_id": 2, "quantity": 1},   # Inverter
    ],
    "modifications": {
        "discount_percent": 5.0,      # 5% discount
        "accessories_cost": 200.0,    # Additional accessories
        "surcharge_fixed": 100.0      # Rush order surcharge
    },
    "vat_rate": 19.0  # German VAT
}

# Generate final price with all calculations
final_result = engine.generate_final_price(calculation_data)

print(f"Final price (net): {final_result.final_price_net}€")
print(f"Final price (gross): {final_result.final_price_gross}€")
print(f"VAT amount: {final_result.vat_amount}€")

# Access dynamic keys for PDF integration
pdf_keys = final_result.dynamic_keys
print(f"Available PDF keys: {list(pdf_keys.keys())}")
```

### Dynamic Key Management

```python
from pricing import DynamicKeyManager, KeyCategory

key_manager = DynamicKeyManager()

# Generate keys from pricing data
pricing_data = {
    "base_price": 5000.0,
    "discount_amount": 250.0,
    "final_price": 4750.0
}

keys = key_manager.generate_keys(
    pricing_data, 
    prefix="PV_", 
    category=KeyCategory.PRICING
)

# Format for PDF templates
pdf_formatted = key_manager.format_for_pdf(keys)
# Result: {"PV_BASE_PRICE": "5.000,00", "PV_FINAL_PRICE": "4.750,00"}
```

## Product Field Integration

The system leverages all existing product database fields:

### Core Fields

- `id`, `category`, `model_name`, `brand`
- `price_euro`, `calculate_per`

### Technical Specifications

- `capacity_w`, `storage_power_kw`, `power_kw`
- `max_cycles`, `warranty_years`
- `efficiency_percent`

### Enhanced Attributes

- `technology`, `feature`, `design`, `upgrade`
- `max_kwh_capacity`, `outdoor_opt`
- `self_supply_feature`, `shadow_fading`, `smart_home`

### Physical Properties

- `length_m`, `width_m`, `weight_kg`
- `origin_country`

### Descriptive Fields

- `description`, `pros`, `cons`, `rating`
- `image_base64`

### Timestamps

- `created_at`, `updated_at`

## Calculate Per Examples

### Per Piece (Stück)

```python
pv_module = PriceComponent(
    model_name="AlphaSolar 450W",
    quantity=20,
    price_euro=180.0,
    calculate_per="Stück"
)
# Result: 20 × 180€ = 3,600€
```

### Per Meter

```python
cable = PriceComponent(
    model_name="Solar Cable 6mm²",
    quantity=50,  # 50 meters
    price_euro=2.5,  # per meter
    calculate_per="Meter"
)
# Result: 50m × 2.5€/m = 125€
```

### Lump Sum (Pauschal)

```python
service = PriceComponent(
    model_name="Installation Service",
    quantity=1,
    price_euro=1500.0,
    calculate_per="pauschal"
)
# Result: 1,500€ (regardless of quantity)
```

### Per kWp

```python
mounting = PriceComponent(
    model_name="Mounting System",
    quantity=9,  # 9 kWp system
    price_euro=50.0,
    calculate_per="kWp",
    capacity_w=1000.0  # 1 kWp reference
)
# Result: 9 kWp × 50€/kWp = 450€
```

## Dynamic Key Generation

### Automatic Key Creation

All pricing values automatically receive dynamic keys:

```python
# Component keys
"ALPHASOLAR_450W_UNIT_PRICE": 180.0
"ALPHASOLAR_450W_TOTAL_PRICE": 3600.0
"ALPHASOLAR_450W_QUANTITY": 20

# System keys
"PV_BASE_PRICE_NET": 4400.0
"PV_FINAL_PRICE_NET": 4470.0
"PV_VAT_AMOUNT": 849.3

# Modification keys
"PV_DISCOUNT_PERCENT": 5.0
"PV_DISCOUNT_PERCENT_AMOUNT": 230.0
"PV_SURCHARGE_FIXED": 100.0
```

### PDF-Ready Formatting

Keys are automatically formatted for German locale:

```python
# Numbers with German formatting
"PV_BASE_PRICE_NET": "4.400,00"
"PV_VAT_AMOUNT": "849,30"

# Boolean values
"OUTDOOR_OPTION": "Ja"
"INDOOR_ONLY": "Nein"
```

### Safe Key Names

Special characters and German umlauts are handled:

```python
"Wärmepumpe Größe" → "WAERMEPUMPE_GROESSE"
"Price (€/kWh)" → "PRICE_EUR_KWH"
"5kW Inverter" → "KEY_5KW_INVERTER"
```

## Pricing Formula

The system implements the specified pricing formula:

```
Final Price = (Matrix Price + Accessories) × (1 - Discount%) × (1 + Surcharge%) - Fixed Discounts + Fixed Surcharges
```

### Example Calculation

```python
Base Price: 5,000€
Accessories: +200€
Subtotal: 5,200€

Discount (5%): -260€ (5% of 5,200€)
After Discount: 4,940€

Surcharge (2%): +98.8€ (2% of 4,940€)
After Surcharge: 5,038.8€

Fixed Discount: -100€
Fixed Surcharge: +50€

Final Price: 4,988.8€
```

## System Types

### PV Systems

```python
pv_engine = PricingEngine("pv")
# Generates keys with "PV_" prefix
```

### Heat Pump Systems

```python
hp_engine = PricingEngine("heatpump")
# Generates keys with "HEATPUMP_" prefix
```

### Combined Systems

```python
combined_engine = PricingEngine("combined")
# Generates keys with "COMBINED_" prefix
```

## Validation

### Input Validation

```python
# Valid data structure
valid_data = {
    "components": [
        {"product_id": 1, "quantity": 10},
        {"model_name": "Test Product", "quantity": 5}
    ],
    "modifications": {
        "discount_percent": 5.0,
        "surcharge_fixed": 100.0
    }
}

is_valid = engine.validate_pricing_data(valid_data)
```

### Validation Rules

- Components must have either `product_id` or `model_name`
- Quantities must be positive numbers
- Percentages should be between 0-100
- Modification values must be numeric
- System type must be valid ("pv", "heatpump", "combined")

## Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/test_enhanced_pricing_engine.py -v
```

### Test Coverage

- ✅ PriceComponent with all calculate_per methods
- ✅ Dynamic key generation and conflict resolution
- ✅ Complex pricing formula calculations
- ✅ PDF formatting and German locale
- ✅ Input validation and error handling
- ✅ Integration tests with complete systems
- ✅ System type validation
- ✅ Key categorization and filtering

## Demo

Run the demonstration script:

```bash
python pricing/demo_enhanced_pricing.py
```

This demonstrates:

- PriceComponent creation with different calculation methods
- Dynamic key generation and PDF formatting
- Complete pricing calculations with modifications
- Input validation examples

## Integration with Existing System

### Product Database

The system integrates seamlessly with the existing `product_db.py`:

```python
# Automatic product lookup
product = get_product_by_id(product_id)
price_component = engine._create_price_component(product, comp_data)
```

### PDF Generation

Dynamic keys integrate with existing PDF templates:

```python
# In PDF generation
pdf_keys = final_result.dynamic_keys
# Use keys in template: {{PV_FINAL_PRICE_NET}}, {{PV_VAT_AMOUNT}}, etc.
```

### Session State

Compatible with Streamlit session state:

```python
# Store pricing results
st.session_state['pricing_result'] = final_result
st.session_state['pdf_keys'] = final_result.dynamic_keys
```

## Requirements

The enhanced pricing system requires:

- Python 3.7+
- Existing product database structure
- Optional: `product_db.py` for database integration
- Optional: `pytest` for running tests

## Future Enhancements

The foundation supports future features:

- Profit margin management
- Advanced discount rules
- Multi-currency support
- Pricing history and audit trails
- Performance optimization and caching
- Real-time pricing updates
- Economic analysis integration

## Error Handling

The system includes comprehensive error handling:

```python
try:
    result = engine.calculate_base_price(components)
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Calculation error: {e}")
```

Common error scenarios:

- Invalid system type
- Missing product data
- Invalid component structure
- Negative quantities
- Invalid modification values

## Performance

The system is designed for performance:

- Efficient key generation algorithms
- Minimal database queries
- Optimized calculation formulas
- Memory-efficient data structures
- Suitable for real-time applications

## License

This enhanced pricing system is part of the PV/Heat Pump application and follows the same licensing terms.
