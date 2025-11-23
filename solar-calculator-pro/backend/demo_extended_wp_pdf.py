"""
Demo script for Extended WP PDF Service

This script demonstrates the usage of the Extended WP PDF Service
for generating WP PDFs with optional additional pages.

Author: Kiro AI
Date: 2025-01-22
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.extended_wp_pdf_service import (
    ExtendedWPPDFService,
    WPComponentSelection
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_extended_wp_pdf():
    """Demo: Generate basic extended WP PDF with detailed calculations"""
    logger.info("=" * 80)
    logger.info("DEMO 1: Basic Extended WP PDF with Detailed Calculations")
    logger.info("=" * 80)
    
    # Initialize service
    service = ExtendedWPPDFService()
    
    # Sample WP data
    wp_data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Max Mustermann',
        'kunde_wohnort': 'Berlin',
        'wp_leistung_kw': 12.5,
        'wp_cop_wert': 4.5,
        'wp_jahresarbeitszahl': 4.2,
        'wp_heizkosten_jahr': 1250.00,
        'wp_heizkosten_monat': 104.17,
        'wp_einsparung_jahr': 2500.00,
        'wp_einsparung_prozent': '66,7%',
        'wp_amortisationszeit': '8 Jahre',
        'wp_co2_einsparung': '4.500 kg/Jahr',
        'wp_effizienzklasse': 'A+++',
        'wp_vorlauftemperatur': '35°C',
        'wp_heizlast_kw': 10.0,
        'wp_warmwasser_liter': 300,
        'langes_datum_heute': '22. Januar 2025',
        'wp_modell_name': 'Viessmann Vitocal 200-S',
        'wp_hersteller': 'Viessmann',
        'total_price': 18999.00
    }
    
    # Component selection: Only detailed calculations
    selection = WPComponentSelection(
        include_detailed_wp_calculations=True
    )
    
    logger.info("Generating extended WP PDF with detailed calculations...")
    pdf_bytes = service.generate_extended_wp_pdf(wp_data, selection)
    
    if pdf_bytes:
        output_path = "demo_basic_extended_wp_pdf.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"✓ PDF generated successfully: {output_path}")
        logger.info(f"  Size: {len(pdf_bytes)} bytes")
    else:
        logger.error("✗ Failed to generate PDF")


def demo_extended_wp_pdf_with_diagrams():
    """Demo: Generate extended WP PDF with additional diagrams"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 2: Extended WP PDF with Additional Diagrams")
    logger.info("=" * 80)
    
    service = ExtendedWPPDFService()
    
    wp_data = {
        'anrede_kunde': 'Frau',
        'kunde_vorname_und_nachname': 'Anna Schmidt',
        'kunde_wohnort': 'München',
        'wp_leistung_kw': 15.0,
        'wp_cop_wert': 4.8,
        'wp_jahresarbeitszahl': 4.5,
        'wp_heizkosten_jahr': 980.00,
        'wp_heizkosten_monat': 81.67,
        'wp_einsparung_jahr': 3200.00,
        'wp_einsparung_prozent': '76,5%',
        'wp_amortisationszeit': '7 Jahre',
        'wp_co2_einsparung': '5.200 kg/Jahr',
        'wp_effizienzklasse': 'A+++',
        'wp_vorlauftemperatur': '32°C',
        'wp_heizlast_kw': 12.5,
        'wp_warmwasser_liter': 400,
        'langes_datum_heute': '22. Januar 2025',
        'wp_modell_name': 'Daikin Altherma 3',
        'wp_hersteller': 'Daikin',
        'total_price': 22500.00
    }
    
    # Component selection: Calculations + Diagrams
    selection = WPComponentSelection(
        include_detailed_wp_calculations=True,
        include_additional_wp_diagrams=True,
        selected_wp_diagram_types=['cop_monthly', 'heating_cost_comparison', 'efficiency_analysis']
    )
    
    logger.info("Generating extended WP PDF with calculations and diagrams...")
    pdf_bytes = service.generate_extended_wp_pdf(wp_data, selection)
    
    if pdf_bytes:
        output_path = "demo_extended_wp_pdf_with_diagrams.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"✓ PDF generated successfully: {output_path}")
        logger.info(f"  Size: {len(pdf_bytes)} bytes")
    else:
        logger.error("✗ Failed to generate PDF")


def demo_get_available_wp_components():
    """Demo: Get available WP components"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 3: Get Available WP Components")
    logger.info("=" * 80)
    
    service = ExtendedWPPDFService()
    
    logger.info("Fetching available WP components...")
    components = service.get_available_wp_components()
    
    logger.info("\nAvailable WP Calculations:")
    for calc in components['wp_calculations']:
        logger.info(f"  - {calc['name']} (ID: {calc['id']})")
    
    logger.info("\nAvailable WP Diagrams:")
    for diagram in components['wp_diagrams']:
        logger.info(f"  - {diagram['name']} (ID: {diagram['id']})")
    
    logger.info("\nWP Datasheets: " + str(len(components['wp_datasheets'])))
    logger.info("WP Documents: " + str(len(components['wp_documents'])))
    logger.info("WP Images: " + str(len(components['wp_images'])))


def demo_full_extended_wp_pdf():
    """Demo: Generate full extended WP PDF with all components"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 4: Full Extended WP PDF with All Components")
    logger.info("=" * 80)
    
    service = ExtendedWPPDFService()
    
    wp_data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Thomas Müller',
        'kunde_wohnort': 'Hamburg',
        'wp_leistung_kw': 18.0,
        'wp_cop_wert': 5.0,
        'wp_jahresarbeitszahl': 4.7,
        'wp_heizkosten_jahr': 850.00,
        'wp_heizkosten_monat': 70.83,
        'wp_einsparung_jahr': 3800.00,
        'wp_einsparung_prozent': '81,7%',
        'wp_amortisationszeit': '6 Jahre',
        'wp_co2_einsparung': '6.100 kg/Jahr',
        'wp_effizienzklasse': 'A+++',
        'wp_vorlauftemperatur': '30°C',
        'wp_heizlast_kw': 15.0,
        'wp_warmwasser_liter': 500,
        'langes_datum_heute': '22. Januar 2025',
        'wp_modell_name': 'Vaillant aroTHERM plus',
        'wp_hersteller': 'Vaillant',
        'total_price': 25999.00
    }
    
    # Component selection: All components
    selection = WPComponentSelection(
        include_detailed_wp_calculations=True,
        include_additional_wp_diagrams=True,
        include_extended_wp_visualizations=True,
        selected_wp_diagram_types=['cop_monthly', 'heating_cost_comparison', 'efficiency_analysis', 'savings_projection']
    )
    
    logger.info("Generating full extended WP PDF with all components...")
    pdf_bytes = service.generate_extended_wp_pdf(wp_data, selection)
    
    if pdf_bytes:
        output_path = "demo_full_extended_wp_pdf.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"✓ PDF generated successfully: {output_path}")
        logger.info(f"  Size: {len(pdf_bytes)} bytes")
    else:
        logger.error("✗ Failed to generate PDF")


def main():
    """Run all demos"""
    logger.info("Extended WP PDF Service Demo")
    logger.info("=" * 80)
    
    try:
        demo_basic_extended_wp_pdf()
        demo_extended_wp_pdf_with_diagrams()
        demo_get_available_wp_components()
        demo_full_extended_wp_pdf()
        
        logger.info("\n" + "=" * 80)
        logger.info("All demos completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error running demos: {e}", exc_info=True)


if __name__ == "__main__":
    main()
