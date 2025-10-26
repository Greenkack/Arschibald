# Task 7.1: KeepTogether Implementation - Integration Guide

## Overview

This guide provides step-by-step instructions for integrating the KeepTogether functionality into the existing PDF generation system.

---

## Integration Points

### 1. Extended PDF Generator Integration

**File**: `extended_pdf_generator.py`

**Current Implementation**: Uses `canvas.Canvas` directly

**New Implementation**: Use `ProtectedChartPageGenerator`

#### Step 1: Import the Protected Generator

```python
# At the top of extended_pdf_generator.py
from pdf_chart_generator_protected import ProtectedChartPageGenerator
```

#### Step 2: Replace ChartPageGenerator Usage

**Before**:

```python
class ExtendedPDFGenerator:
    def generate_extended_pages(self) -> bytes:
        # ...
        chart_generator = ChartPageGenerator(
            analysis_results=self.analysis_results,
            layout='one_per_page',
            theme=self.theme,
            logger=self.logger
        )
        chart_pages_bytes = chart_generator.generate(selected_chart_keys)
```

**After**:

```python
class ExtendedPDFGenerator:
    def generate_extended_pages(self) -> bytes:
        # ...
        # Use protected chart generator with KeepTogether
        chart_generator = ProtectedChartPageGenerator(
            analysis_results=self.analysis_results,
            theme=self.theme,
            logger=self.logger,
            enable_page_protection=True  # Enable KeepTogether
        )
        chart_pages_bytes = chart_generator.generate(selected_chart_keys)
```

#### Step 3: Verify Integration

```python
# After generation, check protection summary
if hasattr(chart_generator, 'get_protection_summary'):
    summary = chart_generator.get_protection_summary()
    if summary:
        self.logger.log_info(
            'ExtendedPDFGenerator',
            f"Applied {summary['total_protections']} page protections"
        )
```

---

### 2. Financing Page Generator Integration

**File**: `extended_pdf_generator.py` (FinancingPageGenerator class)

**Current Implementation**: Uses `canvas.Canvas` directly

**New Implementation**: Use `PageProtectionManager` with platypus

#### Step 1: Import Required Modules

```python
# At the top of extended_pdf_generator.py
from pdf_page_protection import PageProtectionManager
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)
```

#### Step 2: Modify FinancingPageGenerator

**Before**:

```python
class FinancingPageGenerator:
    def generate(self) -> bytes:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Draw financing information directly on canvas
        c.drawString(2*cm, self.height - 2*cm, "Finanzierung")
        # ... more canvas operations
        
        c.save()
        return buffer.getvalue()
```

**After**:

```python
class FinancingPageGenerator:
    def generate(self) -> bytes:
        buffer = io.BytesIO()
        
        # Use SimpleDocTemplate with platypus
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Initialize page protection manager
        protection_manager = PageProtectionManager(
            doc_height=self.height,
            min_space_at_bottom=3*cm,
            enable_logging=True
        )
        protection_manager.set_current_page(9)  # Extended PDF starts at page 9
        
        # Build story with protected elements
        story = []
        
        # Add financing sections with protection
        story.append(self._create_credit_financing_section(protection_manager))
        story.append(Spacer(1, 1*cm))
        story.append(self._create_leasing_financing_section(protection_manager))
        story.append(Spacer(1, 1*cm))
        story.append(self._create_amortization_section(protection_manager))
        
        # Build PDF
        doc.build(story)
        
        # Print protection summary
        protection_manager.print_protection_summary()
        
        return buffer.getvalue()
    
    def _create_credit_financing_section(
        self,
        protection_manager: PageProtectionManager
    ):
        """Create protected credit financing section."""
        # Create title
        title = Paragraph(
            "Kreditfinanzierung",
            self.styles['FinancingTitle']
        )
        
        # Create table
        table_data = [
            ['Position', 'Wert'],
            ['Kreditbetrag', f"{self.final_price:,.2f} €"],
            ['Zinssatz', f"{self.interest_rate:.2f}%"],
            ['Laufzeit', f"{self.years} Jahre"],
            ['Monatliche Rate', f"{self.monthly_rate:,.2f} €"],
            ['Gesamtkosten', f"{self.total_cost:,.2f} €"]
        ]
        
        table = Table(table_data, colWidths=[8*cm, 6*cm])
        table.setStyle(self._get_financing_table_style())
        
        # Create description
        description = Paragraph(
            "Diese Finanzierungsoption bietet Ihnen flexible Konditionen "
            "mit festen monatlichen Raten über die gesamte Laufzeit.",
            self.styles['BodyText']
        )
        
        # Wrap with STRICT protection
        return protection_manager.wrap_financing_section(
            title=title,
            table=table,
            description=description,
            section_id="credit_financing"
        )
```

