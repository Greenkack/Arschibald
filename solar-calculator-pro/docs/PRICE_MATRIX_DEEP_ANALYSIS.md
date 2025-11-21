# Price Matrix Deep Analysis - Task 95

**Date:** 2024-01-21  
**Status:** Complete  
**Requirements:** 1.3, 6.1

## Executive Summary

This document provides a comprehensive deep analysis of all price_matrix_*.py modules and related components in the system. The price matrix system implements an Excel-like INDEX/MATCH lookup mechanism for dynamic pricing based on module count and storage model selection.

---

## 1. Module Overview

### Core Modules Analyzed

1. **price_matrix_store.py** - Data persistence and CRUD operations
2. **price_matrix_validation.py** - Matrix structure validation
3. **price_matrix_lookup.py** - Price lookup with INDEX/MATCH logic
4. **price_matrix_error_handling.py** - Comprehensive error handling
5. **price_matrix_error_handler.py** - Error types and fallback mechanisms
6. **price_matrix_performance.py** - Performance monitoring and optimization
7. **matrix_extras_calculator.py** - Additional costs calculation
8. **special_products.py** - Special product identification
9. **excel/excel_formula_engine.py** - Formula parsing and execution

---

## 2. Matrix Structure and Data Model

### 2.1 Database Schema

The price matrix uses a normalized database structure with 4 main tables:

#### price_matrix_sets (Matrix Metadata)
```sql
CREATE TABLE price_matrix_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 0,
    pricing_mode TEXT DEFAULT 'pauschal',  -- 'pauschal' | 'additiv'
    include_accessories INTEGER DEFAULT 1,
    include_misc INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Key Fields:**
- `pricing_mode`: Determines if price is all-inclusive ('pauschal') or additive ('additiv')
- `include_accessories`: Whether accessories are included in base price
- `include_misc`: Whether miscellaneous items are included in base price

#### price_matrix_rows (Module Counts)
```sql
CREATE TABLE price_matrix_rows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matrix_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    label TEXT NOT NULL,  -- e.g., "10", "15", "20" (module counts)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(matrix_id) REFERENCES price_matrix_sets(id) ON DELETE CASCADE
)
```

#### price_matrix_columns (Storage Models)
```sql
CREATE TABLE price_matrix_columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matrix_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    label TEXT NOT NULL,  -- e.g., "10kWh", "15kWh", "Kein Speicher"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(matrix_id) REFERENCES price_matrix_sets(id) ON DELETE CASCADE
)
```

#### price_matrix_cells (Prices)
```sql
CREATE TABLE price_matrix_cells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matrix_id INTEGER NOT NULL,
    row_id INTEGER NOT NULL,
    column_id INTEGER NOT NULL,
    value REAL,  -- Numeric price value
    raw_input TEXT,  -- Original input (for formulas/text)
    data_type TEXT DEFAULT 'text',  -- 'text', 'number', 'formula', 'date'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(matrix_id, row_id, column_id),
    FOREIGN KEY(matrix_id) REFERENCES price_matrix_sets(id) ON DELETE CASCADE,
    FOREIGN KEY(row_id) REFERENCES price_matrix_rows(id) ON DELETE CASCADE,
    FOREIGN KEY(column_id) REFERENCES price_matrix_columns(id) ON DELETE CASCADE
)
```

**Key Features:**
- `value`: Numeric price for calculations
- `raw_input`: Stores original input (formulas, text)
- `data_type`: Supports multiple data types (Task 3.2)

### 2.2 Matrix Structure Example

```
         A              B              C              D
    (Modulanzahl)  (10kWh)        (15kWh)        (Kein Speicher)
1   Modulanzahl    10kWh          15kWh          Kein Speicher
2   10             15000.00       17500.00       12000.00
3   15             18000.00       20500.00       15000.00
4   20             21000.00       23500.00       18000.00
5   25             24000.00       26500.00       21000.00
```

**Structure Rules:**
- **Column A (Position 0)**: Module counts (numeric, ascending)
- **Row 1 (Position 0)**: Storage model names (text)
- **Price Cells**: Turnkey system prices (numeric)
- **Last Column**: "Kein Speicher" (No Storage) option

---

## 3. Lookup Logic - INDEX/MATCH Implementation

### 3.1 Excel INDEX/MATCH Formula

The system implements Excel's INDEX/MATCH logic:

```excel
=INDEX(A2:A200, VERGLEICH(C37, A2:XX200, 0), VERGLEICH(C65, B2:XX2, 0))
```

**Translation:**
- `C37`: Module count input
- `C65`: Storage model input
- `A2:A200`: Module count column
- `B2:XX2`: Storage model row
- Result: Price at intersection

### 3.2 Lookup Algorithm

#### Step 1: Find Module Count Row (Floor Logic)

```python
def find_module_count_row(matrix_data: dict, module_count: int) -> Tuple[Optional[str], Optional[int]]:
    """
    Finds row for given module count using floor logic:
    1. Exact match preferred
    2. If not found: Use next-smaller number (floor logic)
    3. Error if no suitable row found
    """
