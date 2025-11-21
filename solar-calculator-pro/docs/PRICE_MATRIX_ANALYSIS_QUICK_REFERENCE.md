# Price Matrix Analysis - Quick Reference

**Task 95 Complete** | [Full Analysis](./PRICE_MATRIX_DEEP_ANALYSIS.md)

## Core Modules

| Module | Purpose | Lines | Key Functions |
|--------|---------|-------|---------------|
| `price_matrix_store.py` | Data persistence & CRUD | 885 | `create_matrix`, `lookup_price`, `get_matrix_full` |
| `price_matrix_lookup.py` | INDEX/MATCH logic | 800+ | `calculate_price_from_matrix`, `find_module_count_row` |
| `price_matrix_validation.py` | Structure validation | 500+ | `validate_matrix_for_pricing` |
| `price_matrix_error_handling.py` | Error handling | 600+ | `handle_error_with_fallback`, `classify_error` |
| `price_matrix_performance.py` | Performance monitoring | 600+ | `PerformanceMonitor`, `benchmark_matrix_lookup` |
| `matrix_extras_calculator.py` | Additional costs | 400+ | `calculate_all_extras` |
| `special_products.py` | Special product logic | 200+ | `is_special_product` |
| `excel/excel_formula_engine.py` | Formula engine | 1011 | `execute_formula`, `parse_formula` |

**Total:** ~6,000+ lines of code

---

## Matrix Structure

```
         A              B              C              D
    (Modulanzahl)  (10kWh)        (15kWh)        (Kein Speicher)
1   Modulanzahl    10kWh          15kWh          Kein Speicher
2   10             15000.00       17500.00       12000.00
3   15             18000.00       20500.00       15000.00
4   20             21000.00       23500.00       18000.00
```

**Rules:**
- Column A: Module counts (numeric)
- Row 1: Storage models (text)
- Price cells: Turnkey prices (numeric)
- Last column: "Kein Speicher" option

---

## Lookup Logic (INDEX/MATCH)

### Excel Formula
```excel
=INDEX(A2:A200, VERGLEICH(C37, A2:XX200, 0), VERGLEICH(C65, B2:XX2, 0))
```

### Python Implementation
```python
# Step 1: Find module count row (floor logic)
row_label, row_id = find_module_count_row(matrix_data, module_count)
# Input: 18 modules, Available: [10, 15, 20, 25] → Uses 15

# Step 2: Find storage column (exact match)
column_label, column_id = find_storage_column(matrix_data, storage_model)
# Input: "15kWh" → Finds "15kWh" column

# Step 3: Get price at intersection
price = lookup_price_by_intersection(matrix_data, row_id, column_id)
# Returns: 18000.00
```

---

## Database Schema

### 4 Main Tables

1. **price_matrix_sets** - Matrix metadata
   - `pricing_mode`: 'pauschal' | 'additiv'
   - `include_accessories`, `include_misc`: bool

2. **price_matrix_rows** - Module counts
   - `label`: "10", "15", "20", etc.
   - `position`: Sort order

3. **price_matrix_columns** - Storage models
   - `label`: "10kWh", "15kWh", "Kein Speicher"
   - `position`: Sort order

4. **price_matrix_cells** - Prices
   - `value`: Numeric price
   - `raw_input`: Original input (formulas/text)
   - `data_type`: 'text' | 'number' | 'formula' | 'date'

---

## Pricing Rules

### Base Price (Pauschal Mode)
**Includes:**
- PV modules
- Inverter
- Battery storage
- Mounting system
- Installation
- Permits
- Commissions

### Additional Costs
**Only if selected:**
- Special products (`is_special_product = 1`)
- Additional services
- Extras and special requests

### Modifiers
1. Percentage discount
2. Fixed discount
3. Percentage surcharge
4. Fixed surcharge

---

## Error Handling

### Error Types
```python
MATRIX_NOT_FOUND          # No active matrix
MODULE_COUNT_MISSING      # Module count not in matrix
STORAGE_MODEL_MISSING     # Storage model not in matrix
CELL_EMPTY                # Price cell is empty
CELL_INVALID              # Price cell has invalid value
```

### Fallback Strategies
```python
FLOOR_MODULE_COUNT        # Use next-smaller module count
NO_STORAGE                # Use "Kein Speicher" column
STANDARD_CALCULATION      # Fall back to standard calc
```

### Error Severity
```python
INFO      # Informational
WARNING   # Warning, operation possible
ERROR     # Error, operation limited
CRITICAL  # Critical, operation not possible
```

---

## Formula Engine

### Supported Features
- ✅ Arithmetic: `+`, `-`, `*`, `/`
- ✅ Cell references: `A1`, `B2`
- ✅ Ranges: `A1:A10`
- ✅ Functions: `SUM`, `AVERAGE`, `IF`, `VLOOKUP`, etc.
- ✅ Nested formulas
- ✅ Dependency tracking
- ✅ Circular reference detection
- ✅ Caching