---

### 3. Custom Chart Generation Integration

**Scenario**: You have custom chart generation code that needs protection

#### Step 1: Import PageProtectionManager

```python
from pdf_page_protection import PageProtectionManager
from reportlab.platypus import Paragraph, Image, Spacer
```

#### Step 2: Initialize Manager

```python
# In your PDF generation function
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    min_space_at_bottom=3*cm,
    enable_logging=True
)

# Set current page (9+ for extended PDF)
protection_manager.set_current_page(9)
```

#### Step 3: Wrap Your Charts

```python
# For each chart you generate
def add_protected_chart(story, chart_bytes, chart_name, chart_description):
    # Create elements
    title = Paragraph(chart_name, chart_title_style)
    chart_image = Image(
        io.BytesIO(chart_bytes),
        width=14*cm,
        height=10*cm,
        kind='proportional'
    )
    description = Paragraph(chart_description, description_style)
    
    # Wrap with protection
    protected = protection_manager.wrap_chart_with_description(
        chart=chart_image,
        title=title,
        description=description,
        chart_key=chart_name
    )
    
    # Add to story
    story.append(protected)
    
    # Add spacing with page break check
    spacing_elements = protection_manager.add_spacing_with_pagebreak_check(
        spacing=1.0*cm,
        min_space_for_next=8.0*cm
    )
    story.extend(spacing_elements)
```

---

## Migration Strategy

### Phase 1: Parallel Implementation (Recommended)

1. **Keep existing code** - Don't remove old implementation yet
2. **Add new protected generator** - Implement alongside existing
3. **Add feature flag** - Control which generator to use

```python
class ExtendedPDFGenerator:
    def __init__(self, ..., use_protected_charts: bool = False):
        self.use_protected_charts = use_protected_charts
    
    def generate_extended_pages(self) -> bytes:
        if self.use_protected_charts:
            # Use new protected generator
            chart_generator = ProtectedChartPageGenerator(...)
        else:
            # Use old generator
            chart_generator = ChartPageGenerator(...)
        
        return chart_generator.generate(chart_keys)
```

4. **Test thoroughly** - Compare outputs
5. **Gradual rollout** - Enable for subset of users
6. **Monitor** - Check for issues
7. **Full rollout** - Enable for all users
8. **Remove old code** - After successful rollout

### Phase 2: Direct Replacement (Faster)

1. **Backup current code** - Save working version
2. **Replace generator** - Switch to ProtectedChartPageGenerator
3. **Test thoroughly** - Verify all functionality
4. **Deploy** - Release to production

---

## Configuration Options

### Enable/Disable Page Protection

```python
# Enable protection (default)
generator = ProtectedChartPageGenerator(
    analysis_results=analysis_results,
    theme=theme,
    logger=logger,
    enable_page_protection=True  # ← Enable
)

# Disable protection (for testing/comparison)
generator = ProtectedChartPageGenerator(
    analysis_results=analysis_results,
    theme=theme,
    logger=logger,
    enable_page_protection=False  # ← Disable
)
```

### Configure Minimum Space

```python
# Default: 3cm minimum space at bottom
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    min_space_at_bottom=3*cm  # ← Adjust as needed
)

# More conservative (more page breaks)
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    min_space_at_bottom=5*cm  # ← More space required
)

# Less conservative (fewer page breaks)
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    min_space_at_bottom=2*cm  # ← Less space required
)
```

### Enable/Disable Logging

```python
# Enable logging (default)
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    enable_logging=True  # ← Enable
)

# Disable logging (for production)
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    enable_logging=False  # ← Disable
)
```

---

## Testing Integration

### Unit Tests

