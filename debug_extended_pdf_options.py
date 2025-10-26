"""
Debug script to trace extended PDF options flow
"""
import base64
import io

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Create a fake 8-page base PDF
buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=A4)
for i in range(1, 9):
    c.drawString(100, 750, f"Base PDF - Page {i}")
    c.showPage()
c.save()
base_pdf_bytes = buffer.getvalue()

print("=" * 60)
print("Debugging Extended PDF Options Flow")
print("=" * 60)

# Simulate the options that would come from the UI
inclusion_options = {
    'extended_output_enabled': True,
    'extended_options': {
        'financing_details': True,
        'product_datasheets': [1, 2],  # Fake product IDs
        'company_documents': [1],  # Fake document ID
        'selected_charts': ['monthly_prod_cons_chart_bytes', 'cumulative_cashflow_chart_bytes'],
        'chart_layout': 'two_per_page'
    }
}

print("\n1. Inclusion Options:")
print(
    f"   extended_output_enabled: {
        inclusion_options.get('extended_output_enabled')}")
print(f"   extended_options: {inclusion_options.get('extended_options')}")

# Test project data with real charts
test_project_data = {
    'grand_total': 25000.0,
    'customer_name': 'Test Customer'
}

# Create fake chart bytes (valid PNG)

# 1x1 transparent PNG
fake_png = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
)

test_analysis_results = {
    'monthly_prod_cons_chart_bytes': fake_png,
    'cumulative_cashflow_chart_bytes': fake_png
}

print("\n2. Analysis Results:")
print(f"   Charts available: {list(test_analysis_results.keys())}")

# Test the merge function
print("\n3. Testing _merge_extended_pdf_pages...")
try:
    from pdf_generator import _merge_extended_pdf_pages

    merged_pdf_bytes = _merge_extended_pdf_pages(
        base_pdf_bytes,
        test_project_data,
        test_analysis_results,
        inclusion_options['extended_options'],
        {}
    )

    print(f"   ✓ Merged PDF: {len(merged_pdf_bytes)} bytes")

    # Check page count
    merged_reader = PdfReader(io.BytesIO(merged_pdf_bytes))
    merged_page_count = len(merged_reader.pages)
    print(f"   ✓ Merged PDF has {merged_page_count} pages")

    if merged_page_count > 8:
        print(
            f"   ✓ SUCCESS: Extended pages were added! ({
                merged_page_count -
                8} additional pages)")
    else:
        print(
            f"   ⚠ WARNING: No extended pages added (still {merged_page_count} pages)")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug completed")
print("=" * 60)
