# Task 7: Integration Guide

## Overview

This guide explains how to integrate the page protection system into the existing PDF generation pipeline.

## Quick Start

### 1. Import the Required Modules

```python
from pdf_page_protection import PageProtectionManager
from pdf_chart_generator_protected import ProtectedChartPageGenerator
```

### 2. Initialize the Protection Manager

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# Get document dimensions
width, height = A4

# Create protection manager
protection_manager = PageProtectionManager(
    doc_height=height,
    min_space_at_bottom=3 * cm,
    enable_logging=True
)
```

### 3. Use Protected Chart Generator

```python
# Create protected chart generator
chart_generator = ProtectedChartPageGenerator(
    analysis_results=analysis_results,
    theme=theme,
    logger=logger,
    enable_page_protection=True
)

# Generate protected chart pages
chart_pdf_bytes = chart_generator.generate(chart_keys)
```

## Integration Points

### 1. Extended PDF Generator (`extended_pdf_generator.py`)

#### Current Code (Simplified)

```python
class ExtendedPDFGenerator:
    def __init__(self, offer_data, analysis_results, options, theme, logger):
        self.offer_data = offer_data
        self.analysis_results = analysis_results
        self.options = options
        self.theme = theme
        self.logger = logger
    
    def _generate_chart_pages(self) -> bytes:
        """Generates pages with charts."""
        try:
            generator = ChartPageGenerator(
                self.analysis_results,
                self.options.get('chart_layout', 'one_per_page'),
                self.theme,
                self.logger
            )
            return generator.generate(
                self.options['selected_charts']
            )
        except Exception as e:
            self.logger.log_error('ExtendedPDFGenerator', 'Failed to generate chart pages', e)
            return b''
```

#### Updated Code with Page Protection

```python
class ExtendedPDFGenerator:
    def __init__(self, offer_data, analysis_results, options, theme, logger):
        self.offer_data = offer_data
        self.analysis_results = analysis_results
        self.options = options
        self.theme = theme
        self.logger = logger
        
        # ADD: Initialize page protection manager
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from pdf_page_protection import PageProtectionManager
        
        self.width, self.height = A4
        self.protection_manager = PageProtectionManager(
            doc_height=self.height,
            min_space_at_bottom=3 * cm,
            enable_logging=True
        )
    
    def _generate_chart_pages(self) -> bytes:
        """Generates pages with charts using page protection."""
        try:
            # REPLACE: Use ProtectedChartPageGenerator instead
            from pdf_chart_generator_protected import ProtectedChartPageGenerator
            
            generator = ProtectedChartPageGenerator(
                self.analysis_results,
                self.theme,
                self.logger,
                enable_page_protection=True  # Enable protection
            )
            
            # Set starting page for protection (extended pages start at 9)
            # This will be updated as pages are generated
            self.protection_manager.set_current_page(9)
            
            return generator.generate(
                self.options['selected_charts']
            )
        except Exception as e:
            self.logger.log_error('ExtendedPDFGenerator', 'Failed to generate chart pages', e)
            return b''
```

### 2. Financing Page Generator (`extended_pdf_generator.py`)

#### Current Code (Simplified)

```python
class FinancingPageGenerator:
    def _draw_financing_details(self, c, financing_options):
        """Draw financing details on canvas."""
        y_position = self.height - 4*cm
        
        for option in financing_options:
            # Draw title
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, y_position, option['name'])
            y_position -= 0.5*cm
            
            # Draw table
            table_data = self._create_financing_table(option)
            # ... draw table ...
            y_position -= table_height
            
            # Draw description
            c.setFont("Helvetica", 10)
            c.drawString(2*cm, y_position, option['description'])
            y_position -= 1*cm
