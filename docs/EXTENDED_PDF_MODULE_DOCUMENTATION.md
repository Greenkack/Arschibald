# Extended PDF Module Documentation

## Overview

The Extended PDF module (`extended_pdf_generator.py`) provides optional functionality to extend the standard 8-page PDF with additional pages containing financing details, product datasheets, company documents, and charts/visualizations.

**Key Principle:** This module is completely optional and does not affect the standard 8-page PDF generation. All features are disabled by default.

---

## Module Structure

### Main Classes

#### 1. `ExtendedPDFGenerator`

The main orchestrator class that coordinates the generation of all extended pages.

**Constructor:**

```python
ExtendedPDFGenerator(
    offer_data: dict[str, Any],
    analysis_results: dict[str, Any],
    options: dict[str, Any],
    theme: dict[str, Any] | None = None,
    logger: ExtendedPDFLogger | None = None
)
```

**Parameters:**

- `offer_data`: Dictionary containing offer information (prices, products, customer data)
- `analysis_results`: Dictionary containing analysis results with chart bytes
- `options`: Dictionary with extended output options from UI
- `theme`: Optional theme configuration (colors, fonts)
- `logger`: Optional logger instance for tracking errors and warnings

**Main Method:**

```python
generate_extended_pages() -> bytes
```

Returns PDF bytes containing all extended pages based on the options provided.

**Example Usage:**

```python
from extended_pdf_generator import ExtendedPDFGenerator, ExtendedPDFLogger

# Create logger
logger = ExtendedPDFLogger()

# Define options
options = {
    'financing_details': True,
    'product_datasheets': [1, 2, 3],  # Product IDs
    'company_documents': [1],  # Document IDs
    'selected_charts': [
        'monthly_prod_cons_chart_bytes',
        'cumulative_cashflow_chart_bytes'
    ],
    'chart_layout': 'two_per_page'
}

# Create generator
generator = ExtendedPDFGenerator(
    offer_data=offer_data,
    analysis_results=analysis_results,
    options=options,
    theme=theme,
    logger=logger
)

# Generate extended pages
extended_pdf_bytes = generator.generate_extended_pages()

# Check for errors
summary = logger.get_summary()
if summary['has_errors']:
    print(f"Generation completed with {summary['error_count']} errors")
```

---

#### 2. `FinancingPageGenerator`

Generates pages with financing details and calculations.

**Constructor:**

```python
FinancingPageGenerator(
    offer_data: dict,
    theme: dict,
    logger: ExtendedPDFLogger | None = None
)
```

**Main Method:**

```python
generate() -> bytes
```

Returns PDF bytes with financing overview and detailed calculations.

**Features:**

- Loads financing options from database (`payment_terms` admin settings)
- Displays financing options in styled boxes
- Calculates monthly rates using annuity formula
- Shows total costs and interest charges

**Example Usage:**

```python
from extended_pdf_generator import FinancingPageGenerator, ExtendedPDFLogger

logger = ExtendedPDFLogger()
generator = FinancingPageGenerator(
    offer_data={'grand_total': 25000.0},
    theme={'colors': {'primary': '#1E3A8A'}},
    logger=logger
)

financing_pdf = generator.generate()
```

**Annuity Formula:**

```
Monthly Payment = P * (r * (1 + r)^n) / ((1 + r)^n - 1)

Where:
- P = Principal (loan amount)
- r = Monthly interest rate (annual_rate / 12 / 100)
- n = Number of months
```

---

#### 3. `ProductDatasheetMerger`

Merges product datasheets from the database into the PDF.

**Constructor:**

```python
ProductDatasheetMerger(logger: ExtendedPDFLogger | None = None)
```

**Main Method:**

```python
merge(datasheet_ids: list[int]) -> bytes
```

Returns PDF bytes with merged product datasheets.

**Features:**

- Loads datasheets from database using `product_db.get_product_by_id()`
- Supports PDF datasheets (merged directly)
- Supports image datasheets (converted to PDF)
- Handles missing files gracefully

**Example Usage:**

```python
from extended_pdf_generator import ProductDatasheetMerger

merger = ProductDatasheetMerger()
datasheet_pdf = merger.merge([1, 2, 3])  # Product IDs
```

---

#### 4. `CompanyDocumentMerger`

Merges company documents from the database into the PDF.

**Constructor:**

```python
CompanyDocumentMerger(logger: ExtendedPDFLogger | None = None)
```

**Main Method:**

```python
merge(document_ids: list[int]) -> bytes
```

Returns PDF bytes with merged company documents.