```

**Floor Logic Example:**
- Input: 18 modules
- Available: [10, 15, 20, 25]
- Result: Uses row 15 (largest value ≤ 18)

#### Step 2: Find Storage Column

```python
def find_storage_column(matrix_data: dict, storage_model: Optional[str]) -> Tuple[Optional[str], Optional[int]]:
    """
    Finds column for given storage model:
    1. Exact match with model name (case-insensitive)
    2. If storage_model is None: Search "Kein Speicher" column
    3. Error if model not found
    """
```

**"Kein Speicher" Variants:**
- "kein speicher"
- "ohne speicher"
- "keine batterie"
- "ohne batterie"
- "no storage"
- "none"

#### Step 3: Lookup Price at Intersection

```python
def lookup_price_by_intersection(matrix_data: dict, row_id: int, column_id: int) -> Optional[float]:
    """
    Gets price at row/column intersection:
    - Cell must exist
    - Value must be numeric
    - Error if empty or invalid
    """
```

### 3.3 Complete Lookup Function

```python
def calculate_price_from_matrix(
    module_count: int,
    storage_model: Optional[str],
    matrix_id: Optional[int] = None,
    enable_fallback: bool = False
) -> dict[str, Any]:
    """
    Complete price calculation with:
    1. Input validation
    2. Matrix data loading
    3. Edge case handling
    4. Row lookup (floor logic)
    5. Column lookup
    6. Price retrieval
    7. Comprehensive error handling
    8. Optional fallback strategies
    """
```

**Return Structure:**
```python
{
    'success': bool,
    'base_price': float | None,
    'row_used': str | None,
    'row_id': int | None,
    'column_used': str | None,
    'column_id': int | None,
    'matrix_id': int | None,
    'matrix_name': str | None,
    'error': str | None,
    'error_type': str | None,
    'user_message': str | None,
    'fallback_used': bool,
    'fallback_info': dict | None,
    'debug_info': dict | None
}
```

---

## 4. Pricing Rules and Modifiers

### 4.1 Base Price Components

**Pauschal Mode (All-Inclusive):**
The base price from the matrix includes:
- PV modules
- Inverter
- Battery storage (if selected)
- Mounting system (Unterkonstruktion)
- All cables and materials
- Installation and commissioning
- Permits and approvals (Genehmigungen)
- Commissions and margins (Provisionen)

**Additiv Mode (Component-Based):**
Each component is priced separately and added together.

### 4.2 Additional Costs

Additional costs are calculated ONLY if selected:

```python
def calculate_all_extras(details: dict[str, Any]) -> dict[str, Any]:
    """
    Calculates all additional costs:
    - Special products (is_special_product = 1)
    - Additional services
    - Extras and special requests
    """
```

**Categories:**
1. **Special Products** (`calculate_special_products_cost`)
   - Special modules
   - Special inverters
   - Special storage systems
   - Additional components (optimizers, monitoring)

2. **Services** (`calculate_services_cost`)
   - Optional services only
   - Standard services included in base price

3. **Extras** (`calculate_extras_cost`)
   - Custom items
   - Special requests
   - User-defined positions

### 4.3 Discounts and Surcharges

```python
def apply_discounts_and_surcharges(base_amount: float, details: dict[str, Any]) -> dict[str, Any]:
    """
    Applies discounts and surcharges:
    - Percentage discounts
    - Fixed amount discounts
    - Percentage surcharges
    - Fixed amount surcharges
    """
