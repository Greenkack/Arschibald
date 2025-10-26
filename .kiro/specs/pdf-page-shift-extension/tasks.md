# Implementation Plan: PDF Page Shift Extension (7 → 8 Pages)

## Overview

This implementation plan converts the PDF generation system from 7 to 8 pages by inserting a new page 1 and shifting all existing pages by +1. The plan follows a systematic approach to ensure no functionality is lost.

---

## Tasks

- [x] 1. Analyze and document current codebase

  - Identify all hardcoded references to page numbers 1-7
  - Identify all loops using `range(1, 8)`
  - Identify all page-specific function calls
  - Create a comprehensive list of files requiring changes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Update core PDF generation loop in `pdf_template_engine/dynamic_overlay.py`

  - [x] 2.1 Change `generate_overlay()` function signature default parameter from `total_pages: int = 7` to `total_pages: int = 8`

    - Update function docstring to reflect 8 pages
    - _Requirements: 2.1, 2.2_
  
  - [x] 2.2 Update main page processing loop from `range(1, 8)` to `range(1, 9)`

    - Locate the main loop in `generate_overlay()` function (around line 1032)
    - Change loop range to process 8 pages instead of 7
    - Update any comments referencing "sieben Seiten" to "acht Seiten"
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 2.3 Verify file path construction works for 8 pages

    - Confirm `coords_dir / f"seite{page_num}.yml"` works for page_num 1-8
    - Confirm `template_dir / f"nt_nt_{page_num:02d}.pdf"` works for page_num 01-08
    - Confirm heatpump variant paths work for 8 pages
    - _Requirements: 2.3, 2.4, 2.5_
- [x] 3. Rename and shift all page-specific drawing functions

- [ ] 3. Rename and shift all page-specific drawing functions

  - [x] 3.1 Rename `_draw_page1_test_donuts` to `_draw_page2_test_donuts`

    - Copy function implementation
    - Update docstring: "Seite 1" → "Seite 2"
    - Update internal comments referencing page 1
    - Add comment: `# OLD: page 1 -> NEW: page 2`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.2 Rename `_draw_page1_kpi_donuts` to `_draw_page2_kpi_donuts`

    - Copy function implementation
    - Update docstring: "Seite 1" → "Seite 2"
    - Update internal comments
    - Add comment: `# OLD: page 1 -> NEW: page 2`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.3 Rename `_draw_page3_waterfall_chart` to `_draw_page4_waterfall_chart`

    - Copy function implementation
    - Update docstring: "Seite 3" → "Seite 4"
    - Update internal comments and coordinate references
    - Add comment: `# OLD: page 3 -> NEW: page 4`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.4 Rename `_draw_page3_right_chart_and_separator` to `_draw_page4_right_chart_and_separator`

    - Copy function implementation
    - Update docstring: "Seite 3" → "Seite 4"
    - Update internal comments
    - Add comment: `# OLD: page 3 -> NEW: page 4`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.5 Rename `_draw_page4_component_images` to `_draw_page5_component_images`

    - Copy function implementation
    - Update docstring: "Seite 4" → "Seite 5"
    - Update internal comments
    - Add comment: `# OLD: page 4 -> NEW: page 5`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.6 Rename `_draw_page4_brand_logos` to `_draw_page5_brand_logos`

    - Copy function implementation
    - Update docstring: "Seite 4" → "Seite 5"
    - Update internal comments
    - Add comment: `# OLD: page 4 -> NEW: page 5`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.7 Rename `_draw_page6_storage_donuts` to `_draw_page7_storage_donuts`

    - Copy function implementation
    - Update docstring: "Seite 6" → "Seite 7"
    - Update internal comments
    - Add comment: `# OLD: page 6 -> NEW: page 7`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.8 Rename `_draw_page6_storage_donuts_fixed` to `_draw_page7_storage_donuts_fixed`

    - Copy function implementation
    - Update docstring: "Seite 6" → "Seite 7"
    - Update internal comments
    - Add comment: `# OLD: page 6 -> NEW: page 7`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.9 Rename `_compact_page6_elements` to `_compact_page7_elements`

    - Copy function implementation
    - Update docstring: "Seite 6" → "Seite 7"
    - Update internal comments
    - Add comment: `# OLD: page 6 -> NEW: page 7`
    - _Requirements: 3.1, 3.2_
  
  - [x] 3.10 Create new `_draw_page1_new_content` function for new page 1

    - Create function signature matching other page-specific functions
    - Add placeholder implementation (can be empty or minimal)
    - Add docstring explaining this is the new page 1
    - Add TODO comment for future content implementation
    - _Requirements: 3.5_