**Features:**

- Loads documents from database using `database.get_company_document_file_path()`
- Supports PDF documents
- Handles missing files gracefully

**Example Usage:**

```python
from extended_pdf_generator import CompanyDocumentMerger

merger = CompanyDocumentMerger()
documents_pdf = merger.merge([1, 2])  # Document IDs
```

---

#### 5. `ChartPageGenerator`

Generates pages with charts and visualizations.

**Constructor:**

```python
ChartPageGenerator(
    analysis_results: dict,
    layout: str,
    theme: dict,
    logger: ExtendedPDFLogger | None = None
)
```

**Parameters:**

- `analysis_results`: Dictionary with chart bytes (keys ending in `_chart_bytes`)
- `layout`: Layout type ('one_per_page', 'two_per_page', 'four_per_page')
- `theme`: Theme configuration
- `logger`: Optional logger instance

**Main Method:**

```python
generate(chart_keys: list[str]) -> bytes
```

Returns PDF bytes with chart pages.

**Supported Layouts:**

- `one_per_page`: One chart per page (full size)
- `two_per_page`: Two charts per page (2x1 grid)
- `four_per_page`: Four charts per page (2x2 grid)

**Example Usage:**

```python
from extended_pdf_generator import ChartPageGenerator

generator = ChartPageGenerator(
    analysis_results=analysis_results,
    layout='two_per_page',
    theme=theme
)

chart_keys = [
    'monthly_prod_cons_chart_bytes',
    'cumulative_cashflow_chart_bytes',
    'consumption_coverage_pie_chart_bytes'
]

charts_pdf = generator.generate(chart_keys)
```

**Chart Categories:**

- **Wirtschaftlichkeit**: Cashflow, ROI, Break-Even
- **Produktion & Verbrauch**: Monthly, Daily, Yearly production
- **Eigenverbrauch & Autarkie**: Coverage, Usage, Storage
- **Finanzielle Analyse**: Costs, Revenue, Tariffs
- **CO2 & Umwelt**: CO2 savings
- **Vergleiche & Szenarien**: Scenario comparisons

---

#### 6. `ChartCache`

Performance optimization cache for rendered charts.

**Constructor:**

```python
ChartCache(max_size: int = 100)
```

**Main Methods:**

```python
get(chart_key: str, chart_data: Any) -> bytes | None
put(chart_key: str, chart_data: Any, chart_bytes: bytes) -> None
invalidate(chart_key: str | None = None, chart_data: Any = None) -> None
get_stats() -> dict[str, Any]
clear() -> None
```

**Features:**

- Caches rendered charts by hash of key and data
- LRU eviction when cache is full
- Tracks hit/miss statistics
- Can be invalidated selectively or completely

**Example Usage:**

```python
from extended_pdf_generator import ChartCache

cache = ChartCache(max_size=50)

# Try to get from cache
chart_bytes = cache.get('monthly_chart', chart_data)

if chart_bytes is None:
    # Generate chart
    chart_bytes = generate_chart(chart_data)
    # Store in cache
    cache.put('monthly_chart', chart_data, chart_bytes)

# Get statistics
stats = cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate_percent']}%")
```

---

#### 7. `ExtendedPDFLogger`

Logger for tracking errors, warnings, and info messages during generation.

**Constructor:**

```python
ExtendedPDFLogger()
```

**Main Methods:**

```python
log_error(component: str, message: str, exception: Exception | None = None) -> None
log_warning(component: str, message: str) -> None
log_info(component: str, message: str) -> None
get_summary() -> dict[str, Any]
get_user_friendly_summary() -> str
clear() -> None
```

**Features:**

- Tracks errors with timestamps and exception details
- Tracks warnings and info messages
- Provides summary statistics
- Generates user-friendly summary text

**Example Usage:**

```python
from extended_pdf_generator import ExtendedPDFLogger

logger = ExtendedPDFLogger()

# Log messages
logger.log_info('MyComponent', 'Starting process')
logger.log_warning('MyComponent', 'Missing optional data')
logger.log_error('MyComponent', 'Failed to load file', exception)

# Get summary
summary = logger.get_summary()
print(f"Errors: {summary['error_count']}")
print(f"Warnings: {summary['warning_count']}")

# Get user-friendly text
print(logger.get_user_friendly_summary())
```

---

## Integration with PDF Generator

The extended PDF module integrates with the main PDF generator (`pdf_generator.py`) through the `generate_offer_pdf()` function.

**Integration Flow:**

