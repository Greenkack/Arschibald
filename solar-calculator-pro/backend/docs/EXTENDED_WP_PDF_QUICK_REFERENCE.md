# Extended WP PDF - Quick Reference

## Quick Start

```python
from services.extended_wp_pdf_service import ExtendedWPPDFService, WPComponentSelection

# Initialize
service = ExtendedWPPDFService()

# Select components
selection = WPComponentSelection(
    include_detailed_wp_calculations=True,
    include_additional_wp_diagrams=True,
    selected_wp_diagram_types=['cop_monthly']
)

# Generate
pdf_bytes = service.generate_extended_wp_pdf(wp_data, selection)
```

## WP Component Selection Options

```python
WPComponentSelection(
    include_detailed_wp_calculations=True,      # Detailed COP, JAZ, costs
    include_additional_wp_diagrams=True,        # Extra diagrams
    include_wp_product_datasheets=True,         # Product datasheets
    include_wp_documents=True,                  # Documents from DB
    include_wp_images=True,                     # Images from DB
    include_extended_wp_visualizations=True,    # Extended visualizations
    
    selected_wp_diagram_types=['cop_monthly', 'heating_cost_comparison'],
    selected_wp_product_ids=['wp_product_1'],
    selected_wp_document_ids=['wp_doc_1'],
    selected_wp_image_ids=['wp_img_1']
)
```

## Available WP Diagrams

- `cop_monthly` - Monthly COP values
- `heating_cost_comparison` - Cost comparison with other systems
- `efficiency_analysis` - Efficiency breakdown
- `savings_projection` - Long-term savings

## Available WP Calculations

- `detailed_cop` - Detailed COP calculation
- `detailed_jaz` - Detailed JAZ calculation
- `detailed_heating_costs` - Detailed heating cost breakdown
- `detailed_efficiency` - Detailed efficiency analysis

## Required WP Data Fields

```python
{
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'kunde_wohnort': 'Berlin',
    'wp_leistung_kw': 12.5,
    'wp_cop_wert': 4.5,
    'wp_jahresarbeitszahl': 4.2,
    'wp_heizkosten_jahr': 1250.00,
    'wp_heizkosten_monat': 104.17,
    'wp_einsparung_jahr': 2500.00,
    'wp_effizienzklasse': 'A+++',
    'wp_modell_name': 'Viessmann Vitocal 200-S',
    'total_price': 18999.00
}
```

## API Endpoints

### Generate PDF
```http
POST /api/v1/extended-wp-pdf/generate
```

### Get Available Components
```http
GET /api/v1/extended-wp-pdf/available-components
```

### Preview PDF
```http
POST /api/v1/extended-wp-pdf/preview
```

## File Structure

```
Templates: pdf_templates_static/notext/
  - hp_nt_01.pdf to hp_nt_08.pdf (standard)
  - hp_nt_09.pdf, hp_nt_10.pdf, ... (extended)
  - hp_nt_extended.pdf (generic extended)

Coordinates: coords_wp/
  - wp_seite1.yml to wp_seite8.yml (standard)
  - wp_seite9.yml, wp_seite10.yml, ... (extended)
```

## Common Patterns

### Basic Extended PDF
```python
selection = WPComponentSelection(
    include_detailed_wp_calculations=True
)
pdf = service.generate_extended_wp_pdf(data, selection)
```

### With Diagrams
```python
selection = WPComponentSelection(
    include_detailed_wp_calculations=True,
    include_additional_wp_diagrams=True,
    selected_wp_diagram_types=['cop_monthly', 'heating_cost_comparison']
)
pdf = service.generate_extended_wp_pdf(data, selection)
```

### With Product Datasheets
```python
selection = WPComponentSelection(
    include_wp_product_datasheets=True,
    selected_wp_product_ids=['wp_product_1', 'wp_product_2']
)
pdf = service.generate_extended_wp_pdf(data, selection)
```

### Full Extended PDF
```python
selection = WPComponentSelection(
    include_detailed_wp_calculations=True,
    include_additional_wp_diagrams=True,
    include_wp_product_datasheets=True,
    include_wp_documents=True,
    include_wp_images=True,
    include_extended_wp_visualizations=True,
    selected_wp_diagram_types=['cop_monthly', 'heating_cost_comparison'],
    selected_wp_product_ids=['wp_product_1'],
    selected_wp_document_ids=['wp_doc_1'],
    selected_wp_image_ids=['wp_img_1']
)
pdf = service.generate_extended_wp_pdf(data, selection)
```

## Tips

- ✓ Always validate WP data before generation
- ✓ Use German number formatting (1.250,00 €)
- ✓ Check template availability
- ✓ Handle missing components gracefully
- ✓ Keep PDF size manageable by selecting only needed components
- ✓ Test with sample data first

## Troubleshooting

| Issue | Solution |
|-------|----------|
| PDF generation fails | Check PyPDF installation |
| Missing pages | Verify template files exist |
| Empty content | Check coordinate files |
| No datasheets | Verify database service configured |
| Large file size | Reduce number of components |

## See Also

- [Extended WP PDF Guide](EXTENDED_WP_PDF_GUIDE.md)
- [Standard WP PDF Guide](STANDARD_WP_PDF_GUIDE.md)
