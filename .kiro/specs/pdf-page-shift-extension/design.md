# Design Document: PDF Page Shift Extension (7 → 8 Pages)

## Overview

Das PDF-Generierungssystem wird von 7 auf 8 Seiten erweitert, wobei eine neue Seite 1 eingefügt wird und alle bestehenden Seiten um eine Position nach hinten verschoben werden. Die Architektur basiert auf einem Template-Overlay-System, bei dem statische PDF-Templates mit dynamischen Text-Overlays kombiniert werden.

**Kernprinzip:** Alle Hardcoded-Referenzen auf Seitenzahlen müssen um +1 verschoben werden, während die Schleifengrenzen von `range(1, 8)` auf `range(1, 9)` erweitert werden.

## Architecture

### Current System (7 Pages)

```
┌─────────────────────────────────────────────────────────────┐
│                    PDF Generation Flow                       │
└─────────────────────────────────────────────────────────────┘

1. generate_overlay() in dynamic_overlay.py
   ├─ Loop: for page_num in range(1, 8)  # Pages 1-7
   │  ├─ Load coords/seiteX.yml
   │  ├─ Load pdf_templates_static/notext/nt_nt_0X.pdf
   │  ├─ Apply text overlays from YML coordinates
   │  ├─ Call page-specific functions:
   │  │  ├─ Page 1: _draw_page1_test_donuts()
   │  │  ├─ Page 1: _draw_page1_kpi_donuts()
   │  │  ├─ Page 3: _draw_page3_waterfall_chart()
   │  │  ├─ Page 3: _draw_page3_right_chart_and_separator()
   │  │  ├─ Page 4: _draw_page4_component_images()
   │  │  ├─ Page 4: _draw_page4_brand_logos()
   │  │  ├─ Page 6: _draw_page6_storage_donuts()
   │  │  └─ Page 6: _draw_page6_storage_donuts_fixed()
   │  └─ Merge overlay with template
   └─ Return merged PDF bytes

2. merge_first_seven_pages() in merger.py
   └─ Merges 7 pages with backgrounds
```

### New System (8 Pages)

```
┌─────────────────────────────────────────────────────────────┐
│                    PDF Generation Flow (NEW)                 │
└─────────────────────────────────────────────────────────────┘

1. generate_overlay() in dynamic_overlay.py
   ├─ Loop: for page_num in range(1, 9)  # Pages 1-8 ✓ CHANGED
   │  ├─ Load coords/seiteX.yml (X = 1-8)
   │  ├─ Load pdf_templates_static/notext/nt_nt_0X.pdf (X = 01-08)
   │  ├─ Apply text overlays from YML coordinates
   │  ├─ Call page-specific functions:
   │  │  ├─ Page 1: _draw_page1_new_content() ✓ NEW
   │  │  ├─ Page 2: _draw_page2_test_donuts() ✓ RENAMED (was page1)
   │  │  ├─ Page 2: _draw_page2_kpi_donuts() ✓ RENAMED (was page1)
   │  │  ├─ Page 4: _draw_page4_waterfall_chart() ✓ RENAMED (was page3)
   │  │  ├─ Page 4: _draw_page4_right_chart_and_separator() ✓ RENAMED (was page3)
   │  │  ├─ Page 5: _draw_page5_component_images() ✓ RENAMED (was page4)
   │  │  ├─ Page 5: _draw_page5_brand_logos() ✓ RENAMED (was page4)
   │  │  ├─ Page 7: _draw_page7_storage_donuts() ✓ RENAMED (was page6)
   │  │  └─ Page 7: _draw_page7_storage_donuts_fixed() ✓ RENAMED (was page6)
   │  └─ Merge overlay with template
   └─ Return merged PDF bytes

2. merge_first_eight_pages() in merger.py ✓ RENAMED
   └─ Merges 8 pages with backgrounds
```

## Components and Interfaces

### 1. Core Module: `pdf_template_engine/dynamic_overlay.py`

**Changes Required:**

#### 1.1 Main Function: `generate_overlay()`

```python
# BEFORE (Line ~1032)
def generate_overlay(coords_dir: Path, dynamic_data: dict[str, str], total_pages: int = 7) -> bytes:
    """Erzeugt ein Overlay-PDF für sieben Seiten anhand der coords-Dateien."""
    # ...
    for page_num in range(1, 8):  # OLD: 1-7
        # ...

# AFTER
def generate_overlay(coords_dir: Path, dynamic_data: dict[str, str], total_pages: int = 8) -> bytes:
    """Erzeugt ein Overlay-PDF für acht Seiten anhand der coords-Dateien."""
    # ...
    for page_num in range(1, 9):  # NEW: 1-8
        # ...
```

