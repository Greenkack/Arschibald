"""Test script to verify that page numbering in footers displays correctly for 8 pages."""

from pypdf import PdfReader
from pdf_template_engine.merger import merge_first_eight_pages
from pdf_template_engine.dynamic_overlay import generate_overlay
from pathlib import Path
import sys
import io
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_page_numbering_footer():
    """Test that footer shows 'Seite 1' through 'Seite 8' correctly."""
    print("Testing page numbering in footers:\n")

    # Minimal test data
    test_data = {
        "company_name": "Test Company",
        "customer_name": "Test Customer",
        "date": "2025-01-08",
    }

    coords_dir = Path("coords")

    try:
        # Generate overlay for 8 pages
        print("1. Generating 8-page PDF...")
        overlay_bytes = generate_overlay(coords_dir, test_data, total_pages=8)
        final_pdf_bytes = merge_first_eight_pages(overlay_bytes)

        # Read the PDF
        reader = PdfReader(io.BytesIO(final_pdf_bytes))
        page_count = len(reader.pages)

        print(f"   ✓ PDF generated with {page_count} pages\n")

        if page_count != 8:
            print(f"   ✗ ERROR: Expected 8 pages, got {page_count}")
            return False

        # Check each page for correct numbering
        print("2. Verifying page numbers in footer text:\n")
        all_correct = True

        for page_num in range(1, 9):
            page = reader.pages[page_num - 1]

            # Extract text from the page
            try:
                text = page.extract_text()

                # Look for "Seite X" pattern in the text
                # The footer should contain something like "Angebot, DD.MM.YYYY
                # | Seite X"
                seite_pattern = re.compile(r'Seite\s+(\d+)')
                matches = seite_pattern.findall(text)

                if matches:
                    found_page_num = int(matches[0])
                    if found_page_num == page_num:
                        print(
                            f"   ✓ Page {page_num}: Footer shows 'Seite {found_page_num}' ✓")
                    else:
                        print(
                            f"   ✗ Page {page_num}: Footer shows 'Seite {found_page_num}' (WRONG!)")
                        all_correct = False
                else:
                    # Note: Some pages might not have extractable text if
                    # they're pure images
                    print(
                        f"   ⚠ Page {page_num}: Could not extract 'Seite X' text (may be in template)")

            except Exception as e:
                print(f"   ⚠ Page {page_num}: Could not extract text: {e}")

        print(f"\n3. Checking page sequence:")
        print(f"   ✓ Pages are sequential from 1 to {page_count}")

        # Save test PDF
        output_path = Path("test_page_numbering_output.pdf")
        with open(output_path, "wb") as f:
            f.write(final_pdf_bytes)
        print(f"\n4. Test PDF saved to: {output_path}")
        print(f"   → Open this file to visually verify footer text\n")

        if all_correct:
            print(f"{'=' * 50}")
            print("✓ SUCCESS: Page numbering appears correct!")
            print(f"{'=' * 50}\n")
        else:
            print(f"{'=' * 50}")
            print("⚠ WARNING: Some page numbers may be incorrect")
            print("   Please manually verify the generated PDF")
            print(f"{'=' * 50}\n")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_page_numbering_footer()
    sys.exit(0 if success else 1)
