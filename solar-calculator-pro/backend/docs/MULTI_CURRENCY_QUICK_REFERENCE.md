# Multi-Currency System - Quick Reference

## Quick Start

### 1. Setup Database
```bash
python backend/migrations/add_currency_tables.py
```

### 2. Create Currency
```python
from backend.services.currency_service import CurrencyService
from backend.models.currency_schemas import CurrencyCreate

service = CurrencyService(db)
currency = service.create_currency(
    CurrencyCreate(code="EUR", name="Euro", symbol="€", decimal_places=2, is_default=True)
)
```

### 3. Add Exchange Rate
```python
from backend.models.currency_schemas import ExchangeRateCreate
from datetime import datetime

rate = service.create_exchange_rate(
    ExchangeRateCreate(
        from_currency_code="EUR",
        to_currency_code="USD",
        rate=1.08,
        source="ECB",
        valid_from=datetime.utcnow(),
        is_active=True
    )
)
```

### 4. Convert Currency
```python
from backend.models.currency_schemas import CurrencyConversionRequest

result = service.convert_currency(
    CurrencyConversionRequest(amount=1000.0, from_currency="EUR", to_currency="USD")
)
print(f"{result.converted_amount} {result.to_currency}")
```

## API Endpoints Cheat Sheet

| Operation | Method | Endpoint | Body |
|-----------|--------|----------|------|
| Create Currency | POST | `/currency/currencies` | `{code, name, symbol, decimal_places}` |
| List Currencies | GET | `/currency/currencies` | - |
| Get Currency | GET | `/currency/currencies/code/{code}` | - |
| Create Rate | POST | `/currency/exchange-rates` | `{from_currency_code, to_currency_code, rate}` |
| Get Rate | GET | `/currency/exchange-rates/{from}/{to}` | - |
| Convert | POST | `/currency/convert` | `{amount, from_currency, to_currency}` |
| Multi-Display | POST | `/currency/multi-display` | `{base_amount, base_currency, target_currencies}` |
| Apply Rounding | POST | `/currency/apply-rounding` | `?amount=X&currency_code=Y` |
| Get History | GET | `/currency/history/{from}/{to}` | - |
| Update Rates | POST | `/currency/update-rates` | `{source, currencies, force}` |
| Statistics | GET | `/currency/statistics` | - |

## Common Operations

### Convert Price to Multiple Currencies
```python
request = MultiCurrencyDisplayRequest(
    base_amount=16999.00,
    base_currency="EUR",
    target_currencies=["USD", "GBP", "CHF", "JPY"]
)
result = service.multi_currency_display(request)
```

### Apply Currency-Specific Rounding
```python
# 5-cent rounding for CHF
rounded = service.apply_rounding(123.456, "CHF")  # → 123.45 or 123.50

# No decimals for JPY
rounded = service.apply_rounding(123.456, "JPY")  # → 123.0
```

### Get Historical Rate
```python
from datetime import datetime

rate = service.get_exchange_rate(
    "EUR", "USD",
    date=datetime(2024, 1, 1)
)
```

### Update Rates from API
```python
result = service.update_exchange_rates_from_api(
    CurrencyUpdateRequest(source="ECB", force=False)
)
```

## Rounding Modes

| Mode | Description | Example (123.456) |
|------|-------------|-------------------|
| ROUND_UP | Always up | 123.46 |
| ROUND_DOWN | Always down | 123.45 |
| ROUND_HALF_UP | Nearest, ties up | 123.46 |
| ROUND_HALF_DOWN | Nearest, ties down | 123.45 |
| ROUND_CEILING | Towards +∞ | 123.46 |
| ROUND_FLOOR | Towards -∞ | 123.45 |

## Common Currency Codes

| Code | Name | Symbol | Decimals |
|------|------|--------|----------|
| EUR | Euro | € | 2 |
| USD | US Dollar | $ | 2 |
| GBP | British Pound | £ | 2 |
| CHF | Swiss Franc | CHF | 2 |
| JPY | Japanese Yen | ¥ | 0 |
| CNY | Chinese Yuan | ¥ | 2 |
| AUD | Australian Dollar | A$ | 2 |
| CAD | Canadian Dollar | C$ | 2 |

## Error Handling

```python
try:
    result = service.convert_currency(request)
except ValueError as e:
    # Handle missing rate or invalid currency
    print(f"Conversion error: {e}")
```

## Testing

### Run Tests
```bash
pytest backend/tests/test_currency_service.py -v
```

### Run Demo
```bash
python backend/demo_currency.py
```

## Database Queries

### Get All Active Currencies
```sql
SELECT * FROM currencies WHERE is_active = 1;
```

### Get Current Exchange Rates
```sql
SELECT * FROM exchange_rates WHERE is_active = 1;
```

### Get Rate History
```sql
SELECT * FROM exchange_rate_history 
WHERE from_currency_code = 'EUR' AND to_currency_code = 'USD'
ORDER BY timestamp DESC LIMIT 10;
```

## Performance Tips

1. **Cache Exchange Rates**: Store frequently used rates in memory
2. **Index Currency Codes**: Ensure database indexes on code columns
3. **Batch Conversions**: Use multi-display for multiple currencies
4. **Limit History**: Use date ranges and limits for history queries
5. **Update Scheduling**: Schedule rate updates during off-peak hours

## Integration Examples

### Price Matrix Integration
```python
# Convert price matrix values
def convert_matrix_price(price: float, from_currency: str, to_currency: str):
    result = currency_service.convert_currency(
        CurrencyConversionRequest(
            amount=price,
            from_currency=from_currency,
            to_currency=to_currency
        )
    )
    return result.converted_amount

# Display price in multiple currencies
def display_price_multi_currency(price: float, base_currency: str):
    result = currency_service.multi_currency_display(
        MultiCurrencyDisplayRequest(
            base_amount=price,
            base_currency=base_currency,
            target_currencies=["USD", "GBP", "CHF"]
        )
    )
    return result.conversions
```

### PDF Generation Integration
```python
# Format price with currency symbol
def format_price_with_currency(amount: float, currency_code: str):
    currency = currency_service.get_currency_by_code(currency_code)
    rounded = currency_service.apply_rounding(amount, currency_code)
    return f"{currency.symbol}{rounded:,.2f}"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing rate | Add exchange rate or enable reverse calculation |
| Wrong rounding | Check rounding rule configuration |
| Update fails | Verify API connectivity and source |
| Slow queries | Add indexes, enable caching |
| Duplicate currency | Check existing currencies before creating |

## Resources

- Full Guide: `backend/docs/MULTI_CURRENCY_GUIDE.md`
- Demo Script: `backend/demo_currency.py`
- Test Suite: `backend/tests/test_currency_service.py`
- API Docs: `/docs` endpoint