- [x] 4. Update all page-specific function call sites in `generate_overlay()`

  - [x] 4.1 Update page 1 condition to call `_draw_page1_new_content`

    - Locate `if page_num == 1:` block
    - Replace old function calls with `_draw_page1_new_content(c, dynamic_data, page_width, page_height)`
    - _Requirements: 3.5, 4.1, 4.2_
  
  - [x] 4.2 Update page 2 condition (old page 1) to call renamed functions

    - Change `if page_num == 1:` to `elif page_num == 2:`
    - Update calls to `_draw_page2_test_donuts` and `_draw_page2_kpi_donuts`
    - Add comment: `# OLD: page 1 -> NEW: page 2`
    - _Requirements: 3.1, 3.2, 4.1, 4.2_
  
  - [x] 4.3 Update page 4 condition (old page 3) to call renamed functions

    - Change `if page_num == 3:` to `elif page_num == 4:`
    - Update calls to `_draw_page4_waterfall_chart` and `_draw_page4_right_chart_and_separator`
    - Add comment: `# OLD: page 3 -> NEW: page 4`
    - _Requirements: 3.1, 3.2, 4.1, 4.2_
  
  - [x] 4.4 Update page 5 condition (old page 4) to call renamed functions

    - Change `if page_num == 4:` to `elif page_num == 5:`
    - Update calls to `_draw_page5_component_images` and `_draw_page5_brand_logos`
    - Add comment: `# OLD: page 4 -> NEW: page 5`
    - _Requirements: 3.1, 3.2, 4.1, 4.2_
  
  - [x] 4.5 Update page 7 condition (old page 6) to call renamed functions

    - Change `if page_num == 6:` to `elif page_num == 7:`
    - Update calls to `_draw_page7_storage_donuts` and `_draw_page7_storage_donuts_fixed`
    - Add comment: `# OLD: page 6 -> NEW: page 7`
    - _Requirements: 3.1, 3.2, 4.1, 4.2_

- [x] 5. Update merger module `pdf_template_engine/merger.py`

  - [x] 5.1 Rename `merge_first_seven_pages` to `merge_first_eight_pages`

    - Create new function `merge_first_eight_pages(overlay_bytes: bytes) -> bytes`
    - Update docstring to reflect 8 pages
    - Change loop from `range(1, 8)` to `range(1, 9)`
    - _Requirements: 2.1, 2.2_
  
  - [x] 5.2 Keep old function for backward compatibility

    - Keep `merge_first_seven_pages` function
    - Add deprecation warning
    - Make it call `merge_first_eight_pages` internally
    - Add docstring: "DEPRECATED: Use merge_first_eight_pages() instead"
    - _Requirements: 7.1, 7.2, 7.3_
- [ ] 6. Update helper scripts and utilities

