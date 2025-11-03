"""
Test the full extended PDF flow from pdf_generator.py
"""
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

print("=" * 60)
print("Testing Full Extended PDF Flow")
print("=" * 60)

# Step 1: Create a fake 8-page base PDF
print("\n1. Creating fake 8-page base PDF...")
buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=A4)
for i in range(1, 9):
    c.drawString(100, 750, f"Base PDF - Page {i}")
    c.showPage()
c.save()
base_pdf_bytes = buffer.getvalue()
print(f"   ✓ Created base PDF: {len(base_pdf_bytes)} bytes")

# Verify base PDF
reader = PdfReader(io.BytesIO(base_pdf_bytes))
print(f"   ✓ Base PDF has {len(reader.pages)} pages")

# Step 2: Test _merge_extended_pdf_pages function
print("\n2. Testing _merge_extended_pdf_pages...")

test_project_data = {
    'grand_total': 25000.0,
    'customer_name': 'Test Customer'
}

test_analysis_results = {}

test_extended_options = {
    'financing_details': True,
    'product_datasheets': [],
    'company_documents': [],
    'selected_charts': [],
    'chart_layout': 'one_per_page'
}

test_texts = {}

try:
    from pdf_generator import _merge_extended_pdf_pages
    
    merged_pdf_bytes = _merge_extended_pdf_pages(
        base_pdf_bytes,
        test_project_data,
        test_analysis_results,
        test_extended_options,
        test_texts
    )
    
    print(f"   ✓ Merged PDF: {len(merged_pdf_bytes)} bytes")
    
    # Check page count
    merged_reader = PdfReader(io.BytesIO(merged_pdf_bytes))
    merged_page_count = len(merged_reader.pages)
    print(f"   ✓ Merged PDF has {merged_page_count} pages")
    
    if merged_page_count > 8:
        print(f"   ✓ SUCCESS: Extended pages were added! ({merged_page_count - 8} additional pages)")
    else:
        print(f"   ⚠ WARNING: No extended pages added (still {merged_page_count} pages)")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 3: Test with actual extended options
print("\n3. Testing with extended options enabled...")

test_extended_options_full = {
    'financing_details': True,
    'product_datasheets': [],
    'company_documents': [],
    'selected_charts': [],
    'chart_layout': 'two_per_page'
}

try:
    merged_pdf_bytes_full = _merge_extended_pdf_pages(
        base_pdf_bytes,
        test_project_data,
        test_analysis_results,
        test_extended_options_full,
        test_texts
    )
    
    merged_reader_full = PdfReader(io.BytesIO(merged_pdf_bytes_full))
    merged_page_count_full = len(merged_reader_full.pages)
    print(f"   ✓ Merged PDF has {merged_page_count_full} pages")
    
    if merged_page_count_full > 8:
        print(f"   ✓ SUCCESS: Extended pages were added! ({merged_page_count_full - 8} additional pages)")
    else:
        print(f"   ⚠ WARNING: No extended pages added (still {merged_page_count_full} pages)")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)