### Example Formulas
```python
"=A1 + B1"                    # Arithmetic
"=SUM(A1:A10)"                # Function
"=IF(A1>100, A1*0.9, A1)"     # Conditional
"=A1 * 1.19"                  # VAT calculation
```

---

## Validation Rules

### Required Checks
1. ✅ Column A: Numeric values (module counts)
2. ✅ Row 1: Text values (storage models)
3. ✅ "Kein Speicher" column present
4. ✅ Price cells: Numeric or empty

### Validation Result
```python
{
    'valid': bool,
    'errors': List[str],
    'warnings': List[str],
    'info': {
        'total_rows': int,
        'total_columns': int,
        'module_counts': List[int],
        'storage_models': List[str]
    }
}
```

---

## Performance Optimization

### Caching
- Formula results cached
- Cache key: formula + referenced cell values
- Automatic invalidation on cell changes

### Monitoring
```python
monitor = PerformanceMonitor()
with monitor.track_operation('matrix_lookup'):
    result = calculate_price_from_matrix(20, "15kWh")
report = monitor.generate_report()
```

### Metrics Tracked
- Execution times (min/avg/max)
- Cache hit/miss rates
- Memory usage
- Error rates

---

## API Quick Reference

### Matrix Management
```python
create_matrix(name, description, pricing_mode) -> int
list_matrices() -> list[dict]
set_active_matrix(matrix_id) -> bool
get_active_matrix_id() -> int | None
```

### Price Lookup
```python
calculate_price_from_matrix(
    module_count: int,
    storage_model: Optional[str],
    matrix_id: Optional[int] = None,
    enable_fallback: bool = False
) -> dict
```

### Validation
```python
validate_matrix_for_pricing(matrix_id: int) -> dict
get_validation_summary(validation_result: dict) -> str
```

### Extras Calculation
```python
calculate_all_extras(details: dict) -> dict
apply_discounts_and_surcharges(base_amount: float, details: dict) -> dict
```

---

## Integration Points

### Solar Calculator
- `calculations.py` imports `price_matrix_store`
- Uses `lookup_price()` for base price
- Integrates `matrix_extras_calculator` for additional costs

### Admin Panel
- `admin_panel.py` provides matrix management UI
- Upload, validation, and error display
- Matrix activation and configuration

### Excel Integration
- `excel/excel_formula_engine.py` for formula parsing
- Cell reference resolution
- Dependency management

---

## Migration Readiness

### Backend API Endpoints Needed
```
POST   /api/v1/pricing/matrix/calculate
GET    /api/v1/pricing/matrix/list
POST   /api/v1/pricing/matrix/create
PUT    /api/v1/pricing/matrix/{id}
DELETE /api/v1/pricing/matrix/{id}
POST   /api/v1/pricing/matrix/validate
POST   /api/v1/pricing/matrix/upload
GET    /api/v1/pricing/matrix/{id}/export
```

### Frontend Components Needed
- Matrix grid display (Excel-like)
- Matrix upload interface
- Validation feedback display
- Error message display
- Price calculation form
- Extras configuration

---

## Key Insights

### Strengths
✅ Comprehensive error handling  
✅ Flexible architecture (multiple pricing modes)  
✅ Performance optimization (caching, monitoring)  
✅ Extensive validation system  
✅ Formula engine for advanced calculations  

### Enhancement Opportunities
⚠️ Replace `eval()` with safer parser  
⚠️ Add TTL for cache entries  
⚠️ Add property-based tests  
⚠️ Improve circular reference detection  

---

## Quick Start Example

```python
# 1. Create matrix
matrix_id = create_matrix("Standard Pricing 2024", "Main pricing matrix")

# 2. Add rows (module counts)
add_row(matrix_id, "10", 0)
add_row(matrix_id, "15", 1)
add_row(matrix_id, "20", 2)

# 3. Add columns (storage models)
add_column(matrix_id, "10kWh", 0)
add_column(matrix_id, "15kWh", 1)
add_column(matrix_id, "Kein Speicher", 2)

# 4. Set prices
set_cell_value(matrix_id, row_id_10, col_id_10kwh, 15000.00)
set_cell_value(matrix_id, row_id_15, col_id_15kwh, 20500.00)

# 5. Activate matrix
set_active_matrix(matrix_id)

# 6. Calculate price
result = calculate_price_from_matrix(18, "15kWh", enable_fallback=True)
if result['success']:
    print(f"Price: {result['base_price']} EUR")
    print(f"Used row: {result['row_used']}, column: {result['column_used']}")
```

---

**Full Documentation:** [PRICE_MATRIX_DEEP_ANALYSIS.md](./PRICE_MATRIX_DEEP_ANALYSIS.md)  
**Task Status:** ✅ Complete  
**Requirements:** 1.3, 6.1
