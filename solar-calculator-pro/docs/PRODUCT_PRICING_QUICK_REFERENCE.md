# Product Pricing Management - Quick Reference

## Quick Start

### 1. Create a Price List

```bash
POST /api/v1/pricing/price-lists
{
  "name": "Standard 2024",
  "currency": "EUR",
  "is_default": true,
  "valid_from": "2024-01-01T00:00:00Z"
}
```

### 2. Add Product Price

```bash
POST /api/v1/pricing/product-prices
{
  "price_list_id": 1,
  "product_id": 100,
  "base_price": 100.00
}
```

### 3. Calculate Price

```bash
POST /api/v1/pricing/calculate
{
  "product_id": 100,
  "quantity": 10
}
```

## Pricing Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Standard** | Single price for all quantities | Simple products |
| **Tiered** | Different prices per quantity range | Bulk pricing |
| **Volume Discount** | Automatic discount based on quantity | Encourage larger orders |
| **Promotional** | Time-limited campaigns | Sales, promotions |
| **Customer-Specific** | Special prices for specific customers | VIP, contracts |

## Discount Types

| Type | Example | Calculation |
|------|---------|-------------|
| **Percentage** | 10% off | `price * (discount / 100)` |
| **Fixed Amount** | €50 off | `min(discount, price)` |
| **Tiered Percentage** | 5% for 50+, 10% for 100+ | Based on quantity range |

## Common Operations

### Create Tiered Pricing

```json
{
  "pricing_type": "tiered",
  "tier_config": [
    {"min_quantity": 1, "max_quantity": 10, "price": 100.00},
    {"min_quantity": 11, "max_quantity": 50, "price": 95.00},
    {"min_quantity": 51, "max_quantity": null, "price": 90.00}
  ]
}
```

### Create Volume Discount

```json
{
  "name": "Bulk Discount",
  "discount_type": "percentage",
  "min_quantity": 100,
  "discount_value": 10.0,
  "valid_from": "2024-01-01T00:00:00Z"
}
```

### Create Promotion

```json
{
  "name": "Summer Sale",
  "promo_code": "SUMMER2024",
  "discount_type": "percentage",
  "discount_value": 20.0,
  "max_uses_total": 1000,
  "valid_from": "2024-06-01T00:00:00Z",
  "valid_until": "2024-08-31T23:59:59Z"
}
```

### Create Customer Price

```json
{
  "customer_id": 1,
  "product_id": 100,
  "special_price": 85.00,
  "reason": "VIP customer",
  "valid_from": "2024-01-01T00:00:00Z"
}
```

## Price Calculation Flow

```
1. Get Base Price
   ↓
2. Apply Customer-Specific Price (if exists)
   ↓
3. Calculate Subtotal (price × quantity)
   ↓
4. Apply Volume Discounts
   ↓
5. Apply Promotional Discounts
   ↓
6. Calculate Final Price
   ↓
7. Format in German (16.999,00 €)
```

## API Endpoints Cheat Sheet

### Price Lists
```
POST   /api/v1/pricing/price-lists          Create
GET    /api/v1/pricing/price-lists          List all
GET    /api/v1/pricing/price-lists/{id}     Get one
PUT    /api/v1/pricing/price-lists/{id}     Update
DELETE /api/v1/pricing/price-lists/{id}     Delete
```

### Product Prices
```
POST   /api/v1/pricing/product-prices       Create
PUT    /api/v1/pricing/product-prices/{id}  Update
GET    /api/v1/pricing/product-prices/{id}/history  History
```

### Volume Discounts
```
POST   /api/v1/pricing/volume-discounts     Create
GET    /api/v1/pricing/volume-discounts     List
PUT    /api/v1/pricing/volume-discounts/{id} Update
```

### Promotions
```
POST   /api/v1/pricing/promotions           Create
GET    /api/v1/pricing/promotions/{code}    Get
POST   /api/v1/pricing/promotions/validate  Validate
```

### Customer Prices
```
POST   /api/v1/pricing/customer-prices      Create
GET    /api/v1/pricing/customer-prices/{customer_id}/{product_id}  Get
```

