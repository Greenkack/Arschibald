# Price Increase Service - Quick Reference

## Quick Start

```python
from backend.services.price_increase_service import get_price_increase_service

# Get service
service = get_price_increase_service()

# Set base price
service.set_base_price(16999.00)

# Calculate next price
result = service.calculate_next_price()
print(result["price_formatted"])  # "18.188,93 €"
```

## Common Operations

### Set Configuration

```python
# Set increase rate (default: 7%)
service.set_increase_rate(0.10)  # 10%

# Set strategy
service.set_strategy("cumulative")  # or "fixed", "stepped", "custom"

# Set custom rates
service.set_custom_rates([0.05, 0.10, 0.15])
```

### Calculate Prices

```python
# Next price
price = service.calculate_next_price()

# Specific offer
price = service.calculate_price_for_offer(5)

# All prices at once
prices = service.calculate_all_prices(8)
```

### Get Information

```python
# Current configuration
config = service.get_configuration()

# Price history
history = service.get_price_history()

# Current price
current = service.get_current_price()

# Comparison report
comparison = service.generate_price_comparison()
```

### Reset State

```python
# Reset everything
service.reset_price_state()
```

## Strategies

| Strategy | Formula | Example (7%, base 16.999€) |
|----------|---------|----------------------------|
| **Cumulative** | `price × (1 + rate)` | 18.188,93 → 19.462,16 → 20.824,51 |
| **Fixed** | `base × (1 + rate × n)` | 18.188,93 → 19.378,86 → 20.568,79 |
| **Stepped** | `base × (1 + rate × n)` | 17.848,95 → 18.698,90 → 19.548,85 |
| **Custom** | `base × (1 + custom_rate)` | Custom rates per offer |

## API Endpoints

### Configuration
- `GET /api/v1/price-increase/configuration` - Get config
- `POST /api/v1/price-increase/configuration/increase-rate` - Set rate
- `POST /api/v1/price-increase/configuration/strategy` - Set strategy
- `POST /api/v1/price-increase/configuration/custom-rates` - Set custom rates

### State
- `POST /api/v1/price-increase/base-price` - Set base price
- `POST /api/v1/price-increase/reset` - Reset state
- `GET /api/v1/price-increase/history` - Get history
- `GET /api/v1/price-increase/current-price` - Get current price

### Calculation
- `POST /api/v1/price-increase/calculate-next` - Next price
- `POST /api/v1/price-increase/calculate-for-offer` - Specific offer
- `POST /api/v1/price-increase/calculate-all` - All prices

### Analysis
- `GET /api/v1/price-increase/comparison` - Price comparison

## Response Format

```json
{
  "offer_index": 1,
  "price": 18188.93,
  "price_formatted": "18.188,93 €",
  "increase_rate": 0.07,
  "increase_rate_percentage": "7.00%",
  "increase_amount": 1189.93,
  "increase_amount_formatted": "1.189,93 €",
  "previous_price": 16999.00,
  "previous_price_formatted": "16.999,00 €",
  "base_price": 16999.00,
  "base_price_formatted": "16.999,00 €",
  "strategy": "cumulative"
}
```

## German Formatting

- Decimal separator: **comma (,)**
- Thousand separator: **dot (.)**
- Currency: **€**

Examples:
- `16999.00` → `16.999,00 €`
- `18188.93` → `18.188,93 €`

## Limits

- Min increase rate: **1%** (0.01)
- Max increase rate: **50%** (0.50)
- Max offers: **100**

## Error Handling

```python
try:
    service.calculate_next_price()
except RuntimeError:
    # Base price not set
    service.set_base_price(16999.00)

try:
    service.set_increase_rate(0.60)
except ValueError:
    # Rate out of range
    service.set_increase_rate(0.10)
```

## Testing

```bash
# Run tests
python -m pytest tests/test_price_increase_service.py -v

# Run demo
python demo_price_increase.py
```

## Multi-PDF Scenario

```python
# Setup
service.set_base_price(16999.00)
service.set_increase_rate(0.07)

# Generate 8 offers
prices = service.calculate_all_prices(8)

# Results:
# Offer 0: 16.999,00 € (base)
# Offer 1: 18.188,93 € (+7%)
# Offer 2: 19.462,16 € (+7%)
# Offer 3: 20.824,51 € (+7%)
# ...
# Offer 8: 29.207,21 € (+7%)
```

## Integration Example

```python
from backend.services.product_rotation_service import get_product_rotation_service
from backend.services.price_increase_service import get_price_increase_service

rotation = get_product_rotation_service()
pricing = get_price_increase_service()

# Setup
pricing.set_base_price(16999.00)

# Generate offers
for i in range(8):
    # Rotate products
    products = rotation.select_product_set(
        categories=["pv_module", "inverter", "battery"]
    )
    
    # Calculate price
    price = pricing.calculate_next_price()
    
    print(f"Offer {i+1}: {price['price_formatted']}")
```

## Health Check

```python
health = service.health_check()
print(health.status)  # "healthy"
print(health.details)  # Configuration details
```

## Common Patterns

### Pattern 1: Sequential Generation
```python
service.set_base_price(16999.00)
for i in range(5):
    price = service.calculate_next_price()
    print(price["price_formatted"])
```

### Pattern 2: Batch Generation
```python
service.set_base_price(16999.00)
prices = service.calculate_all_prices(5)
for p in prices:
    print(p["price_formatted"])
```

### Pattern 3: Custom Per Offer
```python
service.set_base_price(16999.00)
service.set_strategy("custom")
service.set_custom_rates([0.05, 0.10, 0.15])
prices = service.calculate_all_prices(3)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| RuntimeError: Base price not set | Call `set_base_price()` first |
| ValueError: Rate out of range | Use rate between 0.01 and 0.50 |
| Empty history | Set base price and calculate at least one offer |
| Wrong strategy | Use: cumulative, fixed, stepped, or custom |

## Performance Tips

1. Use `calculate_all_prices()` for batch operations
2. Reset state between sessions
3. Cache configuration if reusing
4. Use appropriate strategy for your use case

## See Also

- Full Guide: `PRICE_INCREASE_GUIDE.md`
- Tests: `tests/test_price_increase_service.py`
- Demo: `demo_price_increase.py`
- API: `/api/v1/price-increase/health`
