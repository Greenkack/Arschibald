"""
Demo Script for PV Dynamic Keys & PDF Bytes System

This script demonstrates the complete functionality of the PV dynamic key
management and PDF bytes generation system.

Requirements: 1.3, 4.5, 14.1, 14.2
Task: 115 - Standard PV PDF Dynamic Keys & PDF Bytes
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.services.pv_dynamic_key_manager import (
    PVDynamicKeyManager,
    GermanNumberFormatter,
    PVDataModel,
    PVKeyPrefix
)
from backend.services.pv_pdf_bytes_generator import (
    PVPDFBytesGenerator,
    PVCalculationResultPDF,
    PVProductDataPDF
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_german_formatting():
    """Demonstrate German number formatting"""
    logger.info("=" * 60)
    logger.info("DEMO 1: German Number Formatting")
    logger.info("=" * 60)
    
    formatter = GermanNumberFormatter()
    
    # Basic number
    value = 1234567.89
    formatted = formatter.format(value, 2)
    logger.info(f"Number: {value} → {formatted}")
    
    # Currency
    price = 16999.00
    formatted = formatter.format_currency(price)
    logger.info(f"Currency: {price} → {formatted}")
    
    # kWh
    kwh = 12500.50
    formatted = formatter.format_kwh(kwh)
    logger.info(f"kWh: {kwh} → {formatted}")
    
    # Percentage
    percent = 85.5
    formatted = formatter.format_percentage(percent)
    logger.info(f"Percentage: {percent} → {formatted}")
    
    # Years
    years = 12.5
    formatted = formatter.format_years(years)
    logger.info(f"Years: {years} → {formatted}")
    
    logger.info("")


def demo_dynamic_key_manager():
    """Demonstrate dynamic key management"""
    logger.info("=" * 60)
    logger.info("DEMO 2: Dynamic Key Management")
    logger.info("=" * 60)
    
    manager = PVDynamicKeyManager()
    
    # Sample calculation data
    calculation_data = {
        'system_size': 10.5,
        'module_count': 30,
        'annual_production': 12500.0,
        'self_consumption_rate': 85.5,
        'payback_period': 12.5,
        'total_cost': 16999.00,
        'savings_25_years': 45000.00,
        'co2_savings': 125000.0
    }
    
    logger.info("Importing calculation keys...")
    calc_keys = manager.import_calculation_keys(calculation_data)
    logger.info(f"Imported {len(calc_keys)} calculation keys")
    
    # Show some keys
    for original_key, dynamic_key in list(calc_keys.items())[:3]:
        value = manager.get_value_by_key(dynamic_key)
        formatted = manager.get_formatted_value(dynamic_key)
        logger.info(f"  {original_key}:")
        logger.info(f"    Dynamic Key: {dynamic_key}")
        logger.info(f"    Raw Value: {value}")
        logger.info(f"    Formatted: {formatted}")
    
    # Sample product data
    product_data = {
        'module_type': 'Trina Solar TSM-400W',
        'module_power': 400,
        'module_efficiency': 20.5,
        'inverter_type': 'SMA Sunny Tripower 10.0',
        'battery_type': 'BYD Battery-Box Premium HVS 10.2',
        'battery_capacity': 10.2
    }
    
    logger.info("\nImporting product keys...")
    prod_keys = manager.import_product_keys(product_data)
    logger.info(f"Imported {len(prod_keys)} product keys")
    
    # Sample pricing data
    pricing_data = {
        'base_price': 15000.00,
        'total_price': 16999.00,
        'module_price': 8000.00,
        'inverter_price': 3000.00,
        'battery_price': 5000.00
    }
    
    logger.info("\nImporting pricing keys (with German formatting)...")
    price_keys = manager.import_pricing_keys(pricing_data)
    logger.info(f"Imported {len(price_keys)} pricing keys")
    
    # Show formatted prices
    for original_key, dynamic_key in price_keys.items():
        formatted = manager.get_formatted_value(dynamic_key)
        logger.info(f"  {original_key}: {formatted}")
    
    # Export all keys
    logger.info("\nExporting all keys...")
    all_keys = manager.export_all_keys()
    logger.info(f"Total keys exported: {len(all_keys)}")
    
    logger.info("")
    return manager, calculation_data, product_data, pricing_data


def demo_pdf_generation(calculation_data, product_data):
    """Demonstrate PDF generation"""
    logger.info("=" * 60)
    logger.info("DEMO 3: PDF Bytes Generation")
    logger.info("=" * 60)
    
    generator = PVPDFBytesGenerator()
    
    # Generate calculation PDF
    logger.info("Generating calculation results PDF...")
    calc_pdf_bytes = generator.generate_calculation_pdf(calculation_data)
    logger.info(f"Generated PDF: {len(calc_pdf_bytes)} bytes")
    
    # Save to file
    calc_output_path = "demo_pv_calculation_results.pdf"
    with open(calc_output_path, 'wb') as f:
        f.write(calc_pdf_bytes)
    logger.info(f"Saved to: {calc_output_path}")
    
    # Generate product PDF
    logger.info("\nGenerating product datasheet PDF...")
    prod_pdf_bytes = generator.generate_product_pdf(product_data)
    logger.info(f"Generated PDF: {len(prod_pdf_bytes)} bytes")
    
    # Save to file
    prod_output_path = "demo_pv_product_datasheet.pdf"
    with open(prod_output_path, 'wb') as f:
        f.write(prod_pdf_bytes)
    logger.info(f"Saved to: {prod_output_path}")
    
    # Generate chart PDF
    logger.info("\nGenerating chart PDF...")
    chart_data = {
        'labels': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni'],
        'values': [1000, 1200, 1500, 1800, 2000, 2200]
    }
    chart_pdf_bytes = generator.generate_chart_pdf(
        chart_type='PIE',
        chart_data=chart_data,
        title='Monatliche Stromproduktion'
    )
    logger.info(f"Generated PDF: {len(chart_pdf_bytes)} bytes")
    
    # Save to file
    chart_output_path = "demo_pv_chart.pdf"
    with open(chart_output_path, 'wb') as f:
        f.write(chart_pdf_bytes)
    logger.info(f"Saved to: {chart_output_path}")
    
    # Generate 3D visualization PDF
    logger.info("\nGenerating 3D visualization PDF...")
    viz_data = {
        'description': '3D-Visualisierung der PV-Anlage auf Süddach',
        'module_count': 30,
        'roof_area': 50.0,
        'orientation': 'Süd'
    }
    viz_pdf_bytes = generator.generate_3d_visualization_pdf(viz_data)
    logger.info(f"Generated PDF: {len(viz_pdf_bytes)} bytes")
    
    # Save to file
    viz_output_path = "demo_pv_3d_visualization.pdf"
    with open(viz_output_path, 'wb') as f:
        f.write(viz_pdf_bytes)
    logger.info(f"Saved to: {viz_output_path}")
    
    logger.info("")


def demo_pv_data_model():
    """Demonstrate PVDataModel usage"""
    logger.info("=" * 60)
    logger.info("DEMO 4: PVDataModel (Combined Keys + PDF)")
    logger.info("=" * 60)
    
    # Create model
    data = {
        'system_size': 10.5,
        'module_count': 30,
        'annual_production': 12500.0,
        'total_cost': 16999.00
    }
    
    logger.info("Creating PVDataModel...")
    model = PVDataModel(data)
    
    # Generate dynamic key
    logger.info("\nGenerating dynamic key...")
    key = model.generate_dynamic_key(prefix=PVKeyPrefix.SYSTEM_SIZE)
    logger.info(f"Generated key: {key}")
    
    # Get key metadata
    metadata = model.get_key_metadata()
    logger.info(f"Key metadata: {metadata}")
    
    # Generate PDF bytes
    logger.info("\nGenerating PDF bytes...")
    pdf_bytes = model.to_pdf_bytes()
    logger.info(f"Generated PDF: {len(pdf_bytes)} bytes")
    
    # Save PDF
    output_path = "demo_pv_data_model.pdf"
    model.save_pdf(output_path)
    logger.info(f"Saved to: {output_path}")
    
    # Generate base64 PDF
    logger.info("\nGenerating base64-encoded PDF...")
    base64_pdf = model.to_pdf_base64()
    logger.info(f"Base64 PDF length: {len(base64_pdf)} characters")
    logger.info(f"First 50 chars: {base64_pdf[:50]}...")
    
    logger.info("")


def demo_complete_workflow():
    """Demonstrate complete workflow"""
    logger.info("=" * 60)
    logger.info("DEMO 5: Complete Workflow")
    logger.info("=" * 60)
    
    # Step 1: Initialize
    logger.info("Step 1: Initializing manager and generator...")
    manager = PVDynamicKeyManager()
    generator = PVPDFBytesGenerator()
    
    # Step 2: Prepare data
    logger.info("\nStep 2: Preparing sample data...")
    calculation_data = {
        'system_size': 10.5,
        'module_count': 30,
        'annual_production': 12500.0,
        'self_consumption_rate': 85.5,
        'payback_period': 12.5,
        'total_cost': 16999.00,
        'savings_25_years': 45000.00,
        'co2_savings': 125000.0
    }
    
    product_data = {
        'module_type': 'Trina Solar TSM-400W',
        'module_power': 400,
        'inverter_type': 'SMA Sunny Tripower 10.0',
        'battery_type': 'BYD Battery-Box Premium HVS 10.2',
        'battery_capacity': 10.2
    }
    
    pricing_data = {
        'total_price': 16999.00,
        'module_price': 8000.00,
        'inverter_price': 3000.00,
        'battery_price': 5000.00
    }
    
    # Step 3: Import all keys
    logger.info("\nStep 3: Importing all keys...")
    calc_keys = manager.import_calculation_keys(calculation_data)
    prod_keys = manager.import_product_keys(product_data)
    price_keys = manager.import_pricing_keys(pricing_data)
    logger.info(f"Total keys imported: {len(calc_keys) + len(prod_keys) + len(price_keys)}")
    
    # Step 4: Generate PDFs
    logger.info("\nStep 4: Generating PDFs...")
    calc_pdf = generator.generate_calculation_pdf(calculation_data)
    prod_pdf = generator.generate_product_pdf(product_data)
    logger.info(f"Calculation PDF: {len(calc_pdf)} bytes")
    logger.info(f"Product PDF: {len(prod_pdf)} bytes")
    
    # Step 5: Save all PDFs
    logger.info("\nStep 5: Saving PDFs...")
    with open('workflow_calculation.pdf', 'wb') as f:
        f.write(calc_pdf)
    with open('workflow_product.pdf', 'wb') as f:
        f.write(prod_pdf)
    logger.info("All PDFs saved successfully!")
    
    # Step 6: Verify data retrieval
    logger.info("\nStep 6: Verifying data retrieval...")
    for original_key, dynamic_key in calc_keys.items():
        value = manager.get_value_by_key(dynamic_key)
        if value is not None:
            logger.info(f"✓ {original_key}: Retrieved successfully")
        else:
            logger.warning(f"✗ {original_key}: Failed to retrieve")
    
    logger.info("\n✓ Complete workflow finished successfully!")
    logger.info("")


def main():
    """Run all demos"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  PV Dynamic Keys & PDF Bytes System - Demo".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  Task 115: Standard PV PDF Dynamic Keys & PDF Bytes".center(58) + "║")
    logger.info("║" + "  Requirements: 1.3, 4.5, 14.1, 14.2".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    try:
        # Demo 1: German formatting
        demo_german_formatting()
        
        # Demo 2: Dynamic key management
        manager, calculation_data, product_data, pricing_data = demo_dynamic_key_manager()
        
        # Demo 3: PDF generation
        demo_pdf_generation(calculation_data, product_data)
        
        # Demo 4: PVDataModel
        demo_pv_data_model()
        
        # Demo 5: Complete workflow
        demo_complete_workflow()
        
        # Summary
        logger.info("=" * 60)
        logger.info("DEMO COMPLETE")
        logger.info("=" * 60)
        logger.info("\nGenerated files:")
        logger.info("  - demo_pv_calculation_results.pdf")
        logger.info("  - demo_pv_product_datasheet.pdf")
        logger.info("  - demo_pv_chart.pdf")
        logger.info("  - demo_pv_3d_visualization.pdf")
        logger.info("  - demo_pv_data_model.pdf")
        logger.info("  - workflow_calculation.pdf")
        logger.info("  - workflow_product.pdf")
        logger.info("\nAll demos completed successfully! ✓")
        logger.info("")
        
    except Exception as e:
        logger.error(f"\nDemo failed with error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
