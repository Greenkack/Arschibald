# Task 6.1: Firmendokumente laden - Verification Guide

## Quick Verification Checklist

Use this guide to quickly verify that Task 6.1 is correctly implemented.

### ✅ Code Verification

#### 1. Check Function Signature

**Location:** `pdf_generator.py`, line ~5042

```python
def _append_datasheets_and_documents(
    main_pdf_bytes: bytes,
    pv_details: dict[str, Any],
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable | None,  # ✓ Parameter exists
    active_company_id: int | None,                     # ✓ Parameter exists
    company_document_ids_to_include: list[int] | None, # ✓ Parameter exists
    include_additional_components: bool = True
) -> bytes:
```

**Verify:**

- ✅ `db_list_company_documents_func` parameter exists
- ✅ `active_company_id` parameter exists
- ✅ `company_document_ids_to_include` parameter exists

#### 2. Check Conditional Logic

**Location:** `pdf_generator.py`, line ~5202

```python
if company_document_ids_to_include and active_company_id is not None and callable(db_list_company_documents_func):
```

**Verify:**

- ✅ Checks `company_document_ids_to_include` is not empty
- ✅ Checks `active_company_id is not None`
- ✅ Checks `callable(db_list_company_documents_func)`

#### 3. Check Database Function Call

**Location:** `pdf_generator.py`, lines ~5205-5208

```python
all_company_docs_for_active_co = db_list_company_documents_func(
    active_company_id,  # ✓ First parameter
    None                # ✓ Second parameter (all doc types)
)
```

**Verify:**

- ✅ Function called with `active_company_id`
- ✅ Function called with `None` for doc_type

#### 4. Check Filtering Logic

**Location:** `pdf_generator.py`, lines ~5211-5212

```python
for doc_info in all_company_docs_for_active_co:
    if doc_info.get('id') in company_document_ids_to_include:
```

**Verify:**

- ✅ Iterates through all documents
- ✅ Filters by ID in `company_document_ids_to_include`

#### 5. Check Error Handling

**Location:** `pdf_generator.py`, lines ~5203-5258

```python
try:
    # Load and process documents
    ...
except Exception as e_company_docs:
    logging.error(f"Fehler beim Laden der Firmendokumente: {e_company_docs}")
```

**Verify:**

- ✅ Try-except block wraps entire logic
- ✅ Errors are logged
- ✅ Execution continues on error

### ✅ Test Verification

#### Run Test Suite

```bash
python tests/test_task_6_1_company_documents_loading.py
```

**Expected Output:**

```
================================================================================
TASK 6.1: FIRMENDOKUMENTE LADEN - TEST SUITE
================================================================================
...
Ran 7 tests in X.XXXs

OK

✓ ALLE TESTS BESTANDEN!
✓ Task 6.1 ist vollständig implementiert und funktioniert korrekt
```

**Verify:**

- ✅ All 7 tests pass
- ✅ No failures
- ✅ No errors

#### Individual Test Verification

1. **test_requirement_6_1_active_company_id_extracted**
   - ✅ Verifies `active_company_id` is used correctly
   - ✅ Verifies function called with correct ID

2. **test_requirement_6_2_no_company_id_no_loading**
   - ✅ Verifies no loading when `active_company_id=None`
   - ✅ Verifies function not called

3. **test_requirement_6_3_empty_doc_ids_no_loading**
   - ✅ Verifies no loading when list empty
   - ✅ Verifies no loading when list is None

4. **test_requirement_6_4_db_function_called_correctly**
   - ✅ Verifies correct parameters
   - ✅ Verifies `doc_type=None`

5. **test_requirement_6_5_filter_by_ids**
   - ✅ Verifies only selected docs processed
   - ✅ Verifies filtering works correctly

6. **test_requirement_6_14_no_callable_function**
   - ✅ Verifies no errors when function not callable
   - ✅ Verifies PDF returned

7. **test_integration_all_conditions_met**
   - ✅ Verifies complete flow
   - ✅ Verifies all conditions work together

### ✅ Functional Verification

#### Test Scenario 1: Normal Operation

**Setup:**

- `active_company_id = 123`
- `company_document_ids_to_include = [1, 2, 3]`
- `db_list_company_documents_func` returns 3 documents

**Expected Behavior:**

1. ✅ Function is called with company_id=123
2. ✅ All 3 documents are processed
3. ✅ Paths are checked for existence
4. ✅ Valid documents added to PDF

**Verification:**

```python
# Check logging output
INFO:root:Firmendokument gefunden: Doc 1 -> /path/to/doc1.pdf
INFO:root:Firmendokument gefunden: Doc 2 -> /path/to/doc2.pdf
INFO:root:Firmendokument gefunden: Doc 3 -> /path/to/doc3.pdf
```

#### Test Scenario 2: No Company ID

**Setup:**

- `active_company_id = None`
- `company_document_ids_to_include = [1, 2, 3]`

**Expected Behavior:**

1. ✅ Condition check fails
2. ✅ Function is NOT called
3. ✅ No documents processed
4. ✅ No errors thrown

