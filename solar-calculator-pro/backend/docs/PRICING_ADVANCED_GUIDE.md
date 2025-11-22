# Advanced Pricing Service Guide

## Overview

The Advanced Pricing Service extends the basic pricing functionality with sophisticated features for dynamic pricing, discounts, promotions, and multi-currency support.

## Features

### 1. Dynamic Pricing Rules Engine

Create flexible pricing rules that automatically adjust prices based on conditions.

**Example: Volume Discount Rule**
```python
from backend.services.pricing_advanced_service import get_pricing_advanced_service

service = get_pricing_advanced_service()

# Create volume discount rule
result = service.create_pricing_rule(
    name="Bulk Purchase Discount",
    rule_type="volume_discount",
    conditions={'quantity': {'min': 50}},
    actions={'discount_percentage': 15},
    priority=10,
    active=True
)

# Apply rules to a price
result = service.apply_pricing_rules(
    base_price=10000.0,
    context={'quantity': 75}
)
# Result: 15% discount applied
```

### 2. Volume Discount Calculations

Tiered discounts based on purchase quantity.

**Example: Multi-Tier Discounts**
```python
discount_tiers = [
    {'min_quantity': 10, 'discount_percentage': 5},
    {'min_quantity': 50, 'discount_percentage': 10},
    {'min_quantity': 100, 'discount_percentage': 15}
]

result = service.calculate_volume_discount(
    quantity=75,
    unit_price=100.0,
    discount_tiers=discount_tiers
)
# Result: 10% discount (tier 2)
```

### 3. Time-Based Pricing

Adjust prices based on time, day, or season.

**Example: Peak Hours and Seasonal Pricing**
```python
pricing_schedule = {
    'weekday_multiplier': 1.0,
    'weekend_multiplier': 1.1,
    'peak_hours': {
        'start': 9,
        'end': 17,
        'multiplier': 1.2
    },
    'seasonal': {
        'summer': {
            'months': [6, 7, 8],
            'multiplier': 1.15
        },
        'winter': {
            'months': [12, 1, 2],
            'multiplier': 0.95
        }
    }
}

result = service.calculate_time_based_price(
    base_price=1000.0,
    pricing_schedule=pricing_schedule,
    target_date=datetime(2024, 7, 15, 12, 0)  # Summer, noon
)
# Result: 1.15 × 1.2 = 1.38x multiplier
```

### 4. Customer-Specific Pricing

Special pricing for specific customers.

**Example: VIP Customer Discount**
```python
# Create customer-specific rule
service.create_pricing_rule(
    name="VIP Customer Discount",
    rule_type="customer_specific",
    conditions={'customer_id': 'CUST001'},
    actions={'discount_percentage': 20},
    priority=100
)

# Get customer price
result = service.get_customer_price(
    customer_id='CUST001',
    product_id='SOLAR_PANEL_001',
    base_price=5000.0,
    quantity=10
)
# Result: 20% discount for VIP customer
```

### 5. Bundle Pricing Logic

Special pricing for product bundles.

**Example: Solar System Bundle**
```python
items = [
    {'product_id': 'solar_panel', 'quantity': 20, 'unit_price': 250},
    {'product_id': 'inverter', 'quantity': 1, 'unit_price': 1500},
    {'product_id': 'battery', 'quantity': 1, 'unit_price': 5000}
]

bundle_rules = {
    'discount_percentage': 10,
    'free_items': ['installation'],
    'bonus_items': [
        {'product_id': 'warranty_extended', 'quantity': 1}
    ]
}

result = service.calculate_bundle_price(items, bundle_rules)
# Result: 10% off total, free installation, bonus warranty
```

### 6. Promotional Pricing

Create time-limited promotional campaigns.

**Example: Summer Sale**
```python
result = service.create_promotion(
    name="Summer Sale 2024",
    promotion_type="percentage",
    discount_value=25.0,
    valid_from=datetime(2024, 6, 1),
    valid_until=datetime(2024, 8, 31),
    conditions={'product_category': 'solar_panels'},
    max_uses=1000,
    max_uses_per_customer=1
)

# Apply promotion code
result = service.apply_promotion_code(
    promo_code="SUMMER2024",
    base_price=5000.0,
    customer_id="CUST001"
)
# Result: 25% discount
```

### 7. Currency Conversion

Multi-currency support with exchange rates.

**Example: Multi-Currency Pricing**
```python
# Set exchange rates
service.set_exchange_rate('EUR', 'USD', 1.10)
service.set_exchange_rate('EUR', 'GBP', 0.85)
service.set_exchange_rate('EUR', 'CHF', 0.95)

# Get price in multiple currencies
result = service.get_multi_currency_price(
    base_price=10000.0,
    base_currency='EUR',
    target_currencies=['USD', 'GBP', 'CHF']
)
# Result: {
#   'EUR': 10000.0,
#   'USD': 11000.0,
#   'GBP': 8500.0,
#   'CHF': 9500.0
# }
```

