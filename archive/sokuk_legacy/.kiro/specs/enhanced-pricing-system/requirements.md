# Requirements Document

## Introduction

This document outlines the requirements for an enhanced pricing calculation system for the PV and heat pump application. The system will provide comprehensive pricing management with dynamic keys for PDF generation, profit margin calculations, and separate handling of PV and heat pump components while supporting combined offers.

## Requirements

### Requirement 1: Dynamic Pricing System with PDF Integration

**User Story:** As a sales representative, I want all pricing values to have dynamic PDF keys so that any calculated price, discount, or surcharge can be automatically included in generated PDFs.

#### Acceptance Criteria

1. WHEN a price is calculated THEN the system SHALL assign a unique dynamic key for PDF template integration
2. WHEN generating a PDF THEN the system SHALL automatically populate all pricing fields using their dynamic keys
3. WHEN pricing modifications are applied THEN each modification SHALL have its own dynamic key for separate PDF display
4. IF multiple pricing components exist THEN each component SHALL maintain separate dynamic keys for granular PDF control

### Requirement 2: Comprehensive Product Database Pricing

**User Story:** As an administrator, I want to manage individual prices for all products in the database with the ability to set profit margins and pricing rules.

#### Acceptance Criteria

1. WHEN adding a product THEN the system SHALL allow entry of purchase price (Einkaufspreis) and selling price
2. WHEN configuring profit margins THEN the system SHALL support both fixed amount and percentage-based markups
3. WHEN a product has a purchase price of 1200€ THEN the system SHALL allow setting a selling price of 2000€ through markup configuration
4. IF profit margins are configured THEN the system SHALL automatically calculate selling prices from purchase prices
5. WHEN displaying prices THEN the system SHALL clearly distinguish between purchase price, markup, and final selling price

### Requirement 3: Separate PV and Heat Pump Pricing

**User Story:** As a system user, I want PV and heat pump calculations to be completely separate while supporting combined offers.

#### Acceptance Criteria

1. WHEN calculating PV systems THEN the system SHALL use only PV-related products and pricing rules
2. WHEN calculating heat pump systems THEN the system SHALL use only heat pump-related products and pricing rules
3. WHEN both systems are selected THEN the system SHALL calculate each separately first
4. IF both systems are in one offer THEN the PDF SHALL display PV pricing, heat pump pricing, and combined totals separately
5. WHEN generating combined offers THEN the system SHALL maintain separate line items for each system type

### Requirement 4: Advanced Pricing Modifications

**User Story:** As a sales representative, I want comprehensive control over discounts, surcharges, and additional costs with transparent calculation formulas.

#### Acceptance Criteria

1. WHEN applying discounts THEN the system SHALL support percentage-based and fixed-amount discounts
2. WHEN adding surcharges THEN the system SHALL support percentage-based and fixed-amount surcharges  
3. WHEN calculating final prices THEN the system SHALL use the formula: (Matrix Price + Accessories) × (1 - Discount%) × (1 + Surcharge%) - Fixed Discounts + Fixed Surcharges
4. IF accessories are included THEN they SHALL be added before percentage calculations
5. WHEN modifications are applied THEN the system SHALL show detailed breakdown of each modification

### Requirement 5: Component Selection and Pricing Integration

**User Story:** As a user, I want component selection in the solar calculator to automatically integrate with pricing calculations for accurate cost estimation.

#### Acceptance Criteria

1. WHEN selecting PV modules THEN the system SHALL automatically calculate costs based on quantity and unit price
2. WHEN choosing inverters THEN the system SHALL include inverter costs in the total calculation
3. WHEN adding battery storage THEN the system SHALL factor storage costs into the final price
4. IF optional accessories are selected THEN they SHALL be added to the base system cost
5. WHEN component quantities change THEN prices SHALL update automatically in real-time

### Requirement 6: Final Price Calculation for Economic Analysis

**User Story:** As a financial analyst, I want accurate final pricing to enable precise calculations of payback period, ROI, and profitability metrics.

#### Acceptance Criteria

1. WHEN final price is calculated THEN it SHALL include all components, accessories, modifications, and taxes
2. WHEN performing economic analysis THEN the system SHALL use the final price for payback calculations
3. WHEN calculating ROI THEN the system SHALL use the final price as the investment amount
4. IF financing options are selected THEN the system SHALL calculate based on financed amounts
5. WHEN generating profitability reports THEN all calculations SHALL be based on the accurate final price

### Requirement 7: VAT and Tax Management

**User Story:** As an administrator, I want flexible VAT and tax management that can be applied to final pricing calculations.

#### Acceptance Criteria

1. WHEN configuring VAT THEN the system SHALL support different VAT rates for different product categories
2. WHEN calculating final prices THEN VAT SHALL be applied to the net total after all modifications
3. WHEN displaying prices THEN the system SHALL clearly show net price, VAT amount, and gross price
4. IF tax exemptions apply THEN the system SHALL support zero VAT calculations
5. WHEN generating invoices THEN tax calculations SHALL be clearly itemized

### Requirement 8: Profit Margin Configuration

**User Story:** As a business owner, I want to configure profit margins at the product level and globally to ensure consistent profitability.

#### Acceptance Criteria

1. WHEN setting product margins THEN the system SHALL support individual margin configuration per product
2. WHEN applying global margins THEN the system SHALL allow override at the product level
3. WHEN margins are percentage-based THEN the system SHALL calculate: Selling Price = Purchase Price × (1 + Margin%)
4. IF margins are fixed amounts THEN the system SHALL calculate: Selling Price = Purchase Price + Fixed Margin
5. WHEN displaying pricing THEN the system SHALL show purchase price, margin, and selling price separately

### Requirement 9: Accessories and Optional Components

**User Story:** As a sales representative, I want to manage optional accessories and components that can be added to base system pricing.

#### Acceptance Criteria

1. WHEN configuring accessories THEN each accessory SHALL have its own price and dynamic PDF key
2. WHEN accessories are selected THEN they SHALL be added to the base system price
3. WHEN generating quotes THEN accessories SHALL be listed separately in the pricing breakdown
4. IF accessories have different VAT rates THEN the system SHALL handle mixed VAT calculations
5. WHEN accessories are optional THEN the system SHALL clearly indicate optional vs. required components

### Requirement 10: Real-time Price Updates

**User Story:** As a user, I want all pricing calculations to update in real-time as I modify system configurations or pricing parameters.

#### Acceptance Criteria

1. WHEN component quantities change THEN all related prices SHALL update immediately
2. WHEN discounts are modified THEN the final price SHALL recalculate automatically
3. WHEN accessories are added/removed THEN the total price SHALL reflect changes instantly
4. IF profit margins are adjusted THEN selling prices SHALL update in real-time
5. WHEN any pricing parameter changes THEN all dependent calculations SHALL update automatically