**Verification:**

```python
# db_list_company_documents_func should NOT be called
mock_func.assert_not_called()
```

#### Test Scenario 3: Empty Document List

**Setup:**

- `active_company_id = 123`
- `company_document_ids_to_include = []`

**Expected Behavior:**

1. ✅ Condition check fails
2. ✅ Function is NOT called
3. ✅ No documents processed
4. ✅ No errors thrown

**Verification:**

```python
# db_list_company_documents_func should NOT be called
mock_func.assert_not_called()
```

#### Test Scenario 4: Filtering

**Setup:**

- `active_company_id = 123`
- `company_document_ids_to_include = [1, 3]`
- Database returns 4 documents (IDs: 1, 2, 3, 4)

**Expected Behavior:**

1. ✅ Function is called
2. ✅ Only documents 1 and 3 are processed
3. ✅ Documents 2 and 4 are skipped
4. ✅ No errors thrown

**Verification:**

```python
# Check logging output - should only see Doc 1 and Doc 3
INFO:root:Firmendokument gefunden: Doc 1 -> /path/to/doc1.pdf
INFO:root:Firmendokument gefunden: Doc 3 -> /path/to/doc3.pdf
# Doc 2 and Doc 4 should NOT appear
```

### ✅ Integration Verification

#### Check Integration with generate_offer_pdf()

**Location:** `pdf_generator.py`, lines ~5024-5040

```python
if include_all_documents_opt and _PYPDF_AVAILABLE:
    logging.info("Anhängen von Produktdatenblättern und Firmendokumenten...")
    main_pdf_bytes = _append_datasheets_and_documents(
        main_pdf_bytes=main_pdf_bytes,
        pv_details=pv_details_pdf,
        get_product_by_id_func=get_product_by_id_func,
        db_list_company_documents_func=db_list_company_documents_func,
        active_company_id=active_company_id,
        company_document_ids_to_include=company_document_ids_to_include,
        include_additional_components=include_all_documents_opt
    )
```

**Verify:**

- ✅ Function is called from `generate_offer_pdf()`
- ✅ All required parameters are passed
- ✅ `active_company_id` is passed correctly
- ✅ `company_document_ids_to_include` is passed correctly
- ✅ `db_list_company_documents_func` is passed correctly

### ✅ Requirements Verification Matrix

| Requirement | Description | Status | Test |
|------------|-------------|--------|------|
| 6.1 | active_company_id extrahieren | ✅ | test_requirement_6_1 |
| 6.2 | Keine Dokumente wenn keine ID | ✅ | test_requirement_6_2 |
| 6.3 | Keine Dokumente wenn Liste leer | ✅ | test_requirement_6_3 |
| 6.4 | db_list_company_documents_func aufrufen | ✅ | test_requirement_6_4 |
| 6.5 | Nur ausgewählte IDs filtern | ✅ | test_requirement_6_5 |
| 6.14 | Keine Dokumente wenn nicht callable | ✅ | test_requirement_6_14 |

### ✅ Debug Output Verification

When running with company documents, you should see:

```
================================================================================
DEBUG: _append_datasheets_and_documents
================================================================================
Produktdatenblätter gefunden: X
  - ID X: Model Name -> /path/to/datasheet.pdf
Produktdatenblätter fehlend: Y
  - ID Y: Model Name -> Reason
Firmendokumente gefunden: Z
  - ID Z: Document Name -> /path/to/document.pdf
Firmendokumente fehlend: W
  - ID W: Document Name -> Reason
Gesamt anzuhängen: N
================================================================================
```

**Verify:**

- ✅ "Firmendokumente gefunden" section appears
- ✅ Document IDs are listed
- ✅ Document names are shown
- ✅ Paths are displayed
- ✅ Missing documents are logged with reasons

### ✅ Common Issues and Solutions

#### Issue 1: Function Not Called

**Symptom:** `db_list_company_documents_func` is never called

**Check:**

1. Is `active_company_id` not None?
2. Is `company_document_ids_to_include` not empty?
3. Is `db_list_company_documents_func` callable?

**Solution:** Ensure all three conditions are met

#### Issue 2: No Documents Processed

**Symptom:** Documents returned from DB but not processed

**Check:**

1. Are document IDs in `company_document_ids_to_include`?
2. Do documents have `relative_db_path` field?
3. Do file paths exist?

**Solution:** Verify filtering logic and path construction

#### Issue 3: Errors During Loading

**Symptom:** Exceptions thrown during document loading

**Check:**

1. Is try-except block in place?
2. Are errors being logged?
3. Does execution continue after error?

**Solution:** Verify error handling is working correctly

## Final Verification Checklist

Before marking task as complete, verify:

- ✅ All code changes are in place
- ✅ All 7 tests pass
- ✅ All 6 requirements are met
- ✅ Error handling is implemented
- ✅ Logging is working
- ✅ Integration with main function works
- ✅ Documentation is complete

## Conclusion

Task 6.1 "Firmendokumente laden" is **COMPLETE** ✅

All requirements have been implemented, tested, and verified.
