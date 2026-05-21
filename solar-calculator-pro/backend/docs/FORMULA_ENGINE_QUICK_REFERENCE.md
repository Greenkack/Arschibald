# Price Matrix Formula Engine - Quick Reference

**Feature: streamlit-to-electron-migration, Task 140**

## Overview

Excel-like formula engine with INDEX/MATCH support for price matrix lookups. Implements German number formatting and comprehensive error handling.

## Core Features

### Supported Functions

1. **INDEX(array, row_num, [col_num])**
   - Returns value at specified position in array
   - 1-based indexing (Excel-style)
   - Supports 2D arrays

2. **MATCH(lookup_value, lookup_array, [match_type])**
   - Finds position of value in array
   - Returns 1-based position
   - Supports exact match (match_type=0)
   - Case-insensitive string matching

### Formula Examples

```python
# Basic INDEX
engine.evaluate("INDEX(A1:A5, 3)")  # Returns value at A3

# 2D INDEX
engine.evaluate("INDEX(A1:C3, 2, 2)")  # Returns value at B2

# MATCH
engine.evaluate("MATCH(30, A1:A5, 0)")  # Returns position of 30

# Nested INDEX/MATCH (Price Matrix Lookup)
engine.evaluate(
    'INDEX(A3:D5, MATCH(20, A3:A5, 0), MATCH("Model B", B2:D2, 0))'
)
```

## Price Matrix Usage

### Matrix Structure

```
     A          B          C          D
1    
2  (header)  Model A    Model B    kein Speicher
3    10       10000      12000      9000
4    20       15000      18000      14000
5    30       20000      24000      19000
```

### Loading Matrix Data

```python
from services.formula_engine import PriceMatrixFormulaEngine

engine = PriceMatrixFormulaEngine()

module_counts = [10, 20, 30]
battery_models = ["Model A", "Model B", "kein Speicher"]
matrix_data = [
    [10000, 12000, 9000],
    [15000, 18000, 14000],
    [20000, 24000, 19000]
]

engine.load_matrix(matrix_data, module_counts, battery_models)
```

### Price Lookup

```python
# Lookup price for 20 modules with Model B
price = engine.lookup_price(20, "Model B")
print(price)  # 18000

# Format price in German
formatted = engine.format_price_german(price)
print(formatted)  # "18.000,00 €"

# Handle "kein Speicher" (no storage)
price = engine.lookup_price(20, "kein Speicher")
print(price)  # 14000 (uses last column)
```

## German Number Formatting

```python
engine.format_price_german(16999.00)  # "16.999,00 €"
engine.format_price_german(1234.56)   # "1.234,56 €"
engine.format_price_german(999.99)    # "999,99 €"
```

## Error Handling

All error messages are in German:

```python
try:
    engine.evaluate("INDEX(A1:A2, 99)")
except EvaluationError as e:
    print(e)  # "Zeilenindex 99 außerhalb des Bereichs (1-2)"

try:
    engine.evaluate("MATCH(99, A1:A2, 0)")
except EvaluationError as e:
    print(e)  # "Wert '99' nicht gefunden in Array..."
```

## Circular Reference Detection

```python
engine.set_formula("A1", "=A2")
engine.set_formula("A2", "=A1")

try:
    engine.get_value("A1")
except CircularReferenceError as e:
    print(e)  # "Zirkuläre Referenz erkannt: A1 -> A2 -> A1"
```

## Performance Optimization

```python
from services.formula_engine import FormulaOptimizer

optimizer = FormulaOptimizer(engine)

# Optimize for large matrices
optimizer.optimize_matrix_lookup((200, 200))

# Clear cache
optimizer.clear_cache()
```

## Debugging Tools

```python
from services.formula_engine import FormulaDebugger

# Trace formula evaluation
trace = FormulaDebugger.trace_evaluation(engine, "INDEX(A1:A5, 3)")
print(trace["result"])

# Detect circular references
circular_refs = FormulaDebugger.validate_circular_references(engine)
print(circular_refs)
```

## API Integration

```python
# In FastAPI endpoint
from services.formula_engine import PriceMatrixFormulaEngine

@app.post("/api/v1/pricing/lookup")
async def lookup_price(
    module_count: int,
    battery_model: str
):
    engine = PriceMatrixFormulaEngine()
    # Load matrix from database
    engine.load_matrix(matrix_data, module_counts, battery_models)
    
    price = engine.lookup_price(module_count, battery_model)
    formatted_price = engine.format_price_german(price)
    
    return {
        "price": price,
        "formatted_price": formatted_price
    }
```

## Requirements Validated

✅ **1.3**: Excel INDEX/MATCH logic implemented  
✅ **4.5**: Price matrix formula engine  
✅ **6.1**: Modular service architecture  
✅ **14.2**: German number formatting (16.999,00 €)  

## Performance

- Optimized for matrices up to 200×200
- Caching support for repeated lookups
- Efficient column letter/number conversion
- Lazy evaluation of formulas

## Limitations

- Currently supports only INDEX and MATCH functions
- Match type 1 and -1 (sorted arrays) not yet implemented
- No arithmetic operations between cells
- No support for Excel functions like SUM, AVERAGE, etc.

## Future Enhancements

- Add more Excel functions (SUM, AVERAGE, IF, etc.)
- Support for sorted array matching
- Formula dependency graph visualization
- Performance profiling tools
- Formula auto-completion
