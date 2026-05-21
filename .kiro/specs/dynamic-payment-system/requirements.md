# Requirements Document

## Introduction

This feature implements a comprehensive dynamic payment terms configuration system for the solar calculator application. The system allows administrators to configure up to four different payment variants with customizable percentages, optional fixed amounts, and descriptive text templates. Users can then select from these predefined payment options when generating PDFs. Additionally, the feature includes a detailed cost breakdown on PDF page 7 and switchable UI themes for enhanced user experience.

## Requirements

### Requirement 1

**User Story:** As an administrator, I want to configure up to four different payment variants with customizable terms, so that users can choose from predefined payment options that match our business needs.

#### Acceptance Criteria

1. WHEN an administrator accesses the admin panel THEN the system SHALL provide a "Payment Terms Configuration" section
2. WHEN configuring payment variants THEN the system SHALL support exactly four predefined variant types:
   - Variant 1: Payment with down payment (configurable percentages for down payment, after DC installation, after commissioning)
   - Variant 2: 100% after completion (fixed at 100% after delivery/installation/commissioning)
   - Variant 3: No down payment, two installments (configurable percentages for after DC installation and after commissioning)
   - Variant 4: Completely customizable (three configurable fields for custom payment descriptions and percentages)
3. WHEN configuring each variant THEN the system SHALL provide input fields for percentage values that must sum to 100%
4. WHEN configuring each variant THEN the system SHALL provide optional expandable sections for fixed amounts using st.expander
5. WHEN configuring each variant THEN the system SHALL provide a text template field with placeholder support for {p1}, {p2}, {p3} (percentages) and {b1}, {b2}, {b3} (amounts)
6. WHEN saving payment configuration THEN the system SHALL validate that percentage values sum to 100% for each variant
7. WHEN saving payment configuration THEN the system SHALL persist the configuration to a JSON file for global access

### Requirement 2

**User Story:** As a user creating a PDF, I want to select from predefined payment variants, so that I can easily apply appropriate payment terms without manual configuration.

#### Acceptance Criteria

1. WHEN a user accesses the PDF creation interface THEN the system SHALL provide a dropdown or radio button selection for payment variants
2. WHEN a user selects a payment variant THEN the system SHALL load the corresponding configuration from admin settings
3. WHEN generating payment terms text THEN the system SHALL calculate amounts based on the total price if fixed amounts are not specified
4. WHEN generating payment terms text THEN the system SHALL use fixed amounts from admin configuration when specified
5. WHEN generating payment terms text THEN the system SHALL replace placeholders in text templates with actual calculated values
6. WHEN displaying payment information THEN the system SHALL show both percentage and absolute amounts when applicable (e.g., "30% (5,000 €) down payment")

### Requirement 3

**User Story:** As a user viewing the generated PDF, I want to see a comprehensive cost breakdown on page 7, so that I can understand all components of the final price.

#### Acceptance Criteria

1. WHEN generating PDF page 7 THEN the system SHALL display the following cost breakdown items in order:
   - Total system cost (including VAT)
   - VAT deduction (displayed with minus sign)
   - Net amount (after VAT deduction)
   - Discounts/rebates (if applicable, with minus sign)
   - Surcharges/additional costs (if applicable, with plus sign)
   - Accessories/extras (if applicable, with plus sign)
   - Final system cost (with visual separator line above)
2. WHEN calculating cost breakdown THEN the system SHALL use existing values from the solar calculator without recalculation
3. WHEN displaying cost breakdown THEN the system SHALL conditionally show discount, surcharge, and extras lines only when values are greater than zero
4. WHEN displaying final cost THEN the system SHALL include the selected payment terms text below the cost breakdown
5. WHEN rendering cost breakdown THEN the system SHALL use appropriate formatting for currency values and percentages

### Requirement 4

**User Story:** As a user or administrator, I want to switch between different visual themes, so that I can customize the application appearance to match preferences or branding requirements.

#### Acceptance Criteria

1. WHEN accessing theme settings THEN the system SHALL provide a selection of predefined themes:
   - Standard Light Theme (default Streamlit colors)
   - Dark Theme (dark background with light text)
   - Material Design Theme (blue primary accent)
   - Modern Theme (shadcn-UI inspired colors)
2. WHEN selecting a theme THEN the system SHALL allow customization of the primary accent color using a color picker
3. WHEN applying a theme THEN the system SHALL update Streamlit configuration using st._config.set_option
4. WHEN theme changes are applied THEN the system SHALL trigger an application reload using st.experimental_rerun
5. WHEN theme is changed THEN the system SHALL persist the theme selection for future sessions
6. WHEN theme is applied THEN the system SHALL update all UI components including buttons, sliders, charts, and text elements

### Requirement 5

**User Story:** As a developer maintaining the system, I want the payment configuration to integrate seamlessly with existing calculations, so that no duplicate logic is created and data consistency is maintained.

#### Acceptance Criteria

1. WHEN accessing calculation values THEN the system SHALL use existing session state variables from the solar calculator
2. WHEN calculating payment amounts THEN the system SHALL reference existing variables like st.session_state.endpreis, st.session_state.gesamtpreis_inkl_mwst
3. WHEN generating PDF content THEN the system SHALL integrate with existing PDF generation pipeline without modifying core calculation logic
4. WHEN storing payment configuration THEN the system SHALL use a separate configuration file that doesn't interfere with existing data structures
5. WHEN loading payment variants THEN the system SHALL handle missing or corrupted configuration gracefully with default fallbacks
