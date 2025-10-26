#!/usr/bin/env python3
"""Demo Enhanced PDF Generator

Demonstrates the enhanced PDF generation system with dynamic pricing keys,
automatic key population, and pricing breakdown sections.
"""

import os
import sys
from typing import Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pdf_generator import PDFGenerator
    from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory
    print("✓ Successfully imported PDF generator and pricing system")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def create_sample_offer_data() -> dict[str, Any]:
    """Create sample offer data for demonstration"""
    return {
        'customer': {
            'name': 'Max Mustermann',
            'email': 'max.mustermann@example.com',
            'phone': '+49 123 456789',
            'address': 'Musterstraße 123, 12345 Musterstadt'
        },
        'offer_id': 'DEMO-2024-001',
        'date': '2024-01-15',
        'items': [
            {
                'name': 'PV-Module 400W (Tier 1)',
                'quantity': 20,
                'unit_price': 180.0,
                'total_price': 3600.0
            },
            {
                'name': 'Wechselrichter 8kW',
                'quantity': 1,
                'unit_price': 800.0,
                'total_price': 800.0
            },
            {
                'name': 'Batteriespeicher 10kWh',
                'quantity': 1,
                'unit_price': 3500.0,
                'total_price': 3500.0
            },
            {
                'name': 'Installation und Montage',
                'quantity': 1,
                'unit_price': 4705.04,
                'total_price': 4705.04
            }
        ],
        'net_total': 12605.04,
        'vat': 2394.96,
        'grand_total': 15000.0,
        'technical_data': {
            'system_power_kwp': 8.0,
            'annual_yield_kwh': 7200,
            'roof_area_m2': 45,
            'module_count': 20
        }
    }


