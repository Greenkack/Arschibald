# Codebase Analysis: PDF Page Shift Extension (7 → 8 Pages)

**Analysis Date:** 2025-10-08  
**Purpose:** Identify all code locations requiring changes for 7→8 page migration

---

## Executive Summary

This analysis identifies **all hardcoded references** to page numbers, loops, and page-specific functions that must be updated to extend the PDF generation system from 7 to 8 pages.

**Key Findings:**

- **15 files** in active codebase require changes
- **9 page-specific functions** need renaming
- **Multiple loops** using `range(1, 8)` need extension to `range(1, 9)`
- **Numerous conditional checks** (`if i == X`) need page number updates
- **Test files** reference specific page templates that need updating

---

## 1. Core Files Requiring Changes

### 1.1 Primary Module: `pdf_template_engine/dynamic_overlay.py`

**Critical Changes Required:**

#### A. Function Signature (Line ~1032)

```python
# CURRENT:
def generate_overlay(coords_dir: Path, dynamic_data: dict[str, str], total_pages: int = 7) -> bytes:
    """Erzeugt ein Overlay-PDF für sieben Seiten anhand der coords-Dateien."""

# NEEDS TO CHANGE TO:
def generate_overlay(coords_dir: Path, dynamic_data: dict[str, str], total_pages: int = 8) -> bytes:
    """Erzeugt ein Overlay-PDF für acht Seiten anhand der coords-Dateien."""
```

#### B. Main Loop (Line ~1040)

```python
# CURRENT:
for i in range(1, 8):  # Pages 1-7
    yml_path = coords_dir / f"seite{i}.yml"
    elements = parse_coords_file(yml_path)

# NEEDS TO CHANGE TO:
for i in range(1, 9):  # Pages 1-8
```

#### C. Page-Specific Conditional Blocks (Lines 1048-1356)

**All these conditions need page number shifts:**

| Current Line | Current Code | New Code | Notes |
|--------------|--------------|----------|-------|
| ~1048 | `if i == 1:` | `if i == 2:` | Old page 1 → new page 2 |
| ~1052 | `if i == 6:` | `if i == 7:` | Old page 6 → new page 7 |
| ~1056 | `if i == 3:` | `if i == 4:` | Old page 3 → new page 4 |
| ~1059 | `if i == 3:` | `if i == 4:` | Old page 3 → new page 4 |
| ~1071 | `if i == 4:` | `if i == 5:` | Old page 4 → new page 5 |
| ~1126 | `if i == 3:` | `if i == 4:` | Old page 3 → new page 4 |
| ~1143 | `if i == 6:` | `if i == 7:` | Old page 6 → new page 7 |
| ~1157 | `if i == 6 and text in [...]` | `if i == 7 and text in [...]` | Old page 6 → new page 7 |
| ~1162 | `if i == 4 and text == "firmen_name"` | `if i == 5 and text == "firmen_name"` | Old page 4 → new page 5 |
| ~1185 | `if i == 4 and text == "verwendet..."` | `if i == 5 and text == "verwendet..."` | Old page 4 → new page 5 |
| ~1210 | `if i == 6 and key:` | `if i == 7 and key:` | Old page 6 → new page 7 |
| ~1240 | `if i == 3 and text in {...}` | `if i == 4 and text in {...}` | Old page 3 → new page 4 |
| ~1246 | `if i == 3 and (text or "").strip() == "EUR"` | `if i == 4 and (text or "").strip() == "EUR"` | Old page 3 → new page 4 |
| ~1254 | `if i == 3 and key == "battery_usage_savings_eur"` | `if i == 4 and key == "battery_usage_savings_eur"` | Old page 3 → new page 4 |
| ~1264 | `if i == 1 and key in {...}` | `if i == 2 and key in {...}` | Old page 1 → new page 2 |
| ~1267 | `if i == 3 and text and "JAHRE SIMULATION"` | `if i == 4 and text and "JAHRE SIMULATION"` | Old page 3 → new page 4 |
| ~1303 | `elif i == 1 and (text in right_align_tokens_s1)` | `elif i == 2 and (text in right_align_tokens_s1)` | Old page 1 → new page 2 |
| ~1309 | `elif i == 3 and (text in right_align_tokens_s3)` | `elif i == 4 and (text in right_align_tokens_s3)` | Old page 3 → new page 4 |
| ~1315 | `elif i == 7 and (text in right_align_tokens_s7)` | `elif i == 8 and (text in right_align_tokens_s7)` | Old page 7 → new page 8 |
| ~1325 | `if i == 3 and page3_cost_tokens:` | `if i == 4 and page3_cost_tokens:` | Old page 3 → new page 4 |
| ~1353 | `if i == 4:` | `if i == 5:` | Old page 4 → new page 5 |

