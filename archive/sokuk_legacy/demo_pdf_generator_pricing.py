"""Demo: Enhanced PDF Generator with Pricing Integration

Demonstrates the enhanced PDF generation system with integrated dynamic pricing.
Shows automatic key population and pricing breakdown sections in PDF output.
"""

import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pdf_generator import PDFGenerator
    from pdf_pricing_integration import (
        EnhancedPDFGenerator,
        generate_enhanced_pdf_with_pricing,
    )
    from pdf_pricing_templates import PricingTemplateConfig, PricingTemplateManager
    from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are available")
    sys.exit(1)


def create_sample_data() -> tuple:
    """Create sample data for demonstration"""

    # Sample offer data
    offer_data = {
        'customer': {
            'name': 'Max Mustermann',
            'email': 'max.mustermann@example.com',
            'phone': '+49 123 456789',
            'address': 'Musterstraße 123, 12345 Musterstadt'
        },
        'date': '2024-01-15',
        'offer_id': 'OFF-2024-001',
        'items': [
            {
                'name': 'PV-Module 400W (Tier 1)',
                'quantity': 20,
                'unit_price': 180.0,
                'total_price': 3600.0,
                'description': 'Hocheffiziente monokristalline PV-Module'
            },
            {
                'name': 'Wechselrichter 8kW',
                'quantity': 1,
                'unit_price': 800.0,
                'total_price': 800.0,
                'description': 'String-Wechselrichter mit Monitoring'
            },
            {
                'name': 'Batteriespeicher 10kWh',
                'quantity': 1,
                'unit_price': 3500.0,
                'total_price': 3500.0,
                'description': 'Lithium-Ionen Batteriespeicher'
            },
            {
                'name': 'Installation und Inbetriebnahme',
                'quantity': 1,
                'unit_price': 2500.0,
                'total_price': 2500.0,
                'description': 'Komplette Installation inkl. Netzanschluss'
            }
        ],
        'net_total': 12605.04,
        'vat': 2394.96,
        'grand_total': 15000.0
    }

    # Sample module order for PDF
    module_order = [
        {"id": "deckblatt"},
        {"id": "anschreiben"},
        {"id": "preisaufstellung"},
        {"id": "angebotstabelle"}
    ]

    # Sample project data
    project_data = {
        'customer_data': {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'email': 'max.mustermann@example.com',
            'phone_mobile': '+49 123 456789'
        },
        'project_details': {
            'module_quantity': 20,
            'selected_module_capacity_w': 400,
            'anlage_kwp': 8.0,
            'roof_orientation': 'Süd',
            'roof_inclination': 30
        },
        'selected_module': {
            'price_euro': 180.0,
            'model_name': 'Premium Solar Module 400W',
            'manufacturer': 'SolarTech GmbH',
            'efficiency_percent': 21.5
        },
        'selected_inverter': {
            'price_euro': 800.0,
            'model_name': 'Smart Inverter 8kW',
            'manufacturer': 'InverterPro',
            'efficiency_percent': 97.5
        },
        'selected_storage': {
            'price_euro': 3500.0,
            'model_name': 'PowerStorage 10kWh',
            'manufacturer': 'BatteryTech',
            'capacity_kwh': 10.0
        }
    }

    # Sample analysis results
    analysis_results = {
        'anlage_kwp': 8.0,
        'final_price': 15000.0,
        'total_investment_netto': 12605.04,
        'total_investment_brutto': 15000.0,
        'vat_amount': 2394.96,
        'annual_production_kwh': 8500.0,
        'annual_savings': 1200.0,
        'payback_period': 12.5,
        'roi_percent': 8.2,
        'self_consumption_rate': 65.0,
        'feed_in_kwh': 2975.0
    }

    # Sample company info
    company_info = {
        'name': 'SolarExperts GmbH',
        'street': 'Sonnenallee 456',
        'zip_code': '10115',
        'city': 'Berlin',
        'phone': '+49 30 12345678',
        'email': 'info@solarexperts.de',
        'website': 'www.solarexperts.de',
        'tax_number': 'DE123456789',
        'managing_director': 'Dr. Solar Expert'
    }

    # Sample comprehensive pricing data
    pricing_data = {
        'pv_pricing': {
            'base_price': 12000.0,
            'components_total': 11500.0,
            'installation_cost': 2500.0,
            'net_total': 12605.04,
            'vat_amount': 2394.96,
            'gross_total': 15000.0
        },
        'components': {
            'modules_total': 3600.0,
            'modules_quantity': 20,
            'modules_unit_price': 180.0,
            'inverter_total': 800.0,
            'inverter_quantity': 1,
            'inverter_unit_price': 800.0,
            'storage_total': 3500.0,
            'storage_quantity': 1,
            'storage_unit_price': 3500.0,
            'installation_total': 2500.0,
            'monitoring_system': 250.0,
            'surge_protection': 150.0
        },
        'discounts': {
            'early_payment_discount': 300.0,
            'volume_discount': 200.0,
            'seasonal_discount': 100.0
        },
        'surcharges': {
            'rush_order_surcharge': 150.0,
            'weekend_installation': 100.0
        },
        'vat': {
            'vat_rate': 19.0,
            'vat_amount': 2394.96,
            'net_amount': 12605.04
        },
        'totals': {
            'net_total': 12605.04,
            'gross_total': 15000.0,
            'total_discounts': 600.0,
            'total_surcharges': 250.0
        }
    }

    return offer_data, module_order, project_data, analysis_results, company_info, pricing_data