```

#### Updated Code with Page Protection

```python
class FinancingPageGenerator:
    def __init__(self, offer_data, theme, logger):
        self.offer_data = offer_data
        self.theme = theme
        self.logger = logger
        
        # ADD: Initialize page protection
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from pdf_page_protection import PageProtectionManager
        
        self.width, self.height = A4
        self.protection_manager = PageProtectionManager(
            doc_height=self.height,
            min_space_at_bottom=3 * cm,
            enable_logging=True
        )
        
        # Set to page 9 (financing starts on extended pages)
        self.protection_manager.set_current_page(9)
    
    def generate(self) -> bytes:
        """Generate financing pages with page protection."""
        # REPLACE: Use platypus instead of canvas for page protection
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Table, Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        financing_options = self._get_financing_options()
        
        for option in financing_options:
            # Create title
            title = Paragraph(option['name'], styles['Heading2'])
            
            # Create table
            table = self._create_financing_table(option)
            
            # Create description
            description = Paragraph(option['description'], styles['BodyText'])
            
            # WRAP with page protection
            protected_section = self.protection_manager.wrap_financing_section(
                title,
                table,
                description,
                section_id=option['id']
            )
            
            # Add to story
            story.append(protected_section)
            
            # Add spacing between sections
            story.extend(
                self.protection_manager.add_spacing_with_pagebreak_check(
                    spacing=1.0 * cm,
                    min_space_for_next=5.0 * cm
                )
            )
        
        # Build PDF
        doc.build(story)
        
        # Print protection summary
        self.protection_manager.print_protection_summary()
        
        return buffer.getvalue()
```

### 3. Chart Generation in Main PDF Generator

If you're adding charts directly to the main PDF (not through extended generator):

```python
def add_chart_to_pdf(story, chart_bytes, chart_title, chart_description, protection_manager):
    """Add a chart to the PDF story with page protection.
    
    Args:
        story: PDF story list
        chart_bytes: Chart image bytes
        chart_title: Chart title text
        chart_description: Chart description text
        protection_manager: PageProtectionManager instance
    """
    from reportlab.platypus import Paragraph, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    import io
    
    styles = getSampleStyleSheet()
    
    # Create elements
    title = Paragraph(chart_title, styles['Heading2'])
    chart_image = Image(
        io.BytesIO(chart_bytes),
        width=14*cm,
        height=10*cm,
        kind='proportional'
    )
    description = Paragraph(chart_description, styles['BodyText'])
    
    # Check if we're on extended pages (9+)
    if protection_manager.should_apply_protection():
        # Wrap with protection
        protected = protection_manager.wrap_chart_with_description(
            chart_image,
            title,
            description,
            chart_key=chart_title
        )
        story.append(protected)
    else:
        # No protection for pages 1-8
        story.extend([
            title,
            Spacer(1, 0.3*cm),
            chart_image,
            Spacer(1, 0.3*cm),
            description
        ])