**Impact:** This is the main loop that processes all pages. Changing from `range(1, 8)` to `range(1, 9)` extends the system to 8 pages.

#### 1.2 Page-Specific Function Mapping

The function needs to map page numbers to their specific drawing functions. This mapping must be updated:

```python
# BEFORE (conceptual - actual implementation may vary)
if page_num == 1:
    _draw_page1_test_donuts(c, dynamic_data, page_width, page_height)
    _draw_page1_kpi_donuts(c, dynamic_data, page_width, page_height)
elif page_num == 3:
    _draw_page3_waterfall_chart(c, dynamic_data, page_width, page_height)
    _draw_page3_right_chart_and_separator(c, elements, dynamic_data, page_width, page_height)
elif page_num == 4:
    _draw_page4_component_images(c, dynamic_data, page_width, page_height)
    _draw_page4_brand_logos(c, dynamic_data, page_width, page_height)
elif page_num == 6:
    _draw_page6_storage_donuts(c, dynamic_data, page_width, page_height)
    _draw_page6_storage_donuts_fixed(c, dynamic_data, page_width, page_height)

# AFTER
if page_num == 1:
    _draw_page1_new_content(c, dynamic_data, page_width, page_height)  # NEW
elif page_num == 2:  # OLD: page 1
    _draw_page2_test_donuts(c, dynamic_data, page_width, page_height)  # RENAMED
    _draw_page2_kpi_donuts(c, dynamic_data, page_width, page_height)  # RENAMED
elif page_num == 4:  # OLD: page 3
    _draw_page4_waterfall_chart(c, dynamic_data, page_width, page_height)  # RENAMED
    _draw_page4_right_chart_and_separator(c, elements, dynamic_data, page_width, page_height)  # RENAMED
elif page_num == 5:  # OLD: page 4
    _draw_page5_component_images(c, dynamic_data, page_width, page_height)  # RENAMED
    _draw_page5_brand_logos(c, dynamic_data, page_width, page_height)  # RENAMED
elif page_num == 7:  # OLD: page 6
    _draw_page7_storage_donuts(c, dynamic_data, page_width, page_height)  # RENAMED
    _draw_page7_storage_donuts_fixed(c, dynamic_data, page_width, page_height)  # RENAMED
```

#### 1.3 Function Renaming Strategy

**Page-Specific Functions to Rename:**

| Old Function Name | New Function Name | Old Page | New Page | Notes |
|-------------------|-------------------|----------|----------|-------|
| `_draw_page1_test_donuts` | `_draw_page2_test_donuts` | 1 | 2 | Test donut charts |
| `_draw_page1_kpi_donuts` | `_draw_page2_kpi_donuts` | 1 | 2 | KPI donut charts |
| `_draw_page3_waterfall_chart` | `_draw_page4_waterfall_chart` | 3 | 4 | Waterfall diagram |
| `_draw_page3_right_chart_and_separator` | `_draw_page4_right_chart_and_separator` | 3 | 4 | 20-year results |
| `_draw_page4_component_images` | `_draw_page5_component_images` | 4 | 5 | Product images |
| `_draw_page4_brand_logos` | `_draw_page5_brand_logos` | 4 | 5 | Brand logos |
| `_draw_page6_storage_donuts` | `_draw_page7_storage_donuts` | 6 | 7 | Storage donuts |
| `_draw_page6_storage_donuts_fixed` | `_draw_page7_storage_donuts_fixed` | 6 | 7 | Fixed storage donuts |
| `_compact_page6_elements` | `_compact_page7_elements` | 6 | 7 | Element compaction |
| N/A | `_draw_page1_new_content` | N/A | 1 | **NEW** - New page 1 content |

**Implementation Strategy:**

1. Create new functions with new names
2. Copy implementation from old functions
3. Update internal comments and docstrings
4. Mark old functions as deprecated with clear comments
5. Update all call sites to use new function names

#### 1.4 File Path Construction

The system constructs file paths dynamically. These need to be updated:

```python
# BEFORE
coords_file = coords_dir / f"seite{page_num}.yml"  # Works for 1-7
template_file = template_dir / f"nt_nt_{page_num:02d}.pdf"  # Works for 01-07

# AFTER
coords_file = coords_dir / f"seite{page_num}.yml"  # Now works for 1-8
template_file = template_dir / f"nt_nt_{page_num:02d}.pdf"  # Now works for 01-08
```

**No changes needed** - the dynamic construction already supports 8 pages, as long as the files exist.