### Calculate
```
POST   /api/v1/pricing/calculate            Calculate price
```

## Response Format

### Price Calculation Response

```json
{
  "product_id": 100,
  "quantity": 150,
  "breakdown": {
    "base_price": 100.00,
    "unit_price": 85.00,
    "subtotal": 12750.00,
    "volume_discount": 1275.00,
    "promotional_discount": 2295.00,
    "customer_discount": 2250.00,
    "total_discount": 5820.00,
    "final_price": 6930.00,
    "currency": "EUR",
    "pricing_type": "customer_specific",
    "applied_discounts": [...]
  },
  "formatted_price": "6.930,00 €",
  "savings": 5820.00,
  "savings_percentage": 45.65
}
```

## German Number Formatting

| Value | German Format | English Format |
|-------|---------------|----------------|
| 1234.56 | `1.234,56 €` | `€1,234.56` |
| 16999.00 | `16.999,00 €` | `€16,999.00` |
| 0.99 | `0,99 €` | `€0.99` |

## Priority Order

1. **Customer-Specific Price** (highest)
2. **Volume Discounts**
3. **Promotional Discounts** (lowest)

## Validation Rules

### Price List
- Name: Required, unique, max 255 chars
- Currency: 3-letter code (EUR, USD, etc.)
- Valid from: Required
- Only one default price list allowed

### Product Price
- Base price: Required, > 0
- Tier config: No gaps in quantity ranges
- Margin: 0-100%

### Volume Discount
- Min quantity: Required, ≥ 1
- Max quantity: Must be > min quantity
- Discount value: Required, > 0

### Promotion
- Valid until: Must be after valid from
- Promo code: Unique if provided
- Max uses: ≥ 1 if provided

### Customer Price
- Special price: Required, > 0
- Discount percentage: 0-100%

## Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 400 | Price already exists | Update existing price |
| 400 | Cannot delete default price list | Set another as default first |
| 400 | Promo code already exists | Use unique code |
| 404 | Price list not found | Check ID |
| 404 | Product price not found | Check ID |
| 404 | Promo code not found or expired | Verify code and dates |

## Testing

### Test Price Calculation

```bash
# Standard price
curl -X POST http://localhost:8000/api/v1/pricing/calculate \
  -H "Content-Type: application/json" \
  -d '{"product_id": 100, "quantity": 10}'

# With promo code
curl -X POST http://localhost:8000/api/v1/pricing/calculate \
  -H "Content-Type: application/json" \
  -d '{"product_id": 100, "quantity": 10, "promo_code": "SUMMER2024"}'

# With customer
curl -X POST http://localhost:8000/api/v1/pricing/calculate \
  -H "Content-Type: application/json" \
  -d '{"product_id": 100, "quantity": 10, "customer_id": 1}'
```

## Best Practices

✅ **DO:**
- Set validity periods for all pricing
- Document reasons for price changes
- Test calculations before going live
- Monitor promotional usage
- Archive old price lists

❌ **DON'T:**
- Delete price lists with active prices
- Overlap tiered pricing with volume discounts
- Set unrealistic discount limits
- Forget to set expiration dates
- Skip approval for customer prices

## Quick Troubleshooting

| Issue | Check |
|-------|-------|
| Wrong price calculated | Validity dates, customer assignments |
| Promo code not working | Active status, usage limits, restrictions |
| Customer price not applied | Active status, validity dates, approval |
| Discount not applied | Quantity thresholds, product restrictions |

## Performance Tips

- Cache frequently accessed prices
- Use batch operations for bulk updates
- Index customer_id and product_id
- Lazy load price history
- Set reasonable validity periods

## Security Checklist

- [ ] Restrict pricing management to authorized users
- [ ] Implement approval workflow for customer prices
- [ ] Log all price changes with user info
- [ ] Validate all inputs
- [ ] Rate limit API endpoints
- [ ] Encrypt sensitive pricing data

## Support

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Logs**: `logs/app.log`

## Version

**Current Version**: 1.0.0  
**Last Updated**: 2024-01-01  
**Requirements**: 1.3, 6.1