**IMPORTANT:** Need to add NEW condition for page 1:

```python
if i == 1:
    _draw_page1_new_content(c, dynamic_data, page_width, page_height)
```

#### D. Page-Specific Functions to Rename

| Old Function Name | New Function Name | Line | Old Page | New Page |
|-------------------|-------------------|------|----------|----------|
| `_draw_page1_test_donuts` | `_draw_page2_test_donuts` | ~588 | 1 | 2 |
| `_draw_page1_kpi_donuts` | `_draw_page2_kpi_donuts` | ~961 | 1 | 2 |
| `_draw_page1_monthly_production_consumption_chart` | `_draw_page2_monthly_production_consumption_chart` | ~813 | 1 | 2 |
| `_draw_page3_waterfall_chart` | `_draw_page4_waterfall_chart` | ~252 | 3 | 4 |
| `_draw_page3_right_chart_and_separator` | `_draw_page4_right_chart_and_separator` | ~1504 | 3 | 4 |
| `_draw_page4_component_images` | `_draw_page5_component_images` | ~1709 | 4 | 5 |
| `_draw_page4_brand_logos` | `_draw_page5_brand_logos` | ~1752 | 4 | 5 |
| `_draw_page6_storage_donuts` | `_draw_page7_storage_donuts` | ~747 | 6 | 7 |
| `_draw_page6_storage_donuts_fixed` | `_draw_page7_storage_donuts_fixed` | ~668 | 6 | 7 |
| `_compact_page6_elements` | `_compact_page7_elements` | ~1364 | 6 | 7 |
| **NEW FUNCTION** | `_draw_page1_new_content` | N/A | N/A | 1 |

#### E. Module Docstring (Line ~5)

```python
# CURRENT:
"""
Erzeugt Text-Overlays für sieben statische Template-Seiten anhand von Koordinaten
aus coords/seite1.yml … seite7.yml und verschmilzt sie mit den Dateien
pdf_templates_static/notext/nt_nt_01.pdf … nt_nt_07.pdf.
"""

# NEEDS TO CHANGE TO:
"""
Erzeugt Text-Overlays für acht statische Template-Seiten anhand von Koordinaten
aus coords/seite1.yml … seite8.yml und verschmilzt sie mit den Dateien
pdf_templates_static/notext/nt_nt_01.pdf … nt_nt_08.pdf.
"""
```

#### F. merge_with_background() Function (Line ~2028)

```python
# CURRENT:
def merge_with_background(overlay_bytes: bytes, bg_dir: Path) -> bytes:
    """Verschmilzt das Overlay mit nt_nt_01.pdf … nt_nt_07.pdf aus bg_dir."""
    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
    writer = PdfWriter()
    for page_num in range(1, 8):  # OLD: 1-7

# NEEDS TO CHANGE TO:
def merge_with_background(overlay_bytes: bytes, bg_dir: Path) -> bytes:
    """Verschmilzt das Overlay mit nt_nt_01.pdf … nt_nt_08.pdf aus bg_dir."""
    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
    writer = PdfWriter()
    for page_num in range(1, 9):  # NEW: 1-8
```

#### G. Page-Specific Conditional in merge_with_background() (Line ~2049, ~2066)

```python
# CURRENT:
if page_num == 1:  # haus.pdf merge
    ...
if page_num == 3:  # Remove legend texts
    ...

# NEEDS TO CHANGE TO:
if page_num == 1:  # haus.pdf merge - STAYS THE SAME (new page 1)
    ...
if page_num == 4:  # Remove legend texts (OLD page 3)
    ...
```

#### H. generate_main_template_pdf_bytes() Function (Line ~2158)

