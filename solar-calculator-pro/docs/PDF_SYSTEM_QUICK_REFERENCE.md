# PDF System Quick Reference - Task 96

## 🎯 Quick Stats

- **Total PDF Modules:** 18 files (~17,000 lines)
- **YML Coordinates:** 162 files (3 directories)
- **PDF Templates:** 88 files (44 variants × 2 types)
- **Functionalities:** 17 (A-Q) all implemented
- **Migration Priority:** P0 (CRITICAL)
- **Estimated Migration:** 4-6 weeks

---

## 📁 Core Modules

| Module | Purpose | Lines | Priority |
|--------|---------|-------|----------|
| pdf_generator.py | Main engine | 7,678 | P0 |
| doc_output.py | PDF UI | 3,605 | P0 |
| central_pdf_system.py | System manager | 900 | P0 |
| pdf_chart_renderer.py | Charts | 600 | P1 |
| multi_offer_generator.py | Multi-company | 300 | P2 |

---

## 🗂️ YML Coordinate System

```
coords/       → Base offers (54 files)
coords_multi/ → Multi-PDF (54 files)
coords_wp/    → Heat pump (54 files)
```

**Structure:**
```yaml
Text: placeholder_name
Position: (x1, y1, x2, y2)
Schriftart: Helvetica-Bold
Schriftgröße: 14.0
Farbe: 3487029
```

---

## 📄 PDF Templates

**Directory:** `pdf_templates_static/`
- `multi/` - 44 PDFs with text
- `notext/` - 44 PDFs without text

**Variants:**
- Storage: 5-30 kWh (6 options)
- Heat Pump: Yes/No
- Wallbox: Yes/No
- Financing: Yes/No

---

## 🔧 Key Functions

### PDF Generation
```python
from pdf_generator import PDFGenerator

generator = PDFGenerator(
    offer_data=data,
    module_order=modules,
    theme_name="default",
    filename="output.pdf",
    pricing_data=pricing
)
generator.create_pdf()
```

### YML Parsing
```python
import yaml

with open('coords/seite1.yml') as f:
    coords = yaml.safe_load(f)
```

### Template Loading
```python
from pdf_templates import get_cover_letter_template

template = get_cover_letter_template(
    customer_name="Max Mustermann",
    offer_id="ANG-2025-001"
)
```

---

## 🎨 Chart Types

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

---

## 🔌 API Endpoints (To Be Created)

```
POST   /api/v1/pdf/generate
POST   /api/v1/pdf/preview
GET    /api/v1/pdf/templates
POST   /api/v1/pdf/templates/upload
GET    /api/v1/pdf/archive
POST   /api/v1/pdf/archive/{id}/email
```

---

## 📦 Dependencies

**Core:**
- reportlab>=3.6.0
- pypdf>=3.0.0
- Pillow>=9.0.0
- pyyaml>=6.0

**Optional:**
- matplotlib (charts)
- plotly (interactive)

---

## 🚀 Migration Checklist

### Week 1-2 (P0)
- [ ] Migrate pdf_generator.py
- [ ] Setup YML parser
- [ ] Create template manager
- [ ] Implement pricing integration
- [ ] Build core API endpoints

### Week 3-4 (P1)
- [ ] Create PDF UI components
- [ ] Integrate chart rendering
- [ ] Add 3D visualization
- [ ] Implement preview system
- [ ] Setup CRM archiving

### Week 5-6 (P2)
- [ ] Multi-company support
- [ ] Financing calculations
- [ ] Debug tools
- [ ] Performance optimization
- [ ] Complete testing

---

## 🧪 Testing Strategy

**Unit Tests:**
- PDF generation (basic, with pricing, with 3D)
- Template loading and validation
- YML coordinate parsing
- Chart rendering
- Error handling

**Integration Tests:**
- End-to-end PDF generation
- CRM archiving flow
- Multi-company generation
- Email delivery

**Performance Tests:**
- Concurrent generation
- Large PDF handling
- Memory usage
- Generation speed (<3s target)

---

## 📊 Success Metrics

- ✅ All 18 modules migrated
- ✅ 100% test coverage
- ✅ <3s generation time
- ✅ Zero data loss
- ✅ Feature parity
- ✅ <200ms API response

---

## 🔗 Related Documents

- [Complete Analysis](./PDF_SYSTEM_ANALYSIS_COMPLETE.md)
- [Migration Plan](./PDF_MIGRATION_PLAN.md)
- [API Documentation](./PDF_API_DOCUMENTATION.md)
- [Test Strategy](./PDF_TEST_STRATEGY.md)

---

**Last Updated:** 2025-01-21  
**Status:** COMPLETE ✅
