# Product Pricing Management System - Complete Guide

## Overview

The Product Pricing Management System provides comprehensive pricing capabilities including:

- **Tiered Pricing**: Different prices based on quantity ranges
- **Customer-Specific Pricing**: Special prices for individual customers
- **Volume Discounts**: Automatic discounts based on purchase quantity
- **Promotional Pricing**: Time-limited promotional campaigns with promo codes
- **Price Lists**: Multiple price lists for different customer segments or regions
- **Price History**: Complete audit trail of all price changes

## Architecture

### Database Schema

```
price_lists
├── product_prices (1:N)
│   └── price_history (1:N)
├── customer_price_lists (1:N)

volume_discounts (standalone)

promotional_pricing
└── promotional_usage (1:N)

customer_specific_prices (standalone)
```

### Key Components

1. **Price Lists**: Container for product prices
2. **Product Prices**: Individual product pricing within a price list
3. **Volume Discounts**: Quantity-based discount rules
4. **Promotional Pricing**: Campaign-based discounts with promo codes
5. **Customer-Specific Prices**: Override prices for specific customers

## Features

### 1. Price Lists

Price lists allow you to maintain different pricing for different customer segments, regions, or time periods.

**Creating a Price List:**

```python
POST /api/v1/pricing/price-lists
{
  "name": "Standard Retail Prices 2024",
  "description": "Standard pricing for retail customers",
  "currency": "EUR",
  "is_active": true,
  "is_default": true,
  "valid_from": "2024-01-01T00:00:00Z",
  "valid_until": "2024-12-31T23:59:59Z"
}
```

**Features:**
- Multiple price lists can coexist
- One price list can be marked as default
- Price lists have validity periods
- Supports different currencies

### 2. Tiered Pricing

Tiered pricing allows different prices based on quantity ranges.

**Example:**

```python
POST /api/v1/pricing/product-prices
{
  "price_list_id": 1,
  "product_id": 100,
  "base_price": 100.00,
  "pricing_type": "tiered",
  "tier_config": [
    {"min_quantity": 1, "max_quantity": 10, "price": 100.00},
    {"min_quantity": 11, "max_quantity": 50, "price": 95.00},
    {"min_quantity": 51, "max_quantity": null, "price": 90.00}
  ]
}
```

**Pricing Logic:**
- 1-10 units: €100.00 each
- 11-50 units: €95.00 each (5% discount)
- 51+ units: €90.00 each (10% discount)

### 3. Volume Discounts

Volume discounts apply automatic discounts based on purchase quantity.

**Creating a Volume Discount:**

```python
POST /api/v1/pricing/volume-discounts
{
  "name": "Bulk Purchase Discount",
  "description": "10% off for orders of 100+ units",
  "product_id": 100,  // null for all products
  "discount_type": "percentage",
  "min_quantity": 100,
  "max_quantity": null,
  "discount_value": 10.0,
  "is_active": true,
  "valid_from": "2024-01-01T00:00:00Z",
  "valid_until": "2024-12-31T23:59:59Z"
}
```

**Discount Types:**
- `percentage`: Discount as percentage (e.g., 10%)
- `fixed_amount`: Fixed amount off (e.g., €50)
- `tiered_percentage`: Different percentages for different quantity ranges

**Tiered Volume Discount Example:**

```python
{
  "name": "Tiered Bulk Discount",
  "discount_type": "tiered_percentage",
  "tier_config": [
    {"min_qty": 50, "max_qty": 99, "discount": 5.0},
    {"min_qty": 100, "max_qty": 499, "discount": 10.0},
    {"min_qty": 500, "max_qty": null, "discount": 15.0}
  ]
}
```

### 4. Promotional Pricing

Promotional pricing allows time-limited campaigns with optional promo codes.

**Creating a Promotion:**

```python
POST /api/v1/pricing/promotions
{
  "name": "Summer Sale 2024",
  "description": "20% off all solar panels",
  "promo_code": "SUMMER2024",
  "discount_type": "percentage",
  "discount_value": 20.0,
  "max_discount_amount": 500.00,  // Cap discount at €500
  "product_ids": [100, 101, 102],  // Specific products
  "customer_ids": null,  // All customers
  "max_uses_total": 1000,
  "max_uses_per_customer": 1,
  "is_active": true,
  "valid_from": "2024-06-01T00:00:00Z",
  "valid_until": "2024-08-31T23:59:59Z"
}
```

**Features:**
- Optional promo codes
- Usage limits (total and per customer)
- Product/category/customer restrictions
- Maximum discount caps
- Automatic usage tracking

**Validating a Promo Code:**

```python
POST /api/v1/pricing/promotions/validate?promo_code=SUMMER2024&customer_id=1&product_id=100
```

### 5. Customer-Specific Pricing

Override prices for specific customers (e.g., VIP customers, contract pricing).

**Creating Customer-Specific Price:**

```python
POST /api/v1/pricing/customer-prices
{
  "customer_id": 1,
  "product_id": 100,
  "special_price": 85.00,
  "discount_percentage": 15.0,
  "reason": "VIP customer - annual contract",
  "is_active": true,
  "valid_from": "2024-01-01T00:00:00Z",
  "valid_until": "2024-12-31T23:59:59Z"
}
```

**Features:**
- Highest priority in price calculation
- Requires approval workflow (optional)
- Reason tracking for audit
- Validity periods

### 6. Price Calculation

The system automatically calculates the final price considering all applicable discounts.

**Calculate Price:**

```python
POST /api/v1/pricing/calculate
{
  "product_id": 100,
  "quantity": 150,
  "customer_id": 1,
  "promo_code": "SUMMER2024",
  "price_list_id": null  // Uses default or customer's price list
}
```