```python
# CURRENT:
total_pages = 7
if additional_pdf:
    try:
        add_reader = PdfReader(io.BytesIO(additional_pdf))
        total_pages = 7 + len(add_reader.pages)
    except Exception:
        total_pages = 7

# NEEDS TO CHANGE TO:
total_pages = 8
if additional_pdf:
    try:
        add_reader = PdfReader(io.BytesIO(additional_pdf))
        total_pages = 8 + len(add_reader.pages)
    except Exception:
        total_pages = 8
```

---

### 1.2 Merger Module: `pdf_template_engine/merger.py`

**Line ~13:**

```python
# CURRENT:
def merge_first_seven_pages(overlay_bytes: bytes) -> bytes:
    writer = PdfWriter()
    ovl = PdfReader(io.BytesIO(overlay_bytes))
    for i in range(1, 8):  # OLD: 1-7
        base = PdfReader(BG / f"nt_{i:02d}.pdf").pages[0]
        base.merge_page(ovl.pages[i-1])
        writer.add_page(base)

# NEEDS TO CHANGE TO:
def merge_first_eight_pages(overlay_bytes: bytes) -> bytes:
    """Merges 8 pages with their background templates."""
    writer = PdfWriter()
    ovl = PdfReader(io.BytesIO(overlay_bytes))
    for i in range(1, 9):  # NEW: 1-8
        base = PdfReader(BG / f"nt_{i:02d}.pdf").pages[0]
        base.merge_page(ovl.pages[i-1])
        writer.add_page(base)

# KEEP OLD FUNCTION FOR BACKWARD COMPATIBILITY:
def merge_first_seven_pages(overlay_bytes: bytes) -> bytes:
    """DEPRECATED: Use merge_first_eight_pages() instead."""
    import warnings
    warnings.warn("merge_first_seven_pages is deprecated, use merge_first_eight_pages", DeprecationWarning)
    return merge_first_eight_pages(overlay_bytes)
```

---

### 1.3 PDF Generator: `pdf_generator.py`

**Line ~1671, ~1677, ~1680:**

```python
# CURRENT:
total_pages = 7
if additional_pdf:
    try:
        from pypdf import PdfReader
        total_pages = 7 + len(PdfReader(_io.BytesIO(additional_pdf)).pages)
    except Exception:
        total_pages = 7

# NEEDS TO CHANGE TO:
total_pages = 8
if additional_pdf:
    try:
        from pypdf import PdfReader
        total_pages = 8 + len(PdfReader(_io.BytesIO(additional_pdf)).pages)
    except Exception:
        total_pages = 8
```

**Line ~1983, ~1985:**

```python
# CURRENT:
tmp_reader = PdfReader(io.BytesIO(additional_pdf))
total_pages = 7 + len(tmp_reader.pages)
# Zusatzseiten mit Footer versehen: Startnummer = 8 (da Seiten 1-7 schon vorhanden)

# NEEDS TO CHANGE TO:
tmp_reader = PdfReader(io.BytesIO(additional_pdf))
total_pages = 8 + len(tmp_reader.pages)
# Zusatzseiten mit Footer versehen: Startnummer = 9 (da Seiten 1-8 schon vorhanden)
```

---

## 2. Helper Scripts and Utilities

### 2.1 `fix_merge_problem.py`

**Line ~210:**

```python
# CURRENT:
for page_num in range(1, 8):  # Seiten 1-7
    template_path = template_dir / f"nt_nt_{page_num:02d}.pdf"

# NEEDS TO CHANGE TO:
for page_num in range(1, 9):  # Seiten 1-8
    template_path = template_dir / f"nt_nt_{page_num:02d}.pdf"
```

**Line ~114, ~203:**

```python
# CURRENT:
overlay_bytes = generate_overlay(coords_dir, dynamic_data, total_pages=7)

# NEEDS TO CHANGE TO:
overlay_bytes = generate_overlay(coords_dir, dynamic_data, total_pages=8)
```

---

### 2.2 `pdf_template_engine/prepare_backgrounds.py`

**Line ~10:**

```python
# CURRENT:
for i in range(1, 8):
    pdf_in  = SRC / f'{i:02d}.pdf'
    png_out = DST / f'{i:02d}.png'

# NEEDS TO CHANGE TO:
for i in range(1, 9):
    pdf_in  = SRC / f'{i:02d}.pdf'
    png_out = DST / f'{i:02d}.png'
```

---

## 3. Test Files Requiring Updates

### 3.1 `verify_pdf_charts.py`

