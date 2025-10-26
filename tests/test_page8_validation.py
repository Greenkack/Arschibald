"""Test script to verify that page 8 files are correctly detected."""

from pdf_template_engine.dynamic_overlay import validate_page_files
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_validation():
    """Test that all 8 pages validate correctly."""
    coords_dir = Path("coords")
    template_dir = Path("pdf_templates_static/notext")

    print("Testing page file validation for 8 pages:\n")

    all_valid = True
    for page_num in range(1, 9):
        is_valid, missing_files = validate_page_files(
            page_num, coords_dir, template_dir)
        status = "✓ OK" if is_valid else "✗ MISSING"
        print(f"Page {page_num}: {status}")
        if not is_valid:
            all_valid = False
            for missing in missing_files:
                print(f"  - Missing: {missing}")

    print(f"\n{'=' * 50}")
    if all_valid:
        print("✓ All 8 pages have required files!")
        print("  The system should generate 8 pages by default.")
    else:
        print("✗ Some files are missing!")
        print("  The system will fall back to 7 pages.")
    print(f"{'=' * 50}\n")

    return all_valid


if __name__ == "__main__":
    success = test_validation()
    sys.exit(0 if success else 1)
