# Implementation Plan

- [x] 1. Set up enhanced pricing system foundation

  - Create core directory structure for pricing modules
  - Analyze existing comprehensive product database structure with all fields (id, category, model_name, brand, price_euro, calculate_per, capacity_w, storage_power_kw, power_kw, max_cycles, warranty_years, technology, feature, design, upgrade, max_kwh_capacity, outdoor_opt, self_supply_feature, shadow_fading, smart_home, length_m, width_m, weight_kg, efficiency_percent, origin_country, description, pros, cons, rating, image_base64, created_at, updated_at)
  - Implement base pricing engine class with dynamic key generation that leverages all existing product fields
  - Create unit tests for core pricing calculations using comprehensive product data
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Implement dynamic key management system

  - [x] 2.1 Create DynamicKeyManager class with key generation logic

    - Write DynamicKeyManager class with generate_keys() and register_key() methods
    - Implement key categorization system (pricing, components, discounts, etc.)
    - Create PDF-ready formatting methods for dynamic keys
    - Write unit tests for key generation and conflict resolution
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 2.2 Implement key validation and conflict resolution

    - Write validation logic for dynamic key naming conventions
    - Implement conflict resolution for duplicate keys
    - Create key registry system for tracking all generated keys
    - Write tests for validation and conflict scenarios
    - _Requirements: 1.1, 1.4_

- [x] 3. Extend product database with enhanced pricing fields

  - [x] 3.1 Add missing pricing fields to existing product schema

    - Add purchase_price_net, margin_type, margin_value columns to products table (building on existing calculate_per field)
    - Create pricing_rules table for advanced pricing configurations
    - Create pricing_history table for audit trail
    - Implement migration script that preserves existing data including calculate_per field
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.2 Update product_db.py with enhanced pricing functionality

    - Extend existing add_product() and update_product() functions to handle all pricing fields including calculate_per
    - Implement calculation logic for different calculate_per values (per piece, per meter, lump sum, per kWp, etc.)
    - Add functions for managing purchase prices and profit margins
    - Implement pricing history tracking for all existing product fields
    - Write unit tests for enhanced pricing database functions
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
-
- [x] 4. Implement profit margin management system

  - [x] 4.1 Create ProfitMarginManager class with calculate_per support

    - Write ProfitMarginManager with set_product_margin() and calculate_selling_price() methods
    - Implement MarginConfig and MarginBreakdown data classes
    - Create logic for percentage-based and fixed-amount margins with calculate_per integration
    - Add support for different calculation methods (per piece, per meter, lump sum, per kWp, etc.)
    - Write unit tests for margin calculations across all calculate_per scenarios
    - _Requirements: 2.2, 2.3, 2.4, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 4.2 Implement global and category-level margin configuration

    - Add support for global margin settings in admin_settings
    - Implement category-level margin overrides
    - Create priority system for margin application (product > category > global)
    - Write tests for margin hierarchy and priority resolution
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
-
- [x] 5. Create pricing modification engine

  - [x] 5.1 Implement discount and surcharge system

    - Write PricingModificationEngine class with discount/surcharge application
    - Create DiscountConfig and SurchargeConfig data classes
    - Implement percentage-based and fixed-amount modifications
    - Write unit tests for modification calculations
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 5.2 Implement advanced pricing formula

    - Code the correct pricing formula: (Matrix Price + Accessories) × (1 - Discount%) × (1 + Surcharge%) - Fixed Discounts + Fixed Surcharges
    - Create detailed breakdown calculation for transparency
    - Implement validation to prevent negative final prices
    - Write comprehensive tests for formula accuracy
    - _Requirements: 4.3, 4.4, 4.5_

- [x] 6. Integrate with existing solar calculator

  - [x] 6.1 Connect component selection to pricing calculations with calculate_per support

    - Modify solar_calculator.py to trigger pricing calculations on component changes
    - Implement calculate_per logic for different component types (modules per piece, cables per meter, installation lump sum, etc.)
    - Add real-time price updates when quantities or selections change based on calculate_per method
    - Integrate with existing product fields (technology, feature, design, upgrade, etc.) for enhanced pricing
    - Add pricing display to solar calculator UI showing calculation method
    - Write integration tests for calculator-pricing connection with all calculate_per scenarios
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 6.2 Implement accessory and optional component pricing

    - Extend solar calculator to handle optional accessories with individual pricing
    - Create accessory selection UI with real-time price updates
    - Implement accessory categorization and pricing rules
    - Write tests for accessory pricing calculations
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 7. Create separate PV and heat pump pricing engines

  - [x] 7.1 Implement PV-specific pricing engine with full product integration

    - Create PVPricingEngine class extending base PricingEngine
    - Implement PV component pricing logic using all product fields (modules, inverters, storage with technology, feature, design, etc.)
    - Add calculate_per logic for PV components (modules per piece, mounting per kWp, cables per meter)
    - Integrate with existing product attributes (efficiency_percent, warranty_years, max_kwh_capacity, etc.)
    - Add PV-specific pricing rules and validations
    - Write unit tests for PV pricing calculations with comprehensive product data
    - _Requirements: 3.1, 3.2, 5.1, 5.2, 5.3_

  - [x] 7.2 Enhance heat pump pricing engine

    - Extend existing heatpump_pricing.py with new pricing system integration
    - Implement heat pump component pricing with profit margins
    - Add heat pump-specific pricing rules and BEG subsidy integration
    - Write unit tests for enhanced heat pump pricing
    - _Requirements: 3.1, 3.2, 5.1, 5.2, 5.3_

  - [x] 7.3 Create combined pricing system

    - Implement CombinedPricingEngine for PV + heat pump offers
    - Create logic to calculate separate totals and combined totals
    - Implement combined system discounts and surcharges
    - Write tests for combined pricing scenarios
    - _Requirements: 3.3, 3.4, 3.5_

