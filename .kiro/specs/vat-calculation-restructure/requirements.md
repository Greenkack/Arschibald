# Requirements Document

## Introduction

This document outlines the requirements for restructuring the VAT calculation order in the solar calculator. After component selection, both VAT and provision must be added internally. The PDF should display the VAT-inclusive price directly, which also includes the hidden provision. At the end, VAT is deducted to show the final net price.

## Requirements

### Requirement 1: VAT Calculation Order Restructuring

**User Story:** As a sales representative, I want the system to internally add VAT and provision after component selection, display VAT-inclusive prices in the PDF, and deduct VAT at the end for the final net price.

#### Acceptance Criteria

1. WHEN components are selected THEN the system SHALL calculate base component costs first
2. WHEN internal calculations are performed THEN the system SHALL add both VAT and provision (default 1500€, hidden) to the component total
3. WHEN displaying prices in PDF THEN the system SHALL show VAT-inclusive prices that contain the hidden provision
4. WHEN discounts and surcharges are applied THEN they SHALL be calculated on the VAT-inclusive amount (which includes hidden provision)
5. WHEN final calculation is performed THEN the system SHALL deduct VAT from the total to show net final price

### Requirement 2: Provision Integration in Calculation Flow

**User Story:** As a business owner, I want the provision to be included internally in the calculation flow together with VAT addition.

#### Acceptance Criteria

1. WHEN provision is configured THEN it SHALL default to 1500€ and remain hidden from user interface
2. WHEN internal calculations are performed THEN provision SHALL be added together with VAT after component costs
3. WHEN provision amount changes THEN all subsequent calculations SHALL update accordingly
4. IF provision is set to zero THEN the calculation SHALL proceed without provision addition
5. WHEN displaying prices THEN provision SHALL be invisibly included in the VAT-inclusive amounts shown

### Requirement 3: VAT Deduction Process

**User Story:** As a financial analyst, I want VAT to be deducted only at the end of the calculation to show net pricing.

#### Acceptance Criteria

1. WHEN VAT deduction occurs THEN it SHALL be the final step in the calculation process
2. WHEN discounts/surcharges are calculated THEN they SHALL use the gross amount (without VAT considerations)
3. WHEN final VAT deduction occurs THEN it SHALL calculate VAT from the gross total and subtract it
4. IF VAT rate changes THEN the deduction SHALL use the current VAT rate
5. WHEN displaying final price THEN it SHALL show the net amount after VAT deduction

### Requirement 4: Calculation Flow Transparency

**User Story:** As a user, I want to understand how the new calculation flow works even though some steps may be hidden in the interface.

#### Acceptance Criteria

1. WHEN calculation is performed THEN the system SHALL follow the exact sequence: Components → Internal (+VAT +Provision) → Display VAT-inclusive prices → Discounts/Surcharges → -VAT → Net Final Price
2. WHEN debugging is enabled THEN all calculation steps SHALL be visible and traceable
3. WHEN errors occur THEN the system SHALL identify which step in the calculation flow failed
4. IF intermediate values are needed THEN each step SHALL store its result for reference
5. WHEN calculations complete THEN the final net price SHALL be the primary displayed value

### Requirement 5: Integration with Existing Systems

**User Story:** As a system administrator, I want the new VAT calculation order to integrate seamlessly with existing PDF generation and pricing systems.

#### Acceptance Criteria

1. WHEN PDF is generated THEN it SHALL use the net final price from the new calculation flow
2. WHEN pricing data is passed to other systems THEN it SHALL include both gross and net amounts
3. WHEN payment terms are calculated THEN they SHALL be based on the net final price
4. IF other systems expect gross amounts THEN the system SHALL provide both gross and net values
5. WHEN integration points are updated THEN existing functionality SHALL remain intact

### Requirement 6: Backward Compatibility and Migration

**User Story:** As a system maintainer, I want to ensure that existing calculations can be migrated to the new VAT calculation order without data loss.

#### Acceptance Criteria

1. WHEN the new calculation is implemented THEN existing saved calculations SHALL be recalculated using the new flow
2. WHEN migration occurs THEN the system SHALL preserve all component selections and configurations
3. WHEN comparing old vs new calculations THEN the system SHALL provide a comparison report
4. IF discrepancies are found THEN the system SHALL flag them for manual review
5. WHEN migration is complete THEN all systems SHALL use the new calculation order consistently