#### 1.5 Heatpump Variant Support

The system supports a heatpump variant with different templates:

```python
# BEFORE
if is_heatpump:
    coords_dir = Path("coords_wp")  # wp_seite1.yml - wp_seite7.yml
    template_prefix = "hp_nt_"  # hp_nt_01.pdf - hp_nt_07.pdf
else:
    coords_dir = Path("coords")  # seite1.yml - seite7.yml
    template_prefix = "nt_nt_"  # nt_nt_01.pdf - nt_nt_07.pdf

# AFTER
if is_heatpump:
    coords_dir = Path("coords_wp")  # wp_seite1.yml - wp_seite8.yml ✓
    template_prefix = "hp_nt_"  # hp_nt_01.pdf - hp_nt_08.pdf ✓
else:
    coords_dir = Path("coords")  # seite1.yml - seite8.yml ✓
    template_prefix = "nt_nt_"  # nt_nt_01.pdf - nt_nt_08.pdf ✓
```

**User has already prepared all files** - no file creation needed, only code updates.

### 2. Merger Module: `pdf_template_engine/merger.py`

**Changes Required:**

```python
# BEFORE
def merge_first_seven_pages(overlay_bytes: bytes) -> bytes:
    writer = PdfWriter()
    ovl = PdfReader(io.BytesIO(overlay_bytes))

    for i in range(1, 8):  # OLD: 1-7
        base = PdfReader(BG / f"nt_{i:02d}.pdf").pages[0]
        base.merge_page(ovl.pages[i-1])
        writer.add_page(base)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()

# AFTER
def merge_first_eight_pages(overlay_bytes: bytes) -> bytes:
    """Merges 8 pages with their background templates."""
    writer = PdfWriter()
    ovl = PdfReader(io.BytesIO(overlay_bytes))

    for i in range(1, 9):  # NEW: 1-8
        base = PdfReader(BG / f"nt_{i:02d}.pdf").pages[0]
        base.merge_page(ovl.pages[i-1])
        writer.add_page(base)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()

# Keep old function for backward compatibility (deprecated)
def merge_first_seven_pages(overlay_bytes: bytes) -> bytes:
    """DEPRECATED: Use merge_first_eight_pages() instead."""
    import warnings
    warnings.warn("merge_first_seven_pages is deprecated, use merge_first_eight_pages", DeprecationWarning)
    return merge_first_eight_pages(overlay_bytes)
```

### 3. Coordinate Files: `coords/` and `coords_wp/`

**Status:** ✅ Already prepared by user

- `coords/seite1.yml` - `coords/seite8.yml` (new page 1 + shifted pages 2-8)
- `coords_wp/wp_seite1.yml` - `coords_wp/wp_seite8.yml` (heatpump variant)

**No changes needed** - files are ready.

### 4. PDF Templates: `pdf_templates_static/notext/`

**Status:** ✅ Already prepared by user

- `nt_nt_01.pdf` - `nt_nt_08.pdf` (new page 1 + shifted pages 2-8)
- `hp_nt_01.pdf` - `hp_nt_08.pdf` (heatpump variant)

**No changes needed** - files are ready.

### 5. Helper Scripts and Tests

**Files that need updates:**

1. **`fix_merge_problem.py`** (Line 210)

   ```python
   # BEFORE
   for page_num in range(1, 8):  # Seiten 1-7
   
   # AFTER
   for page_num in range(1, 9):  # Seiten 1-8
   ```

2. **Test files** that reference specific pages:
   - `verify_pdf_charts.py` - References `nt_nt_06.pdf` (now `nt_nt_07.pdf`)
   - `debug_seite6_problem.py` - References `seite6.yml` (now `seite7.yml`)
   - `debug_pdf_charts_complete.py` - References `nt_nt_06.pdf` (now `nt_nt_07.pdf`)
   - `direct_chart_test.py` - References `nt_nt_06.pdf` (now `nt_nt_07.pdf`)
   - `debug_logo_pdf.py` - References `nt_nt_04.pdf` (now `nt_nt_05.pdf`)

## Data Models

### Page Mapping Model