- [x] 8. Implement VAT and tax management

  - [x] 8.1 Create VAT calculation system

    - Write VATManager class with support for different VAT rates
    - Implement category-specific VAT handling
    - Create net/gross price calculation methods
    - Write unit tests for VAT calculations
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 8.2 Integrate VAT with pricing calculations

    - Modify pricing engines to include VAT calculations
    - Update dynamic key generation to include VAT-related keys
    - Implement VAT display in pricing breakdowns
    - Write integration tests for VAT-inclusive pricing
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
-
- [x] 9. Enhance PDF integration with dynamic keys

  - [x] 9.1 Update PDF generation system

    - Modify pdf_generator.py to use dynamic pricing keys
    - Implement automatic key population in PDF templates
    - Create pricing breakdown sections in PDF output
    - Write tests for PDF pricing integration
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 9.2 Create PDF pricing templates

    - Design PDF templates with dynamic pricing placeholders
    - Implement separate PV and heat pump pricing sections
    - Create combined pricing template for dual offers
    - Write tests for template rendering with pricing data
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.4, 3.5_

- [x] 10. Implement real-time pricing updates

  - [x] 10.1 Create pricing update system

    - Implement event-driven pricing recalculation
    - Create debounced update mechanism to prevent excessive calculations
    - Add pricing change detection and notification system
    - Write tests for real-time update functionality
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 10.2 Integrate with Streamlit session state

    - Modify calculations.py to use new pricing system
    - Update session state management for pricing data
    - Implement pricing cache invalidation strategies
    - Write integration tests for session state pricing updates
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
-
- [x] 11. Create admin interface for pricing configuration

  - [x] 11.1 Build profit margin management UI

    - Create admin interface for setting product-level margins
    - Implement global and category margin configuration
    - Add margin calculation preview and validation
    - Write UI tests for margin management interface
    - _Requirements: 2.2, 2.3, 2.4, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 11.2 Implement pricing rule management interface

    - Create UI for managing discount and surcharge rules
    - Implement pricing rule priority and condition configuration
    - Add pricing rule testing and preview functionality
    - Write tests for pricing rule management interface
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 12. Implement economic analysis integration

  - [x] 12.1 Connect final pricing to economic calculations

    - Modify economic analysis functions to use final pricing from new system
    - Update payback period calculations with accurate final prices
    - Implement ROI calculations based on final investment amounts
    - Write tests for economic analysis with new pricing system
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 12.2 Create profitability reporting

    - Implement profit margin reporting and analysis
    - Create pricing trend analysis functionality
    - Add component cost analysis and optimization suggestions
    - Write tests for profitability reporting features
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 13. Implement comprehensive error handling and validation

  - [x] 13.1 Create pricing validation system

    - Implement input validation for all pricing calculations
    - Create error handling for invalid component configurations
    - Add validation for margin and modification settings
    - Write comprehensive error handling tests
    - _Requirements: All requirements - validation layer_

  - [x] 13.2 Implement pricing audit and logging

    - Create audit trail for all pricing changes
    - Implement comprehensive logging for pricing calculations
    - Add error monitoring and alerting for pricing issues
    - Write tests for audit and logging functionality
    - _Requirements: All requirements - audit and monitoring_

- [x] 14. Performance optimization and caching

  - [x] 14.1 Implement pricing calculation caching

    - Create intelligent caching system for pricing calculations
    - Implement cache invalidation strategies
    - Add performance monitoring for pricing operations
    - Write performance tests and benchmarks
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 14.2 Optimize database queries for pricing

    - Add database indexes for pricing-related queries
    - Optimize product lookup and pricing calculation queries
    - Implement connection pooling for high-load scenarios
    - Write performance tests for database operations
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 15. Implement calculate_per calculation engine

  - [x] 15.1 Create comprehensive calculation method handler

    - Implement calculation logic for "per piece" (Stück) pricing
    - Add calculation logic for "per meter" (Meter) pricing for cables and mounting
    - Implement "lump sum" (pauschal) pricing for services and packages
    - Add "per kWp" pricing for system-dependent components
    - Create validation and error handling for each calculation method
    - Write comprehensive tests for all calculate_per scenarios
    - _Requirements: 2.1, 2.2, 5.1, 5.2, 5.3_

  - [x] 15.2 Integrate calculate_per with existing product features

    - Connect calculate_per with technology field for technology-specific pricing
    - Integrate with feature field for feature-based pricing adjustments
    - Use design field for design-specific pricing variations
    - Implement upgrade field integration for upgrade pricing
    - Connect with efficiency_percent for efficiency-based pricing
    - Write tests for feature-integrated pricing calculations
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 16. Create comprehensive test suite and documentation
  - [ ] 16.1 Implement end-to-end testing with full product integration
    - Create complete PV system pricing test scenarios using all product fields
    - Implement heat pump system pricing test scenarios with comprehensive data
    - Add combined system pricing test scenarios
    - Test all calculate_per methods with real product configurations
    - Write integration tests for PDF generation with enhanced pricing
    - _Requirements: All requirements - comprehensive testing_

  - [-] 16.2 Create user and developer documentation

    - Write user guide for pricing configuration and management including calculate_per usage
    - Create developer documentation for pricing system APIs with product field integration
    - Document pricing calculation formulas and business rules for all calculation methods
    - Create troubleshooting guide for pricing issues including calculate_per problems
    - Document all product fields and their impact on pricing calculations
    - _Requirements: All requirements - documentation_