```

**Application Order:**
1. Base amount
2. Apply percentage discount
3. Apply fixed discount
4. Apply percentage surcharge
5. Apply fixed surcharge
6. Final amount

---

## 5. Validation Rules

### 5.1 Matrix Structure Validation

```python
def validate_matrix_for_pricing(matrix_id: int) -> Dict[str, Any]:
    """
    Validates matrix structure:
    - Column A contains numeric values (module counts)
    - Row 1 contains text values (storage models)
    - At least one "Kein Speicher" column present
    - All price cells contain numbers or are empty
    """
```

**Validation Checks:**

1. **Column A Numeric** (Requirement 2.1)
   - All values except header must be numeric
   - Represents module counts
   - Must be parseable as float

2. **Row 1 Text** (Requirement 2.2)
   - All values except first cell must be text
   - Represents storage model names
   - Can be any string

3. **"Kein Speicher" Column** (Requirement 2.3)
   - At least one column must match keywords
   - Required for "no storage" option
   - Case-insensitive matching

4. **Price Cells Numeric** (Requirement 2.4)
   - All price cells must be numeric or empty
   - No text in price cells
   - Positive values only

### 5.2 Validation Result Structure

```python
{
    'valid': bool,
    'errors': List[str],
    'warnings': List[str],
    'info': {
        'total_rows': int,
        'total_columns': int,
        'total_cells': int,
        'module_counts': List[int],
        'storage_models': List[str],
        'empty_price_cells': int,
        'no_storage_column': str
    }
}
```

---

## 6. Error Handling System

### 6.1 Error Types

```python
class ErrorCategory(Enum):
    MATRIX_NOT_FOUND = "matrix_not_found"
    MODULE_COUNT_MISSING = "module_count_missing"
    STORAGE_MODEL_MISSING = "storage_model_missing"
    CELL_EMPTY = "cell_empty"
    CELL_INVALID = "cell_invalid"
    VALIDATION_FAILED = "validation_failed"
    INPUT_INVALID = "input_invalid"
    SYSTEM_ERROR = "system_error"

class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

### 6.2 Custom Exception Classes

```python
class PriceMatrixError(Exception):
    """Base exception for price matrix errors"""
    
class MatrixNotFoundError(PriceMatrixError):
    """No active matrix found"""
    
class ModuleCountNotFoundError(PriceMatrixError):
    """Module count not in matrix"""
    
class StorageModelNotFoundError(PriceMatrixError):
    """Storage model not in matrix"""
    
class PriceCellEmptyError(PriceMatrixError):
    """Price cell is empty"""
    
class InvalidPriceError(PriceMatrixError):
    """Price cell contains invalid value"""
```

### 6.3 Error Handling Flow

```python
def handle_error_with_fallback(
    error: Exception,
    module_count: int,
    storage_model: Optional[str],
    matrix_data: Optional[Dict[str, Any]] = None,
    enable_fallback: bool = True,
    notify_admin: bool = True
) -> Dict[str, Any]:
    """
    Comprehensive error handling:
    1. Classify error
    2. Create user-friendly message
    3. Try fallback strategies
    4. Notify admin if critical
    5. Return structured result
    """
```

### 6.4 Fallback Strategies

```python
class FallbackStrategy(Enum):
    NONE = "none"
    FLOOR_MODULE_COUNT = "floor_module"  # Use next-smaller module count
    NO_STORAGE = "no_storage"  # Use "Kein Speicher" column
    STANDARD_CALCULATION = "standard_calc"  # Use standard calculation
    DEFAULT_PRICE = "default_price"  # Use default price
```

**Fallback Logic:**
1. **Module Count Missing**: Use floor logic (next-smaller count)
2. **Storage Model Missing**: Try "Kein Speicher" column
3. **Matrix Not Found**: Fall back to standard calculation
4. **Cell Empty/Invalid**: No automatic fallback (requires admin action)

---

## 7. Formula Engine Integration

### 7.1 Excel Formula Engine

The system includes a complete Excel formula engine for advanced matrix features:

```python
class FormulaEngine:
    """
    Excel formula parser and executor supporting:
    - Arithmetic operations (+, -, *, /)
    - Excel functions (SUM, AVERAGE, IF, VLOOKUP, etc.)
    - Cell references (A1, B2)
    - Ranges (A1:A10)
    - Nested formulas
    - Caching for performance
    """
```

### 7.2 Supported Formula Types

1. **Arithmetic Expressions**
   ```python
   "=A1 + B1"
   "=A1 * 1.19"  # Add VAT
   "=(A1 + B1) / 2"
   ```

