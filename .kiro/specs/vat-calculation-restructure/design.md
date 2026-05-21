# Design Document

## Overview

This design document outlines the technical approach for restructuring the VAT calculation order in the solar calculator. The new calculation flow will internally add VAT and provision after component selection, display VAT-inclusive prices in the PDF, apply discounts/surcharges to the VAT-inclusive amount, and finally deduct VAT to show the net final price.

## Architecture

### Current System Analysis

Based on the analysis of `solar_calculator.py`, the current system follows this flow:

1. Components → VAT added early → Provision → Discounts/Surcharges → Final price

The current implementation in `_display_pricing_information()` shows:

```python
# Current logic (lines ~400-500 in solar_calculator.py)
net_total_amount = pricing_display.get('net_total', 0.0)
provision_euro = 1500.0  # Standard provision
net_with_provision = net_total_amount + provision_euro
vat_rate = 0.19
vat_amount = net_with_provision * vat_rate
brutto_basis = net_with_provision + vat_amount
```

### New System Design

The new system will implement this flow:

1. **Components** → Calculate base component costs
2. **Internal Addition** → Add VAT and provision internally
3. **PDF Display** → Show VAT-inclusive prices (containing hidden provision)
4. **Discounts/Surcharges** → Apply to VAT-inclusive amounts
5. **Final VAT Deduction** → Subtract VAT to get net final price

## Components and Interfaces

### 1. Core Calculation Engine

**Location**: `solar_calculator.py` - `_display_pricing_information()` function

**Modifications Required**:

- Restructure the calculation flow in the pricing display section
- Implement internal VAT and provision addition after component calculation
- Ensure PDF displays VAT-inclusive prices
- Add final VAT deduction step

### 2. Pricing Integration Layer

**Location**: `solar_calculator_pricing_integration.py`

**Interface Changes**:

- Update `get_pricing_display_for_ui()` to support new calculation flow
- Modify pricing data structure to include both gross and net amounts
- Ensure backward compatibility with existing PDF integration

### 3. PDF Template Integration

**Location**: `pdf_template_engine/placeholders.py`

**Required Updates**:

- Ensure PDF placeholders use VAT-inclusive prices from new calculation
- Update dynamic key generation to include both gross and net values
- Maintain compatibility with existing PDF templates

### 4. Session State Management

**Location**: Throughout `solar_calculator.py`

**Changes**:

- Update session state storage to include new calculation steps
- Store both gross and net amounts for PDF access
- Maintain provision data (hidden but accessible)

## Data Models

### Calculation Flow Data Structure

```python
class VATCalculationFlow:
    """Data model for the new VAT calculation flow"""
    
    # Step 1: Component costs
    component_total: float
    
    # Step 2: Internal additions (hidden in UI)
    provision_amount: float = 1500.0  # Default hidden provision
    vat_rate: float = 0.19
    internal_vat_amount: float
    vat_inclusive_total: float  # This is displayed in PDF
    
    # Step 3: Modifications
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    surcharge_percent: float = 0.0
    surcharge_amount: float = 0.0
    rebates_eur: float = 0.0
    special_costs_eur: float = 0.0
    miscellaneous_eur: float = 0.0
    
    # Step 4: Final calculation
    gross_total_after_modifications: float
    final_vat_to_deduct: float
    net_final_price: float
```

### PDF Integration Data Structure

```python
class PDFPricingData:
    """Data structure for PDF integration"""
    
    # Displayed prices (VAT-inclusive, provision hidden)
    displayed_component_total: float
    displayed_vat_amount: float
    displayed_gross_total: float
    
    # Modification details
    discount_details: Dict[str, Any]
    surcharge_details: Dict[str, Any]
    
    # Final results
    final_gross_total: float
    final_vat_deduction: float
    final_net_price: float
    
    # Dynamic keys for PDF templates
    dynamic_keys: Dict[str, Any]
```

## Error Handling

### Calculation Validation

1. **Component Total Validation**
   - Ensure component total is positive
   - Handle missing or invalid component data
   - Fallback to zero if calculation fails

2. **VAT Calculation Validation**
   - Validate VAT rate (must be between 0 and 1)
   - Ensure VAT amounts are calculated correctly
   - Handle edge cases where VAT rate is zero

3. **Provision Validation**
   - Ensure provision amount is non-negative
   - Handle cases where provision is disabled
   - Validate provision configuration

