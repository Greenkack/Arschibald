# Multi-Currency System Guide

## Overview

The Multi-Currency System provides comprehensive support for handling multiple currencies in the price matrix system. It includes currency management, exchange rate management, automatic conversions, currency-specific rounding, and historical tracking.

## Features

### 1. Currency Management
- Create and manage multiple currencies
- Support for ISO 4217 currency codes
- Configurable decimal places per currency
- Active/inactive status management
- Default currency selection

### 2. Exchange Rate Management
- Create and update exchange rates between currencies
- Support for multiple rate sources (ECB, manual, API)
- Historical rate tracking
- Automatic rate deactivation when updating
- Bidirectional conversion support

### 3. Currency Conversion
- Convert amounts between any two currencies
- Automatic reverse rate calculation
- Multi-currency display for single amounts
- Date-based historical conversions

### 4. Currency-Specific Rounding
- Configurable rounding modes (ROUND_UP, ROUND_DOWN, ROUND_HALF_UP, etc.)
- Precision control (decimal places)
- Minimum unit rounding (e.g., 5-cent rounding)
- Currency-specific rules

### 5. Exchange Rate History
- Automatic tracking of all rate changes
- Historical rate queries with date ranges
- Source tracking for audit purposes

### 6. Automatic Updates
- API integration for automatic rate updates
- Scheduled update support
- Update logging and error tracking
- Configurable update sources

## Database Schema

### Tables

#### currencies
- `id`: Primary key
- `code`: ISO 4217 currency code (EUR, USD, GBP, etc.)
- `name`: Full currency name
- `symbol`: Currency symbol (€, $, £, etc.)
- `decimal_places`: Number of decimal places (0-4)
- `is_active`: Active status
- `is_default`: Default currency flag
- `created_at`, `updated_at`: Timestamps

#### exchange_rates
- `id`: Primary key
- `from_currency_id`: Source currency
- `to_currency_id`: Target currency
- `rate`: Exchange rate value
- `source`: Rate source (ECB, manual, etc.)
- `valid_from`: Start date
- `valid_to`: End date (optional)
- `is_active`: Active status
- `created_at`, `updated_at`: Timestamps

#### exchange_rate_history
- `id`: Primary key
- `from_currency_code`: Source currency code
- `to_currency_code`: Target currency code
- `rate`: Historical rate value
- `source`: Rate source
- `timestamp`: Rate timestamp
- `created_at`: Record creation timestamp

#### currency_rounding_rules
- `id`: Primary key
- `currency_id`: Currency reference
- `rounding_mode`: Rounding mode (ROUND_HALF_UP, etc.)
- `rounding_precision`: Decimal places
- `min_unit`: Minimum rounding unit (optional)
- `description`: Rule description
- `created_at`, `updated_at`: Timestamps

#### currency_update_logs
- `id`: Primary key
- `update_type`: Update type (manual, automatic, api)
- `source`: Update source
- `currencies_updated`: Number of currencies updated
- `rates_updated`: Number of rates updated
- `status`: Update status (success, partial, failed)
- `error_message`: Error details (if any)
- `started_at`, `completed_at`: Timestamps

## API Endpoints

### Currency Management

#### Create Currency
```http
POST /api/v1/currency/currencies
Content-Type: application/json

{
  "code": "EUR",
  "name": "Euro",
  "symbol": "€",
  "decimal_places": 2,
  "is_active": true,
  "is_default": true
}
```

#### List Currencies
```http
GET /api/v1/currency/currencies?active_only=false
```

#### Get Currency by Code
```http
GET /api/v1/currency/currencies/code/EUR
```

#### Update Currency
```http
PUT /api/v1/currency/currencies/1
Content-Type: application/json

{
  "name": "European Euro",
  "is_active": true
}
```

#### Delete Currency
```http
DELETE /api/v1/currency/currencies/1
```

#### Get Default Currency
```http
GET /api/v1/currency/currencies/default/get
```

### Exchange Rate Management

#### Create Exchange Rate
```http
POST /api/v1/currency/exchange-rates
Content-Type: application/json

{
  "from_currency_code": "EUR",
  "to_currency_code": "USD",
  "rate": 1.08,
  "source": "ECB",
  "valid_from": "2024-01-01T00:00:00Z",
  "is_active": true
}
```

#### Get Exchange Rate
```http
GET /api/v1/currency/exchange-rates/EUR/USD?date=2024-01-01T00:00:00Z
```

#### List Exchange Rates
```http
GET /api/v1/currency/exchange-rates?currency_code=EUR&active_only=true
```

### Currency Conversion

#### Convert Currency
```http
POST /api/v1/currency/convert
Content-Type: application/json

{
  "amount": 1000.0,
  "from_currency": "EUR",
  "to_currency": "USD",
  "date": "2024-01-01T00:00:00Z"
}
```

Response:
```json
{
  "original_amount": 1000.0,
  "converted_amount": 1080.0,
  "from_currency": "EUR",
  "to_currency": "USD",
  "exchange_rate": 1.08,
  "conversion_date": "2024-01-01T00:00:00Z",
  "source": "ECB"
}
```

#### Multi-Currency Display
```http
POST /api/v1/currency/multi-display
Content-Type: application/json

{
  "base_amount": 16999.00,
  "base_currency": "EUR",
  "target_currencies": ["USD", "GBP", "CHF", "JPY"]
}
```

### Currency Rounding

#### Create Rounding Rule
```http
POST /api/v1/currency/rounding-rules
Content-Type: application/json

{
  "currency_code": "CHF",
  "rounding_mode": "ROUND_HALF_UP",
  "rounding_precision": 2,
  "min_unit": 0.05,
  "description": "Swiss Franc 5-cent rounding"
}
```

