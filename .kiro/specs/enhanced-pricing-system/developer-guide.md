# Enhanced Pricing System - Developer Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [API Reference](#api-reference)
4. [Database Schema](#database-schema)
5. [Product Field Integration](#product-field-integration)
6. [Pricing Calculation Engine](#pricing-calculation-engine)
7. [Dynamic Key System](#dynamic-key-system)
8. [Extension Points](#extension-points)
9. [Testing Framework](#testing-framework)
10. [Performance Considerations](#performance-considerations)

## Architecture Overview

The Enhanced Pricing System follows a modular architecture with clear separation of concerns:

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
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Modularity**: Each component has a single responsibility
2. **Extensibility**: Easy to add new pricing engines or calculation methods
3. **Performance**: Efficient caching and database optimization
4. **Reliability**: Comprehensive error handling and validation
5. **Maintainability**: Clear interfaces and documentation

## Core Components

### 1. Enhanced Pricing Engine (`pricing/enhanced_pricing_engine.py`)

The core pricing calculation engine that orchestrates all pricing operations.

```python
class PricingEngine:
    """
    Core pricing calculation engine with dynamic key generation
    
    Attributes:
        system_type (str): 'pv', 'heatpump', or 'combined'
        key_manager (DynamicKeyManager): Manages dynamic key generation
        margin_manager (ProfitMarginManager): Handles profit margin calculations
        modification_engine (PricingModificationEngine): Processes discounts/surcharges
    """
    
    def __init__(self, system_type: str = "pv"):
        self.system_type = system_type
        self.key_manager = DynamicKeyManager()
        self.margin_manager = ProfitMarginManager()
        self.modification_engine = PricingModificationEngine()
        self.vat_manager = VATManager()
        self.cache = PricingCache()
    
    def calculate_system_pricing(self, components: List[Dict], 
                               modifications: Dict = None) -> PricingResult:
        """
        Calculate complete system pricing with all modifications
        
        Args:
            components: List of component dictionaries with pricing data
            modifications: Optional pricing modifications (discounts, surcharges)
            
        Returns:
            PricingResult: Complete pricing calculation with dynamic keys
        """
```

### 2. Dynamic Key Manager (`pricing/dynamic_key_manager.py`)

Manages dynamic key generation for PDF integration.

```python
class DynamicKeyManager:
    """
    Manages dynamic key generation and PDF integration
    
    Key Categories:
    - PRICING: Base pricing keys
    - COMPONENTS: Individual component keys
    - DISCOUNTS: Discount-related keys
    - SURCHARGES: Surcharge-related keys
    - TAXES: VAT and tax keys
    - TOTALS: Final total keys
    """
    
    def generate_keys(self, pricing_data: Dict, prefix: str = "") -> Dict[str, Any]:
        """
        Generate dynamic keys for pricing data
        
        Args:
            pricing_data: Dictionary containing pricing information
            prefix: Optional prefix for key names
            
        Returns:
            Dict[str, Any]: Generated dynamic keys
        """
        
    def register_key(self, key: str, value: Any, category: str = "pricing"):
        """
        Register a new dynamic key
        
        Args:
            key: Key name (will be converted to uppercase)
            value: Key value
            category: Key category for organization
        """
```

### 3. Calculate Per Engine (`pricing/calculate_per_engine.py`)

Handles different calculation methods for product pricing.

```python
class CalculatePerEngine:
    """
    Handles different calculation methods for product pricing
    
    Supported Methods:
    - Stück (per piece)
    - Meter (per meter)
    - pauschal (lump sum)
    - kWp (per kilowatt peak)
    """
    
    SUPPORTED_METHODS = {
        "Stück": "per_piece",
        "Meter": "per_meter", 
        "pauschal": "lump_sum",
        "kWp": "per_kwp"
    }
    
    def calculate_price(self, product: Dict, quantity: float, 
                       system_size_kwp: float = None) -> CalculationResult:
        """
        Calculate price based on product's calculate_per method
        
        Args:
            product: Product dictionary with pricing information
            quantity: Quantity to calculate for
            system_size_kwp: System size in kWp (required for per_kwp calculations)
            
        Returns:
            CalculationResult: Calculation result with breakdown
        """
```

### 4. Profit Margin Manager (`pricing/profit_margin_manager.py`)

Manages profit margin calculations and configurations.

```python
class ProfitMarginManager:
    """
    Manages profit margin calculations and configurations
    
    Margin Types:
    - percentage: Percentage-based margins
    - fixed: Fixed amount margins
    
    Priority Order:
    1. Product-specific margins
    2. Category-level margins  
    3. Global margins
    """
    
    def calculate_selling_price(self, purchase_price: float, 
                              product_id: int = None,
                              category: str = None) -> MarginResult:
        """
        Calculate selling price with appropriate margin
        
        Args:
            purchase_price: Product purchase price
            product_id: Optional product ID for product-specific margins
            category: Optional category for category-level margins
            
        Returns:
            MarginResult: Selling price calculation with margin breakdown
        """
```

## API Reference

### Core Pricing API

#### Calculate System Pricing

```python
def calculate_system_pricing(system_type: str, components: List[Dict], 
                           modifications: Dict = None) -> PricingResult:
    """
    Calculate complete system pricing
    
    Args:
        system_type: 'pv', 'heatpump', or 'combined'
        components: List of component configurations
        modifications: Optional pricing modifications
        
    Returns:
        PricingResult with complete pricing breakdown
    """
```

#### Get Dynamic Keys

```python
def get_dynamic_keys(pricing_result: PricingResult, 
                    format_for_pdf: bool = True) -> Dict[str, str]:
    """
    Get dynamic keys for PDF integration
    
    Args:
        pricing_result: Result from pricing calculation
        format_for_pdf: Whether to format values for PDF display
        
    Returns:
        Dictionary of dynamic keys and formatted values
    """
```

### Product Integration API

#### Calculate Product Price

```python
def calculate_product_price(product_id: int, quantity: float,
                          system_size_kwp: float = None) -> ProductPricingResult:
    """
    Calculate price for a specific product
    
    Args:
        product_id: Product database ID
        quantity: Quantity to calculate
        system_size_kwp: System size for per_kwp calculations
        
    Returns:
        ProductPricingResult with detailed breakdown
    """
```

#### Update Product Pricing

```python
def update_product_pricing(product_id: int, pricing_config: Dict) -> bool:
    """
    Update product pricing configuration
    
    Args:
        product_id: Product database ID
        pricing_config: New pricing configuration
        
    Returns:
        Success status
    """
```

### Margin Management API

#### Set Product Margin

```python
def set_product_margin(product_id: int, margin_config: MarginConfig) -> bool:
    """
    Set margin configuration for specific product
    
    Args:
        product_id: Product database ID
        margin_config: Margin configuration
        
    Returns:
        Success status
    """
```

#### Get Margin Breakdown

```python
def get_margin_breakdown(product_id: int) -> MarginBreakdown:
    """
    Get detailed margin breakdown for product
    
    Args:
        product_id: Product database ID
        
    Returns:
        MarginBreakdown with detailed margin information
    """
```

## Database Schema

### Enhanced Products Table

```sql
CREATE TABLE products (
    -- Existing fields
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    model_name TEXT NOT NULL,
    brand TEXT,
    price_euro REAL DEFAULT 0.0,
    calculate_per TEXT DEFAULT 'Stück',
    capacity_w REAL,
    storage_power_kw REAL,
    power_kw REAL,
    max_cycles INTEGER,
    warranty_years INTEGER,
    technology TEXT,
    feature TEXT,
    design TEXT,
    upgrade TEXT,
    max_kwh_capacity REAL,
    outdoor_opt TEXT,
    self_supply_feature TEXT,
    shadow_fading TEXT,
    smart_home TEXT,
    length_m REAL,
    width_m REAL,
    weight_kg REAL,
    efficiency_percent REAL,
    origin_country TEXT,
    description TEXT,
    pros TEXT,
    cons TEXT,
    rating REAL,
    image_base64 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Enhanced pricing fields
    purchase_price_net REAL DEFAULT 0.0,
    margin_type TEXT DEFAULT 'percentage',
    margin_value REAL DEFAULT 0.0,
    margin_priority INTEGER DEFAULT 0,
    pricing_category TEXT,
    last_price_update TIMESTAMP
);
```

### Pricing Rules Table

```sql
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
```

### Pricing History Table

```sql
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

## Product Field Integration

### Field Impact on Pricing

| Field | Type | Pricing Impact | Usage Example |
|-------|------|----------------|---------------|
| `calculate_per` | TEXT | Determines calculation method | "Stück", "Meter", "pauschal", "kWp" |
| `price_euro` | REAL | Base selling price | 180.50 |
| `purchase_price_net` | REAL | Cost price for margin calculation | 144.40 |
| `margin_type` | TEXT | Type of margin calculation | "percentage", "fixed" |
| `margin_value` | REAL | Margin amount or percentage | 25.0 (for 25%) |
| `category` | TEXT | Category-specific pricing rules | "PV Module", "Heat Pump" |
| `technology` | TEXT | Technology-based pricing adjustments | "Monocrystalline" |
| `efficiency_percent` | REAL | Efficiency-based pricing | 22.1 |
| `warranty_years` | INTEGER | Warranty-based pricing | 25 |
| `capacity_w` | REAL | Capacity-based calculations | 400 |
| `power_kw` | REAL | Power-based calculations | 10.5 |

### Calculate Per Method Implementation

```python
def calculate_per_price(product: Dict, quantity: float, system_size_kwp: float = None) -> float:
    """
    Calculate price based on product's calculate_per method
    
    Implementation for each method:
    
    Stück (per piece):
        total_price = unit_price * quantity
        
    Meter (per meter):
        total_price = price_per_meter * length_in_meters
        
    pauschal (lump sum):
        total_price = fixed_price (quantity ignored)
        
    kWp (per kilowatt peak):
        total_price = price_per_kwp * system_size_kwp
    """
    
    calculate_per = product.get('calculate_per', 'Stück')
    unit_price = product.get('price_euro', 0.0)
    
    if calculate_per == 'Stück':
        return unit_price * quantity
    elif calculate_per == 'Meter':
        return unit_price * quantity  # quantity represents meters
    elif calculate_per == 'pauschal':
        return unit_price  # Fixed price regardless of quantity
    elif calculate_per == 'kWp':
        if system_size_kwp is None:
            raise ValueError("System size in kWp required for per_kwp calculation")
        return unit_price * system_size_kwp
    else:
        raise ValueError(f"Unsupported calculate_per method: {calculate_per}")
```

## Pricing Calculation Engine

### Core Calculation Flow

```python
def calculate_system_pricing(components: List[Dict], modifications: Dict = None) -> PricingResult:
    """
    Complete pricing calculation flow:
    
    1. Calculate base component prices using calculate_per methods
    2. Apply profit margins based on configuration hierarchy
    3. Add accessories and optional components
    4. Apply percentage-based discounts and surcharges
    5. Apply fixed-amount discounts and surcharges
    6. Calculate VAT and final totals
    7. Generate dynamic keys for PDF integration
    """
    
    # Step 1: Calculate base component prices
    base_prices = []
    for component in components:
        component_price = calculate_component_price(component)
        base_prices.append(component_price)
    
    # Step 2: Apply profit margins
    margin_adjusted_prices = []
    for price_info in base_prices:
        margin_result = apply_profit_margin(price_info)
        margin_adjusted_prices.append(margin_result)
    
    # Step 3: Calculate subtotal
    subtotal = sum(price.total_price for price in margin_adjusted_prices)
    
    # Step 4: Add accessories
    if modifications and 'accessories' in modifications:
        accessory_total = calculate_accessories(modifications['accessories'])
        subtotal += accessory_total
    
    # Step 5: Apply modifications using the pricing formula
    final_price = apply_pricing_formula(subtotal, modifications)
    
    # Step 6: Calculate VAT
    vat_result = calculate_vat(final_price)
    
    # Step 7: Generate dynamic keys
    dynamic_keys = generate_dynamic_keys(
        base_prices, margin_adjusted_prices, final_price, vat_result
    )
    
    return PricingResult(
        base_prices=base_prices,
        margin_adjusted_prices=margin_adjusted_prices,
        subtotal=subtotal,
        final_price_net=final_price,
        final_price_gross=vat_result.gross_price,
        vat_amount=vat_result.vat_amount,
        dynamic_keys=dynamic_keys
    )
```

### Pricing Formula Implementation

```python
def apply_pricing_formula(base_price: float, modifications: Dict) -> float:
    """
    Apply the complete pricing formula:
    (Matrix Price + Accessories) × (1 - Discount%) × (1 + Surcharge%) - Fixed Discounts + Fixed Surcharges
    
    Args:
        base_price: Base price including accessories
        modifications: Dictionary containing discounts and surcharges
        
    Returns:
        Final calculated price
    """
    
    current_price = base_price
    
    # Apply percentage discounts
    percentage_discounts = modifications.get('percentage_discounts', [])
    for discount in percentage_discounts:
        discount_multiplier = 1 - (discount['value'] / 100)
        current_price *= discount_multiplier
    
    # Apply percentage surcharges
    percentage_surcharges = modifications.get('percentage_surcharges', [])
    for surcharge in percentage_surcharges:
        surcharge_multiplier = 1 + (surcharge['value'] / 100)
        current_price *= surcharge_multiplier
    
    # Apply fixed discounts
    fixed_discounts = modifications.get('fixed_discounts', [])
    for discount in fixed_discounts:
        current_price -= discount['value']
    
    # Apply fixed surcharges
    fixed_surcharges = modifications.get('fixed_surcharges', [])
    for surcharge in fixed_surcharges:
        current_price += surcharge['value']
    
    # Ensure price doesn't go negative
    return max(0.0, current_price)
```

## Dynamic Key System

### Key Generation Strategy

```python
class DynamicKeyManager:
    """
    Dynamic key generation follows these patterns:
    
    Base Keys:
    - BASE_PRICE_NET
    - BASE_PRICE_GROSS
    - FINAL_PRICE_NET
    - FINAL_PRICE_GROSS
    
    Component Keys:
    - {COMPONENT_TYPE}_PRICE (e.g., PV_MODULE_PRICE)
    - {COMPONENT_TYPE}_QUANTITY
    - {COMPONENT_TYPE}_UNIT_PRICE
    
    Modification Keys:
    - DISCOUNT_{NAME}
    - SURCHARGE_{NAME}
    - TOTAL_DISCOUNTS
    - TOTAL_SURCHARGES
    
    VAT Keys:
    - VAT_RATE
    - VAT_AMOUNT
    - NET_TOTAL
    - GROSS_TOTAL
    """
    
    def generate_component_keys(self, component: Dict, price_info: Dict) -> Dict[str, str]:
        """Generate keys for individual components"""
        component_name = self._sanitize_key_name(component.get('model_name', 'COMPONENT'))
        
        return {
            f"{component_name}_PRICE": self._format_currency(price_info['total_price']),
            f"{component_name}_QUANTITY": str(price_info['quantity']),
            f"{component_name}_UNIT_PRICE": self._format_currency(price_info['unit_price']),
            f"{component_name}_CALCULATE_PER": component.get('calculate_per', 'Stück')
        }
    
    def _sanitize_key_name(self, name: str) -> str:
        """Convert name to valid key format"""
        return re.sub(r'[^A-Z0-9_]', '_', name.upper())
    
    def _format_currency(self, amount: float) -> str:
        """Format currency for PDF display"""
        return f"{amount:,.2f} €"
```

### PDF Integration

```python
def integrate_with_pdf(pricing_result: PricingResult, pdf_template: str) -> str:
    """
    Integrate pricing keys with PDF template
    
    Args:
        pricing_result: Complete pricing calculation result
        pdf_template: PDF template with placeholder keys
        
    Returns:
        PDF template with populated pricing values
    """
    
    dynamic_keys = pricing_result.dynamic_keys
    
    # Replace all dynamic keys in template
    populated_template = pdf_template
    for key, value in dynamic_keys.items():
        placeholder = f"{{{key}}}"
        populated_template = populated_template.replace(placeholder, str(value))
    
    return populated_template
```

## Extension Points

### Adding New Calculation Methods

```python
class CustomCalculatePerEngine(CalculatePerEngine):
    """
    Extend the base engine with custom calculation methods
    """
    
    SUPPORTED_METHODS = {
        **CalculatePerEngine.SUPPORTED_METHODS,
        "per_m2": "per_square_meter",
        "per_room": "per_room"
    }
    
    def calculate_per_square_meter(self, product: Dict, area_m2: float) -> float:
        """Custom calculation for area-based pricing"""
        return product['price_euro'] * area_m2
    
    def calculate_per_room(self, product: Dict, room_count: int) -> float:
        """Custom calculation for room-based pricing"""
        return product['price_euro'] * room_count
```

### Adding New Pricing Engines

```python
class CustomPricingEngine(PricingEngine):
    """
    Custom pricing engine for specialized systems
    """
    
    def __init__(self):
        super().__init__(system_type="custom")
        self.custom_rules = CustomPricingRules()
    
    def calculate_system_pricing(self, components: List[Dict], 
                               modifications: Dict = None) -> PricingResult:
        """Custom pricing calculation logic"""
        # Implement custom pricing logic
        pass
```

## Testing Framework

### Unit Test Structure

```python
import pytest
from pricing.enhanced_pricing_engine import PricingEngine
from pricing.calculate_per_engine import CalculatePerEngine

class TestPricingEngine:
    """Test suite for pricing engine functionality"""
    
    @pytest.fixture
    def sample_product(self):
        return {
            'id': 1,
            'model_name': 'Test Module',
            'price_euro': 180.0,
            'calculate_per': 'Stück',
            'purchase_price_net': 144.0,
            'margin_type': 'percentage',
            'margin_value': 25.0
        }
    
    def test_per_piece_calculation(self, sample_product):
        """Test per piece calculation method"""
        engine = CalculatePerEngine()
        result = engine.calculate_price(sample_product, quantity=20)
        
        assert result.total_price == 3600.0  # 180 * 20
        assert result.calculation_method == 'per_piece'
        assert result.unit_price == 180.0
    
    def test_profit_margin_calculation(self, sample_product):
        """Test profit margin application"""
        engine = PricingEngine()
        result = engine.calculate_component_pricing(sample_product, quantity=1)
        
        # Should use selling price (144 * 1.25 = 180)
        assert result.selling_price == 180.0
        assert result.margin_amount == 36.0
```

### Integration Test Examples

```python
class TestPricingIntegration:
    """Integration tests for complete pricing workflows"""
    
    def test_complete_pv_system_pricing(self):
        """Test complete PV system pricing calculation"""
        components = [
            {'id': 1, 'model_name': 'PV Module', 'calculate_per': 'Stück', 'quantity': 20},
            {'id': 2, 'model_name': 'Inverter', 'calculate_per': 'Stück', 'quantity': 1},
            {'id': 3, 'model_name': 'Mounting', 'calculate_per': 'kWp', 'system_size_kwp': 8.0}
        ]
        
        modifications = {
            'percentage_discounts': [{'name': 'early_payment', 'value': 3.0}],
            'fixed_surcharges': [{'name': 'delivery', 'value': 150.0}]
        }
        
        engine = PricingEngine(system_type='pv')
        result = engine.calculate_system_pricing(components, modifications)
        
        assert result.final_price_net > 0
        assert 'FINAL_PRICE_NET' in result.dynamic_keys
        assert 'PV_MODULE_PRICE' in result.dynamic_keys
```

## Performance Considerations

### Caching Strategy

```python
class PricingCache:
    """
    Intelligent caching for pricing calculations
    
    Cache Levels:
    1. Component price cache (product_id + quantity)
    2. Margin calculation cache (product_id + margin_config)
    3. System pricing cache (components + modifications hash)
    """
    
    def __init__(self):
        self.component_cache = {}
        self.margin_cache = {}
        self.system_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_component_price(self, cache_key: str) -> Optional[ComponentPricingResult]:
        """Get cached component price if available and valid"""
        if cache_key in self.component_cache:
            cached_result, timestamp = self.component_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_result
        return None
    
    def cache_component_price(self, cache_key: str, result: ComponentPricingResult):
        """Cache component pricing result"""
        self.component_cache[cache_key] = (result, time.time())
```

### Database Optimization

```python
# Recommended database indexes for pricing performance
CREATE INDEX idx_products_calculate_per ON products(calculate_per);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_pricing_category ON products(pricing_category);
CREATE INDEX idx_pricing_rules_applies_to ON pricing_rules(applies_to, target_id);
CREATE INDEX idx_pricing_rules_active ON pricing_rules(is_active, priority);
CREATE INDEX idx_pricing_history_product_id ON pricing_history(product_id);
```

### Performance Monitoring

```python
class PricingPerformanceMonitor:
    """Monitor pricing calculation performance"""
    
    def __init__(self):
        self.calculation_times = []
        self.cache_hit_rates = {}
        self.error_counts = {}
    
    def record_calculation_time(self, operation: str, duration: float):
        """Record timing for pricing operations"""
        self.calculation_times.append({
            'operation': operation,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        return {
            'avg_calculation_time': self._calculate_average_time(),
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'error_rate': self._calculate_error_rate()
        }
```

## Error Handling

### Custom Exception Classes

```python
class PricingError(Exception):
    """Base class for pricing-related errors"""
    pass

class InvalidCalculatePerError(PricingError):
    """Raised when calculate_per method is invalid"""
    pass

class MarginCalculationError(PricingError):
    """Raised when margin calculation fails"""
    pass

class PriceValidationError(PricingError):
    """Raised when price validation fails"""
    pass

class DynamicKeyError(PricingError):
    """Raised when dynamic key generation fails"""
    pass
```

### Error Recovery Strategies

```python
def safe_calculate_pricing(components: List[Dict], modifications: Dict = None) -> PricingResult:
    """
    Safe pricing calculation with error recovery
    
    Recovery strategies:
    1. Use fallback calculation methods
    2. Apply default margins if custom margins fail
    3. Skip invalid components with logging
    4. Generate basic keys if dynamic key generation fails
    """
    
    try:
        return calculate_system_pricing(components, modifications)
    except InvalidCalculatePerError as e:
        logger.warning(f"Invalid calculate_per method, using fallback: {e}")
        return calculate_with_fallback_method(components, modifications)
    except MarginCalculationError as e:
        logger.warning(f"Margin calculation failed, using default margins: {e}")
        return calculate_with_default_margins(components, modifications)
    except Exception as e:
        logger.error(f"Pricing calculation failed: {e}")
        return create_error_pricing_result(str(e))
```

This developer guide provides comprehensive documentation for extending and maintaining the enhanced pricing system. It covers all major components, APIs, and integration points needed for development work.