def demo_basic_pdf_generator():
    """Demonstrate basic PDF generator with pricing integration"""
    print("=== Demo: Basic PDF Generator with Pricing ===")

    offer_data, module_order, project_data, analysis_results, company_info, pricing_data = create_sample_data()

    # Create PDF generator with pricing data
    generator = PDFGenerator(
        offer_data=offer_data,
        module_order=module_order,
        theme_name="default",
        filename="demo_basic_pricing.pdf",
        pricing_data=pricing_data
    )

    print(
        f"Created PDF generator with {len(generator.pricing_keys)} pricing keys")

    # Show some generated keys
    if generator.pricing_keys:
        print("\nSample generated pricing keys:")
        for i, (key, value) in enumerate(
                list(generator.pricing_keys.items())[:5]):
            print(f"  {key}: {value}")
        if len(generator.pricing_keys) > 5:
            print(f"  ... and {len(generator.pricing_keys) - 5} more keys")

    # Generate PDF
    try:
        generator.create_pdf()
        print("\n✓ PDF generated successfully: demo_basic_pricing.pdf")

        # Check file size
        if os.path.exists("demo_basic_pricing.pdf"):
            file_size = os.path.getsize("demo_basic_pricing.pdf")
            print(f"  File size: {file_size:,} bytes")

    except Exception as e:
        print(f"✗ Error generating PDF: {e}")


def demo_enhanced_pdf_generator():
    """Demonstrate enhanced PDF generator"""
    print("\n=== Demo: Enhanced PDF Generator ===")

    offer_data, module_order, project_data, analysis_results, company_info, pricing_data = create_sample_data()

    # Create enhanced PDF generator
    enhanced_generator = EnhancedPDFGenerator(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_info,
        pricing_data=pricing_data
    )

    print(
        f"Created enhanced PDF generator with {len(enhanced_generator.pricing_keys)} pricing keys")

    # Generate pricing breakdown data
    breakdown = enhanced_generator.generate_pricing_breakdown_data()
    print(f"\nGenerated pricing breakdown with {len(breakdown)} categories:")
    for category, data in breakdown.items():
        if isinstance(data, dict):
            print(f"  {category}: {len(data)} items")
        else:
            print(f"  {category}: {type(data).__name__}")

    # Generate enhanced dynamic data
    enhanced_data = enhanced_generator.get_enhanced_dynamic_data()
    print(f"\nEnhanced dynamic data contains {len(enhanced_data)} keys")

    # Generate PDF
    try:
        pdf_bytes = enhanced_generator.generate_pdf_with_pricing(
            filename="demo_enhanced_pricing.pdf"
        )

        if pdf_bytes:
            print("✓ Enhanced PDF generated successfully: demo_enhanced_pricing.pdf")
            print(f"  PDF size: {len(pdf_bytes):,} bytes")
        else:
            print("✗ Enhanced PDF generation returned no data")

    except Exception as e:
        print(f"✗ Error generating enhanced PDF: {e}")