```

## Complete Integration Example

Here's a complete example showing how to integrate page protection into a PDF generation workflow:

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, Spacer, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet
import io

from pdf_page_protection import PageProtectionManager
from pdf_chart_generator_protected import ProtectedChartPageGenerator


def generate_complete_pdf_with_protection(
    offer_data,
    analysis_results,
    chart_keys,
    theme
):
    """Generate a complete PDF with page protection.
    
    This example shows how to:
    1. Generate standard pages 1-8 without protection
    2. Generate extended pages 9+ with full protection
    3. Include charts, tables, and financing information
    """
    
    # Initialize
    width, height = A4
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Create page protection manager
    protection_manager = PageProtectionManager(
        doc_height=height,
        min_space_at_bottom=3 * cm,
        enable_logging=True
    )
    
    # ========================================
    # PAGES 1-8: Standard PDF (No Protection)
    # ========================================
    
    protection_manager.set_current_page(1)
    
    # Page 1: Cover
    story.append(Paragraph("Angebot", styles['Title']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"für {offer_data['customer_name']}", styles['Normal']))
    story.append(PageBreak())
    
    # Pages 2-8: Standard content
    # ... add standard content without protection ...
    
    for page in range(2, 9):
        protection_manager.set_current_page(page)
        story.append(Paragraph(f"Page {page} Content", styles['Heading1']))
        story.append(Spacer(1, 1*cm))
        # Add content normally - no protection applied
        story.append(PageBreak())
    
    # ========================================
    # PAGES 9+: Extended PDF (With Protection)
    # ========================================
    
    protection_manager.set_current_page(9)
    
    # Page 9: Financing Information
    story.append(Paragraph("Finanzierungsinformationen", styles['Heading1']))
    story.append(Spacer(1, 0.5*cm))
    
    # Add financing sections with strict protection
    financing_options = [
        {
            'name': 'Kreditfinanzierung',
            'data': [
                ['Kreditbetrag', '25.000 €'],
                ['Zinssatz', '3,5%'],
                ['Laufzeit', '10 Jahre'],
                ['Monatliche Rate', '245 €']
            ],
            'description': 'Attraktive Kreditkonditionen für Ihre PV-Anlage.'
        },
        {
            'name': 'Leasingfinanzierung',
            'data': [
                ['Leasingbetrag', '25.000 €'],
                ['Zinssatz', '4,0%'],
                ['Laufzeit', '10 Jahre'],
                ['Monatliche Rate', '255 €']
            ],
            'description': 'Flexible Leasingoption mit Kaufoption am Ende.'
        }
    ]
    
    for option in financing_options:
        # Create elements
        title = Paragraph(option['name'], styles['Heading2'])
        table = Table(option['data'])
        description = Paragraph(option['description'], styles['Normal'])
        
        # Wrap with STRICT protection for financing
        protected = protection_manager.wrap_financing_section(
            title,
            table,
            description,
            section_id=option['name']
        )
        
        story.append(protected)
        
        # Add spacing with conditional page break
        story.extend(
            protection_manager.add_spacing_with_pagebreak_check(
                spacing=1.0 * cm,
                min_space_for_next=5.0 * cm
            )
        )
    
    # Pages 10+: Charts with Protection
    protection_manager.set_current_page(10)
    
    # Generate protected chart pages
    chart_generator = ProtectedChartPageGenerator(
        analysis_results,
        theme,
        logger=None,
        enable_page_protection=True
    )
    
    # Get chart PDF bytes
    chart_pdf_bytes = chart_generator.generate(chart_keys)
    
    # Merge chart pages into main PDF
    # (This would typically be done at the PDF merging stage)
    
    # Build the PDF
    doc.build(story)
    
    # Print protection summary
    print("\n" + "="*60)
    print("PAGE PROTECTION SUMMARY")
    print("="*60)
    protection_manager.print_protection_summary()
    
    return buffer.getvalue()


# Usage example
if __name__ == '__main__':
    offer_data = {
        'customer_name': 'Max Mustermann',
        # ... other offer data ...
    }
    
    analysis_results = {
        'monthly_prod_cons_chart_bytes': b'...',  # Chart image bytes
        'cost_projection_chart_bytes': b'...',
        # ... other charts ...
    }
    
    chart_keys = [
        'monthly_prod_cons_chart_bytes',
        'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes'
    ]
    
    theme = {
        'colors': {
            'primary': '#1E3A8A',
            'secondary': '#3B82F6'
        },
        'fonts': {
            'title': 'Helvetica-Bold',
            'body': 'Helvetica'
        }
    }
    
    # Generate PDF with protection
    pdf_bytes = generate_complete_pdf_with_protection(
        offer_data,
        analysis_results,
        chart_keys,
        theme
    )
    
    # Save to file
    with open('protected_offer.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print("\nPDF generated successfully with page protection!")
```

## Migration Checklist

Use this checklist when integrating page protection into existing code:

### Phase 1: Preparation

- [ ] Review existing PDF generation code
- [ ] Identify all places where charts are added
- [ ] Identify all places where tables are added
- [ ] Identify financing information sections
- [ ] Note current page numbering scheme

### Phase 2: Import and Initialize

- [ ] Add imports for `PageProtectionManager`
- [ ] Add imports for `ProtectedChartPageGenerator`
- [ ] Initialize `PageProtectionManager` in constructor
- [ ] Set initial page number (usually 9 for extended pages)

### Phase 3: Update Chart Generation

- [ ] Replace `ChartPageGenerator` with `ProtectedChartPageGenerator`
- [ ] Update chart generation calls to use protection
- [ ] Test chart generation with protection enabled
- [ ] Verify charts stay together with descriptions

### Phase 4: Update Financing Sections

- [ ] Convert canvas-based financing to platypus
- [ ] Wrap financing sections with `wrap_financing_section()`
- [ ] Test financing section protection
- [ ] Verify strict protection is applied

### Phase 5: Update Tables

- [ ] Wrap tables with `wrap_table_with_title()`
- [ ] Test table protection
- [ ] Verify tables stay with titles

### Phase 6: Add Spacing and Breaks