**Changes:** Reference to `nt_nt_06.pdf` → `nt_nt_07.pdf`  
**Changes:** Function call `_draw_page6_storage_donuts` → `_draw_page7_storage_donuts`

### 3.2 `debug_seite6_problem.py`

**Line ~109:**

```python
# CURRENT:
coords_file = Path("coords/seite6.yml")

# NEEDS TO CHANGE TO:
coords_file = Path("coords/seite7.yml")
```

**Changes:** Reference to `nt_nt_06.pdf` → `nt_nt_07.pdf`

### 3.3 `debug_pdf_charts_complete.py`

**Line ~169, ~217:**

```python
# CURRENT:
overlay_bytes = generate_overlay(coords_dir, dynamic_data, total_pages=7)
template_path = Path("pdf_templates_static/notext/nt_nt_06.pdf")

# NEEDS TO CHANGE TO:
overlay_bytes = generate_overlay(coords_dir, dynamic_data, total_pages=8)
template_path = Path("pdf_templates_static/notext/nt_nt_07.pdf")
```

### 3.4 `direct_chart_test.py`

**Line ~135, ~200:**

```python
# CURRENT:
template_path = Path("pdf_templates_static/notext/nt_nt_06.pdf")
overlay_bytes = generate_overlay(coords_dir, dynamic_data, total_pages=7)

# NEEDS TO CHANGE TO:
template_path = Path("pdf_templates_static/notext/nt_nt_07.pdf")
overlay_bytes = generate_overlay(coords_dir, dynamic_data, total_pages=8)
```

### 3.5 `debug_logo_pdf.py`

**Line ~75:**

```python
# CURRENT:
template_path = "pdf_templates_static/notext/nt_nt_04.pdf"

# NEEDS TO CHANGE TO:
template_path = "pdf_templates_static/notext/nt_nt_05.pdf"
```

### 3.6 `debug_wasserfall_data.py`

**Line ~58, ~114:**

```python
# CURRENT:
total_pages=7

# NEEDS TO CHANGE TO:
total_pages=8
```

### 3.7 `tests/test_hp_functions.py`

**Line ~57:**

```python
# CURRENT:
for i in range(1, 8):
    wp_file = os.path.join(coords_wp_path, f'wp_seite{i}.yml')

# NEEDS TO CHANGE TO:
for i in range(1, 9):
    wp_file = os.path.join(coords_wp_path, f'wp_seite{i}.yml')
```

### 3.8 `tests/test_seite6_charts.py`

**Line ~80:**

```python
# CURRENT:
for page_num in range(1, 8):  # Seiten 1-7
    template_path = template_dir / f"nt_nt_{page_num:02d}.pdf"

# NEEDS TO CHANGE TO:
for page_num in range(1, 9):  # Seiten 1-8
    template_path = template_dir / f"nt_nt_{page_num:02d}.pdf"
```

### 3.9 `tests/test_template_system.py`

**Line ~28, ~54:**

```python
# CURRENT:
for i in range(1, 8):
    pv_file = template_dir / f"nt_nt_{i:02d}.pdf"
    hp_file = template_dir / f"hp_nt_{i:02d}.pdf"
...
for i in range(1, 8):
    yaml_file = coords_dir / f"seite{i}.yml"

# NEEDS TO CHANGE TO:
for i in range(1, 9):
    pv_file = template_dir / f"nt_nt_{i:02d}.pdf"
    hp_file = template_dir / f"hp_nt_{i:02d}.pdf"
...
for i in range(1, 9):
    yaml_file = coords_dir / f"seite{i}.yml"
```

### 3.10 Multiple Test Files with `total_pages=7`

**Files requiring `total_pages=7` → `total_pages=8` change:**

- `tests/test_all_three_fixes.py` (Line ~98)
- `tests/test_product_images.py` (Line ~61)
- `tests/test_seite1_donuts.py` (Line ~54)
- `debug_seite6_donuts.py` (Line ~82, ~145)

---

## 4. Documentation Files

### 4.1 `PDF_SYSTEM_DOCUMENTATION.md`

**Line ~10:**

```markdown
# CURRENT:
- **Templates**: `nt_nt_01.pdf` bis `nt_nt_07.pdf` (7 Seiten)
- **Koordinaten**: `coords/seite1.yml` bis `coords/seite7.yml`

# NEEDS TO CHANGE TO:
- **Templates**: `nt_nt_01.pdf` bis `nt_nt_08.pdf` (8 Seiten)
- **Koordinaten**: `coords/seite1.yml` bis `coords/seite8.yml`
```

