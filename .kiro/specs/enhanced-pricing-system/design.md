# Design Document

## Overview

The Enhanced Pricing System will extend the existing PV and heat pump application with a comprehensive, dynamic pricing calculation engine. The system will provide granular control over pricing components, profit margins, discounts, and surcharges while maintaining separate calculations for PV and heat pump systems. All pricing values will be assigned dynamic keys for seamless PDF integration.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced Pricing System                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   PV Pricing    │  │  Heat Pump      │  │   Combined      │ │
│  │   Engine        │  │  Pricing Engine │  │   Pricing       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Dynamic Key    │  │   Profit        │  │   Discount &    │ │
│  │  Generator      │  │   Margin        │  │   Surcharge     │ │
│  │                 │  │   Manager       │  │   Engine        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Product       │  │   Price Matrix  │  │   VAT & Tax     │ │
│  │   Database      │  │   Store         │  │   Manager       │ │
│  │   Integration   │  │   (Enhanced)    │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   PDF Key       │  │   Real-time     │  │   Economic      │ │
│  │   Integration   │  │   Updates       │  │   Analysis      │ │
│  │                 │  │                 │  │   Integration   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Component Integration

The system integrates with existing components:

- **product_db.py**: Enhanced with pricing fields and profit margin configuration
- **price_matrix_store.py**: Extended for dynamic pricing rules
- **calculations.py**: Modified to use new pricing engine
- **pdf_generator.py**: Enhanced with dynamic key integration
- **solar_calculator.py**: Connected to real-time pricing updates
- **heatpump_pricing.py**: Integrated with unified pricing system

## Components and Interfaces

### 1. Enhanced Pricing Engine (`enhanced_pricing_engine.py`)

**Purpose**: Core pricing calculation engine with dynamic key generation

**Key Classes**:

```python
class PricingEngine:
    def __init__(self, system_type: str)  # 'pv' or 'heatpump'
    def calculate_base_price(self, components: Dict) -> PricingResult
    def apply_modifications(self, base_price: float, modifications: Dict) -> PricingResult
    def generate_final_price(self, calculation_data: Dict) -> FinalPricingResult

class PricingResult:
    base_price: float
    components: List[PriceComponent]
    dynamic_keys: Dict[str, Any]
    metadata: Dict[str, Any]

class FinalPricingResult(PricingResult):
    final_price_net: float
    final_price_gross: float
    total_discounts: float
    total_surcharges: float
    vat_amount: float
    profit_margin: float
```

**Key Methods**:

- `calculate_component_pricing()`: Individual component price calculation
- `apply_profit_margins()`: Profit margin application
- `calculate_discounts_surcharges()`: Discount and surcharge processing
- `generate_dynamic_keys()`: PDF key generation
- `validate_pricing_data()`: Input validation

### 2. Dynamic Key Manager (`dynamic_key_manager.py`)

**Purpose**: Manages dynamic key generation and PDF integration

**Key Classes**:

```python
class DynamicKeyManager:
    def __init__(self)
    def generate_keys(self, pricing_data: Dict, prefix: str = "") -> Dict[str, Any]
    def register_key(self, key: str, value: Any, category: str = "pricing")
    def get_all_keys(self, filter_category: str = None) -> Dict[str, Any]
    def format_for_pdf(self, keys: Dict) -> Dict[str, str]

class KeyCategory:
    PRICING = "pricing"
    COMPONENTS = "components"
    DISCOUNTS = "discounts"
    SURCHARGES = "surcharges"
    TAXES = "taxes"
    TOTALS = "totals"
```

**Key Features**:

- Automatic key generation with consistent naming
- Category-based key organization
- PDF-ready formatting
- Conflict resolution for duplicate keys

### 3. Profit Margin Manager (`profit_margin_manager.py`)

**Purpose**: Handles profit margin configuration and calculation

**Key Classes**:

```python
class ProfitMarginManager:
    def __init__(self)
    def set_product_margin(self, product_id: int, margin_config: MarginConfig)
    def set_global_margin(self, margin_config: MarginConfig)
    def calculate_selling_price(self, purchase_price: float, product_id: int = None) -> float
    def get_margin_breakdown(self, product_id: int) -> MarginBreakdown

class MarginConfig:
    margin_type: str  # 'percentage' or 'fixed'
    margin_value: float
    applies_to: str  # 'product', 'category', 'global'
    priority: int

class MarginBreakdown:
    purchase_price: float
    margin_amount: float
    selling_price: float
    margin_percentage: float
    source: str  # 'product', 'category', 'global'
```