- [x] 6. Update helper scripts and utilities

  - [x] 6.1 Update `fix_merge_problem.py` loop from `range(1, 8)` to `range(1, 9)`

    - Locate loop around line 210
    - Update range to process 8 pages
    - Update comments
    - _Requirements: 2.1, 2.2_
  
  - [x] 6.2 Update test file `verify_pdf_charts.py`

    - Change reference from `nt_nt_06.pdf` to `nt_nt_07.pdf` (storage donuts moved from page 6 to 7)
    - Update function call from `_draw_page6_storage_donuts` to `_draw_page7_storage_donuts`
    - _Requirements: 3.1, 5.1, 5.2_
  
  - [x] 6.3 Update test file `debug_seite6_problem.py`

    - Change reference from `seite6.yml` to `seite7.yml`
    - Change reference from `nt_nt_06.pdf` to `nt_nt_07.pdf`
    - Update comments referencing page 6 to page 7
    - _Requirements: 4.1, 4.2, 5.1, 5.2_
  
  - [x] 6.4 Update test file `debug_pdf_charts_complete.py`

    - Change reference from `nt_nt_06.pdf` to `nt_nt_07.pdf`
    - Update function call from `_draw_page6_storage_donuts` to `_draw_page7_storage_donuts`
    - Update comments
    - _Requirements: 3.1, 5.1, 5.2_
  
  - [x] 6.5 Update test file `direct_chart_test.py`

    - Change reference from `nt_nt_06.pdf` to `nt_nt_07.pdf`
    - Update comments
    - _Requirements: 5.1, 5.2_
  
  - [x] 6.6 Update debug file `debug_logo_pdf.py`

    - Change reference from `nt_nt_04.pdf` to `nt_nt_05.pdf` (component images moved from page 4 to 5)
    - Update comments
    - _Requirements: 5.1, 5.2_
  
  - [x] 6.7 Update documentation comments in `pdf_generator.py`

    - Locate comment around line 2023: "seite1.yml … seite6.yml"
    - Update to: "seite1.yml … seite8.yml"
    - _Requirements: 9.1, 9.2, 9.3_
- [x] 7. Add file validation and error handling

- [ ] 7. Add file validation and error handling

  - [x] 7.1 Create `validate_page_files()` function in `dynamic_overlay.py`

    - Implement function to check if YML and PDF files exist for a given page
    - Return tuple of (is_valid, missing_files)
    - Support both normal and heatpump variants
    - _Requirements: 7.1, 7.2_
  
  - [x] 7.2 Add validation call before PDF generation

    - Call `validate_page_files()` for all pages 1-8 before starting generation
    - Log warnings for missing files
    - Provide clear error messages
    - _Requirements: 7.1, 7.2, 7.4_
  
  - [x] 7.3 Add graceful degradation for missing files

    - If page 8 files are missing, fall back to 7 pages
    - Log warning about fallback
    - Continue generation with available pages
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 8. Update page numbering and footer logic

  - [x] 8.1 Search for footer/header generation code

    - Locate code that generates "Seite X" text in footers
    - Identify maximum page number references
    - _Requirements: 6.1, 6.2_
  
  - [x] 8.2 Update maximum page number from 7 to 8

    - Change any hardcoded max page references
    - Update footer generation to support page 8
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 8.3 Verify page numbering displays correctly

    - Ensure footer shows "Seite 1" through "Seite 8"
    - Check that page numbers are sequential
    - _Requirements: 6.1, 6.2, 6.5_

- [x] 9. Create comprehensive test suite

  - [x] 9.1 Create test for 8-page PDF generation

    - Write test function `test_generate_8_page_pdf()`
    - Generate PDF with test data
    - Verify PDF has exactly 8 pages
    - _Requirements: 8.1, 8.2_
  
  - [x] 9.2 Create test for page-specific content placement

    - Write test function `test_page_content_placement()`
    - Verify new page 1 has new content
    - Verify page 2 has old page 1 content (e.g., "IHR PERSÖNLICHES ANGEBOT")
    - Verify page 4 has waterfall chart (old page 3)
    - Verify page 7 has storage donuts (old page 6)
    - _Requirements: 8.1, 8.3, 8.4_
  
  - [x] 9.3 Create test for file existence

    - Write test function `test_all_page_files_exist()`
    - Verify all seite1.yml through seite8.yml exist
    - Verify all nt_nt_01.pdf through nt_nt_08.pdf exist
    - Verify all wp_seite1.yml through wp_seite8.yml exist
    - Verify all hp_nt_01.pdf through hp_nt_08.pdf exist
    - _Requirements: 8.1, 8.5_
  
  - [x] 9.4 Create test for function renaming

    - Write test function `test_renamed_functions_exist()`
    - Verify all new function names exist in module
    - Verify functions can be called without errors
    - _Requirements: 8.1, 8.5_
