"""
Demo Script for Standard PV PDF Service

This script demonstrates how to use the Standard PV PDF Template System
to generate professional solar offer PDFs.

Author: Kiro AI
Date: 2025-01-22
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.standard_pv_pdf_service import StandardPVPDFService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_pdf_generation():
    """Demo 1: Basic PDF generation with minimal data"""
    logger.info("=" * 60)
    logger.info("DEMO 1: Basic PDF Generation")
    logger.info("=" * 60)
    
    # Initialize service
    service = StandardPVPDFService()
    
    # Prepare minimal data
    data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Max Mustermann',
        'kunde_wohnort': 'Berlin',
        'kWp_anlage_anlage': '10,5 kWp',
        'langes_datum_heute': datetime.now().strftime("%d. %B %Y"),
    }
    
    logger.info("Generating PDF with data:")
    for key, value in data.items():
        logger.info(f"  {key}: {value}")
    
    # Generate PDF
    try:
        pdf_bytes = service.generate_complete_pdf(data, include_pages=[1])
        
        if pdf_bytes:
            output_file = "demo_basic_pv_pdf.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            logger.info(f" PDF generated successfully: {output_file}")
            logger.info(f"  Size: {len(pdf_bytes):,} bytes")
        else:
            logger.error(" PDF generation failed")
            
    except Exception as e:
        logger.error(f" Error: {e}", exc_info=True)


def demo_complete_pdf_with_pricing():
    """Demo 2: Complete PDF with pricing and German formatting"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 2: Complete PDF with Pricing")
    logger.info("=" * 60)
    
    service = StandardPVPDFService()
    
    # Customer data
    customer_data = {
        'anrede_kunde': 'Frau',
        'kunde_vorname_und_nachname': 'Anna Schmidt',
        'kunde_wohnort': 'München',
        'kunde_strasse': 'Sonnenstraße 42',
        'kunde_plz': '80331',
    }
    
    # Calculation data
    calculation_data = {
        'kWp_anlage_anlage': '12,8 kWp',
        'module_count': '32',
        'annual_production': '14.500 kWh',
        'self_consumption_rate': '68,5%',
        'payback_period': '11,2 Jahre',
        'co2_savings': '9.800 kg',
        'langes_datum_heute': datetime.now().strftime("%d. %B %Y"),
    }
    
    # Pricing data
    pricing_data = {
        'total_price': 19999.00,
        'module_price': 9500.00,
        'inverter_price': 3500.00,
        'battery_price': 5000.00,
        'installation_price': 1999.00,
    }
    
    logger.info("Customer: {} from {}".format(
        customer_data['kunde_vorname_und_nachname'],
        customer_data['kunde_wohnort']
    ))
    logger.info("System: {}".format(calculation_data['kWp_anlage_anlage']))
    logger.info("Price: {}".format(
        StandardPVPDFService._format_german_currency(pricing_data['total_price'])
    ))
    
    try:
        pdf_bytes = service.generate_pdf_with_german_formatting(
            calculation_data=calculation_data,
            customer_data=customer_data,
            pricing_data=pricing_data
        )
        
        if pdf_bytes:
            output_file = "demo_complete_pv_pdf.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            logger.info(f" Complete PDF generated: {output_file}")
            logger.info(f"  Size: {len(pdf_bytes):,} bytes")
            logger.info(f"  Pages: 8")
        else:
            logger.error(" PDF generation failed")
            
    except Exception as e:
        logger.error(f" Error: {e}", exc_info=True)


def demo_specific_pages():
    """Demo 3: Generate only specific pages"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 3: Generate Specific Pages Only")
    logger.info("=" * 60)
    
    service = StandardPVPDFService()
    
    data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Thomas Weber',
        'kunde_wohnort': 'Hamburg',
        'kWp_anlage_anlage': '8,4 kWp',
        'langes_datum_heute': datetime.now().strftime("%d. %B %Y"),
    }
    
    # Generate only pages 1, 2, and 3
    pages_to_generate = [1, 2, 3]
    logger.info(f"Generating pages: {pages_to_generate}")
    
    try:
        pdf_bytes = service.generate_complete_pdf(
            data,
            include_pages=pages_to_generate
        )
        
        if pdf_bytes:
            output_file = "demo_partial_pv_pdf.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            logger.info(f" Partial PDF generated: {output_file}")
            logger.info(f"  Size: {len(pdf_bytes):,} bytes")
            logger.info(f"  Pages: {len(pages_to_generate)}")
        else:
            logger.error(" PDF generation failed")
            
    except Exception as e:
        logger.error(f" Error: {e}", exc_info=True)


def demo_german_formatting():
    """Demo 4: German number formatting examples"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 4: German Number Formatting")
    logger.info("=" * 60)
    
    test_amounts = [
        99.99,
        1234.56,
        16999.00,
        123456.78,
        1000000.00,
    ]
    
    logger.info("Currency formatting examples:")
    for amount in test_amounts:
        formatted = StandardPVPDFService._format_german_currency(amount)
        logger.info(f"  {amount:>12.2f} → {formatted}")


