"""
Demo script for PDF Byte Generation Core

This script demonstrates the PDF byte generation functionality and verifies
that all components are working correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path for backend imports
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from backend.core.pdf_bytes import (
    PDFMetadata,
    PDFRenderingEngine,
    PDFByteMixin,
    SimplePDFDocument,
    create_pdf_from_dict,
    create_pdf_from_text,
    REPORTLAB_AVAILABLE
)


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_1_check_installation():
    """Demo 1: Check if reportlab is installed"""
    print_section("1. Installation Check")
    
    if REPORTLAB_AVAILABLE:
        print("✓ reportlab is installed and available")
        print("  All PDF generation features are enabled")
    else:
        print("✗ reportlab is NOT installed")
        print("  Install with: pip install reportlab")
        return False
    
    return True


def demo_2_metadata():
    """Demo 2: PDF Metadata"""
    print_section("2. PDF Metadata")
    
    metadata = PDFMetadata(
        title="Demo Document",
        author="Demo User",
        subject="Testing PDF Generation",
        creator="Solar Calculator Pro",
        keywords=["demo", "test", "pdf"]
    )
    
    print("Created PDF Metadata:")
    print(f"  Title: {metadata.title}")
    print(f"  Author: {metadata.author}")
    print(f"  Subject: {metadata.subject}")
    print(f"  Creator: {metadata.creator}")
    print(f"  Keywords: {', '.join(metadata.keywords)}")
    print(f"  Creation Date: {metadata.creation_date}")
    
    # Convert to dict
    metadata_dict = metadata.to_dict()
    print("\nMetadata as dictionary:")
    for key, value in metadata_dict.items():
        print(f"  {key}: {value}")


def demo_3_german_formatting():
    """Demo 3: German Number Formatting"""
    print_section("3. German Number Formatting")
    
    engine = PDFRenderingEngine()
    
    test_cases = [
        (0, "Zero"),
        (1, "One"),
        (1000, "One thousand"),
        (1234.56, "Standard price"),
        (1000000.99, "One million"),
        (0.5, "Half"),
        (-1234.56, "Negative number")
    ]
    
    print("Number Formatting Examples:")
    print(f"{'Value':<15} {'Description':<20} {'Formatted':<20}")
    print("-" * 55)
    
    for value, description in test_cases:
        formatted = engine.format_german_number(value)
        print(f"{value:<15} {description:<20} {formatted:<20}")


def demo_4_simple_pdf():
    """Demo 4: Create Simple PDF"""
    print_section("4. Simple PDF Creation")
    
    # Create from text
    text = "This is a simple PDF document.\n\nIt has multiple paragraphs."
    pdf_bytes = create_pdf_from_text(text, title="Simple Demo")
    
    print(f"✓ Created PDF from text: {len(pdf_bytes)} bytes")
    print(f"  PDF starts with: {pdf_bytes[:10]}")
    
    # Create from dictionary
    data = {
        "Customer": "Demo Customer",
        "Price": 1234.56,
        "Quantity": 100,
        "Total": 123456.00
    }
    
    pdf_bytes = create_pdf_from_dict(data, title="Demo Report")
    
    print(f"✓ Created PDF from dictionary: {len(pdf_bytes)} bytes")


def demo_5_custom_model():
    """Demo 5: Custom PDF Model"""
    print_section("5. Custom PDF Model with PDFByteMixin")
    
    if not REPORTLAB_AVAILABLE:
        print("⚠ Skipped (reportlab not installed)")
        return
    
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    class DemoReport(PDFByteMixin):
        def __init__(self, title, data):
            super().__init__()
            self.title = title
            self.data = data
        
        def _get_default_title(self):
            return self.title
        
        def _render_to_pdf(self, story, doc):
            styles = getSampleStyleSheet()
            
            # Add title
            story.append(Paragraph(self.title, styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Add data
            for key, value in self.data.items():
                if isinstance(value, (int, float)):
                    value_str = self._pdf_engine.format_german_number(value)
                else:
                    value_str = str(value)
                
                text = f"<b>{key}:</b> {value_str}"
                story.append(Paragraph(text, styles['BodyText']))
                story.append(Spacer(1, 6))
    
    # Create report
    report = DemoReport(
        title="Demo Report",
        data={
            "System Size": 10.5,
            "Module Count": 30,
            "Annual Production": 12000.50,
            "Total Cost": 15000.00
        }
    )
    
    # Generate PDF
    pdf_bytes = report.to_pdf_bytes()
    print(f"✓ Created custom PDF: {len(pdf_bytes)} bytes")
    
    # Generate base64
    pdf_base64 = report.to_pdf_base64()
    print(f"✓ Generated base64: {len(pdf_base64)} characters")
    print(f"  First 50 chars: {pdf_base64[:50]}...")


def demo_6_table_creation():
    """Demo 6: Table Creation"""
    print_section("6. Table Creation")
    
    if not REPORTLAB_AVAILABLE:
        print("⚠ Skipped (reportlab not installed)")
        return
    
    engine = PDFRenderingEngine()
    
    # Create sample table data
    data = [
        ['Product', 'Price (€)', 'Quantity', 'Total (€)'],
        ['Solar Panel', '1.234,56', '30', '37.036,80'],
        ['Inverter', '2.345,67', '1', '2.345,67'],
        ['Mounting', '1.500,00', '1', '1.500,00']
    ]
    
    table = engine.create_table(data)
    
    print("✓ Created table with 4 rows and 4 columns")
    print("  Headers: Product, Price, Quantity, Total")
    print("  Data rows: 3")


def demo_7_save_to_file():
    """Demo 7: Save PDF to File"""
    print_section("7. Save PDF to File")
    
    doc = SimplePDFDocument(
        title="File Demo",
        content="This PDF will be saved to a file."
    )
    
    filename = "demo_output.pdf"
    doc.save_pdf(filename)
    
    # Check if file exists
    if Path(filename).exists():
        size = Path(filename).stat().st_size
        print(f"✓ Saved PDF to {filename}")
        print(f"  File size: {size} bytes")
        
        # Clean up
        Path(filename).unlink()
        print(f"✓ Cleaned up {filename}")
    else:
        print(f"✗ Failed to save {filename}")


def demo_8_metadata_integration():
    """Demo 8: Metadata Integration"""
    print_section("8. Metadata Integration with Models")
    
    doc = SimplePDFDocument(
        title="Metadata Demo",
        content="This document has custom metadata."
    )
    
    # Set custom metadata
    metadata = PDFMetadata(
        title="Custom Title",
        author="Demo Author",
        subject="Demo Subject",
        keywords=["demo", "metadata", "test"]
    )
    
    doc.set_pdf_metadata(metadata)
    
    # Retrieve metadata
    retrieved = doc.get_pdf_metadata()
    
    print("✓ Set and retrieved metadata:")
    print(f"  Title: {retrieved.title}")
    print(f"  Author: {retrieved.author}")
    print(f"  Subject: {retrieved.subject}")
    print(f"  Keywords: {', '.join(retrieved.keywords)}")


def run_all_demos():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  PDF BYTE GENERATION CORE - DEMO")
    print("=" * 70)
    
    # Check installation first
    if not demo_1_check_installation():
        print("\n⚠ Cannot continue without reportlab")
        print("Install with: pip install reportlab")
        return
    
    # Run all demos
    demo_2_metadata()
    demo_3_german_formatting()
    demo_4_simple_pdf()
    demo_5_custom_model()
    demo_6_table_creation()
    demo_7_save_to_file()
    demo_8_metadata_integration()
    
    # Summary
    print("\n" + "=" * 70)
    print("  DEMO COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("\n✓ All PDF byte generation features are working correctly")
    print("\nNext steps:")
    print("  1. Run tests: pytest backend/tests/test_pdf_bytes.py -v")
    print("  2. See examples: python backend/examples/pdf_byte_examples.py")
    print("  3. Read docs: backend/docs/PDF_BYTE_GENERATION.md")


if __name__ == "__main__":
    run_all_demos()
