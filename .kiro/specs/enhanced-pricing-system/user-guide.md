# Enhanced Pricing System - User Guide

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Product Configuration](#product-configuration)
4. [Calculate Per Methods](#calculate-per-methods)
5. [Profit Margin Management](#profit-margin-management)
6. [Pricing Rules and Modifications](#pricing-rules-and-modifications)
7. [System-Specific Pricing](#system-specific-pricing)
8. [PDF Integration](#pdf-integration)
9. [Common Workflows](#common-workflows)
10. [Troubleshooting](#troubleshooting)

## Overview

The Enhanced Pricing System provides comprehensive pricing management for PV and heat pump systems. It supports:

- Dynamic pricing calculations with multiple calculation methods
- Flexible profit margin management
- Advanced discount and surcharge systems
- Separate PV and heat pump pricing engines
- Real-time pricing updates
- Automatic PDF integration with dynamic keys

## Getting Started

### Accessing the Pricing System

1. **Admin Panel**: Navigate to the Admin Panel for pricing configuration
2. **Product Database**: Manage individual product pricing
3. **Pricing Rules**: Configure global and category-level pricing rules
4. **Profit Margins**: Set up margin configurations

### Initial Setup

1. Configure your product database with pricing information
2. Set up profit margins (global, category, or product-specific)
3. Configure VAT rates for different product categories
4. Set up any default pricing rules or modifications

## Product Configuration

### Adding Products with Pricing

When adding products to the database, you can configure:

- **Purchase Price (Net)**: The cost price of the product
- **Margin Configuration**: How profit margins are calculated
- **Calculate Per Method**: How quantities are calculated (per piece, per meter, etc.)
- **Pricing Category**: For category-level pricing rules

### Product Fields and Pricing Impact

| Field | Impact on Pricing | Example |
|-------|------------------|---------|
| `calculate_per` | Determines calculation method | "Stück", "Meter", "pauschal", "kWp" |
| `price_euro` | Base selling price | 180.50 |
| `category` | Applies category-specific margins | "PV Module", "Heat Pump" |
| `technology` | Technology-specific pricing adjustments | "Monocrystalline", "Polycrystalline" |
| `efficiency_percent` | Efficiency-based pricing variations | 22.1 |
| `warranty_years` | Warranty-based pricing adjustments | 25 |
| `capacity_w` | Capacity-based calculations | 400 |
| `power_kw` | Power-based calculations | 10.5 |

## Calculate Per Methods

The system supports multiple calculation methods for different product types:

### 1. Per Piece (Stück)

- **Use Case**: Individual components like modules, inverters
- **Calculation**: `Total Price = Unit Price × Quantity`
- **Example**: 20 PV modules × €180 = €3,600

### 2. Per Meter (Meter)

- **Use Case**: Cables, mounting rails, piping
- **Calculation**: `Total Price = Price per Meter × Length in Meters`
- **Example**: 50m cable × €2.50/m = €125

### 3. Lump Sum (pauschal)

- **Use Case**: Installation services, planning, permits
- **Calculation**: `Total Price = Fixed Amount`
- **Example**: Installation service = €2,500 (regardless of system size)

### 4. Per kWp (kWp)

- **Use Case**: System-dependent components, mounting systems
- **Calculation**: `Total Price = Price per kWp × System Size in kWp`
- **Example**: Mounting system: 8 kWp × €150/kWp = €1,200

### Configuring Calculate Per Methods

1. In the product database, select the appropriate `calculate_per` value
2. Set the unit price accordingly
3. The system will automatically apply the correct calculation method

## Profit Margin Management

### Margin Types

1. **Percentage-Based Margins**
   - Formula: `Selling Price = Purchase Price × (1 + Margin%)`
   - Example: €100 purchase price + 25% margin = €125 selling price

2. **Fixed-Amount Margins**
   - Formula: `Selling Price = Purchase Price + Fixed Amount`
   - Example: €100 purchase price + €30 fixed margin = €130 selling price

### Margin Hierarchy

The system applies margins in this priority order:

1. **Product-specific margins** (highest priority)
2. **Category-level margins**
3. **Global margins** (lowest priority)

### Setting Up Margins

#### Global Margins

1. Go to Admin Panel → Profit Margin Management
2. Set default margin percentage or fixed amount
3. This applies to all products without specific margins

#### Category Margins

1. Navigate to Admin Panel → Pricing Rules
2. Create a new rule for a specific category
3. Set margin type and value

#### Product-Specific Margins

1. In Product Database, edit individual products
2. Set custom margin for that specific product
3. This overrides category and global margins

## Pricing Rules and Modifications

### Discounts

#### Percentage Discounts

- Applied as: `Discounted Price = Original Price × (1 - Discount%)`
- Example: €1,000 with 5% discount = €950

#### Fixed Amount Discounts

- Applied as: `Discounted Price = Original Price - Fixed Amount`
- Example: €1,000 with €100 discount = €900

### Surcharges

#### Percentage Surcharges

- Applied as: `Final Price = Base Price × (1 + Surcharge%)`
- Example: €1,000 with 3% surcharge = €1,030

#### Fixed Amount Surcharges

- Applied as: `Final Price = Base Price + Fixed Amount`
- Example: €1,000 with €50 surcharge = €1,050

### Pricing Formula

The complete pricing formula is:

```
Final Price = (Matrix Price + Accessories) × (1 - Discount%) × (1 + Surcharge%) - Fixed Discounts + Fixed Surcharges
```

### Creating Pricing Rules

1. Navigate to Admin Panel → Pricing Rules
2. Click "Add New Rule"
3. Configure:
   - Rule name and description
   - Rule type (discount/surcharge)
   - Application scope (global/category/product)
   - Conditions and values
4. Set priority and activation status

## System-Specific Pricing

### PV System Pricing

PV systems use the PV Pricing Engine which handles:

- **Modules**: Calculated per piece
- **Inverters**: Calculated per piece or per kWp
- **Mounting Systems**: Calculated per kWp
- **Cables**: Calculated per meter
- **Storage Systems**: Calculated per piece or per kWh

### Heat Pump Pricing

Heat pump systems use the Heat Pump Pricing Engine which handles:

- **Heat Pump Units**: Calculated per piece
- **Installation Components**: Mix of per piece and lump sum
- **Piping**: Calculated per meter
- **Electrical Components**: Calculated per piece
- **BEG Subsidies**: Automatic integration

### Combined Systems

When both PV and heat pump are selected:

1. Each system is calculated separately first
2. Combined totals are calculated
3. System-specific discounts may apply
4. PDF shows separate breakdowns for each system

## PDF Integration

### Dynamic Keys

The system automatically generates dynamic keys for PDF templates:

- `BASE_PRICE_NET`: Net base price
- `BASE_PRICE_GROSS`: Gross base price
- `FINAL_PRICE_NET`: Final net price
- `FINAL_PRICE_GROSS`: Final gross price
- `VAT_AMOUNT`: VAT amount
- `TOTAL_DISCOUNT`: Total discount amount
- `TOTAL_SURCHARGE`: Total surcharge amount

### Component-Specific Keys

Each component gets its own keys:

- `PV_MODULE_PRICE`: PV module total price
- `INVERTER_PRICE`: Inverter total price
- `STORAGE_PRICE`: Storage system total price
- `HEATPUMP_PRICE`: Heat pump total price

### Using Keys in Templates

Keys are automatically populated in PDF templates. No manual intervention required.

## Common Workflows

### Workflow 1: Setting Up a New Product

1. Add product to database with basic information
2. Set purchase price and calculate_per method
3. Configure profit margin (if different from global)
4. Test pricing calculation
5. Verify PDF key generation

### Workflow 2: Creating a PV System Quote

1. Select PV components in solar calculator
2. System automatically calculates pricing
3. Apply any discounts or surcharges
4. Review pricing breakdown
5. Generate PDF with dynamic pricing

### Workflow 3: Adjusting Profit Margins

1. Navigate to Profit Margin Management
2. Select scope (global/category/product)
3. Adjust margin values
4. Preview impact on existing quotes
5. Apply changes

### Workflow 4: Managing Pricing Rules

1. Go to Pricing Rules management
2. Create or edit rules
3. Set conditions and priorities
4. Test rule application
5. Monitor rule performance

## Troubleshooting

### Common Issues and Solutions

#### Issue: Incorrect Pricing Calculations

**Symptoms**: Prices don't match expected values
**Solutions**:

1. Check calculate_per method is correct
2. Verify profit margins are applied correctly
3. Review pricing rule priorities
4. Check for conflicting modifications

#### Issue: PDF Keys Not Populating

**Symptoms**: PDF shows placeholder keys instead of values
**Solutions**:

1. Verify pricing calculation completed successfully
2. Check dynamic key generation
3. Ensure PDF template uses correct key names
4. Review PDF integration logs

#### Issue: Real-time Updates Not Working

**Symptoms**: Prices don't update when components change
**Solutions**:

1. Check browser console for JavaScript errors
2. Verify session state management
3. Clear browser cache
4. Restart application if needed

#### Issue: Calculate Per Method Problems

**Symptoms**: Wrong calculation method applied
**Solutions**:

1. Verify product's calculate_per field value
2. Check for typos in calculate_per values
3. Ensure quantity units match calculation method
4. Review product configuration

### Getting Help

1. Check application logs for error messages
2. Review pricing calculation breakdown
3. Verify product and rule configurations
4. Contact system administrator if issues persist

### Performance Issues

If pricing calculations are slow:

1. Check database indexes on pricing tables
2. Review caching configuration
3. Monitor system resources
4. Consider optimizing complex pricing rules

## Best Practices

### Product Configuration

- Use consistent calculate_per values
- Set realistic profit margins
- Keep product information up to date
- Regular pricing audits

### Pricing Rules

- Keep rules simple and clear
- Avoid conflicting rules
- Document rule purposes
- Regular rule reviews

### System Maintenance

- Monitor pricing calculation performance
- Regular database maintenance
- Keep pricing data backed up
- Update documentation as system evolves

## Advanced Features

### Bulk Pricing Updates

- Use admin interface for bulk margin updates
- Import/export pricing configurations
- Batch processing for large product catalogs

### Pricing Analytics

- Monitor most profitable products
- Track pricing trends
- Analyze discount/surcharge usage
- Generate pricing reports

### Integration with External Systems

- API endpoints for pricing calculations
- Export pricing data
- Integration with accounting systems
- Real-time pricing feeds