```python
# tests/test_integration_protected_charts.py

import pytest
from pdf_chart_generator_protected import ProtectedChartPageGenerator

def test_protected_chart_generation():
    """Test that protected chart generator works."""
    analysis_results = {
        'monthly_prod_cons_chart_bytes': b'fake_chart_data',
        'cost_projection_chart_bytes': b'fake_chart_data'
    }
    
    generator = ProtectedChartPageGenerator(
        analysis_results=analysis_results,
        theme={},
        logger=None,
        enable_page_protection=True
    )
    
    chart_keys = [
        'monthly_prod_cons_chart_bytes',
        'cost_projection_chart_bytes'
    ]
    
    result = generator.generate(chart_keys)
    
    assert result is not None
    assert len(result) > 0
    assert isinstance(result, bytes)

def test_protection_summary():
    """Test that protection summary is generated."""
    analysis_results = {
        'monthly_prod_cons_chart_bytes': b'fake_chart_data'
    }
    
    generator = ProtectedChartPageGenerator(
        analysis_results=analysis_results,
        theme={},
        logger=None,
        enable_page_protection=True
    )
    
    generator.generate(['monthly_prod_cons_chart_bytes'])
    
    summary = generator.get_protection_summary()
    
    assert summary is not None
    assert summary['total_protections'] > 0
```

### Integration Tests

```python
# tests/test_integration_full_pdf.py

def test_full_pdf_generation_with_protection():
    """Test full PDF generation with page protection."""
    from extended_pdf_generator import ExtendedPDFGenerator
    
    # Create test data
    project_data = {...}
    analysis_results = {...}
    extended_options = {...}
    
    # Generate PDF
    generator = ExtendedPDFGenerator(
        offer_data=project_data,
        analysis_results=analysis_results,
        options=extended_options,
        theme=None,
        logger=None
    )
    
    pdf_bytes = generator.generate_extended_pages()
    
    # Verify PDF was generated
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    
    # Verify it's a valid PDF
    from pypdf import PdfReader
    import io
    
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) > 0
```

---

## Troubleshooting

### Issue 1: Charts Not Protected

**Symptom**: Charts are still splitting across pages

**Possible Causes**:

1. Page protection not enabled
2. Current page < 9
3. KeepTogether not being used

**Solution**:

```python
# Verify protection is enabled
assert generator.enable_page_protection is True

# Verify current page is 9+
assert protection_manager.current_page >= 9

# Verify KeepTogether is being used
assert isinstance(result, KeepTogether)
```

### Issue 2: Too Many Page Breaks

**Symptom**: Excessive blank space, too many page breaks

**Possible Causes**:

1. min_space_at_bottom too large
2. Elements too large for single page

**Solution**:

```python
# Reduce minimum space requirement
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    min_space_at_bottom=2*cm  # ← Reduce from 3cm
)

# Or handle oversized elements
if element_too_large:
    # Let ReportLab split automatically
    story.append(element)
else:
    # Use KeepTogether
    story.append(protection_manager.wrap_chart_with_description(...))
```

### Issue 3: Missing Charts

**Symptom**: Some charts don't appear in PDF

**Possible Causes**:

1. Chart bytes not in analysis_results
2. Chart key mismatch
3. Error during chart generation

**Solution**:

```python
# Verify chart exists
if chart_key not in analysis_results:
    logger.log_warning(f'Chart {chart_key} not found')
    continue

# Verify chart bytes are valid
chart_bytes = analysis_results[chart_key]
if not chart_bytes or len(chart_bytes) == 0:
    logger.log_warning(f'Chart {chart_key} has no data')
    continue

# Add error handling
try:
    chart_image = Image(io.BytesIO(chart_bytes), ...)
except Exception as e:
    logger.log_error(f'Error creating chart {chart_key}: {e}')
    # Show error message instead
    story.append(Paragraph(f"Error: {chart_key}", error_style))
```

### Issue 4: Performance Issues

**Symptom**: PDF generation is slow

**Possible Causes**:

1. Too many protection checks
2. Large images not optimized
3. Excessive logging

**Solution**:

```python
# Disable logging in production
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    enable_logging=False  # ← Disable for performance
)

# Optimize images before adding
from PIL import Image as PILImage

def optimize_chart_image(chart_bytes, max_width=1400, max_height=1000):
    img = PILImage.open(io.BytesIO(chart_bytes))
    img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()

# Use optimized images
optimized_bytes = optimize_chart_image(chart_bytes)
chart_image = Image(io.BytesIO(optimized_bytes), ...)
```