#### Get Rounding Rule
```http
GET /api/v1/currency/rounding-rules/CHF
```

#### Apply Rounding
```http
POST /api/v1/currency/apply-rounding?amount=123.456&currency_code=CHF
```

### Exchange Rate History

#### Get History
```http
GET /api/v1/currency/history/EUR/USD?start_date=2024-01-01&end_date=2024-12-31&limit=100
```

### Automatic Updates

#### Update Exchange Rates
```http
POST /api/v1/currency/update-rates
Content-Type: application/json

{
  "source": "ECB",
  "currencies": ["USD", "GBP", "CHF"],
  "force": false
}
```

### Statistics

#### Get Statistics
```http
GET /api/v1/currency/statistics
```

Response:
```json
{
  "total_currencies": 8,
  "active_currencies": 7,
  "total_exchange_rates": 15,
  "active_exchange_rates": 12,
  "last_update": "2024-01-01T12:00:00Z",
  "default_currency": "EUR"
}
```

## Usage Examples

### Python Service Usage

```python
from backend.services.currency_service import CurrencyService
from backend.models.currency_schemas import (
    CurrencyCreate, ExchangeRateCreate, CurrencyConversionRequest
)

# Create service
service = CurrencyService(db)

# Create currency
currency = service.create_currency(
    CurrencyCreate(
        code="EUR",
        name="Euro",
        symbol="€",
        decimal_places=2,
        is_default=True
    )
)

# Create exchange rate
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

# Convert currency
result = service.convert_currency(
    CurrencyConversionRequest(
        amount=1000.0,
        from_currency="EUR",
        to_currency="USD"
    )
)

print(f"1000 EUR = {result.converted_amount} USD")
```

### Frontend Integration

```typescript
import axios from 'axios';

// Convert currency
const convertCurrency = async (amount: number, from: string, to: string) => {
  const response = await axios.post('/api/v1/currency/convert', {
    amount,
    from_currency: from,
    to_currency: to
  });
  return response.data;
};

// Multi-currency display
const displayMultiCurrency = async (amount: number, baseCurrency: string) => {
  const response = await axios.post('/api/v1/currency/multi-display', {
    base_amount: amount,
    base_currency: baseCurrency,
    target_currencies: ['USD', 'GBP', 'CHF', 'JPY']
  });
  return response.data;
};

// Usage
const result = await convertCurrency(1000, 'EUR', 'USD');
console.log(`Converted: ${result.converted_amount} ${result.to_currency}`);
```

## Rounding Modes

### Available Modes

- **ROUND_UP**: Always round up
- **ROUND_DOWN**: Always round down
- **ROUND_HALF_UP**: Round to nearest, ties go up (standard)
- **ROUND_HALF_DOWN**: Round to nearest, ties go down
- **ROUND_CEILING**: Round towards positive infinity
- **ROUND_FLOOR**: Round towards negative infinity

### Examples

```python
# Standard 2 decimal places
service.apply_rounding(123.456, "EUR")  # → 123.46

# 5-cent rounding
service.apply_rounding(1.22, "CHF")  # → 1.20
service.apply_rounding(1.23, "CHF")  # → 1.25

# No decimals (JPY)
service.apply_rounding(123.456, "JPY")  # → 123.0
```

## Best Practices

### 1. Currency Setup
- Always set one currency as default
- Use standard ISO 4217 codes
- Configure decimal places correctly for each currency
- Set appropriate rounding rules

### 2. Exchange Rates
- Update rates regularly (daily recommended)
- Use reliable sources (ECB, central banks)
- Keep historical rates for audit purposes
- Deactivate old rates instead of deleting

### 3. Conversions
- Always apply currency-specific rounding
- Handle missing rates gracefully
- Use historical rates for past transactions
- Cache frequently used conversions

### 4. Performance
- Index currency codes for fast lookups
- Cache active exchange rates
- Limit history queries with date ranges
- Use batch operations for multiple conversions

### 5. Error Handling
- Validate currency codes before operations
- Check for missing exchange rates
- Handle API failures gracefully
- Log all update operations

## Migration Guide

### Initial Setup

1. Run migration script:
```bash
python backend/migrations/add_currency_tables.py
```

2. Seed initial data (included in migration)

3. Configure default currency

4. Add exchange rates

### Updating Existing System

1. Add currency columns to price matrix tables
2. Convert existing prices to multi-currency
3. Set up exchange rates
4. Update price calculation logic
5. Test conversions thoroughly

## Troubleshooting

### Common Issues

#### Missing Exchange Rate
**Problem**: Conversion fails with "No exchange rate found"
**Solution**: Add the required exchange rate or enable reverse rate calculation

#### Incorrect Rounding
**Problem**: Amounts not rounding as expected
**Solution**: Check rounding rule configuration, verify precision and min_unit settings

#### Update Failures
**Problem**: Automatic updates fail
**Solution**: Check API connectivity, verify source configuration, review error logs

#### Performance Issues
**Problem**: Slow conversion queries
**Solution**: Add database indexes, enable caching, optimize rate lookups

## Support

For issues or questions:
- Check the demo script: `backend/demo_currency.py`
- Review test cases: `backend/tests/test_currency_service.py`
- Consult API documentation: `/docs` endpoint
- Contact development team

## Future Enhancements

- Real-time rate updates via WebSocket
- Advanced rate prediction algorithms
- Multi-source rate aggregation
- Currency hedging calculations
- Cryptocurrency support
- Custom rate formulas
- Rate alert system