2. **Excel Functions**
   ```python
   "=SUM(A1:A10)"
   "=AVERAGE(B1:B5)"
   "=IF(A1>100, A1*0.9, A1)"  # 10% discount if > 100
   "=VLOOKUP(A1, B1:C10, 2, FALSE)"
   ```

3. **Cell References**
   ```python
   "=A1"  # Simple reference
   "=Sheet1!A1"  # Cross-sheet reference
   ```

4. **Ranges**
   ```python
   "=SUM(A1:A10)"
   "=AVERAGE(B1:B5, D1:D5)"
   ```

### 7.3 Formula Execution Flow

```python
def execute_formula(self, formula: str, context: Dict[Tuple[int, int], Any]) -> Any:
    """
    1. Parse formula
    2. Check cache
    3. Replace cell references with values
    4. Execute based on type:
       - Function: Call Excel function
       - Arithmetic: Evaluate expression
       - Reference: Return cell value
       - Value: Return constant
    5. Cache result
    6. Return value
    """
```

### 7.4 Dependency Management

```python
def build_dependency_graph(self, cells: Dict[Tuple[int, int], Cell]) -> None:
    """
    Creates dependency graph showing which cells depend on which:
    - Enables efficient recalculation
    - Detects circular references
    - Determines calculation order
    """

def get_calculation_order(self, cells: Dict[Tuple[int, int], Cell]) -> List[Tuple[int, int]]:
    """
    Topological sort to determine calculation order:
    - Dependencies calculated before dependents
    - Raises CircularReferenceError if circular dependency detected
    """
```

---

## 8. Performance Optimization

### 8.1 Performance Monitoring

```python
class PerformanceMonitor:
    """
    Tracks performance metrics:
    - Operation execution times
    - Cache hit/miss rates
    - Memory usage
    - Error rates
    """
```

**Metrics Tracked:**
- Total operations
- Average execution time
- Min/max execution time
- Cache hit rate
- Memory usage
- Error count

### 8.2 Caching System

**Formula Cache:**
```python
def _build_cache_key(self, formula: str, context: Dict[Tuple[int, int], Any]) -> str:
    """
    Creates cache key from formula and referenced cell values:
    - Format: "formula|ref1:val1|ref2:val2|..."
    - Ensures cache only used when dependencies unchanged
    """
```

**Cache Invalidation:**
```python
def invalidate_cache(self, changed_cells: Optional[List[Tuple[int, int]]] = None):
    """
    Invalidates cache for affected cells:
    - If changed_cells specified: Only invalidate dependent entries
    - If None: Clear entire cache
    """
```

### 8.3 Performance Benchmarking

```python
def benchmark_matrix_lookup(
    module_counts: list[int],
    storage_models: list[str],
    iterations: int = 100
) -> dict[str, Any]:
    """
    Benchmarks lookup performance:
    - Tests multiple combinations
    - Measures execution time
    - Calculates lookups per second
    - Identifies bottlenecks
    """
```

---

## 9. Special Products System

### 9.1 Special Product Identification

```python
def is_special_product(product_id: int) -> bool:
    """
    Checks if product is marked as special product:
    - Special products: Additional cost in matrix mode
    - Standard products: Included in base price
    """
```

**Standard Product Categories:**
- PV-Module
- Wechselrichter
- Batteriespeicher
- Speicher
- Storage

**Special Product Examples:**
- Special mounting systems
- Additional optimizers
- Special equipment
- Additional components

### 9.2 Special Product Calculation

```python
def calculate_special_products_cost(details: dict[str, Any]) -> dict[str, Any]:
    """
    Calculates costs for special products:
    1. Check each selected product
    2. If marked as special: Add to additional costs
    3. If standard: Already in base price
    4. Return breakdown
    """
```

---

## 10. Data Flow Diagrams

### 10.1 Price Calculation Flow

```
User Input
    ↓
[Module Count, Storage Model]
    ↓
validate_input_parameters()
    ↓
get_active_matrix_id()
    ↓
get_matrix_full(matrix_id)
    ↓
find_module_count_row() → Floor Logic
    ↓
find_storage_column() → Exact Match
    ↓
lookup_price_by_intersection()
    ↓
calculate_all_extras()
    ↓
apply_discounts_and_surcharges()
    ↓
Final Price
```

### 10.2 Error Handling Flow