1. Check if `extended_output_enabled` is True in options
2. Generate standard 8-page PDF
3. If extended output enabled:
   - Create `ExtendedPDFGenerator` instance
   - Generate extended pages
   - Merge with base PDF
4. Return final PDF

**Code Example:**

```python
# In pdf_generator.py
def generate_offer_pdf(offer_data, analysis_results, options):
    # Generate base 8-page PDF
    base_pdf = generate_base_pdf(offer_data, analysis_results)
    
    # Check if extended output is enabled
    if options.get('extended_output_enabled', False):
        try:
            from extended_pdf_generator import ExtendedPDFGenerator, ExtendedPDFLogger
            
            logger = ExtendedPDFLogger()
            generator = ExtendedPDFGenerator(
                offer_data,
                analysis_results,
                options,
                logger=logger
            )
            
            extended_pages = generator.generate_extended_pages()
            
            if extended_pages:
                # Merge base PDF with extended pages
                final_pdf = merge_pdfs(base_pdf, extended_pages)
                return final_pdf
            else:
                # Fallback to base PDF if no extended pages
                return base_pdf
        
        except Exception as e:
            print(f"Error generating extended PDF: {e}")
            # Fallback to base PDF on error
            return base_pdf
    
    return base_pdf
```

---

## Error Handling and Graceful Degradation

The module implements robust error handling with graceful degradation:

### Principles

1. **Never break the standard PDF**: If extended generation fails, fall back to the 8-page PDF
2. **Log all errors**: Use `ExtendedPDFLogger` to track all issues
3. **Continue on partial failures**: If one section fails, continue with others
4. **Provide user feedback**: Show warnings in UI when issues occur

### Error Scenarios

| Scenario | Behavior |
|----------|----------|
| Missing datasheet file | Log warning, skip datasheet, continue |
| Missing company document | Log warning, skip document, continue |
| Chart rendering fails | Log error, skip chart, continue |
| Financing data unavailable | Log warning, skip financing pages |
| Complete failure | Return empty bytes, fall back to base PDF |

### Example Error Handling

```python
try:
    extended_pages = generator.generate_extended_pages()
    
    # Check for errors
    summary = logger.get_summary()
    
    if summary['has_errors']:
        # Show warning to user
        st.warning(
            f"Extended PDF generated with {summary['error_count']} errors. "
            "Some content may be missing."
        )
    
    if summary['has_warnings']:
        # Show info to user
        st.info(
            f"{summary['warning_count']} warnings during generation. "
            "Check logs for details."
        )

except Exception as e:
    # Critical failure - fall back to base PDF
    st.error("Extended PDF generation failed. Using standard PDF.")
    return base_pdf
```

---

## Performance Optimization

### Caching Strategy

The module uses `ChartCache` to avoid re-rendering the same charts:

```python
# Create cache instance
cache = ChartCache(max_size=100)

# In chart generation
chart_bytes = cache.get(chart_key, chart_data)
if chart_bytes is None:
    chart_bytes = render_chart(chart_data)
    cache.put(chart_key, chart_data, chart_bytes)
```

### Efficient PDF Merging

The module uses single-pass merging to reduce memory usage:

```python
# Instead of multiple intermediate PDFs
# Old approach:
# pdf1 = generate_financing()
# pdf2 = generate_datasheets()
# pdf3 = merge(pdf1, pdf2)
# pdf4 = generate_charts()
# final = merge(pdf3, pdf4)

# New approach: Single-pass merging
writer = PdfWriter()
for section in sections:
    section_bytes = generate_section()
    add_pages_to_writer_efficient(writer, section_bytes)
final = writer.write()
```

### Image Optimization

Images are scaled before embedding to reduce PDF size:

```python
# Scale large images to 300 DPI
max_width = 2480  # A4 width at 300 DPI
max_height = 3508  # A4 height at 300 DPI

if img.width > max_width or img.height > max_height:
    img.thumbnail((max_width, max_height), Image.LANCZOS)
```

---

## Testing

### Unit Tests

Located in `tests/` directory:

- `test_extended_pdf_options.py`: Tests option parsing
- `test_financing_calculations.py`: Tests financing calculations
- `test_chart_layouts.py`: Tests chart layout generation
- `test_error_handling.py`: Tests error handling and fallbacks

### Integration Tests

- `test_integration_extended_pdf.py`: Full end-to-end tests

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_extended_pdf_options.py