- [ ] Replace manual spacing with `add_spacing_between_charts()`
- [ ] Add conditional page breaks where needed
- [ ] Test automatic page break behavior

### Phase 7: Testing

- [ ] Generate test PDFs with various content
- [ ] Verify pages 1-8 are unchanged
- [ ] Verify pages 9+ have protection
- [ ] Check protection log for issues
- [ ] Test with edge cases (very large elements, many charts)

### Phase 8: Monitoring

- [ ] Enable protection logging
- [ ] Review protection summaries
- [ ] Adjust `min_space_at_bottom` if needed
- [ ] Optimize spacing values based on results

## Troubleshooting

### Issue: Elements Still Splitting Across Pages

**Possible Causes:**

1. Protection not enabled (`enable_page_protection=False`)
2. Current page < 9 (protection only applies to pages 9+)
3. Element too large for one page (will split naturally)

**Solutions:**

```python
# Verify protection is enabled
protection_manager = PageProtectionManager(
    doc_height=height,
    enable_logging=True  # Enable logging to see what's happening
)

# Check current page
print(f"Current page: {protection_manager.current_page}")
print(f"Protection active: {protection_manager.should_apply_protection()}")

# For very large elements, check the log
protection_manager.print_protection_summary()
```

### Issue: Too Many Page Breaks

**Possible Causes:**

1. `min_space_at_bottom` too large
2. Elements larger than expected
3. Too many conditional page breaks

**Solutions:**

```python
# Reduce minimum space requirement
protection_manager = PageProtectionManager(
    doc_height=height,
    min_space_at_bottom=2 * cm  # Reduced from 3cm
)

# Adjust conditional page break threshold
story.extend(
    protection_manager.add_spacing_with_pagebreak_check(
        spacing=1.0 * cm,
        min_space_for_next=4.0 * cm  # Reduced from 5cm
    )
)
```

### Issue: Protection Log Shows Unexpected Behavior

**Solution:**
Review the protection log to understand what's happening:

```python
# Get detailed summary
summary = protection_manager.get_protection_summary()

print(f"Total protections: {summary['total_protections']}")
print("\nBy type:")
for element_type, count in summary['by_type'].items():
    print(f"  {element_type}: {count}")

print("\nBy page:")
for page, count in summary['by_page'].items():
    print(f"  Page {page}: {count}")

# Review individual log entries
for entry in summary['log']:
    print(f"[Page {entry['page']}] {entry['action']}: {entry['element_type']}")
    if entry['details']:
        print(f"  Details: {entry['details']}")
```

## Best Practices

1. **Always enable logging during development**

   ```python
   protection_manager = PageProtectionManager(
       doc_height=height,
       enable_logging=True  # Enable during development
   )
   ```

2. **Set page numbers correctly**

   ```python
   # Update page number as you progress through the PDF
   protection_manager.set_current_page(9)  # Starting extended pages
   ```

3. **Use appropriate protection methods**
   - Charts with descriptions: `wrap_chart_with_description()`
   - Tables with titles: `wrap_table_with_title()`
   - Financing sections: `wrap_financing_section()` (strict)
   - Charts with legends: `wrap_chart_with_legend()`

4. **Add spacing intelligently**

   ```python
   # Between charts
   story.append(protection_manager.add_spacing_between_charts(1.0 * cm))
   
   # With conditional page break
   story.extend(
       protection_manager.add_spacing_with_pagebreak_check(
           spacing=1.0 * cm,
           min_space_for_next=5.0 * cm
       )
   )
   ```

5. **Review protection summaries**

   ```python
   # After PDF generation
   protection_manager.print_protection_summary()
   ```

## Conclusion

The page protection system is designed to integrate seamlessly into existing PDF generation code. By following this guide, you can add professional page protection to your PDFs with minimal code changes.

Key benefits:

- ✓ Professional page layout
- ✓ No split charts or tables
- ✓ Automatic page breaks
- ✓ Backward compatible (pages 1-8 unchanged)
- ✓ Comprehensive logging
- ✓ Easy to integrate

For questions or issues, refer to:

- `TASK_7_PAGE_PROTECTION_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `TASK_7_VERIFICATION_CHECKLIST.md` - Requirements verification
- `TASK_7_VISUAL_GUIDE.md` - Visual examples
- `tests/test_page_protection.py` - Unit tests and examples