### 4. Enhanced Product Database Integration

**Database Schema Extensions**:

```sql
-- Add to existing products table
ALTER TABLE products ADD COLUMN purchase_price_net REAL DEFAULT 0.0;
ALTER TABLE products ADD COLUMN margin_type TEXT DEFAULT 'percentage';
ALTER TABLE products ADD COLUMN margin_value REAL DEFAULT 0.0;
ALTER TABLE products ADD COLUMN margin_priority INTEGER DEFAULT 0;
ALTER TABLE products ADD COLUMN pricing_category TEXT;
ALTER TABLE products ADD COLUMN last_price_update TIMESTAMP;

-- New table for pricing rules
CREATE TABLE pricing_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT NOT NULL,
    rule_type TEXT NOT NULL, -- 'margin', 'discount', 'surcharge'
    applies_to TEXT NOT NULL, -- 'product', 'category', 'global'
    target_id INTEGER, -- product_id or category reference
    rule_config TEXT, -- JSON configuration
    is_active INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New table for pricing history
CREATE TABLE pricing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    old_price REAL,
    new_price REAL,
    change_reason TEXT,
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
```

### 5. Pricing Modification Engine

**Purpose**: Handles discounts, surcharges, and pricing adjustments

**Key Classes**:

```python
class PricingModificationEngine:
    def __init__(self)
    def add_discount(self, discount_config: DiscountConfig)
    def add_surcharge(self, surcharge_config: SurchargeConfig)
    def calculate_modifications(self, base_price: float) -> ModificationResult

class DiscountConfig:
    discount_type: str  # 'percentage', 'fixed', 'tiered'
    discount_value: float
    conditions: Dict[str, Any]
    description: str
    dynamic_key: str

class ModificationResult:
    original_amount: float
    total_discounts: float
    total_surcharges: float
    final_amount: float
    applied_modifications: List[Dict]
    dynamic_keys: Dict[str, Any]
```

## Data Models

### Core Pricing Data Structure

```python
@dataclass
class PricingCalculation:
    system_type: str  # 'pv', 'heatpump', 'combined'
    components: List[ComponentPricing]
    base_price_net: float
    modifications: PricingModifications
    final_price_net: float
    final_price_gross: float
    vat_amount: float
    dynamic_keys: Dict[str, Any]
    calculation_timestamp: datetime
    
@dataclass
class ComponentPricing:
    component_id: int
    component_name: str
    category: str
    quantity: int
    purchase_price_net: float
    margin_config: MarginConfig
    selling_price_net: float
    total_price_net: float
    dynamic_keys: Dict[str, Any]

@dataclass
class PricingModifications:
    discounts: List[DiscountApplication]
    surcharges: List[SurchargeApplication]
    accessories: List[AccessoryPricing]
    total_discount_amount: float
    total_surcharge_amount: float
    dynamic_keys: Dict[str, Any]
```

### PDF Integration Data Model

```python
@dataclass
class PDFPricingData:
    # Base pricing keys
    base_price_net: str  # "BASE_PRICE_NET"
    base_price_gross: str  # "BASE_PRICE_GROSS"
    
    # Component keys (dynamic based on selection)
    component_keys: Dict[str, str]  # {"PV_MODULE_PRICE": "1234.56"}
    
    # Modification keys
    discount_keys: Dict[str, str]  # {"DISCOUNT_EARLY_PAYMENT": "123.45"}
    surcharge_keys: Dict[str, str]  # {"SURCHARGE_RUSH_ORDER": "67.89"}
    
    # Final pricing keys
    final_price_net: str  # "FINAL_PRICE_NET"
    final_price_gross: str  # "FINAL_PRICE_GROSS"
    vat_amount: str  # "VAT_AMOUNT"
    
    # Formatted display keys
    formatted_keys: Dict[str, str]  # Human-readable versions
```

## Error Handling

### Pricing Calculation Errors