```python
# Page mapping: OLD -> NEW
PAGE_SHIFT_MAPPING = {
    # OLD PAGE -> NEW PAGE
    1: 2,  # Old page 1 becomes new page 2
    2: 3,  # Old page 2 becomes new page 3
    3: 4,  # Old page 3 becomes new page 4
    4: 5,  # Old page 4 becomes new page 5
    5: 6,  # Old page 5 becomes new page 6
    6: 7,  # Old page 6 becomes new page 7
    7: 8,  # Old page 7 becomes new page 8
}

# Function name mapping: OLD -> NEW
FUNCTION_NAME_MAPPING = {
    "_draw_page1_test_donuts": "_draw_page2_test_donuts",
    "_draw_page1_kpi_donuts": "_draw_page2_kpi_donuts",
    "_draw_page3_waterfall_chart": "_draw_page4_waterfall_chart",
    "_draw_page3_right_chart_and_separator": "_draw_page4_right_chart_and_separator",
    "_draw_page4_component_images": "_draw_page5_component_images",
    "_draw_page4_brand_logos": "_draw_page5_brand_logos",
    "_draw_page6_storage_donuts": "_draw_page7_storage_donuts",
    "_draw_page6_storage_donuts_fixed": "_draw_page7_storage_donuts_fixed",
    "_compact_page6_elements": "_compact_page7_elements",
}
```

### Configuration Model

```python
# PDF Generation Configuration
PDF_CONFIG = {
    "total_pages": 8,  # Changed from 7
    "page_range": range(1, 9),  # Changed from range(1, 8)
    "coords_dir": "coords",
    "coords_wp_dir": "coords_wp",
    "template_dir": "pdf_templates_static/notext",
    "template_prefix_normal": "nt_nt_",
    "template_prefix_heatpump": "hp_nt_",
    "coords_file_pattern": "seite{page_num}.yml",
    "coords_wp_file_pattern": "wp_seite{page_num}.yml",
    "template_file_pattern": "{prefix}{page_num:02d}.pdf",
}
```

## Error Handling

### 1. Missing File Detection

```python
def validate_page_files(page_num: int, is_heatpump: bool = False) -> tuple[bool, list[str]]:
    """Validates that all required files exist for a given page number.
    
    Returns:
        (is_valid, missing_files)
    """
    missing = []
    
    # Check coordinates file
    coords_dir = Path("coords_wp" if is_heatpump else "coords")
    coords_prefix = "wp_" if is_heatpump else ""
    coords_file = coords_dir / f"{coords_prefix}seite{page_num}.yml"
    if not coords_file.exists():
        missing.append(str(coords_file))
    
    # Check template file
    template_dir = Path("pdf_templates_static/notext")
    template_prefix = "hp_nt_" if is_heatpump else "nt_nt_"
    template_file = template_dir / f"{template_prefix}{page_num:02d}.pdf"
    if not template_file.exists():
        missing.append(str(template_file))
    
    return (len(missing) == 0, missing)
```

### 2. Graceful Degradation

```python
def generate_overlay_safe(coords_dir: Path, dynamic_data: dict[str, str], total_pages: int = 8) -> bytes:
    """Safe version of generate_overlay with error handling."""
    try:
        return generate_overlay(coords_dir, dynamic_data, total_pages)
    except FileNotFoundError as e:
        print(f"⚠️ Warning: Missing file {e.filename}")
        print(f"   Falling back to {total_pages - 1} pages")
        return generate_overlay(coords_dir, dynamic_data, total_pages - 1)
    except Exception as e:
        print(f"❌ Error generating overlay: {e}")
        raise
```

### 3. Backward Compatibility

```python
def detect_page_count() -> int:
    """Auto-detects whether 7 or 8 page system is available."""
    coords_dir = Path("coords")
    
    # Check if seite8.yml exists
    if (coords_dir / "seite8.yml").exists():
        # Check if nt_nt_08.pdf exists
        template_dir = Path("pdf_templates_static/notext")
        if (template_dir / "nt_nt_08.pdf").exists():
            return 8
    
    return 7  # Fallback to 7 pages
```

## Testing Strategy

### 1. Unit Tests

```python
def test_page_count_extension():
    """Test that the system correctly handles 8 pages."""
    assert PDF_CONFIG["total_pages"] == 8
    assert len(list(PDF_CONFIG["page_range"])) == 8

def test_page_shift_mapping():
    """Test that old page numbers map to new page numbers correctly."""
    assert PAGE_SHIFT_MAPPING[1] == 2
    assert PAGE_SHIFT_MAPPING[6] == 7
    assert PAGE_SHIFT_MAPPING[7] == 8

def test_function_renaming():
    """Test that function names are correctly mapped."""
    assert FUNCTION_NAME_MAPPING["_draw_page1_test_donuts"] == "_draw_page2_test_donuts"
    assert FUNCTION_NAME_MAPPING["_draw_page6_storage_donuts"] == "_draw_page7_storage_donuts"
```

### 2. Integration Tests