def create_sample_pricing_data() -> dict[str, Any]:
    """Create sample pricing data for demonstration"""
    return {
        'pv_pricing': {
            'base_price': 12000.0,
            'components_total': 11500.0,
            'installation_cost': 500.0,
            'system_efficiency': 0.85
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
            'installation_total': 4705.04,
            'installation_quantity': 1,
            'installation_unit_price': 4705.04
        },
        'discounts': {
            'early_payment_discount': 300.0,
            'volume_discount': 200.0,
            'loyalty_discount': 100.0
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


def demo_basic_functionality():
    """Demonstrate basic PDF generator functionality"""
    print("\n" + "=" * 60)
    print("DEMO: Basic PDF Generator Functionality")
    print("=" * 60)

    # Create sample data
    offer_data = create_sample_offer_data()
    pricing_data = create_sample_pricing_data()

    # Create PDF generator
    generator = PDFGenerator(
        offer_data=offer_data,
        module_order=[],
        theme_name="default",
        filename="demo_basic.pdf",
        pricing_data=pricing_data
    )

    print("✓ Created PDF generator with pricing data")
    print(f"  - Offer ID: {offer_data['offer_id']}")
    print(f"  - Customer: {offer_data['customer']['name']}")
    print(f"  - Total: {offer_data['grand_total']:.2f} €")

    # Test pricing key generation
    print("\n📊 Pricing Key Generation:")
    print(f"  - Generated {len(generator.pricing_keys)} dynamic keys")

    if generator.pricing_keys:
        print("  - Sample keys:")
        for i, (key, value) in enumerate(
                list(generator.pricing_keys.items())[:5]):
            print(f"    {key}: {value}")
        if len(generator.pricing_keys) > 5:
            print(f"    ... and {len(generator.pricing_keys) - 5} more")

    return generator


def demo_dynamic_keys():
    """Demonstrate dynamic key functionality"""
    print("\n" + "=" * 60)
    print("DEMO: Dynamic Key Management")
    print("=" * 60)

    # Create sample data
    offer_data = create_sample_offer_data()
    pricing_data = create_sample_pricing_data()

    # Create PDF generator
    generator = PDFGenerator(
        offer_data=offer_data,
        module_order=[],
        theme_name="default",
        filename="demo_keys.pdf",
        pricing_data=pricing_data
    )

    # Get all dynamic keys
    all_keys = generator.get_all_dynamic_keys()

    print(f"📋 All Dynamic Keys ({len(all_keys)} total):")

    # Group keys by category
    categories = {
        'Customer': [k for k in all_keys.keys() if 'CUSTOMER' in k],
        'Offer': [k for k in all_keys.keys() if 'OFFER' in k],
        'Components': [k for k in all_keys.keys() if 'COMPONENT' in k],
        'Discounts': [k for k in all_keys.keys() if 'DISCOUNT' in k],
        'Totals': [k for k in all_keys.keys() if 'TOTAL' in k],
        'VAT': [k for k in all_keys.keys() if 'VAT' in k]
    }

    for category, keys in categories.items():
        if keys:
            print(f"\n  {category} Keys ({len(keys)}):")
            for key in keys[:3]:  # Show first 3 keys
                print(f"    {key}: {all_keys[key]}")
            if len(keys) > 3:
                print(f"    ... and {len(keys) - 3} more")

    return generator


def demo_template_population():
    """Demonstrate template placeholder population"""
    print("\n" + "=" * 60)
    print("DEMO: Template Placeholder Population")
    print("=" * 60)

    # Create sample data
    offer_data = create_sample_offer_data()
    pricing_data = create_sample_pricing_data()

    # Create PDF generator
    generator = PDFGenerator(
        offer_data=offer_data,
        module_order=[],
        theme_name="default",
        filename="demo_template.pdf",
        pricing_data=pricing_data
    )

    # Sample template content
    template_content = """
    ANGEBOT FÜR PHOTOVOLTAIKANLAGE

    Kunde: {{CUSTOMER_NAME}}
    E-Mail: {{CUSTOMER_EMAIL}}
    Telefon: {{CUSTOMER_PHONE}}

    Angebotsnummer: {{OFFER_ID}}
    Datum: {{OFFER_DATE}}

    PREISÜBERSICHT:
    Nettosumme: {{NET_TOTAL}}
    Mehrwertsteuer: {{VAT_AMOUNT}}
    Gesamtsumme: {{GROSS_TOTAL}}

    Mit freundlichen Grüßen
    Ihr Solar-Team
    """

    print("📄 Original Template:")
    print(template_content)

    # Populate template
    populated_content = generator.populate_template_placeholders(
        template_content)

    print("\n📄 Populated Template:")
    print(populated_content)

    return generator


def demo_pricing_summary():
    """Demonstrate pricing summary functionality"""
    print("\n" + "=" * 60)
    print("DEMO: Pricing Summary")
    print("=" * 60)

    # Create sample data
    offer_data = create_sample_offer_data()
    pricing_data = create_sample_pricing_data()

    # Create PDF generator
    generator = PDFGenerator(
        offer_data=offer_data,
        module_order=[],
        theme_name="default",
        filename="demo_summary.pdf",
        pricing_data=pricing_data
    )

    # Get pricing summary
    summary = generator.get_pricing_summary()

    print("📊 Pricing Summary:")
    print(f"  - Keys Generated: {summary['keys_generated']}")

    print(f"\n  Component Keys ({len(summary['components'])}):")
    for key, value in list(summary['components'].items())[:5]:
        print(f"    {key}: {value}")

    print(f"\n  Modification Keys ({len(summary['modifications'])}):")
    for key, value in list(summary['modifications'].items())[:5]:
        print(f"    {key}: {value}")

    print(f"\n  Total Keys ({len(summary['totals'])}):")
    for key, value in list(summary['totals'].items())[:5]:
        print(f"    {key}: {value}")

    return generator


def demo_pdf_creation():
    """Demonstrate actual PDF creation with pricing breakdown"""
    print("\n" + "=" * 60)
    print("DEMO: PDF Creation with Pricing Breakdown")
    print("=" * 60)

    # Create sample data
    offer_data = create_sample_offer_data()
    pricing_data = create_sample_pricing_data()

    # Define module order for PDF
    module_order = [
        {"id": "deckblatt"},
        {"id": "preisaufstellung"},
        {"id": "wirtschaftlichkeit"},
        {"id": "technische_daten"}
    ]

    # Create PDF generator
    generator = PDFGenerator(
        offer_data=offer_data,
        module_order=module_order,
        theme_name="default",
        filename="demo_complete.pdf",
        pricing_data=pricing_data
    )

    print("📄 Creating PDF with modules:")
    for module in module_order:
        print(f"  - {module['id']}")

    try:
        # Create the PDF (this would normally generate a file)
        print("\n🔄 Generating PDF...")
        print("  - Filename: demo_complete.pdf")
        print(f"  - Pricing keys: {len(generator.pricing_keys)}")
        print(f"  - Dynamic keys: {len(generator.get_all_dynamic_keys())}")

        # Note: We're not actually calling create_pdf() to avoid file creation
        # in demo
        print("✓ PDF generation setup complete")
        print("  (PDF creation skipped in demo mode)")

    except Exception as e:
        print(f"✗ Error during PDF creation: {e}")

    return generator


def main():
    """Run all demonstrations"""
    print("Enhanced PDF Generator Demo")
    print("=" * 60)
    print("This demo shows the enhanced PDF generation system with")
    print("dynamic pricing keys and automatic key population.")

    try:
        # Run demonstrations
        demo_basic_functionality()
        demo_dynamic_keys()
        demo_template_population()
        demo_pricing_summary()
        demo_pdf_creation()

        print("\n" + "=" * 60)
        print("✓ All demonstrations completed successfully!")
        print("=" * 60)

        print("\nKey Features Demonstrated:")
        print("• Dynamic pricing key generation")
        print("• Automatic key population in PDF templates")
        print("• Pricing breakdown sections")
        print("• Template placeholder replacement")
        print("• Comprehensive pricing summaries")
        print("• Error handling and fallback mechanisms")

    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
