# Implementation Plan

- [ ] 1. Set up dynamic payment configuration data structures and validation
  - Create PaymentVariant and PaymentSegment data classes with proper validation
  - Implement percentage sum validation (must equal 100%)
  - Add text template placeholder validation
  - Write unit tests for data structure validation
  - _Requirements: 1.6, 1.7, 5.5_

- [ ] 2. Extend payment_terms.py with dynamic configuration manager
  - Create DynamicPaymentConfigManager class with CRUD operations
  - Implement load_payment_variants() and save_payment_variants() methods
  - Add calculate_payment_amounts() method for amount calculations
  - Implement generate_payment_text() with placeholder replacement
  - Add backward compatibility with existing PaymentTermsManager
  - _Requirements: 1.1, 1.2, 1.3, 5.1, 5.2_

- [ ] 3. Create admin UI for payment configuration
  - Add payment configuration section to admin_panel.py
  - Implement variant editor forms with st.number_input for percentages
  - Add st.expander sections for optional fixed amounts
  - Create text template editors with st.text_area
  - Implement real-time validation and error display
  - Add save/load functionality with success/error messages
  - _Requirements: 1.1, 1.4, 1.5, 1.6, 1.7_

- [ ] 4. Implement user payment variant selection interface
  - Add payment variant dropdown to PDF creation UI
  - Load available variants from admin configuration
  - Display variant descriptions and preview calculations
  - Integrate with existing PDF generation workflow
  - _Requirements: 2.1, 2.2_

- [ ] 5. Create payment amount calculation engine
  - Implement dynamic amount calculation based on total price
  - Handle fixed amounts vs percentage-based calculations
  - Add support for mixed fixed/percentage segments
  - Ensure calculations always sum to total amount
  - Write comprehensive unit tests for edge cases
  - _Requirements: 2.3, 2.4_

- [ ] 6. Develop payment text generation with placeholder replacement
  - Implement template engine for {p1}, {p2}, {p3} and {b1}, {b2}, {b3} placeholders
  - Add currency formatting for amount placeholders
  - Handle percentage formatting with % symbol
  - Support conditional display of amounts vs percentages
  - Add fallback text generation for missing templates
  - _Requirements: 2.5, 2.6_

- [ ] 7. Enhance PDF generator with cost breakdown on page 7
  - Extend pdf_generator.py with generate_cost_breakdown_page() function
  - Implement cost line item formatting with proper alignment
  - Add conditional display logic for discounts, surcharges, and extras
  - Create visual separator line before final amount
  - Integrate with existing session state variables for cost data
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 5.3_

- [ ] 8. Integrate payment terms text into PDF cost breakdown
  - Add payment terms section below cost breakdown on page 7
  - Format payment terms text with proper styling
  - Ensure text wraps correctly within PDF margins
  - Add visual spacing between cost breakdown and payment terms
  - Test with all four payment variants
  - _Requirements: 3.5_

- [ ] 9. Create theme management data structures
  - Define ThemeConfiguration class with all theme properties
  - Create predefined theme dictionary with Standard, Dark, Material, and Modern themes
  - Implement theme validation for color codes and configuration
  - Add theme persistence to admin settings
  - _Requirements: 4.1, 4.5_

- [ ] 10. Implement Streamlit theme switching functionality
  - Create StreamlitThemeManager class for theme application
  - Implement st._config.set_option integration for theme changes
  - Add st.experimental_rerun trigger after theme application
  - Create rollback mechanism for failed theme applications
  - Handle theme persistence across sessions
  - _Requirements: 4.3, 4.4, 4.5_

- [ ] 11. Build admin UI for theme management
  - Add theme selection dropdown with predefined themes
  - Implement color picker for primary accent color customization
  - Create theme preview functionality
  - Add apply theme button with confirmation
  - Implement theme reset to defaults functionality
  - _Requirements: 4.1, 4.2_

- [ ] 12. Add comprehensive error handling and validation
  - Implement try-catch blocks around all payment calculations
  - Add graceful fallbacks for missing configuration data
  - Create user-friendly error messages for validation failures
  - Add logging for debugging payment and theme issues
  - Implement configuration backup before changes
  - _Requirements: 1.6, 5.4, 5.5_

- [ ] 13. Create integration tests for complete payment workflow
  - Test admin configuration → user selection → PDF generation flow
  - Verify payment calculations with various total amounts
  - Test all four payment variants in PDF output
  - Validate cost breakdown formatting and accuracy
  - Test theme switching with payment configuration UI
  - _Requirements: 1.1, 2.1, 3.1, 4.3_

- [ ] 14. Implement backward compatibility and migration
  - Ensure existing payment_terms.py functions continue working
  - Add migration function for legacy payment configurations
  - Test compatibility with existing PDF generation
  - Verify admin panel integration doesn't break existing functionality
  - Add feature flags for gradual rollout
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 15. Add configuration export/import functionality
  - Implement JSON export for payment configurations
  - Create import validation and error handling
  - Add configuration backup before imports
  - Include theme configurations in export/import
  - Add timestamp and version metadata to exports
  - _Requirements: 1.7, 4.5_

- [ ] 16. Finalize UI integration and polish
  - Ensure consistent styling across all new UI components
  - Add helpful tooltips and user guidance
  - Implement proper loading states during configuration saves
  - Add confirmation dialogs for destructive actions
  - Test responsive layout on different screen sizes
  - _Requirements: 1.1, 2.1, 4.1_