4. **Final Price Validation**
   - Ensure final net price is positive
   - Validate that VAT deduction doesn't exceed gross total
   - Handle rounding errors in calculations

### Error Recovery

```python
def safe_vat_calculation(component_total: float, provision: float, vat_rate: float) -> Dict[str, float]:
    """Safe VAT calculation with error handling"""
    try:
        if component_total < 0:
            raise ValueError("Component total cannot be negative")
        if provision < 0:
            raise ValueError("Provision cannot be negative")
        if not (0 <= vat_rate <= 1):
            raise ValueError("VAT rate must be between 0 and 1")
            
        # Perform calculation
        base_amount = component_total + provision
        vat_amount = base_amount * vat_rate
        vat_inclusive_total = base_amount + vat_amount
        
        return {
            "base_amount": base_amount,
            "vat_amount": vat_amount,
            "vat_inclusive_total": vat_inclusive_total,
            "success": True
        }
    except Exception as e:
        return {
            "base_amount": 0.0,
            "vat_amount": 0.0,
            "vat_inclusive_total": 0.0,
            "success": False,
            "error": str(e)
        }
```

## Testing Strategy

### Unit Tests

1. **Calculation Flow Tests**
   - Test each step of the new calculation flow
   - Verify VAT addition and deduction logic
   - Test provision integration
   - Validate final price calculations

2. **Edge Case Tests**
   - Zero component costs
   - Zero provision
   - Zero VAT rate
   - Maximum discount scenarios
   - Rounding precision tests

3. **Integration Tests**
   - Test PDF data generation
   - Verify session state updates
   - Test dynamic key generation
   - Validate backward compatibility

### Test Implementation Structure

```python
class TestVATCalculationRestructure:
    """Test suite for VAT calculation restructuring"""
    
    def test_basic_calculation_flow(self):
        """Test the basic calculation flow: Components → +VAT+Provision → Discounts → -VAT"""
        pass
    
    def test_provision_integration(self):
        """Test that provision is correctly added internally"""
        pass
    
    def test_vat_inclusive_display(self):
        """Test that PDF displays VAT-inclusive prices"""
        pass
    
    def test_final_vat_deduction(self):
        """Test final VAT deduction for net price"""
        pass
    
    def test_discount_surcharge_application(self):
        """Test that discounts/surcharges apply to VAT-inclusive amounts"""
        pass
    
    def test_pdf_integration(self):
        """Test PDF integration with new calculation flow"""
        pass
    
    def test_session_state_compatibility(self):
        """Test session state compatibility"""
        pass
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        pass
```

## Implementation Plan

### Phase 1: Core Calculation Logic

- Modify `_display_pricing_information()` function in `solar_calculator.py`
- Implement new calculation flow structure
- Add internal VAT and provision addition
- Implement final VAT deduction

### Phase 2: PDF Integration

- Update PDF data generation to use VAT-inclusive prices
- Modify dynamic key generation
- Ensure backward compatibility with existing templates

### Phase 3: Session State Updates

- Update session state storage for new calculation data
- Ensure all pricing data is properly stored
- Maintain compatibility with existing analysis functions

### Phase 4: Testing and Validation

- Implement comprehensive test suite
- Validate calculations against requirements
- Test PDF generation with new data
- Perform integration testing

## Migration Strategy

### Backward Compatibility

1. **Existing Calculations**
   - Preserve existing session state structure where possible
   - Add new fields without removing old ones initially
   - Provide migration path for existing data

2. **PDF Templates**
   - Ensure existing PDF templates continue to work
   - Add new placeholders without breaking existing ones
   - Provide fallback values for missing data

3. **API Compatibility**
   - Maintain existing function signatures
   - Add new optional parameters for new functionality
   - Ensure existing integrations continue to work

### Migration Steps

1. **Preparation Phase**
   - Backup existing calculation logic
   - Create feature flag for new calculation flow
   - Implement parallel calculation for comparison

2. **Implementation Phase**
   - Deploy new calculation logic behind feature flag
   - Test with sample data
   - Compare results with old system

3. **Validation Phase**
   - Enable new system for testing
   - Validate PDF generation
   - Perform user acceptance testing

4. **Rollout Phase**
   - Enable new system by default
   - Monitor for issues
   - Remove old calculation logic after validation period