```
Error Occurs
    ↓
classify_error()
    ↓
create_user_friendly_message()
    ↓
try_fallback() ?
    ├─ Yes → Apply Fallback Strategy
    │           ↓
    │       Retry Calculation
    │           ↓
    │       Success? → Return Result
    │           ↓
    │       Failure → Continue to Error
    │
    └─ No → Return Error
            ↓
        notify_admin() ?
            ↓
        Return Error Result
```

### 10.3 Formula Execution Flow

```
Formula Input
    ↓
parse_formula()
    ↓
Check Cache?
    ├─ Hit → Return Cached Result
    │
    └─ Miss → Continue
            ↓
        extract_cell_references()
            ↓
        replace_cell_references()
            ↓
        execute_based_on_type()
            ├─ Function → _execute_function()
            ├─ Arithmetic → _execute_arithmetic()
            ├─ Reference → Return Cell Value
            └─ Value → Return Constant
            ↓
        Cache Result
            ↓
        Return Result
```

---

## 11. API Reference

### 11.1 Core Functions

#### Matrix Management
```python
create_matrix(name, description, pricing_mode, include_accessories, include_misc) -> int
list_matrices() -> list[dict]
set_active_matrix(matrix_id) -> bool
get_active_matrix_id() -> int | None
delete_matrix(matrix_id) -> bool
clone_matrix(matrix_id, new_name) -> int | None
```

#### Matrix Structure
```python
add_row(matrix_id, label, position) -> int | None
add_column(matrix_id, label, position) -> int | None
remove_row(row_id) -> bool
remove_column(column_id) -> bool
set_cell_value(matrix_id, row_id, column_id, value, raw_input, data_type) -> bool
```

#### Matrix Data
```python
get_matrix_full(matrix_id) -> dict | None
export_matrix_csv(matrix_id, delimiter) -> str | None
import_matrix_csv(name, csv_text, delimiter) -> int | None
```

#### Price Lookup
```python
lookup_price(matrix_id, row_label, column_label) -> float | None
lookup_price_with_meta(matrix_id, row_label, column_label) -> dict
calculate_price_from_matrix(module_count, storage_model, matrix_id, enable_fallback) -> dict
calculate_price_from_matrix_safe(module_count, storage_model, matrix_id, enable_fallback, notify_admin) -> dict
```

#### Validation
```python
validate_matrix_for_pricing(matrix_id) -> dict
get_validation_summary(validation_result) -> str
validate_matrix_with_error_handling(matrix_id) -> dict
```

#### Error Handling
```python
classify_error(error) -> PriceMatrixErrorInfo
format_error_message_for_ui(error_info, include_suggestions, include_details) -> str
handle_error_with_fallback(error, module_count, storage_model, matrix_data, enable_fallback, notify_admin) -> dict
```

#### Extras Calculation
```python
calculate_special_products_cost(details) -> dict
calculate_services_cost(details) -> dict
calculate_extras_cost(details) -> dict
apply_discounts_and_surcharges(base_amount, details) -> dict
calculate_all_extras(details) -> dict
```

### 11.2 Formula Engine Functions

```python
parse_formula(formula) -> dict
execute_formula(formula, context) -> Any
build_dependency_graph(cells) -> None
get_dependent_cells(cell) -> Set[Tuple[int, int]]
get_calculation_order(cells) -> List[Tuple[int, int]]
recalculate_affected_cells(changed_cell, cells, context) -> dict
invalidate_cache(changed_cells) -> None
```

---

## 12. Integration Points

### 12.1 Database Integration

**Module:** `database.py`
- `get_db_connection()`: Database connection
- `INITIAL_ADMIN_SETTINGS`: Default settings including matrix config

### 12.2 Solar Calculator Integration

**Module:** `calculations.py`
- Imports `price_matrix_store` for price lookup
- Uses `lookup_price()` for base price calculation
- Integrates with `matrix_extras_calculator` for additional costs

### 12.3 Admin Panel Integration

**Module:** `admin_panel.py`
- Matrix upload interface
- Matrix management UI
- Validation display
- Error reporting

### 12.4 Excel Integration

**Module:** `excel/excel_formula_engine.py`
- Formula parsing
- Cell reference resolution
- Dependency management
- Caching

---

## 13. Key Insights and Recommendations

### 13.1 Strengths

1. **Comprehensive Error Handling**
   - Multiple error types with clear categorization
   - User-friendly error messages
   - Fallback strategies for common issues
   - Admin notifications for critical errors

