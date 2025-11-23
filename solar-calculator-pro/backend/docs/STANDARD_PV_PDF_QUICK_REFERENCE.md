# Standard PV PDF System - Quick Reference

## Quick Start

```python
from services.standard_pv_pdf_service import StandardPVPDFService

service = StandardPVPDFService()
pdf_bytes = service.generate_complete_pdf({
    'anrede_kunde': 'Herr',
    'kunde_vorname_und_nachname': 'Max Mustermann',
    'kunde_wohnort': 'Berlin',
    'kWp_anlage_anlage': '10,5 kWp',
    'total_price': 16999.00
})
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/standard-pv-pdf/generate` | POST | Generate complete PDF |
| `/api/v1/standard-pv-pdf/generate-info` | POST | Get PDF info without file |
| `/api/v1/standard-pv-pdf/templates/available` | GET | List available templates |
| `/api/v1/standard-pv-pdf/coordinates/page/{n}` | GET | Get page coordinates |

## German Number Formatting

| Input | Output |
|-------|--------|
| `16999.00` | `16.999,00 €` |
| `1234.56` | `1.234,56 €` |
| `10.5` | `10,5 kWp` |
| `12000` | `12.000 kWh` |

## Dynamic Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `anrede_kunde` | Salutation | Herr/Frau |
| `kunde_vorname_und_nachname` | Full name | Max Mustermann |
| `kunde_wohnort` | City | Berlin |
| `kWp_anlage_anlage` | System size | 10,5 kWp |
| `langes_datum_heute` | Date | 22. Januar 2025 |

## Page Structure

1. **Deckblatt** - Cover page
2. **Anschreiben** - Cover letter
3. **Angebotspositionen** - Offer positions
4. **Preisaufstellung** - Price breakdown
5. **Wirtschaftlichkeit** - Economic analysis
6. **Technische Daten** - Technical data
7. **3D-Visualisierung** - 3D visualization
8. **Zusammenfassung** - Summary

## Chart Types

1. CIRCLE
2. DONUT
3. BAR
4. COLUMN
5. LINE
6. AREA
7. PIE
8. POLAR
9. RADAR
10. WATERFALL

## Common Commands

### Generate PDF
```python
pdf_bytes = service.generate_complete_pdf(data)
```

### Generate Specific Pages
```python
pdf_bytes = service.generate_complete_pdf(data, include_pages=[1, 2, 3])
```

### Save PDF
```python
with open('angebot.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Format Currency
```python
formatted = StandardPVPDFService._format_german_currency(16999.00)
# Result: "16.999,00 €"
```

## File Locations

- **Templates**: `pdf_templates_static/notext/nt_nt_01.pdf` to `nt_nt_08.pdf`
- **Coordinates**: `coords/seite1.yml` to `seite8.yml`
- **Service**: `backend/services/standard_pv_pdf_service.py`
- **API**: `backend/api/v1/standard_pv_pdf.py`
- **Tests**: `backend/tests/test_standard_pv_pdf_service.py`

## Error Handling

```python
try:
    pdf_bytes = service.generate_complete_pdf(data)
except Exception as e:
    logger.error(f"PDF generation failed: {e}")
```

## Testing

```bash
# Run all tests
pytest backend/tests/test_standard_pv_pdf_service.py -v

# Run specific test
pytest backend/tests/test_standard_pv_pdf_service.py::TestStandardPVPDFService::test_format_german_currency -v
```

## Dependencies

```
reportlab>=4.0.0
pypdf>=3.0.0  # or PyPDF2>=3.0.0
```

## Key Classes

- `YMLCoordinateParser` - Parse YML coordinate files
- `TemplateLoader` - Load PDF templates
- `PlaceholderSystem` - Manage placeholders
- `PositioningEngine` - Position text on pages
- `StandardPVPDFService` - Main service orchestrator

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Template not found | Check `pdf_templates_static/notext/` directory |
| Coordinates not found | Check `coords/` directory |
| Font not rendering | Use Helvetica or Times-Roman |
| Color incorrect | Verify color integer in YML |
| PDF merge failed | Check PyPDF installation |

## Performance Tips

- Cache templates for repeated generation
- Generate pages in parallel for large batches
- Use streaming for large PDFs
- Optimize image sizes before embedding

## Next Steps

1. Review full documentation: `STANDARD_PV_PDF_GUIDE.md`
2. Check API examples in tests
3. Explore coordinate files structure
4. Customize templates as needed