-

- [x] 10. Manual testing and validation

  - [-] 10.1 Generate test PDF with real data

    - Use actual calculation data from the app
    - Generate 8-page PDF
    - Save to test output directory
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [x] 10.2 Visual inspection of all 8 pages

    - Open generated PDF in viewer
    - Verify page 1 shows new content (or placeholder)
    - Verify page 2 shows old page 1 content
    - Verify page 3 shows old page 2 content
    - Verify page 4 shows waterfall chart (old page 3)
    - Verify page 5 shows component images (old page 4)
    - Verify page 6 shows old page 5 content
    - Verify page 7 shows storage donuts (old page 6)
    - Verify page 8 shows old page 7 content
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [x] 10.3 Verify text alignment and coordinates

    - Check that all text overlays align correctly with templates
    - Verify no text is cut off or misplaced
    - Check that coordinates from YML files are applied correctly
    - _Requirements: 8.3, 10.1, 10.5_
  
  - [x] 10.4 Verify charts and graphics

    - Check waterfall chart on page 4 renders correctly
    - Check donut charts on page 2 render correctly
    - Check storage donuts on page 7 render correctly
    - Check component images on page 5 render correctly
    - Check brand logos on page 5 render correctly
    - _Requirements: 8.3, 10.2, 10.3, 10.4_
  
  - [ ] 10.5 Test heatpump variant
    - Generate 8-page PDF with heatpump mode enabled
    - Verify it uses hp_nt_XX.pdf templates
    - Verify it uses wp_seiteX.yml coordinates
    - Verify all 8 pages render correctly
    - _Requirements: 2.5, 8.1, 8.2_

- [ ] 11. Documentation and cleanup
  - [ ] 11.1 Add migration comments to all modified functions
    - Add `# MIGRATION: 7→8 pages` comments
    - Document old vs new page numbers
    - Add date of migration
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ] 11.2 Update module docstrings

    - Update `dynamic_overlay.py` module docstring from "sieben" to "acht" pages
    - Update `merger.py` module docstring
    - _Requirements: 9.1, 9.2_
  
  - [ ] 11.3 Create migration summary document
    - Document all changed files
    - Document all renamed functions
    - Document page number mapping (old → new)
    - Document testing results
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ] 11.4 Mark deprecated functions
    - Add deprecation warnings to old function names (if kept)
    - Add comments explaining why they're deprecated
    - Document replacement functions
    - _Requirements: 9.1, 9.2, 9.4_

- [ ] 12. Final verification and sign-off
  - [ ] 12.1 Run all automated tests
    - Execute unit tests
    - Execute integration tests
    - Verify all tests pass
    - _Requirements: 8.1, 8.5_
  
  - [ ] 12.2 Generate multiple test PDFs with different data
    - Test with minimal data
    - Test with maximum data
    - Test with edge cases
    - Verify all generate correctly with 8 pages
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [ ] 12.3 Verify no functionality loss
    - Compare old 7-page PDF with new 8-page PDF (pages 2-8)
    - Verify all content from old pages 1-7 appears on new pages 2-8
    - Verify no text is missing
    - Verify no graphics are missing
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 12.4 Performance check
    - Measure PDF generation time for 8 pages
    - Compare with 7-page generation time
    - Verify performance is acceptable (should be similar)
    - _Requirements: 8.1_
  
  - [ ] 12.5 Create before/after comparison
    - Generate side-by-side comparison of old vs new PDFs
    - Document differences
    - Verify all differences are intentional (new page 1)
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

---

## Notes

- **Critical:** All page-specific functions must be renamed systematically to avoid confusion
- **Important:** Test files referencing specific pages must be updated to match new page numbers
- **Reminder:** User has already prepared all YML and PDF template files - no file creation needed
- **Safety:** Keep old function names initially with deprecation warnings for easier rollback
- **Validation:** Always verify file existence before attempting to load templates or coordinates
