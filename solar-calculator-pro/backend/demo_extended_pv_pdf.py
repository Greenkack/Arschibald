"""
Demonstration of Extended PV PDF Service

This script demonstrates the usage of the Extended PV PDF Service
with various component selections.

Author: Kiro AI
Date: 2025-01-22
"""

import logging
from pathlib import Path

from services.extended_pv_pdf_service import (
    ExtendedPVPDFService,
    ComponentSelection
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_standard_pages_only():
    """Demo: Generate PDF with standard 8 pages only"""
    logger.info("=" * 80)
    logger.info("DEMO 1: Standard 8 Pages Only")
    logger.info("=" * 80)
    
    # Initialize service
    service = ExtendedPVPDFService()
    
    # Sample data
    data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Max Mustermann',
        'kunde_wohnort': 'Berlin',
        'kWp_anlage_anlage': '10,5 kWp',
        'langes_datum_heute': '22. Januar 2025',
        'total_price': 16999.00
    }
    
    # Component selection (all False = standard pages only)
    selection = ComponentSelection()
    
    # Generate PDF
    logger.info("Generating PDF with standard 8 pages only...")
    pdf_bytes = service.generate_extended_pdf(data, selection)
    
    if pdf_bytes:
        output_path = "demo_output/extended_pv_standard_only.pdf"
        Path("demo_output").mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f" PDF generated: {output_path}")
        logger.info(f"  Size: {len(pdf_bytes):,} bytes")
    else:
        logger.error(" Failed to generate PDF")
    
    logger.info("")


def demo_with_detailed_calculations():
    """Demo: Generate PDF with detailed calculations"""
    logger.info("=" * 80)
    logger.info("DEMO 2: Standard Pages + Detailed Calculations")
    logger.info("=" * 80)
    
    service = ExtendedPVPDFService()
    
    data = {
        'anrede_kunde': 'Frau',
        'kunde_vorname_und_nachname': 'Anna Schmidt',
        'kunde_wohnort': 'München',
        'kWp_anlage_anlage': '12,0 kWp',
        'langes_datum_heute': '22. Januar 2025',
        'total_price': 18999.00,
        'detailed_roi': 8.5,
        'payback_period': 11.8,
        'annual_production': 14000,
        'annual_savings': 2400,
        'co2_savings': 8500
    }
    
    # Enable detailed calculations
    selection = ComponentSelection(
        include_detailed_calculations=True
    )
    
    logger.info("Generating PDF with detailed calculations...")
    pdf_bytes = service.generate_extended_pdf(data, selection)
    
    if pdf_bytes:
        output_path = "demo_output/extended_pv_with_calculations.pdf"
        Path("demo_output").mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f" PDF generated: {output_path}")
        logger.info(f"  Size: {len(pdf_bytes):,} bytes")
        logger.info(f"  Pages: 8 standard + 1 calculation = 9 total")
    else:
        logger.error(" Failed to generate PDF")
    
    logger.info("")


def demo_with_diagrams():
    """Demo: Generate PDF with additional diagrams"""
    logger.info("=" * 80)
    logger.info("DEMO 3: Standard Pages + Additional Diagrams")
    logger.info("=" * 80)
    
    service = ExtendedPVPDFService()
    
    data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Thomas Müller',
        'kunde_wohnort': 'Hamburg',
        'kWp_anlage_anlage': '15,0 kWp',
        'langes_datum_heute': '22. Januar 2025',
        'total_price': 22999.00
    }
    
    # Enable additional diagrams
    selection = ComponentSelection(
        include_additional_diagrams=True,
        selected_diagram_types=[
            'production_monthly',
            'consumption_analysis',
            'savings_projection'
        ]
    )
    
    logger.info("Generating PDF with additional diagrams...")
    logger.info(f"  Selected diagrams: {', '.join(selection.selected_diagram_types)}")
    pdf_bytes = service.generate_extended_pdf(data, selection)
    
    if pdf_bytes:
        output_path = "demo_output/extended_pv_with_diagrams.pdf"
        Path("demo_output").mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f" PDF generated: {output_path}")
        logger.info(f"  Size: {len(pdf_bytes):,} bytes")
        logger.info(f"  Pages: 8 standard + 3 diagrams = 11 total")
    else:
        logger.error(" Failed to generate PDF")
    
    logger.info("")


