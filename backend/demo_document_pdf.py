"""
Demo: Document PDF Conversion Service

This demo shows how to use the DocumentPDFService to convert various
document formats to PDF and merge multiple PDFs.

Requirements: 14.8
Task: 228
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.document_pdf_service import (
    DocumentPDFService,
    word_to_pdf,
    excel_to_pdf,
    text_to_pdf,
    merge_pdfs
)
from core.pdf_bytes import PDFMetadata


def demo_text_to_pdf():
    """Demo: Convert text to PDF"""
    print("\n" + "="*60)
    print("DEMO 1: Text to PDF Conversion")
    print("="*60)
    
    service = DocumentPDFService()
    
    # Example 1: Simple text
    text_content = """Solar Calculator Pro - User Guide

Welcome to Solar Calculator Pro!

This application helps you calculate solar energy systems with precision.

Features:
- Solar panel calculations
- Heat pump integration
- 3D visualization
- PDF report generation
- Price matrix management

Getting Started:
1. Enter your location
2. Specify roof dimensions
3. Select solar modules
4. Review calculations
5. Generate PDF report

For more information, visit our website or contact support."""
    
    metadata = PDFMetadata(
        title="Solar Calculator Pro - User Guide",
        author="Solar Calculator Team",
        subject="User Documentation",
        keywords=["solar", "calculator", "guide"]
    )
    
    pdf_bytes = service.text_to_pdf_bytes(
        text_content=text_content,
        metadata=metadata,
        preserve_formatting=False
    )
    
    # Save to file
    output_file = "demo_text_document.pdf"
    with open(output_file, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" Created text PDF: {output_file}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Title: {metadata.title}")
    
    return pdf_bytes


def demo_formatted_text_to_pdf():
    """Demo: Convert formatted text to PDF"""
    print("\n" + "="*60)
    print("DEMO 2: Formatted Text to PDF")
    print("="*60)
    
    service = DocumentPDFService()
    
    # Code-like content with preserved formatting
    code_content = """# Solar Calculation Example

def calculate_solar_system(roof_area, module_power):
    \"\"\"Calculate solar system size\"\"\"
    module_area = 1.7  # m²
    efficiency = 0.85
    
    max_modules = int(roof_area / module_area * efficiency)
    system_power = max_modules * module_power
    
    return {
        'modules': max_modules,
        'power_kwp': system_power / 1000,
        'area_used': max_modules * module_area
    }

# Example usage
result = calculate_solar_system(50, 400)
print(f"System: {result['power_kwp']} kWp")
print(f"Modules: {result['modules']}")
"""
    
    metadata = PDFMetadata(
        title="Solar Calculation Code Example",
        author="Development Team",
        subject="Code Documentation"
    )
    
    pdf_bytes = service.text_to_pdf_bytes(
        text_content=code_content,
        metadata=metadata,
        preserve_formatting=True  # Preserve line breaks and spacing
    )
    
    output_file = "demo_code_document.pdf"
    with open(output_file, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" Created formatted text PDF: {output_file}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Formatting: Preserved")
    
    return pdf_bytes


def demo_german_numbers_in_pdf():
    """Demo: German number formatting in PDF"""
    print("\n" + "="*60)
    print("DEMO 3: German Number Formatting")
    print("="*60)
    
    service = DocumentPDFService()
    
    # Text with German-formatted numbers
    text_content = """Preiskalkulation - Solar Anlage

Systemgröße: 10,50 kWp
Anzahl Module: 30 Stück
Dachfläche: 52,75 m²

Kosten:
- Module: 12.450,00 €
- Wechselrichter: 3.200,00 €
- Montage: 4.500,00 €
- Installation: 2.850,00 €
-----------------------------------
Gesamtkosten: 23.000,00 €

Jährliche Produktion: 11.250,50 kWh
Eigenverbrauch: 4.500,25 kWh (40,00%)
Einspeisung: 6.750,25 kWh (60,00%)

Wirtschaftlichkeit:
- Jährliche Einsparung: 1.234,56 €
- Amortisationszeit: 18,65 Jahre
- Rendite (25 Jahre): 8,75%