---

## Best Practices

### 1. Always Set Current Page

```python
# GOOD: Set current page before using protection
protection_manager.set_current_page(9)
protected = protection_manager.wrap_chart_with_description(...)

# BAD: Forget to set current page
protected = protection_manager.wrap_chart_with_description(...)  # Uses default page 1
```

### 2. Use Appropriate Protection Level

```python
# For regular charts: Standard protection
protected = protection_manager.wrap_chart_with_description(...)

# For financing: STRICT protection
protected = protection_manager.wrap_financing_section(...)

# For tables: Standard protection
protected = protection_manager.wrap_table_with_title(...)
```

### 3. Add Spacing Between Elements

```python
# GOOD: Add spacing with page break check
story.append(protected_chart_1)
spacing = protection_manager.add_spacing_with_pagebreak_check(
    spacing=1.0*cm,
    min_space_for_next=8.0*cm
)
story.extend(spacing)
story.append(protected_chart_2)

# BAD: No spacing
story.append(protected_chart_1)
story.append(protected_chart_2)  # Too close!
```

### 4. Handle Optional Elements

```python
# GOOD: Check if description exists
description = None
if description_text:
    description = Paragraph(description_text, description_style)

protected = protection_manager.wrap_chart_with_description(
    chart=chart,
    title=title,
    description=description  # Can be None
)

# BAD: Assume description always exists
description = Paragraph(description_text, description_style)  # May fail!
```

### 5. Log Protection Decisions

```python
# GOOD: Enable logging during development
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    enable_logging=True  # ← Enable for debugging
)

# After generation, review summary
summary = protection_manager.get_protection_summary()
print(f"Applied {summary['total_protections']} protections")
protection_manager.print_protection_summary()

# In production: Disable logging for performance
protection_manager = PageProtectionManager(
    doc_height=29.7*cm,
    enable_logging=False  # ← Disable in production
)
```

---

## Rollback Plan

If issues arise after integration:

### Step 1: Identify Issue

```python
# Check logs for errors
logger.get_summary()

# Check protection summary
protection_manager.print_protection_summary()

# Compare with old PDF
old_pdf = generate_with_old_method()
new_pdf = generate_with_new_method()
compare_pdfs(old_pdf, new_pdf)
```

### Step 2: Quick Fix

```python
# Disable page protection temporarily
generator = ProtectedChartPageGenerator(
    analysis_results=analysis_results,
    theme=theme,
    logger=logger,
    enable_page_protection=False  # ← Disable temporarily
)
```

### Step 3: Rollback to Old Implementation

```python
# Switch back to old generator
chart_generator = ChartPageGenerator(  # ← Old implementation
    analysis_results=self.analysis_results,
    layout='one_per_page',
    theme=self.theme,
    logger=self.logger
)
```

### Step 4: Fix and Redeploy

1. Identify root cause
2. Fix issue in development
3. Test thoroughly
4. Redeploy with fix

---

## Monitoring

### Metrics to Track

1. **PDF Generation Success Rate**
   - Before: X%
   - After: Should be ≥ X%

2. **PDF Generation Time**
   - Before: Y seconds
   - After: Should be ≤ Y + 10%

3. **PDF File Size**
   - Before: Z MB
   - After: Should be ≈ Z MB

4. **User Complaints**
   - Track: Split charts, missing content, layout issues
   - Target: 0 complaints

### Logging

```python
# Log key metrics
logger.log_info('PDFGeneration', f'Generated PDF in {duration:.2f}s')
logger.log_info('PDFGeneration', f'PDF size: {len(pdf_bytes) / 1024:.2f} KB')
logger.log_info('PDFGeneration', f'Applied {protections} page protections')

# Log errors
if error:
    logger.log_error('PDFGeneration', f'Error: {error}', exception)
```

---

## Conclusion

The KeepTogether implementation is ready for integration with:

✅ Clear integration points
✅ Step-by-step instructions
✅ Configuration options
✅ Testing guidelines
✅ Troubleshooting guide
✅ Best practices
✅ Rollback plan
✅ Monitoring strategy

Follow this guide to successfully integrate page protection into your PDF generation system!
