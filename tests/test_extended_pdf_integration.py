"""
Test script to verify extended PDF generation integration
"""
import io
from pypdf import PdfReader

# Test data
test_offer_data = {
    'grand_total': 25000.0,
    'customer_name': 'Test Customer'
}

test_analysis_results = {
    'monthly_prod_cons_chart_bytes': b'fake_chart_data_1',
    'cumulative_cashflow_chart_bytes': b'fake_chart_data_2'
}

test_options = {
    'financing_details': True,
    'product_datasheets': [],
    'company_documents': [],
    'selected_charts': ['monthly_prod_cons_chart_bytes'],
    'chart_layout': 'one_per_page'
}

print("=" * 60)
print("Testing Extended PDF Generator")
print("=" * 60)

# Test 1: Import modules
print("\n1. Testing module imports...")
try:
    from extended_pdf_generator import ExtendedPDFGenerator, ExtendedPDFLogger
    print("   ✓ Modules imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test 2: Create logger
print("\n2. Creating logger...")
try:
    logger = ExtendedPDFLogger()
    print("   ✓ Logger created")
except Exception as e:
    print(f"   ✗ Logger creation failed: {e}")
    exit(1)

# Test 3: Create generator
print("\n3. Creating ExtendedPDFGenerator...")
try:
    generator = ExtendedPDFGenerator(
        offer_data=test_offer_data,
        analysis_results=test_analysis_results,
        options=test_options,
        logger=logger
    )
    print("   ✓ Generator created")
except Exception as e:
    print(f"   ✗ Generator creation failed: {e}")
    exit(1)

# Test 4: Generate extended pages
print("\n4. Generating extended pages...")
try:
    extended_bytes = generator.generate_extended_pages()
    print(f"   ✓ Extended pages generated: {len(extended_bytes)} bytes")

    if extended_bytes:
        # Check if it's a valid PDF
        try:
            reader = PdfReader(io.BytesIO(extended_bytes))
            page_count = len(reader.pages)
            print(f"   ✓ Valid PDF with {page_count} pages")
        except Exception as e:
            print(f"   ✗ Invalid PDF: {e}")
    else:
        print("   ⚠ No extended pages generated (empty bytes)")

except Exception as e:
    print(f"   ✗ Generation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check logger
print("\n5. Checking logger summary...")
try:
    summary = logger.get_summary()
    print(f"   Errors: {summary['error_count']}")
    print(f"   Warnings: {summary['warning_count']}")
    print(f"   Info: {summary['info_count']}")

    if summary['has_errors']:
        print("\n   Errors:")
        for error in summary['errors']:
            print(f"     - [{error['component']}] {error['message']}")

    if summary['has_warnings']:
        print("\n   Warnings:")
        for warning in summary['warnings']:
            print(f"     - [{warning['component']}] {warning['message']}")

except Exception as e:
    print(f"   ✗ Logger check failed: {e}")

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)