def demo_pricing_templates():
    """Demonstrate pricing template system"""
    print("\n=== Demo: Pricing Templates ===")

    # Create template manager
    template_manager = PricingTemplateManager()

    # Create PV template
    pv_template = template_manager.create_template('pv')
    print(
        f"Created PV template with {len(pv_template.placeholders)} placeholders")

    # Create heat pump template
    hp_template = template_manager.create_template('heatpump')
    print(
        f"Created heat pump template with {len(hp_template.placeholders)} placeholders")

    # Create combined template
    combined_template = template_manager.create_template('combined')
    print(
        f"Created combined template with {len(combined_template.placeholders)} placeholders")

    # Sample pricing data for rendering
    sample_pricing = {
        'PV_MODULES_QUANTITY': 20,
        'PV_MODULES_UNIT_PRICE': 180.0,
        'PV_MODULES_TOTAL_PRICE': 3600.0,
        'PV_NET_TOTAL': 12605.04,
        'PV_VAT_AMOUNT': 2394.96,
        'PV_GROSS_TOTAL': 15000.0
    }

    # Render PV template
    rendered_pv = template_manager.render_template('pv', sample_pricing)
    print(f"\nRendered PV template with {len(rendered_pv)} populated fields")

    # Show some rendered values
    print("\nSample rendered PV values:")
    for key, value in list(rendered_pv.items())[:3]:
        if value:  # Only show non-empty values
            print(f"  {key}: {value}")

    # Export template documentation
    pv_docs = template_manager.export_template_documentation('pv')
    print(f"\nPV template documentation contains {len(pv_docs)} sections")


def demo_dynamic_key_manager():
    """Demonstrate dynamic key manager"""
    print("\n=== Demo: Dynamic Key Manager ===")

    # Create key manager
    key_manager = DynamicKeyManager()

    # Sample data for key generation
    sample_data = {
        'modules': {
            'quantity': 20,
            'unit_price': 180.0,
            'total_price': 3600.0
        },
        'inverter': {
            'quantity': 1,
            'unit_price': 800.0,
            'total_price': 800.0
        },
        'totals': {
            'net_total': 12605.04,
            'vat_amount': 2394.96,
            'gross_total': 15000.0
        }
    }

    # Generate keys for different categories
    component_keys = key_manager.generate_keys(
        sample_data,
        prefix="COMPONENTS",
        category=KeyCategory.COMPONENTS
    )

    print(f"Generated {len(component_keys)} component keys")

    # Get all keys
    all_keys = key_manager.get_all_keys()
    print(f"Total keys in registry: {len(all_keys)}")

    # Get keys by category
    component_category_keys = key_manager.get_keys_by_category(
        KeyCategory.COMPONENTS)
    print(f"Component category keys: {len(component_category_keys)}")

    # Format for PDF
    pdf_keys = key_manager.format_for_pdf(all_keys)
    print(f"PDF-formatted keys: {len(pdf_keys)}")

    # Show some formatted keys
    print("\nSample PDF-formatted keys:")
    for i, (key, value) in enumerate(list(pdf_keys.items())[:3]):
        print(f"  {key}: {value}")


def demo_integration_function():
    """Demonstrate the integration function"""
    print("\n=== Demo: Integration Function ===")

    offer_data, module_order, project_data, analysis_results, company_info, pricing_data = create_sample_data()

    # Use the integration function
    try:
        pdf_bytes = generate_enhanced_pdf_with_pricing(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            pricing_data=pricing_data,
            filename="demo_integration.pdf"
        )

        if pdf_bytes:
            print("✓ Integration function generated PDF successfully")
            print(f"  PDF size: {len(pdf_bytes):,} bytes")
            print("  Saved as: demo_integration.pdf")
        else:
            print("✗ Integration function returned no data")

    except Exception as e:
        print(f"✗ Error with integration function: {e}")


def main():
    """Run all demonstrations"""
    print("Enhanced PDF Generator with Pricing Integration - Demo")
    print("=" * 60)

    try:
        # Run all demos
        demo_basic_pdf_generator()
        demo_enhanced_pdf_generator()
        demo_pricing_templates()
        demo_dynamic_key_manager()
        demo_integration_function()

        print("\n" + "=" * 60)
        print("Demo completed successfully!")

        # List generated files
        generated_files = [
            "demo_basic_pricing.pdf",
            "demo_enhanced_pricing.pdf",
            "demo_integration.pdf"
        ]

        print("\nGenerated files:")
        for filename in generated_files:
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"  ✓ {filename} ({file_size:,} bytes)")
            else:
                print(f"  ✗ {filename} (not found)")

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
