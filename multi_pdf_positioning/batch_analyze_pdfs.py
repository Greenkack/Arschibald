"""
Batch PDF Analysis Script

This script analyzes all 48 PDF templates and saves the results.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer
from multi_pdf_positioning.config import PDF_DIR, ANALYSIS_DIR, FIRMEN, SEITEN


def main():
    """Run batch analysis of all PDFs."""
    print("=" * 60)
    print("Multi-PDF Positioning System - Batch PDF Analysis")
    print("=" * 60)

    # Initialize analyzer
    analyzer = PDFAnalyzer(pdf_dir=str(PDF_DIR))

    # Analyze all PDFs
    try:
        analyzer.analyze_all_pdfs(
            firmen=FIRMEN,
            seiten=SEITEN
        )

        print(f"\n{'=' * 60}")
        print("Analysis Summary")
        print("=" * 60)

        # Display summary by firma
        for firma in FIRMEN:
            firma_analyses = analyzer.get_analysis_by_firma(firma)
            if firma_analyses:
                print(f"\nFirma {firma}:")
                print(f"  PDFs analyzed: {len(firma_analyses)}")
                print(f"  Color palette: {firma_analyses[0].color_palette}")

                # Calculate average safe zone area
                total_area = 0
                for analysis in firma_analyses:
                    for zone in analysis.safe_zones:
                        area = (zone.x2 - zone.x1) * (zone.y2 - zone.y1)
                        total_area += area

                avg_area = total_area / len(firma_analyses)
                print(f"  Avg safe zone area: {avg_area:.1f} sq points")

        # Save results
        output_file = ANALYSIS_DIR / "pdf_analysis.json"
        analyzer.save_analysis_results(
            str(output_file),
            include_summary=True
        )

        print(f"\n{'=' * 60}")
        print("Batch analysis complete!")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\nError during batch analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
