# Implementation Plan

- [ ] 1. Implement core VAT calculation restructuring in solar calculator
  - Modify the `_display_pricing_information()` function in `solar_calculator.py` to implement new calculation flow
  - Replace current calculation logic with: Components → Internal (VAT + Provision) → Display VAT-inclusive → Discounts/Surcharges → Final VAT deduction
  - Ensure provision (1500€ default) is added internally but hidden in UI display
  - _Requirements: 1.1, 1.2, 1.3, 2.2, 3.1_

- [ ] 1.1 Create new calculation flow data structure
  - Define `VATCalculationFlow` class or data structure to manage the new calculation steps
  - Implement methods for each calculation step: component total, internal additions, modifications, final deduction
  - Add validation for each calculation step
  - _Requirements: 1.1, 1.4, 4.1, 4.4_

- [ ] 1.2 Implement internal VAT and provision addition
  - Modify component total calculation to add VAT and provision internally after component selection
  - Ensure VAT-inclusive amount includes hidden provision for PDF display
  - Store both gross (VAT-inclusive) and net amounts for different use cases
  - _Requirements: 1.2, 2.1, 2.2, 2.3_

- [ ] 1.3 Update discount and surcharge application logic
  - Modify discount/surcharge calculations to work on VAT-inclusive amounts (containing hidden provision)
  - Ensure percentage-based discounts and surcharges use the correct base amount
  - Update fixed-amount discounts and surcharges to work with new flow
  - _Requirements: 1.4, 4.1, 4.2_

- [ ] 1.4 Implement final VAT deduction for net price
  - Add final calculation step that deducts VAT from gross total after all modifications
  - Calculate VAT amount correctly from gross total using VAT rate
  - Ensure final net price is the primary result displayed to users
  - _Requirements: 1.5, 3.3, 3.5, 4.1_

- [ ] 2. Update PDF integration for VAT-inclusive pricing display
  - Modify PDF data generation to use VAT-inclusive prices that contain hidden provision
  - Update dynamic key generation in pricing integration to include both gross and net values
  - Ensure PDF templates display the correct VAT-inclusive amounts
  - _Requirements: 5.1, 5.2, 4.3_

- [ ] 2.1 Update pricing display data structure
  - Modify `get_pricing_display_for_ui()` function to support new calculation flow
  - Update pricing data structure to include VAT-inclusive amounts for PDF display
  - Ensure backward compatibility with existing PDF integration points
  - _Requirements: 5.1, 5.3, 6.2_

- [ ] 2.2 Generate dynamic keys for new calculation values
  - Update dynamic key manager to generate keys for VAT-inclusive prices
  - Add keys for provision amount (hidden), VAT amounts, and final net price
  - Ensure PDF templates can access both gross and net values through dynamic keys
  - _Requirements: 5.2, 5.5, 4.4_

- [ ] 3. Update session state management for new calculation data
  - Modify session state storage to include new calculation steps and intermediate values
  - Store VAT-inclusive amounts, provision data, and final net price in session state
  - Ensure compatibility with existing analysis and PDF generation functions
  - _Requirements: 5.4, 6.1, 6.5_

- [ ] 3.1 Store calculation flow data in session state
  - Update session state structure to include all steps of new calculation flow
  - Store component total, VAT-inclusive total, modification details, and final net price
  - Ensure data is accessible for PDF generation and other system integrations
  - _Requirements: 6.1, 6.2, 5.4_

- [ ] 3.2 Maintain backward compatibility with existing session state
  - Preserve existing session state keys that other parts of the system depend on
  - Add new keys without breaking existing functionality
  - Provide fallback values for systems that expect old data structure
  - _Requirements: 6.1, 6.2, 6.5_

- [ ] 4. Implement error handling and validation
  - Add comprehensive error handling for each step of the new calculation flow
  - Validate input values (component totals, VAT rates, provision amounts)
  - Implement fallback behavior for calculation errors
  - _Requirements: 4.2, 4.3, 4.4_

- [ ] 4.1 Add calculation validation functions
  - Implement validation for component totals (must be non-negative)
  - Validate VAT rate (must be between 0 and 1)
  - Validate provision amount (must be non-negative)
  - Add validation for final price calculations (net price must be positive)
  - _Requirements: 4.2, 4.3, 4.4_

- [ ] 4.2 Implement error recovery mechanisms
  - Create safe calculation functions that handle errors gracefully
  - Implement fallback values for failed calculations
  - Add error logging and user-friendly error messages
  - _Requirements: 4.2, 4.3, 4.4_

- [ ]* 5. Create comprehensive test suite for VAT calculation restructuring
  - Write unit tests for each step of the new calculation flow
  - Test edge cases including zero values, maximum discounts, and rounding scenarios
  - Create integration tests for PDF generation and session state management
  - _Requirements: All requirements_

- [ ]* 5.1 Write unit tests for calculation flow
  - Test basic calculation flow: Components → Internal additions → Modifications → Final deduction
  - Test provision integration and VAT calculations
  - Test discount and surcharge application on VAT-inclusive amounts
  - Test final VAT deduction logic
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 5.2 Write integration tests for PDF and session state
  - Test PDF data generation with new calculation flow
  - Test dynamic key generation for PDF templates
  - Test session state updates and backward compatibility
  - Test integration with existing analysis functions
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 6.2_

- [ ]* 5.3 Write edge case and error handling tests
  - Test zero component costs, zero provision, zero VAT rate scenarios
  - Test maximum discount scenarios and rounding precision
  - Test error handling and recovery mechanisms
  - Test validation functions for all input parameters
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 6. Update documentation and migration support
  - Update code documentation to reflect new calculation flow
  - Create migration guide for existing data and integrations
  - Document new session state structure and PDF integration changes
  - _Requirements: 6.3, 6.4, 6.5_

- [ ] 6.1 Document new calculation flow
  - Add comprehensive code comments explaining each step of new calculation
  - Document data structures and their purposes
  - Create developer documentation for the new VAT calculation system
  - _Requirements: 4.1, 6.3_

- [ ] 6.2 Create migration documentation
  - Document changes to session state structure
  - Provide migration guide for existing PDF templates
  - Document backward compatibility considerations
  - _Requirements: 6.1, 6.2, 6.4, 6.5_
