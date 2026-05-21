# Advanced Pricing Service - Quick Reference

## Service Initialization

```python
from backend.services.pricing_advanced_service import get_pricing_advanced_service

service = get_pricing_advanced_service()
```

## Quick Examples

### Volume Discount
```python
result = service.calculate_volume_discount(
    quantity=50,
    unit_price=100.0,
    discount_tiers=[
        {'min_quantity': 10, 'discount_percentage': 5},
        {'min_quantity': 50, 'discount_percentage': 10}
    ]
)
# Returns: 10% discount, final_total = 4500.0
```

### Time-Based Pricing
```python
result = service.calculate_time_based_price(
    base_price=1000.0,
    pricing_schedule={
        'weekend_multiplier': 1.1,
        'peak_hours': {'start': 9, 'end': 17, 'multiplier': 1.2}
    }
)
```

### Customer-Specific Pricing
```python
result = service.get_customer_price(
    customer_id='CUST001',
    product_id='PROD001',
    base_price=1000.0,
    quantity=1
)
```

### Bundle Pricing
```python
result = service.calculate_bundle_price(
    items=[
        {'product_id': 'A', 'quantity': 10, 'unit_price': 100},
        {'product_id': 'B', 'quantity': 1, 'unit_price': 500}
    ],
    bundle_rules={'discount_percentage': 10}
)
```

### Promotional Code
```python
result = service.apply_promotion_code(
    promo_code='SUMMER2024',
    base_price=1000.0,
    customer_id='CUST001'
)
```

### Currency Conversion
```python
# Set rate
service.set_exchange_rate('EUR', 'USD', 1.10)

# Convert
result = service.convert_currency(
    amount=1000.0,
    from_currency='EUR',
    to_currency='USD'
)
# Returns: 1100.0 USD
```

### Price History
```python
# Record change
service.record_price_change(
    product_id='PROD001',
    old_price=1000.0,
    new_price=1100.0,
    reason='Market adjustment'
)

# Get history
history = service.get_price_history(product_id='PROD001')

# Get trend
trend = service.get_price_trend(product_id='PROD001', days=30)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/pricing/advanced/rules` | POST | Create pricing rule |
| `/pricing/advanced/rules/apply` | POST | Apply rules to price |
| `/pricing/advanced/volume-discount` | POST | Calculate volume discount |
| `/pricing/advanced/time-based` | POST | Calculate time-based price |
| `/pricing/advanced/customer-price` | POST | Get customer-specific price |
| `/pricing/advanced/bundle` | POST | Calculate bundle price |
| `/pricing/advanced/promotions` | POST | Create promotion |
| `/pricing/advanced/promotions/apply` | POST | Apply promo code |
| `/pricing/advanced/currency/exchange-rate` | POST | Set exchange rate |
| `/pricing/advanced/currency/convert` | POST | Convert currency |
| `/pricing/advanced/currency/multi-currency` | POST | Get multi-currency price |
| `/pricing/advanced/history/record` | POST | Record price change |
| `/pricing/advanced/history` | GET | Get price history |
| `/pricing/advanced/history/trend/{id}` | GET | Get price trend |

## Rule Types

- `volume_discount` - Quantity-based discounts
- `time_based` - Time/date-based pricing
- `customer_specific` - Customer-specific pricing
- `bundle` - Bundle pricing
- `promotional` - Promotional campaigns
- `seasonal` - Seasonal pricing

## Response Format

All methods return:
```python
{
    'success': True/False,
    'error': 'Error message' (if failed),
    # ... additional data
}
```

## Common Patterns

### Stacking Discounts
```python
# 1. Volume discount
volume_result = service.calculate_volume_discount(...)
price = volume_result['final_total']

# 2. Customer discount
customer_result = service.get_customer_price(
    base_price=price, ...
)
price = customer_result['final_price']

# 3. Promotional discount
promo_result = service.apply_promotion_code(
    base_price=price, ...
)
final_price = promo_result['final_price']
```

### Multi-Currency Display
```python
result = service.get_multi_currency_price(
    base_price=10000.0,
    base_currency='EUR',
    target_currencies=['USD', 'GBP', 'CHF']
)

for currency, price in result['prices'].items():
    print(f"{currency}: {price}")
```

## Testing

Run tests:
```bash
pytest backend/tests/test_pricing_advanced_service.py -v
```

## Requirements

- Requirements: 1.3, 4.5, 6.1
- Python 3.10+
- Dependencies: decimal, datetime

## See Also

- [Full Guide](PRICING_ADVANCED_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
