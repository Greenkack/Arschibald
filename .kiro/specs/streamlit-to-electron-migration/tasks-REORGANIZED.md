# Implementation Plan - REORGANIZED

**WICHTIG**: Diese Task-Liste wurde neu organisiert, sodass grundlegende Funktionen (Formatierung, Validierung, Core-Utilities) ZUERST implementiert werden, bevor sie in anderen Features verwendet werden.

**Alle Dateien gehören in den Ordner: `solar-calculator-pro/`**

## Phase 1: Core Utilities & Formatters (FOUNDATION)

Diese Phase MUSS zuerst abgeschlossen werden, da alle anderen Features diese Utilities verwenden!

- [x] 1. German Number Formatter Core
  - Create GermanNumberFormatter class
  - Implement format() method (number -> "1.234,56")
  - Implement parse() method ("1.234,56" -> number)
  - Create formatCurrency() method
  - Implement formatPercent() method
  - Build validation for German number format
  - _Requirements: 14.1, 14.2, 14.6_
  - **Location**: `solar-calculator-pro/backend/core/german_formatter.py`


- [x] 2. Custom German Input Components




  - Create GermanNumberInput component
  - Build GermanCurrencyInput component
  - Implement GermanPercentInput component
  - Create GermanSlider with formatted display
  - Build validation and error handling
  - Implement bidirectional conversion
  - _Requirements: 14.3, 14.6, 14.9_
  - **Location**: `solar-calculator-pro/frontend/src/components/inputs/`

- [ ] 3. Dynamic Key System Infrastructure
  - Create DynamicKeyMixin class
  - Implement unique key generation algorithm
  - Build key prefix system for different data types
  - Create key validation and verification
  - Implement key indexing for fast lookup
  - _Requirements: 14.4, 14.7_
  - **Location**: `solar-calculator-pro/backend/core/dynamic_keys.py`

- [ ] 4. PDF Byte Generation Core
  - Create PDFByteMixin class
  - Implement to_pdf_bytes() method
  - Build to_pdf_base64() method
  - Create PDF rendering engine
  - Implement PDF metadata system
  - _Requirements: 14.5, 14.8_
  - **Location**: `solar-calculator-pro/backend/core/pdf_bytes.py`

- [ ] 5. Universal Data Model
  - Create UniversalDataModel base class
  - Integrate DynamicKeyMixin
  - Integrate PDFByteMixin
  - Implement formatted value retrieval
  - Build locale-aware formatting
  - Create data serialization
  - _Requirements: 14.4, 14.5, 14.10_
  - **Location**: `solar-calculator-pro/backend/models/universal_data.py`

- [ ] 6. Validation Framework
  - Create base validator classes
  - Implement number validation
  - Build string validation
  - Create date/time validation
  - Implement custom validation rules
  - Build validation error handling
  - _Requirements: 4.4, 11.3_
  - **Location**: `solar-calculator-pro/backend/core/validators.py`

- [ ] 7. Error Handling Framework
  - Create custom exception classes
  - Implement error codes system
  - Build error message templates
  - Create error logging
  - Implement user-friendly error responses
  - _Requirements: 4.3, 4.4, 11.3_
  - **Location**: `solar-calculator-pro/backend/core/errors.py`