---

## 5. Archive Files (Optional - Low Priority)

The following files in `archive/sokuk_legacy/` contain similar patterns but are archived:

- `archive/sokuk_legacy/pdf_template_engine/dynamic_overlay.py`
- `archive/sokuk_legacy/pdf_template_engine/merger.py`
- `archive/sokuk_legacy/fix_merge_problem.py`
- `archive/sokuk_legacy/debug_pdf_charts_complete.py`
- `archive/sokuk_legacy/direct_chart_test.py`
- `archive/sokuk_legacy/tests/test_hp_functions.py`
- `archive/sokuk_legacy/tests/test_template_system.py`
- `archive/sokuk_legacy/test_seite6_charts.py`

**Recommendation:** Update only if these files are still in use, otherwise skip.

---

## 6. Summary of Changes by Category

### 6.1 Loop Changes: `range(1, 8)` → `range(1, 9)`

| File | Line(s) | Context |
|------|---------|---------|
| `pdf_template_engine/dynamic_overlay.py` | ~1040, ~2031 | Main page processing loops |
| `pdf_template_engine/merger.py` | ~13 | Merge loop |
| `pdf_template_engine/prepare_backgrounds.py` | ~10 | Background preparation |
| `fix_merge_problem.py` | ~210 | Test/debug loop |
| `tests/test_hp_functions.py` | ~57 | Test loop |
| `tests/test_seite6_charts.py` | ~80 | Test loop |
| `tests/test_template_system.py` | ~28, ~54 | Test loops |

### 6.2 Page-Specific Conditionals: `if i == X`

**Total:** ~20 conditional blocks in `pdf_template_engine/dynamic_overlay.py` need page number updates

### 6.3 Function Renamings

**Total:** 10 functions (9 existing + 1 new)

### 6.4 Parameter Changes: `total_pages=7` → `total_pages=8`

**Total:** ~15 occurrences across test files and helper scripts

### 6.5 Hardcoded Page References

**Total:** ~10 occurrences in `pdf_generator.py` and helper scripts

---

## 7. Files NOT Requiring Changes

The following files dynamically construct paths and will work automatically with 8 pages:

- Coordinate files: `coords/seite1.yml` - `coords/seite8.yml` ✅ Already prepared
- Template files: `pdf_templates_static/notext/nt_nt_01.pdf` - `nt_nt_08.pdf` ✅ Already prepared
- Heatpump coords: `coords_wp/wp_seite1.yml` - `wp_seite8.yml` ✅ Already prepared
- Heatpump templates: `pdf_templates_static/notext/hp_nt_01.pdf` - `hp_nt_08.pdf` ✅ Already prepared

---

## 8. Implementation Priority

### Priority 1 (Critical - Must Change)

1. `pdf_template_engine/dynamic_overlay.py` - Core generation logic
2. `pdf_template_engine/merger.py` - Merge logic
3. `pdf_generator.py` - Main PDF generator

### Priority 2 (High - Should Change)

4. `fix_merge_problem.py` - Helper script
5. `pdf_template_engine/prepare_backgrounds.py` - Background preparation

### Priority 3 (Medium - Test Files)

6. All test files in `tests/` directory
7. Debug scripts (`debug_*.py`)

### Priority 4 (Low - Documentation)

8. `PDF_SYSTEM_DOCUMENTATION.md`
9. Archive files (if still in use)

---

## 9. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing a conditional check | High | Systematic search completed |
| Function call mismatch | High | All functions identified and mapped |
| Test failures | Medium | All test files identified |
| Documentation outdated | Low | Documentation files identified |

---

## 10. Validation Checklist

After implementation, verify:

- [ ] All loops use `range(1, 9)`
- [ ] All page conditionals updated (old page + 1)
- [ ] All functions renamed correctly
- [ ] All function calls updated
- [ ] All `total_pages=7` changed to `total_pages=8`
- [ ] All hardcoded `7` references changed to `8`
- [ ] New page 1 function created
- [ ] New page 1 conditional added
- [ ] Documentation updated
- [ ] Tests pass

---

**End of Analysis**
