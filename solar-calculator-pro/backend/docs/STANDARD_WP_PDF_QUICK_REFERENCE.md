# Standard WP PDF - Quick Reference

## Quick Start

```python
from services.standard_wp_pdf_service import StandardWPPDFService

service = StandardWPPDFService()

data = {
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'kunde_wohnort': 'Berlin',
    'wp_leistung_kw': 12.5,
    'wp_cop_wert': 4.5,
    'wp_modell_name': 'Viessmann Vitocal 200-S',
    'wp_hersteller': 'Viessmann'
}

pdf_bytes = service.generate_complete_pdf(data)
```

## File Structure

```
pdf_templates_static/notext/
├── hp_nt_01.pdf to hp_nt_08.pdf

coords_wp/
├── wp_seite1.yml to wp_seite8.yml
```

## Essential Placeholders

### Required
- `anrede_kunde` - Herr/Frau
- `kunde_vorname_und_nachname` - Full name
- `kunde_wohnort` - City
- `wp_leistung_kw` - Power (kW)
- `wp_cop_wert` - COP value
- `wp_modell_name` - Model name

### Heat Pump Specific
- `wp_jahresarbeitszahl` - JAZ
- `wp_heizkosten_jahr` - Annual heating costs
- `wp_heizkosten_monat` - Monthly heating costs
- `wp_einsparung_jahr` - Annual savings
- `wp_effizienzklasse` - Efficiency class
- `wp_hersteller` - Manufacturer

## API Endpoints

### Generate PDF
```
POST /api/v1/standard-wp-pdf/generate
```

### Get Templates
```
GET /api/v1/standard-wp-pdf/templates
```

### Get Placeholders
```
GET /api/v1/standard-wp-pdf/placeholders
```

### Validate Data
```
POST /api/v1/standard-wp-pdf/validate-data
```

### Health Check
```
GET /api/v1/standard-wp-pdf/health
```

## German Formatting

```python
# Currency
service._format_german_currency(16999.00)
# → "16.999,00 €"

# Decimal
service._format_german_decimal(4.5, 1)
# → "4,5"
```

## Common Patterns

### Full PDF with Formatting
```python
pdf_bytes = service.generate_pdf_with_german_formatting(
    calculation_data={...},
    customer_data={...},
    pricing_data={...}
)
```

### Partial Pages
```python
pdf_bytes = service.generate_complete_pdf(
    data,
    include_pages=[1, 2, 3]
)
```

### Custom Data
```python
pdf_bytes = service.generate_complete_pdf({
    'wp_modell_name': 'Custom Model',
    'wp_cop_wert': '4,5',
    # ... any placeholders
})
```

## Error Handling

```python
try:
    pdf_bytes = service.generate_complete_pdf(data)
    if pdf_bytes:
        with open('output.pdf', 'wb') as f:
            f.write(pdf_bytes)
except Exception as e:
    logger.error(f"PDF generation failed: {e}")
```

## Testing

```bash
# Run tests
pytest test_standard_wp_pdf_service.py -v

# Run demo
python demo_standard_wp_pdf.py
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Empty PDF | Check templates exist |
| Missing text | Verify coordinates files |
| Wrong format | Use `generate_pdf_with_german_formatting()` |
| Import error | Install pypdf and reportlab |

## Dependencies

```bash
pip install pypdf reportlab
# or
pip install PyPDF2 reportlab
```

## Complete Example

```python
from services.standard_wp_pdf_service import StandardWPPDFService

# Initialize
service = StandardWPPDFService()

# Complete data
data = {
    # Customer
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'kunde_wohnort': 'Berlin',
    'langes_datum_heute': '22. Januar 2025',
    
    # Heat Pump
    'wp_leistung_kw': 12.5,
    'wp_cop_wert': 4.5,
    'wp_jahresarbeitszahl': 4.2,
    'wp_modell_name': 'Viessmann Vitocal 200-S',
    'wp_hersteller': 'Viessmann',
    'wp_effizienzklasse': 'A+++',
    'wp_vorlauftemperatur': '35°C',
    'wp_heizlast_kw': 10.0,
    'wp_warmwasser_liter': 300,
    
    # Costs
    'wp_heizkosten_jahr': 1250.00,
    'wp_heizkosten_monat': 104.17,
    'wp_einsparung_jahr': 2500.00,
    'wp_einsparung_prozent': '66,7%',
    'wp_amortisationszeit': '8 Jahre',
    
    # Environment
    'wp_co2_einsparung': '4.500 kg/Jahr',
    
    # Pricing
    'total_price': 18999.00
}

# Generate
pdf_bytes = service.generate_pdf_with_german_formatting(
    calculation_data=data,
    customer_data=data,
    pricing_data=data
)

# Save
with open('wp_angebot.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

## Key Differences from PV PDF

| Feature | PV PDF | WP PDF |
|---------|--------|--------|
| Templates | `nt_nt_XX.pdf` | `hp_nt_XX.pdf` |
| Coordinates | `coords/seiteX.yml` | `coords_wp/wp_seiteX.yml` |
| Focus | Solar calculations | Heat pump calculations |
| Key Values | kWp, modules | COP, JAZ, heating costs |

## Next Steps

1. ✅ Review [Complete Guide](STANDARD_WP_PDF_GUIDE.md)
2. ✅ Run demo script
3. ✅ Test with your data
4. ✅ Integrate into your application
5. ✅ Monitor and optimize