2. **Flexible Architecture**
   - Supports multiple pricing modes (pauschal/additiv)
   - Extensible formula engine
   - Normalized database structure
   - Version control ready (multiple matrices)

3. **Performance Optimization**
   - Formula caching
   - Dependency tracking
   - Performance monitoring
   - Efficient lookup algorithms

4. **Validation System**
   - Comprehensive structure validation
   - Clear validation messages
   - Detailed error reporting
   - Example structures provided

### 13.2 Areas for Enhancement

1. **Formula Engine**
   - Currently uses `eval()` for arithmetic (security concern)
   - Consider using `ast.literal_eval` with whitelist
   - Add more Excel functions
   - Improve circular reference detection

2. **Caching**
   - Implement TTL (Time-To-Live) for cache entries
   - Add cache size limits
   - Implement LRU (Least Recently Used) eviction
   - Add cache warming strategies

3. **Testing**
   - Add property-based tests for lookup logic
   - Add integration tests for formula engine
   - Add performance regression tests
   - Add edge case tests

4. **Documentation**
   - Add inline code examples
   - Create video tutorials
   - Add troubleshooting guide
   - Create API documentation

### 13.3 Migration Considerations

For the Electron migration (Task 95 context):

1. **Backend API Design**
   - All functions should be exposed via REST endpoints
   - WebSocket support for real-time updates
   - Batch operations for performance
   - Streaming for large matrices

2. **Frontend Integration**
   - React components for matrix display
   - Excel-like grid component
   - Real-time validation feedback
   - Drag-and-drop matrix upload

3. **Data Synchronization**
   - Offline support with local cache
   - Conflict resolution strategies
   - Real-time collaboration support
   - Version control integration

---

## 14. Conclusion

The price matrix system is a comprehensive, well-architected solution for dynamic pricing based on module count and storage model selection. It implements Excel-like INDEX/MATCH logic with extensive error handling, validation, and performance optimization.

**Key Features:**
- ✅ Normalized database structure
- ✅ Floor logic for module count matching
- ✅ Comprehensive error handling with fallbacks
- ✅ Formula engine for advanced calculations
- ✅ Performance monitoring and caching
- ✅ Special products and extras calculation
- ✅ Validation system with detailed feedback

**Ready for Migration:**
The system is well-structured for migration to the Electron/React architecture, with clear separation of concerns and comprehensive API surface.

---

## Appendix A: File Locations

```
price_matrix_store.py                    # Core data persistence (885 lines)
price_matrix_validation.py               # Structure validation (500+ lines)
price_matrix_lookup.py                   # Lookup logic (800+ lines)
price_matrix_error_handling.py           # Error handling (600+ lines)
price_matrix_error_handler.py            # Error types (400+ lines)
price_matrix_performance.py              # Performance monitoring (600+ lines)
matrix_extras_calculator.py              # Additional costs (400+ lines)
special_products.py                      # Special product logic (200+ lines)
excel/excel_formula_engine.py            # Formula engine (1011 lines)
excel/excel_models.py                    # Data models
excel/excel_utils.py                     # Utility functions
excel/python_function_recipes.py         # Excel functions
```

**Total Lines of Code:** ~6,000+ lines

---

## Appendix B: Database Queries

### Common Queries

**Get Active Matrix:**
```sql
SELECT id FROM price_matrix_sets WHERE is_active=1 LIMIT 1
```

**Get Matrix Full Data:**
```sql
-- Metadata
SELECT id, name, description, is_active, pricing_mode, include_accessories, include_misc 
FROM price_matrix_sets WHERE id=?

-- Rows
SELECT id, position, label FROM price_matrix_rows 
WHERE matrix_id=? ORDER BY position ASC

-- Columns
SELECT id, position, label FROM price_matrix_columns 
WHERE matrix_id=? ORDER BY position ASC

-- Cells
SELECT row_id, column_id, value, raw_input, data_type 
FROM price_matrix_cells WHERE matrix_id=?
```

**Lookup Price:**
```sql
-- Find row by label
SELECT id FROM price_matrix_rows 
WHERE matrix_id=? AND label=?

-- Find column by label
SELECT id FROM price_matrix_columns 
WHERE matrix_id=? AND label=?

-- Get cell value
SELECT value FROM price_matrix_cells 
WHERE matrix_id=? AND row_id=? AND column_id=?
```

---

**Analysis Complete**  
**Task 95 Status:** ✅ Complete  
**Next Steps:** Ready for implementation in Electron/React architecture