# Run with coverage
pytest --cov=extended_pdf_generator tests/
```

---

## Troubleshooting

### Common Issues

#### 1. No extended pages generated

**Symptoms:** Extended PDF is same as base PDF

**Causes:**

- `extended_output_enabled` is False
- No options selected (no charts, no datasheets, etc.)
- All sections failed to generate

**Solution:**

- Check options dictionary
- Check logger for errors: `logger.get_summary()`
- Verify data availability

#### 2. Missing datasheets

**Symptoms:** Datasheets not appearing in PDF

**Causes:**

- Datasheet file not found in filesystem
- Invalid product IDs
- Datasheet path not set in database

**Solution:**

- Check product database for `datasheet_path`
- Verify file exists at path
- Check logger warnings

#### 3. Charts not rendering

**Symptoms:** Chart pages empty or missing

**Causes:**

- Chart bytes not in `analysis_results`
- Invalid chart keys
- Image format not supported

**Solution:**

- Verify chart keys end with `_chart_bytes`
- Check `analysis_results` dictionary
- Ensure charts are generated before PDF creation

#### 4. Performance issues

**Symptoms:** PDF generation takes too long

**Causes:**

- Too many charts selected
- Large datasheet files
- Cache not being used

**Solution:**

- Reduce number of charts
- Optimize datasheet file sizes
- Enable chart caching
- Use efficient merging

---

## Best Practices

### 1. Always use logging

```python
logger = ExtendedPDFLogger()
generator = ExtendedPDFGenerator(..., logger=logger)

# After generation
summary = logger.get_summary()
if summary['has_errors']:
    # Handle errors
    pass
```

### 2. Validate options before generation

```python
def validate_options(options):
    if not options.get('extended_output_enabled'):
        return False
    
    # Check if any content is selected
    has_content = (
        options.get('financing_details') or
        options.get('product_datasheets') or
        options.get('company_documents') or
        options.get('selected_charts')
    )
    
    return has_content
```

### 3. Use caching for repeated generations

```python
# Create cache once and reuse
cache = ChartCache(max_size=100)

# Pass to generator
generator = ChartPageGenerator(..., cache=cache)
```

### 4. Provide user feedback

```python
with st.spinner('Generating extended PDF...'):
    extended_pdf = generator.generate_extended_pages()

summary = logger.get_summary()
if summary['has_warnings']:
    st.warning(f"{summary['warning_count']} warnings occurred")
```

### 5. Always fall back to base PDF

```python
try:
    final_pdf = generate_extended_pdf(...)
except Exception as e:
    st.error("Extended generation failed. Using standard PDF.")
    final_pdf = base_pdf
```

---

## API Reference

### ExtendedPDFGenerator

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | offer_data, analysis_results, options, theme, logger | None | Initialize generator |
| `generate_extended_pages` | None | bytes | Generate all extended pages |

### FinancingPageGenerator

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | offer_data, theme, logger | None | Initialize generator |
| `generate` | None | bytes | Generate financing pages |
| `_calculate_monthly_rate` | amount, annual_rate, months | float | Calculate monthly payment |

### ProductDatasheetMerger

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | logger | None | Initialize merger |
| `merge` | datasheet_ids | bytes | Merge product datasheets |

### CompanyDocumentMerger

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | logger | None | Initialize merger |
| `merge` | document_ids | bytes | Merge company documents |

### ChartPageGenerator

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | analysis_results, layout, theme, logger | None | Initialize generator |
| `generate` | chart_keys | bytes | Generate chart pages |

### ChartCache

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | max_size | None | Initialize cache |
| `get` | chart_key, chart_data | bytes \| None | Get cached chart |
| `put` | chart_key, chart_data, chart_bytes | None | Store chart in cache |
| `invalidate` | chart_key, chart_data | None | Invalidate cache entries |
| `get_stats` | None | dict | Get cache statistics |
| `clear` | None | None | Clear entire cache |

### ExtendedPDFLogger

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | None | None | Initialize logger |
| `log_error` | component, message, exception | None | Log error message |
| `log_warning` | component, message | None | Log warning message |
| `log_info` | component, message | None | Log info message |
| `get_summary` | None | dict | Get summary of all messages |
| `get_user_friendly_summary` | None | str | Get formatted text summary |
| `clear` | None | None | Clear all messages |

---

## Version History

- **v1.0.0** (2025-01-09): Initial release with all core features
  - Extended PDF generation
  - Financing pages
  - Product datasheet merging
  - Company document merging
  - Chart page generation
  - Caching and performance optimization
  - Error handling and logging

---

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the logger output for detailed error messages
3. Consult the API reference for method signatures
4. Check the test files for usage examples