**Response:**

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
    "applied_discounts": [
      {
        "type": "customer_specific",
        "amount": 2250.00,
        "description": "VIP customer - annual contract"
      },
      {
        "type": "volume_discount",
        "amount": 1275.00,
        "description": "Bulk Purchase Discount"
      },
      {
        "type": "promotional",
        "amount": 2295.00,
        "description": "Summer Sale 2024",
        "code": "SUMMER2024"
      }
    ]
  },
  "formatted_price": "6.930,00 €",
  "savings": 5820.00,
  "savings_percentage": 45.65
}
```

### 7. Price History

All price changes are automatically tracked.

**Get Price History:**

```python
GET /api/v1/pricing/product-prices/{product_price_id}/history
```

**Response:**

```json
[
  {
    "id": 1,
    "product_price_id": 1,
    "old_price": 100.00,
    "new_price": 95.00,
    "change_percentage": -5.0,
    "change_reason": "Market adjustment",
    "changed_by": "admin@example.com",
    "changed_at": "2024-01-15T10:30:00Z"
  }
]
```

## Price Calculation Priority

The system applies discounts in the following order:

1. **Customer-Specific Price** (highest priority)
   - If exists, replaces base price
   
2. **Volume Discounts**
   - Applied to subtotal
   - Multiple volume discounts can stack
   
3. **Promotional Discounts**
   - Applied after volume discounts
   - Subject to usage limits and restrictions

## German Number Formatting

All prices are formatted in German locale:

- **Currency**: `16.999,00 €` (not `€16,999.00`)
- **Decimal**: Comma (`,`) as decimal separator
- **Thousands**: Dot (`.`) as thousands separator
- **Precision**: Always 2 decimal places

## API Endpoints

### Price Lists

- `POST /api/v1/pricing/price-lists` - Create price list
- `GET /api/v1/pricing/price-lists` - Get all price lists
- `GET /api/v1/pricing/price-lists/{id}` - Get price list by ID
- `PUT /api/v1/pricing/price-lists/{id}` - Update price list
- `DELETE /api/v1/pricing/price-lists/{id}` - Delete price list

### Product Prices

- `POST /api/v1/pricing/product-prices` - Create product price
- `PUT /api/v1/pricing/product-prices/{id}` - Update product price
- `GET /api/v1/pricing/product-prices/{id}/history` - Get price history

### Volume Discounts

- `POST /api/v1/pricing/volume-discounts` - Create volume discount
- `GET /api/v1/pricing/volume-discounts` - Get volume discounts
- `PUT /api/v1/pricing/volume-discounts/{id}` - Update volume discount

### Promotional Pricing

- `POST /api/v1/pricing/promotions` - Create promotion
- `GET /api/v1/pricing/promotions/{code}` - Get promotion by code
- `POST /api/v1/pricing/promotions/validate` - Validate promo code

### Customer-Specific Pricing

- `POST /api/v1/pricing/customer-prices` - Create customer price
- `GET /api/v1/pricing/customer-prices/{customer_id}/{product_id}` - Get customer price

### Price Calculation

- `POST /api/v1/pricing/calculate` - Calculate final price

## Best Practices

### 1. Price List Management

- Always have one default price list
- Use descriptive names with dates
- Set appropriate validity periods
- Archive old price lists instead of deleting

### 2. Tiered Pricing

- Ensure no gaps in quantity ranges
- Make tier boundaries clear to customers
- Test calculations with edge cases

### 3. Volume Discounts

- Don't overlap with tiered pricing
- Set reasonable minimum quantities
- Monitor discount effectiveness

### 4. Promotional Pricing

- Use unique, memorable promo codes
- Set usage limits to control costs
- Monitor usage in real-time
- Communicate end dates clearly

### 5. Customer-Specific Pricing

- Document reasons for special pricing
- Implement approval workflow
- Review periodically
- Set expiration dates

### 6. Price Changes

- Always provide change reasons
- Notify affected customers
- Maintain price history
- Test impact before applying

## Security Considerations

1. **Access Control**: Restrict pricing management to authorized users
2. **Approval Workflow**: Require approval for customer-specific pricing
3. **Audit Trail**: All changes are logged with user and timestamp
4. **Validation**: All inputs are validated before processing
5. **Rate Limiting**: API endpoints are rate-limited

## Performance Optimization

1. **Caching**: Frequently accessed prices are cached
2. **Indexing**: Database indexes on key fields
3. **Batch Operations**: Support for bulk price updates
4. **Lazy Loading**: Price history loaded on demand

## Troubleshooting

### Price Not Calculating Correctly

1. Check price list validity dates
2. Verify customer price list assignments
3. Check discount validity periods
4. Review discount applicability rules

### Promo Code Not Working

1. Verify code is active and within validity period
2. Check usage limits
3. Verify product/customer restrictions
4. Check if code has expired

### Customer Not Getting Special Price

1. Verify customer-specific price is active
2. Check validity dates
3. Ensure price is approved (if required)
4. Check customer ID matches

## Migration from Legacy System

If migrating from an existing pricing system:

1. Export all current prices
2. Create price lists for different segments
3. Import product prices
4. Set up volume discounts
5. Migrate promotional campaigns
6. Import customer-specific prices
7. Test calculations thoroughly
8. Run parallel for validation period

## Support

For issues or questions:
- Check API documentation: `/docs`
- Review error messages in responses
- Check logs for detailed error information
- Contact support with specific examples

## Changelog

### Version 1.0.0 (2024-01-01)
- Initial release
- Tiered pricing support
- Volume discounts
- Promotional pricing
- Customer-specific pricing
- Price history tracking
- German number formatting