### 8. Price History Tracking

Track and analyze price changes over time.

**Example: Price Trend Analysis**
```python
# Record price change
service.record_price_change(
    product_id='SOLAR_PANEL_001',
    old_price=250.0,
    new_price=275.0,
    reason='Raw material cost increase',
    changed_by='admin'
)

# Get price history
history = service.get_price_history(
    product_id='SOLAR_PANEL_001',
    start_date=datetime.now() - timedelta(days=90)
)

# Analyze trend
trend = service.get_price_trend(
    product_id='SOLAR_PANEL_001',
    days=30
)
# Result: trend='increasing', average_change=+5.2%
```

## API Endpoints

### Dynamic Pricing Rules

```
POST /api/v1/pricing/advanced/rules
POST /api/v1/pricing/advanced/rules/apply
```

### Volume Discounts

```
POST /api/v1/pricing/advanced/volume-discount
```

### Time-Based Pricing

```
POST /api/v1/pricing/advanced/time-based
```

### Customer-Specific Pricing

```
POST /api/v1/pricing/advanced/customer-price
```

### Bundle Pricing

```
POST /api/v1/pricing/advanced/bundle
```

### Promotional Pricing

```
POST /api/v1/pricing/advanced/promotions
POST /api/v1/pricing/advanced/promotions/apply
```

### Currency Conversion

```
POST /api/v1/pricing/advanced/currency/exchange-rate
POST /api/v1/pricing/advanced/currency/convert
POST /api/v1/pricing/advanced/currency/multi-currency
```

### Price History

```
POST /api/v1/pricing/advanced/history/record
GET  /api/v1/pricing/advanced/history
GET  /api/v1/pricing/advanced/history/trend/{product_id}
```

## Integration Examples

### Complete Pricing Flow

```python
# 1. Get base price from matrix
base_result = base_pricing_service.calculate_price(
    module_count=30,
    storage_model="Battery 10kWh"
)
base_price = base_result['price']

# 2. Apply volume discount
volume_result = advanced_service.calculate_volume_discount(
    quantity=30,
    unit_price=base_price / 30,
    discount_tiers=[
        {'min_quantity': 20, 'discount_percentage': 5},
        {'min_quantity': 50, 'discount_percentage': 10}
    ]
)

# 3. Apply customer-specific pricing
customer_result = advanced_service.get_customer_price(
    customer_id='CUST001',
    product_id='SOLAR_SYSTEM',
    base_price=volume_result['final_total'],
    quantity=1
)

# 4. Apply promotional code
promo_result = advanced_service.apply_promotion_code(
    promo_code='SPRING2024',
    base_price=customer_result['final_price'],
    customer_id='CUST001'
)

# 5. Convert to multiple currencies
final_result = advanced_service.get_multi_currency_price(
    base_price=promo_result['final_price'],
    base_currency='EUR',
    target_currencies=['USD', 'GBP']
)

# 6. Record price for history
advanced_service.record_price_change(
    product_id='SOLAR_SYSTEM',
    old_price=base_price,
    new_price=final_result['prices']['EUR'],
    reason='Volume discount + VIP + Promotion',
    changed_by='system'
)
```

## Best Practices

1. **Rule Priority**: Use priority values to control rule application order
   - Promotions: 100+
   - Customer-specific: 50-99
   - Volume discounts: 10-49
   - General rules: 1-9

2. **Date Validation**: Always set valid_from and valid_until for time-sensitive rules

3. **Caching**: The service caches rules in memory for performance

4. **Currency Rates**: Update exchange rates regularly (daily recommended)

5. **Price History**: Record all significant price changes for audit trail

6. **Testing**: Test pricing rules thoroughly before activation

## Error Handling

All methods return a dictionary with `success` boolean:

```python
result = service.calculate_volume_discount(...)

if result['success']:
    final_price = result['final_total']
else:
    error_message = result['error']
    # Handle error
```

## Performance Considerations

- Rules are cached in memory
- Use appropriate priority values to minimize rule evaluations
- Limit history queries with date ranges and limits
- Consider database persistence for production use

## Requirements

- Requirements: 1.3, 4.5, 6.1
- Dependencies: decimal, datetime, logging
- Base service: PricingService

## See Also

- [Pricing Service Guide](PRICING_SERVICE_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [German Number Formatting](../../../frontend/GERMAN_INPUT_QUICK_REFERENCE.md)
