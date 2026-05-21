"""
Demo Script for Standard WP PDF Service

This script demonstrates the usage of the Standard WP PDF Service
for generating 8-page heat pump PDF documents.

Author: Kiro AI
Date: 2025-01-22
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.standard_wp_pdf_service import (
    StandardWPPDFService,
    WPPlaceholderSystem
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_wp_pdf_generation():
    """
    Demo 1: Basic WP PDF Generation
    
    Demonstrates generating a simple 8-page heat pump PDF with
    customer data and basic calculations.
    """
    print("\n" + "="*80)
    print("DEMO 1: Basic WP PDF Generation")
    print("="*80)
    
    # Initialize service
    service = StandardWPPDFService()
    
    # Sample data
    sample_data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Max Mustermann',
        'kunde_wohnort': 'Berlin',
        'wp_leistung_kw': 12.5,
        'wp_cop_wert': 4.5,
        'wp_jahresarbeitszahl': 4.2,
        'wp_modell_name': 'Viessmann Vitocal 200-S',
        'wp_hersteller': 'Viessmann',
        'langes_datum_heute': '22. Januar 2025'
    }
    
    print("\n Sample Data:")
    for key, value in sample_data.items():
        print(f"  {key}: {value}")
    
    try:
        pdf_bytes = service.generate_complete_pdf(sample_data)
        
        if pdf_bytes:
            output_file = "demo_wp_basic.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"\n PDF generated successfully!")
            print(f"   File: {output_file}")
            print(f"   Size: {len(pdf_bytes):,} bytes")
        else:
            print("\n PDF generation failed (no bytes returned)")
            
    except Exception as e:
        print(f"\n  Error: {e}")
        print("   (This is expected if templates are not available)")


def demo_complete_wp_pdf_with_formatting():
    """
    Demo 2: Complete WP PDF with German Formatting
    
    Demonstrates generating a complete heat pump PDF with all
    calculations, pricing, and German number formatting.
    """
    print("\n" + "="*80)
    print("DEMO 2: Complete WP PDF with German Formatting")
    print("="*80)
    
    # Initialize service
    service = StandardWPPDFService()
    
    # Complete calculation data
    calculation_data = {
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
        'wp_modell_name': 'Viessmann Vitocal 200-S',
        'wp_hersteller': 'Viessmann'
    }
    
    # Customer data
    customer_data = {
        'anrede_kunde': 'Frau',
        'kunde_vorname_und_nachname': 'Anna Schmidt',
        'kunde_wohnort': 'München',
        'langes_datum_heute': '22. Januar 2025'
    }
    
    # Pricing data
    pricing_data = {
        'total_price': 18999.00
    }
    
    print("\n Calculation Data:")
    for key, value in calculation_data.items():
        print(f"  {key}: {value}")
    
    print("\n Customer Data:")
    for key, value in customer_data.items():
        print(f"  {key}: {value}")
    
    print("\n Pricing Data:")
    for key, value in pricing_data.items():
        print(f"  {key}: {value}")
    
    try:
        pdf_bytes = service.generate_pdf_with_german_formatting(
            calculation_data=calculation_data,
            customer_data=customer_data,
            pricing_data=pricing_data
        )
        
        if pdf_bytes:
            output_file = "demo_wp_complete.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"\n PDF generated successfully!")
            print(f"   File: {output_file}")
            print(f"   Size: {len(pdf_bytes):,} bytes")
            
            # Show formatted values
            print(f"\n German Formatting Examples:")
            print(f"   Total Price: {service._format_german_currency(pricing_data['total_price'])}")
            print(f"   Heating Costs/Year: {service._format_german_currency(calculation_data['wp_heizkosten_jahr'])}")
            print(f"   COP Value: {service._format_german_decimal(calculation_data['wp_cop_wert'], 1)}")
        else:
            print("\n PDF generation failed (no bytes returned)")
            
    except Exception as e:
        print(f"\n  Error: {e}")
        print("   (This is expected if templates are not available)")


def demo_partial_page_generation():
    """
    Demo 3: Partial Page Generation
    
    Demonstrates generating only specific pages of the WP PDF.
    """
    print("\n" + "="*80)
    print("DEMO 3: Partial Page Generation")
    print("="*80)
    
    # Initialize service
    service = StandardWPPDFService()
    
    # Sample data
    sample_data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Thomas Müller',
        'kunde_wohnort': 'Hamburg',
        'wp_leistung_kw': 15.0,
        'wp_cop_wert': 4.8,
        'wp_modell_name': 'Daikin Altherma 3',
        'wp_hersteller': 'Daikin'
    }
    
    # Generate only pages 1-3
    include_pages = [1, 2, 3]
    
    print(f"\n Generating pages: {include_pages}")
    print("\n Sample Data:")
    for key, value in sample_data.items():
        print(f"  {key}: {value}")
    
    try:
        pdf_bytes = service.generate_complete_pdf(
            sample_data,
            include_pages=include_pages
        )
        
        if pdf_bytes:
            output_file = "demo_wp_partial.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"\n Partial PDF generated successfully!")
            print(f"   File: {output_file}")
            print(f"   Pages: {len(include_pages)}")
            print(f"   Size: {len(pdf_bytes):,} bytes")
        else:
            print("\n PDF generation failed (no bytes returned)")
            
    except Exception as e:
        print(f"\n  Error: {e}")
        print("   (This is expected if templates are not available)")


def demo_placeholder_system():
    """
    Demo 4: Placeholder System
    
    Demonstrates the WP placeholder system and available placeholders.
    """
    print("\n" + "="*80)
    print("DEMO 4: WP Placeholder System")
    print("="*80)
    
    print("\n Static Placeholders:")
    for placeholder in sorted(WPPlaceholderSystem.STATIC_PLACEHOLDERS.keys()):
        print(f"  • {placeholder}")
    
    print(f"\n Dynamic Placeholders ({len(WPPlaceholderSystem.DYNAMIC_PLACEHOLDERS)}):")
    for placeholder in sorted(WPPlaceholderSystem.DYNAMIC_PLACEHOLDERS):
        print(f"  • {placeholder}")
    
    # Test placeholder replacement
    print("\n Placeholder Replacement Examples:")
    test_data = {
        'wp_modell_name': 'Viessmann Vitocal 200-S',
        'wp_cop_wert': '4,5',
        'wp_hersteller': 'Viessmann'
    }
    
    for placeholder in ['wp_modell_name', 'wp_cop_wert', 'wp_hersteller', 'wp_leistung_kw']:
        result = WPPlaceholderSystem.replace_placeholder(placeholder, test_data)
        status = "" if result != placeholder else ""
        print(f"  {status} {placeholder} → {result}")


def demo_german_formatting():
    """
    Demo 5: German Number Formatting
    
    Demonstrates German formatting for currency and decimal values.
    """
    print("\n" + "="*80)
    print("DEMO 5: German Number Formatting")
    print("="*80)
    
    service = StandardWPPDFService()
    
    print("\n Currency Formatting:")
    test_amounts = [99.99, 1250.50, 16999.00, 18999.00, 1000000.00]
    for amount in test_amounts:
        formatted = service._format_german_currency(amount)
        print(f"  {amount:>12.2f} → {formatted}")
    
    print("\n Decimal Formatting:")
    test_values = [
        (4.5, 1, "COP Value"),
        (4.25, 2, "JAZ"),
        (12.5, 1, "Power (kW)"),
        (3500.75, 2, "Large Value")
    ]
    for value, decimals, description in test_values:
        formatted = service._format_german_decimal(value, decimals)
        print(f"  {description:15} {value:>8} → {formatted}")


def demo_service_info():
    """
    Demo 6: Service Information
    
    Displays information about the WP PDF service configuration.
    """
    print("\n" + "="*80)
    print("DEMO 6: Service Information")
    print("="*80)
    
    service = StandardWPPDFService()
    
    print("\n Directory Configuration:")
    print(f"  Template Directory: {service.template_loader.template_dir}")
    print(f"  Coordinates Directory: {service.coords_dir}")
    
    print("\n Expected Files:")
    print("  Templates:")
    for i in range(1, 9):
        print(f"    • hp_nt_{i:02d}.pdf")
    
    print("\n  Coordinates:")
    for i in range(1, 9):
        print(f"    • wp_seite{i}.yml")
    
    # Check if directories exist
    template_exists = service.template_loader.template_dir.exists()
    coords_exists = service.coords_dir.exists()
    
    print("\n Directory Status:")
    print(f"  Template Directory: {' EXISTS' if template_exists else ' NOT FOUND'}")
    print(f"  Coordinates Directory: {' EXISTS' if coords_exists else ' NOT FOUND'}")
    
    # Try to load templates
    try:
        templates = service.template_loader.get_all_templates()
        print(f"\n Available Templates: {len(templates)}/8")
        for page_num in sorted(templates.keys()):
            print(f"   Page {page_num}")
    except Exception as e:
        print(f"\n  Could not load templates: {e}")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("STANDARD WP PDF SERVICE - DEMONSTRATION")
    print("="*80)
    print("\nThis demo showcases the Standard WP (Heat Pump) PDF Service")
    print("for generating 8-page heat pump PDF documents.")
    
    # Run all demos
    demo_basic_wp_pdf_generation()
    demo_complete_wp_pdf_with_formatting()
    demo_partial_page_generation()
    demo_placeholder_system()
    demo_german_formatting()
    demo_service_info()
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print("\n All demos executed successfully!")
    print("\nGenerated files:")
    print("  • demo_wp_basic.pdf (if templates available)")
    print("  • demo_wp_complete.pdf (if templates available)")
    print("  • demo_wp_partial.pdf (if templates available)")
    print("\n")


if __name__ == "__main__":
    main()