def demo_coordinate_inspection():
    """Demo 5: Inspect coordinate files"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 5: Coordinate File Inspection")
    logger.info("=" * 60)
    
    service = StandardPVPDFService()
    
    # Load coordinates for page 1
    logger.info("Loading coordinates for page 1...")
    elements = service.load_page_coordinates(1)
    
    if elements:
        logger.info(f" Found {len(elements)} text elements")
        logger.info("\nFirst 5 elements:")
        for i, elem in enumerate(elements[:5], 1):
            logger.info(f"\n  Element {i}:")
            logger.info(f"    Text: {elem.get('text', 'N/A')}")
            logger.info(f"    Font: {elem.get('font', 'N/A')}")
            logger.info(f"    Size: {elem.get('font_size', 'N/A')}")
            pos = elem.get('position', {})
            if pos:
                logger.info(f"    Position: ({pos.get('x')}, {pos.get('y')})")
    else:
        logger.warning(" No coordinates found")


def demo_template_availability():
    """Demo 6: Check template availability"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 6: Template Availability Check")
    logger.info("=" * 60)
    
    service = StandardPVPDFService()
    
    logger.info("Checking available templates...")
    templates = service.template_loader.get_all_templates()
    
    if templates:
        logger.info(f" Found {len(templates)} templates:")
        for page_num in sorted(templates.keys()):
            size = len(templates[page_num])
            logger.info(f"  Page {page_num}: {size:,} bytes")
    else:
        logger.warning(" No templates found")
        logger.info("  Make sure templates exist in: pdf_templates_static/notext/")


def demo_error_handling():
    """Demo 7: Error handling examples"""
    logger.info("\n" + "=" * 60)
    logger.info("DEMO 7: Error Handling")
    logger.info("=" * 60)
    
    service = StandardPVPDFService()
    
    # Test 1: Missing data
    logger.info("\nTest 1: Generate with missing data")
    try:
        pdf_bytes = service.generate_complete_pdf({}, include_pages=[1])
        if pdf_bytes:
            logger.info(" PDF generated (with empty placeholders)")
        else:
            logger.warning(" PDF generation failed")
    except Exception as e:
        logger.error(f" Error: {e}")
    
    # Test 2: Invalid page number
    logger.info("\nTest 2: Load coordinates for invalid page")
    try:
        elements = service.load_page_coordinates(99)
        if elements:
            logger.info(f" Found {len(elements)} elements")
        else:
            logger.warning(" No coordinates found (expected)")
    except Exception as e:
        logger.error(f" Error: {e}")


def main():
    """Run all demos"""
    logger.info("" + "=" * 58 + "")
    logger.info("" + " " * 10 + "Standard PV PDF Service - Demo Suite" + " " * 11 + "")
    logger.info("" + "=" * 58 + "")
    
    demos = [
        ("Basic PDF Generation", demo_basic_pdf_generation),
        ("Complete PDF with Pricing", demo_complete_pdf_with_pricing),
        ("Specific Pages", demo_specific_pages),
        ("German Formatting", demo_german_formatting),
        ("Coordinate Inspection", demo_coordinate_inspection),
        ("Template Availability", demo_template_availability),
        ("Error Handling", demo_error_handling),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            logger.error(f"Demo '{name}' failed: {e}", exc_info=True)
    
    logger.info("\n" + "=" * 60)
    logger.info("All demos completed!")
    logger.info("=" * 60)
    logger.info("\nGenerated files:")
    logger.info("  - demo_basic_pv_pdf.pdf")
    logger.info("  - demo_complete_pv_pdf.pdf")
    logger.info("  - demo_partial_pv_pdf.pdf")


if __name__ == "__main__":
    main()