```python
class PricingError(Exception):
    """Base class for pricing-related errors"""
    pass

class InvalidComponentError(PricingError):
    """Raised when component data is invalid"""
    pass

class MarginCalculationError(PricingError):
    """Raised when margin calculation fails"""
    pass

class PriceMatrixError(PricingError):
    """Raised when price matrix lookup fails"""
    pass

class DynamicKeyError(PricingError):
    """Raised when dynamic key generation fails"""
    pass
```

### Error Recovery Strategies

1. **Graceful Degradation**: Use fallback pricing when advanced features fail
2. **Validation Layers**: Multiple validation points to catch errors early
3. **Logging**: Comprehensive logging for debugging pricing issues
4. **User Feedback**: Clear error messages for user-facing issues

## Testing Strategy

### Unit Tests

1. **Pricing Engine Tests**
   - Component pricing calculation accuracy
   - Margin application correctness
   - Discount/surcharge calculations
   - Dynamic key generation

2. **Integration Tests**
   - Product database integration
   - Price matrix integration
   - PDF key generation
   - Real-time updates

3. **End-to-End Tests**
   - Complete PV system pricing
   - Complete heat pump pricing
   - Combined system pricing
   - PDF generation with dynamic keys

### Test Data Strategy

```python
# Test fixtures for consistent testing
SAMPLE_PV_COMPONENTS = {
    "modules": {"quantity": 20, "unit_price": 180.0, "margin": 0.25},
    "inverter": {"quantity": 1, "unit_price": 800.0, "margin": 0.30},
    "storage": {"quantity": 1, "unit_price": 3500.0, "margin": 0.20}
}

SAMPLE_MODIFICATIONS = {
    "discounts": [{"type": "early_payment", "value": 3.0, "unit": "percent"}],
    "surcharges": [{"type": "rush_order", "value": 200.0, "unit": "fixed"}]
}
```

### Performance Testing

1. **Load Testing**: Handle multiple concurrent pricing calculations
2. **Memory Testing**: Ensure efficient memory usage with large product catalogs
3. **Response Time**: Sub-second response for real-time updates

## Implementation Phases

### Phase 1: Core Pricing Engine (Week 1-2)

- Implement `PricingEngine` class
- Basic component pricing calculation
- Simple margin application
- Dynamic key generation foundation

### Phase 2: Product Database Integration (Week 2-3)

- Extend product database schema
- Implement `ProfitMarginManager`
- Product-level pricing configuration
- Database migration scripts

### Phase 3: Advanced Modifications (Week 3-4)

- Implement `PricingModificationEngine`
- Discount and surcharge system
- Complex pricing rules
- Validation and error handling

### Phase 4: PDF Integration (Week 4-5)

- Complete dynamic key system
- PDF template integration
- Real-time key updates
- Testing and validation

### Phase 5: System Integration (Week 5-6)

- Solar calculator integration
- Heat pump system integration
- Combined pricing calculations
- End-to-end testing

### Phase 6: UI and Admin Features (Week 6-7)

- Admin interface for pricing configuration
- Real-time pricing displays
- Profit margin management UI
- User documentation

## Security Considerations

### Data Protection

- Encrypt sensitive pricing data in database
- Secure API endpoints for pricing calculations
- Audit trail for pricing changes
- Role-based access to pricing configuration

### Input Validation

- Validate all pricing inputs
- Prevent SQL injection in pricing queries
- Sanitize dynamic key generation
- Rate limiting for pricing API calls

### Business Logic Security

- Prevent negative pricing
- Validate margin calculations
- Ensure pricing consistency
- Protect against pricing manipulation

## Performance Optimization

### Caching Strategy

- Cache frequently accessed product prices
- Cache calculated margins
- Cache dynamic key mappings
- Invalidate cache on price updates

### Database Optimization

- Index pricing-related columns
- Optimize pricing calculation queries
- Use prepared statements
- Connection pooling for high load

### Real-time Updates

- Efficient change detection
- Minimal recalculation scope
- Debounced update triggers
- Progressive enhancement for UI updates

## Monitoring and Analytics

### Pricing Metrics

- Average calculation time
- Most frequently used components
- Margin distribution analysis
- Discount/surcharge usage patterns

### Error Monitoring

- Pricing calculation failures
- Dynamic key generation errors
- Database connection issues
- PDF integration problems

### Business Intelligence

- Pricing trend analysis
- Profit margin reporting
- Component popularity metrics
- Customer pricing preferences