CO₂-Einsparung: 5.625,25 kg/Jahr
"""
    
    metadata = PDFMetadata(
        title="Preiskalkulation Solar Anlage",
        author="Solar Calculator Pro",
        subject="Angebotskalkulation"
    )
    
    pdf_bytes = service.text_to_pdf_bytes(
        text_content=text_content,
        metadata=metadata
    )
    
    output_file = "demo_german_numbers.pdf"
    with open(output_file, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" Created German numbers PDF: {output_file}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Numbers: German format (1.234,56)")
    
    return pdf_bytes


def demo_merge_pdfs():
    """Demo: Merge multiple PDFs"""
    print("\n" + "="*60)
    print("DEMO 4: Merge Multiple PDFs")
    print("="*60)
    
    service = DocumentPDFService()
    
    # Create multiple PDFs
    pdf1 = service.text_to_pdf_bytes(
        text_content="Document 1: Project Overview\n\nThis is the first document.",
        metadata=PDFMetadata(title="Project Overview")
    )
    
    pdf2 = service.text_to_pdf_bytes(
        text_content="Document 2: Technical Specifications\n\nDetailed technical information.",
        metadata=PDFMetadata(title="Technical Specifications")
    )
    
    pdf3 = service.text_to_pdf_bytes(
        text_content="Document 3: Cost Analysis\n\nFinancial breakdown and analysis.",
        metadata=PDFMetadata(title="Cost Analysis")
    )
    
    print(f" Created 3 individual PDFs")
    print(f"  PDF 1: {len(pdf1):,} bytes")
    print(f"  PDF 2: {len(pdf2):,} bytes")
    print(f"  PDF 3: {len(pdf3):,} bytes")
    
    # Merge PDFs
    merged_metadata = PDFMetadata(
        title="Complete Project Documentation",
        author="Solar Calculator Pro",
        subject="Merged Project Documents",
        keywords=["project", "documentation", "complete"]
    )
    
    merged_pdf = service.merge_pdf_documents(
        [pdf1, pdf2, pdf3],
        output_metadata=merged_metadata
    )
    
    output_file = "demo_merged_document.pdf"
    with open(output_file, 'wb') as f:
        f.write(merged_pdf)
    
    print(f"\n Merged into single PDF: {output_file}")
    print(f"  Size: {len(merged_pdf):,} bytes")
    print(f"  Pages: 3 documents merged")
    
    return merged_pdf


def demo_batch_conversion():
    """Demo: Convert multiple documents"""
    print("\n" + "="*60)
    print("DEMO 5: Batch Document Conversion")
    print("="*60)
    
    service = DocumentPDFService()
    
    # Multiple documents to convert
    documents = [
        {
            'content': "Report 1: Daily Summary\n\nSummary of daily operations.",
            'title': "Daily Summary"
        },
        {
            'content': "Report 2: Weekly Analysis\n\nWeekly performance analysis.",
            'title': "Weekly Analysis"
        },
        {
            'content': "Report 3: Monthly Review\n\nMonthly review and statistics.",
            'title': "Monthly Review"
        }
    ]
    
    pdf_list = []
    for i, doc in enumerate(documents, 1):
        pdf_bytes = service.text_to_pdf_bytes(
            text_content=doc['content'],
            metadata=PDFMetadata(title=doc['title'])
        )
        pdf_list.append(pdf_bytes)
        print(f" Converted document {i}: {doc['title']} ({len(pdf_bytes):,} bytes)")
    
    # Save individually
    for i, pdf_bytes in enumerate(pdf_list, 1):
        output_file = f"demo_batch_doc_{i}.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
    
    print(f"\n Created {len(pdf_list)} individual PDFs")
    
    # Also create merged version
    merged = service.merge_pdf_documents(
        pdf_list,
        output_metadata=PDFMetadata(title="All Reports Combined")
    )
    
    output_file = "demo_batch_merged.pdf"
    with open(output_file, 'wb') as f:
        f.write(merged)
    
    print(f" Created merged PDF: {output_file} ({len(merged):,} bytes)")
    
    return pdf_list, merged


def demo_convenience_functions():
    """Demo: Using convenience functions"""
    print("\n" + "="*60)
    print("DEMO 6: Convenience Functions")
    print("="*60)
    
    # Create a temporary text file
    temp_file = "temp_demo.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write("This is a test document created for the demo.\n\n")
        f.write("It demonstrates the convenience functions.\n\n")
        f.write("Price: 1.234,56 €\n")
        f.write("Quantity: 1.000 units\n")
    
    # Use convenience function
    pdf_bytes = text_to_pdf(
        temp_file,
        output_path="demo_convenience.pdf",
        metadata=PDFMetadata(title="Convenience Function Demo")
    )
    
    print(f" Used text_to_pdf() convenience function")
    print(f"  Input: {temp_file}")
    print(f"  Output: demo_convenience.pdf")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    
    # Clean up temp file
    import os
    os.remove(temp_file)
    
    return pdf_bytes


def demo_unicode_support():
    """Demo: Unicode character support"""
    print("\n" + "="*60)
    print("DEMO 7: Unicode Character Support")
    print("="*60)
    
    service = DocumentPDFService()
    
    # Text with various Unicode characters
    text_content = """Internationale Zeichen

Deutsch: äöüßÄÖÜ
Französisch: éèêëàâ
Spanisch: ñáéíóú
Griechisch: αβγδε
Russisch: абвгд

Währungen: €£¥$¢
Mathematik: ∑∫∂√∞
Pfeile: ←→↑↓
Symbole: ©®™§¶

Emojis: 
"""
    
    metadata = PDFMetadata(
        title="Unicode Character Test",
        author="Solar Calculator Pro",
        subject="Character Encoding Test"
    )
    
    pdf_bytes = service.text_to_pdf_bytes(
        text_content=text_content,
        metadata=metadata
    )
    
    output_file = "demo_unicode.pdf"
    with open(output_file, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f" Created Unicode PDF: {output_file}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Characters: German, French, Spanish, Greek, Russian, Symbols")
    
    return pdf_bytes


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("DOCUMENT PDF CONVERSION SERVICE - DEMO")
    print("="*60)
    print("\nThis demo shows various document conversion capabilities:")
    print("- Text to PDF conversion")
    print("- Formatted text with preserved spacing")
    print("- German number formatting")
    print("- PDF merging")
    print("- Batch conversion")
    print("- Unicode character support")
    
    try:
        # Run demos
        demo_text_to_pdf()
        demo_formatted_text_to_pdf()
        demo_german_numbers_in_pdf()
        demo_merge_pdfs()
        demo_batch_conversion()
        demo_convenience_functions()
        demo_unicode_support()
        
        print("\n" + "="*60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nGenerated files:")
        print("- demo_text_document.pdf")
        print("- demo_code_document.pdf")
        print("- demo_german_numbers.pdf")
        print("- demo_merged_document.pdf")
        print("- demo_batch_doc_1.pdf")
        print("- demo_batch_doc_2.pdf")
        print("- demo_batch_doc_3.pdf")
        print("- demo_batch_merged.pdf")
        print("- demo_convenience.pdf")
        print("- demo_unicode.pdf")
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
