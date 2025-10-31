"""Test script to verify that 8-page PDF generation works correctly."""

from pypdf import PdfReader
from pdf_template_engine.merger import merge_first_eight_pages
from pdf_template_engine.dynamic_overlay import generate_overlay
from pathlib import Path
import sys
import io

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_8_page_generation():
    """Test that the system generates 8 pages."""
    print("Testing 8-page PDF generation:\n")

    # Minimal test data
    test_data = {
        "company_name": "Test Company",
        "customer_name": "Test Customer",
        "date": "2025-01-08",
    }

    coords_dir = Path("coords")

    try:
        # Generate overlay for 8 pages
        print("1. Generating overlay for 8 pages...")
        overlay_bytes = generate_overlay(coords_dir, test_data, total_pages=8)

        # Check overlay page count
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
        overlay_page_count = len(overlay_reader.pages)
        print(f"   ✓ Overlay generated with {overlay_page_count} pages")

        if overlay_page_count != 8:
            print(f"   ✗ ERROR: Expected 8 pages, got {overlay_page_count}")
            return False

        # Merge with backgrounds
        print("\n2. Merging with background templates...")
        final_pdf_bytes = merge_first_eight_pages(overlay_bytes)

        # Check final page count
        final_reader = PdfReader(io.BytesIO(final_pdf_bytes))
        final_page_count = len(final_reader.pages)
        print(f"   ✓ Final PDF generated with {final_page_count} pages")

        if final_page_count != 8:
            print(f"   ✗ ERROR: Expected 8 pages, got {final_page_count}")
            return False

        # Save test PDF
        output_path = Path("test_8_pages_output.pdf")
        with open(output_path, "wb") as f:
            f.write(final_pdf_bytes)
        print(f"\n3. Test PDF saved to: {output_path}")

        print(f"\n{'=' * 50}")
        print("✓ SUCCESS: 8-page PDF generation works correctly!")
        print(f"{'=' * 50}\n")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_8_page_generation()
    sys.exit(0 if success else 1)