def demo_with_all_components():
    """Demo: Generate PDF with all components"""
    logger.info("=" * 80)
    logger.info("DEMO 4: Standard Pages + All Components")
    logger.info("=" * 80)
    
    service = ExtendedPVPDFService()
    
    data = {
        'anrede_kunde': 'Herr Dr.',
        'kunde_vorname_und_nachname': 'Michael Weber',
        'kunde_wohnort': 'Frankfurt',
        'kWp_anlage_anlage': '20,0 kWp',
        'langes_datum_heute': '22. Januar 2025',
        'total_price': 29999.00,
        'detailed_roi': 9.2,
        'payback_period': 10.9,
        'annual_production': 22000,
        'annual_savings': 3200
    }
    
    # Enable all components
    selection = ComponentSelection(
        include_detailed_calculations=True,
        include_additional_diagrams=True,
        include_extended_visualizations=True,
        selected_diagram_types=[
            'production_monthly',
            'savings_projection'
        ]
    )
    
    logger.info("Generating PDF with all components...")
    logger.info("   Detailed calculations")
    logger.info("   Additional diagrams (2)")
    logger.info("   Extended visualizations")
    
    pdf_bytes = service.generate_extended_pdf(data, selection)
    
    if pdf_bytes:
        output_path = "demo_output/extended_pv_complete.pdf"
        Path("demo_output").mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f" PDF generated: {output_path}")
        logger.info(f"  Size: {len(pdf_bytes):,} bytes")
        logger.info(f"  Pages: 8 standard + 4 additional = 12 total")
    else:
        logger.error(" Failed to generate PDF")
    
    logger.info("")


def demo_available_components():
    """Demo: Get available components"""
    logger.info("=" * 80)
    logger.info("DEMO 5: Available Components")
    logger.info("=" * 80)
    
    service = ExtendedPVPDFService()
    
    logger.info("Getting available components...")
    components = service.get_available_components()
    
    logger.info("\nAvailable Calculations:")
    for calc in components['calculations']:
        logger.info(f"  • {calc['name']} (ID: {calc['id']})")
    
    logger.info("\nAvailable Diagrams:")
    for diagram in components['diagrams']:
        logger.info(f"  • {diagram['name']} (ID: {diagram['id']})")
    
    logger.info("\nAvailable Datasheets:")
    if components['datasheets']:
        for datasheet in components['datasheets']:
            logger.info(f"  • {datasheet['name']} (ID: {datasheet['id']})")
    else:
        logger.info("  (None - requires product IDs)")
    
    logger.info("\nAvailable Documents:")
    if components['documents']:
        for doc in components['documents']:
            logger.info(f"  • {doc['name']} (ID: {doc['id']})")
    else:
        logger.info("  (None - requires product IDs)")
    
    logger.info("")


def demo_with_product_specific_components():
    """Demo: Generate PDF with product-specific components"""
    logger.info("=" * 80)
    logger.info("DEMO 6: Product-Specific Components")
    logger.info("=" * 80)
    
    service = ExtendedPVPDFService()
    
    # Get available components for specific products
    product_ids = ['product_123', 'product_456']
    logger.info(f"Getting components for products: {', '.join(product_ids)}")
    components = service.get_available_components(product_ids=product_ids)
    
    logger.info(f"\nProduct-Specific Datasheets: {len(components['datasheets'])}")
    logger.info(f"Product-Specific Documents: {len(components['documents'])}")
    
    # Generate PDF with product components
    data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Stefan Becker',
        'kunde_wohnort': 'Stuttgart',
        'kWp_anlage_anlage': '18,0 kWp',
        'langes_datum_heute': '22. Januar 2025',
        'total_price': 26999.00
    }
    
    selection = ComponentSelection(
        include_product_datasheets=True,
        include_documents=True,
        selected_product_ids=product_ids,
        selected_document_ids=['doc_123', 'doc_456']
    )
    
    logger.info("\nGenerating PDF with product-specific components...")
    pdf_bytes = service.generate_extended_pdf(data, selection)
    
    if pdf_bytes:
        output_path = "demo_output/extended_pv_with_products.pdf"
        Path("demo_output").mkdir(exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f" PDF generated: {output_path}")
        logger.info(f"  Size: {len(pdf_bytes):,} bytes")
    else:
        logger.error(" Failed to generate PDF")
    
    logger.info("")


def main():
    """Run all demos"""
    logger.info("\n")
    logger.info("" + "=" * 78 + "")
    logger.info("" + " " * 20 + "EXTENDED PV PDF SERVICE DEMO" + " " * 30 + "")
    logger.info("" + "=" * 78 + "")
    logger.info("\n")
    
    try:
        # Run demos
        demo_standard_pages_only()
        demo_with_detailed_calculations()
        demo_with_diagrams()
        demo_with_all_components()
        demo_available_components()
        demo_with_product_specific_components()
        
        # Summary
        logger.info("=" * 80)
        logger.info("DEMO SUMMARY")
        logger.info("=" * 80)
        logger.info(" All demos completed successfully")
        logger.info(" Check demo_output/ folder for generated PDFs")
        logger.info("")
        logger.info("Key Features Demonstrated:")
        logger.info("  1. Standard 8-page PDF generation")
        logger.info("  2. Optional detailed calculations page")
        logger.info("  3. Optional additional diagram pages")
        logger.info("  4. Optional extended visualizations")
        logger.info("  5. Product-specific datasheets and documents")
        logger.info("  6. Dynamic component selection")
        logger.info("  7. Database integration for flexible content")
        logger.info("")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