```python
def test_full_pdf_generation_8_pages():
    """Test that a full 8-page PDF can be generated."""
    dynamic_data = get_test_data()
    coords_dir = Path("coords")
    
    pdf_bytes = generate_overlay(coords_dir, dynamic_data, total_pages=8)
    
    # Verify PDF has 8 pages
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(pdf_reader.pages) == 8

def test_page_specific_functions():
    """Test that page-specific functions are called on correct pages."""
    # Mock canvas and data
    c = Mock()
    dynamic_data = get_test_data()
    
    # Test new page 2 (old page 1)
    _draw_page2_test_donuts(c, dynamic_data, 595, 842)
    assert c.drawString.called
    
    # Test new page 4 (old page 3)
    _draw_page4_waterfall_chart(c, dynamic_data, 595, 842)
    assert c.rect.called
```

### 3. Visual Regression Tests

```python
def test_visual_content_placement():
    """Test that content appears on the correct pages."""
    pdf_bytes = generate_test_pdf_8_pages()
    
    # Extract text from each page
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    
    # Page 1 should have new content
    page1_text = pdf_reader.pages[0].extract_text()
    assert "NEW_PAGE_1_MARKER" in page1_text
    
    # Page 2 should have old page 1 content
    page2_text = pdf_reader.pages[1].extract_text()
    assert "IHR PERSÖNLICHES ANGEBOT" in page2_text
    
    # Page 4 should have waterfall chart (old page 3)
    page4_text = pdf_reader.pages[3].extract_text()
    assert "Direkt" in page4_text or "Einspeisung" in page4_text
```

### 4. File Existence Tests

```python
def test_all_required_files_exist():
    """Test that all required YML and PDF files exist."""
    for page_num in range(1, 9):
        # Normal variant
        is_valid, missing = validate_page_files(page_num, is_heatpump=False)
        assert is_valid, f"Missing files for page {page_num}: {missing}"
        
        # Heatpump variant
        is_valid, missing = validate_page_files(page_num, is_heatpump=True)
        assert is_valid, f"Missing heatpump files for page {page_num}: {missing}"
```

## Implementation Phases

### Phase 1: Core System Extension

1. Update `generate_overlay()` loop from `range(1, 8)` to `range(1, 9)`
2. Update `merge_first_seven_pages()` to `merge_first_eight_pages()`
3. Update default `total_pages` parameter from 7 to 8
4. Add validation for 8-page file existence

### Phase 2: Function Renaming

1. Create new functions with shifted names (e.g., `_draw_page2_test_donuts`)
2. Copy implementation from old functions
3. Update docstrings and comments
4. Mark old functions as deprecated

### Phase 3: Call Site Updates

1. Update all `if page_num == X:` conditions to new page numbers
2. Update function calls to use new function names
3. Update comments that reference specific pages

### Phase 4: Helper Script Updates

1. Update `fix_merge_problem.py` loop
2. Update test files to reference new page numbers
3. Update debug scripts to reference new file names

### Phase 5: Testing and Validation

1. Run unit tests
2. Run integration tests
3. Generate test PDFs and verify visually
4. Check all 8 pages render correctly
5. Verify content is on correct pages

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missing file references | Medium | High | Implement file validation before generation |
| Incorrect page mapping | Medium | High | Use mapping constants, add unit tests |
| Function call mismatches | Low | High | Systematic renaming with search/replace |
| Backward compatibility issues | Low | Medium | Keep deprecated functions, add warnings |
| Visual regression | Medium | Medium | Visual regression tests, manual verification |
| Test failures | High | Low | Update tests systematically |

## Rollback Strategy

If issues arise:

1. **Immediate Rollback:**
   - Revert `range(1, 9)` back to `range(1, 8)`
   - Revert function names to original
   - System falls back to 7 pages

2. **Partial Rollback:**
   - Keep 8-page support but make it optional
   - Add configuration flag: `use_8_pages = False`
   - Auto-detect based on file existence

3. **Data Preservation:**
   - Old 7-page YML and PDF files are not deleted
   - Can coexist with 8-page files
   - System can detect and use appropriate version

## Success Criteria

1. ✅ PDF generation produces 8 pages
2. ✅ New page 1 appears first with correct content
3. ✅ Old page 1 content appears on new page 2
4. ✅ Old page 7 content appears on new page 8
5. ✅ All page-specific functions execute on correct pages
6. ✅ Waterfall chart appears on page 4 (was page 3)
7. ✅ Storage donuts appear on page 7 (was page 6)
8. ✅ Component images appear on page 5 (was page 4)
9. ✅ All text overlays align correctly with templates
10. ✅ No functionality is lost from the 7-page system
