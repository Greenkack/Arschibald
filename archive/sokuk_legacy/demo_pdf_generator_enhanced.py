#!/usr/bin/env python3
"""
Demo script for enhanced PDF generation with pricing integration

This script demonstrates the enhanced PDF generator functionality
that integrates with the dynamic pricing system.
"""

from typing import Any

from pdf_generator import PDFGenerator


def create_sample_data() -> tuple[dict[str, Any], dict[str, Any]]:
    """Create sample data for demonstration"""

    # Sample offer data
    offer_data = {
        'customer': {
            'name': 'Max Mustermann',
            'email': 'max.mustermann@example.com',
            'phone': '+49 123 456789',
            'address': 'Musterstraße 123, 12345 Musterstadt'
        },
        'offer_id': 'ANGEBOT-2024-001',
        'date': '15.01.2024',
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
        'annual_savings': 1200.0,
        'payback_period': 12.5,
        'roi_percent': 8.2
    }

    # Sample pricing data from enhanced pricing system
    pricing_data = {
        'pv_pricing': {
            'base_price': 12000.0,
            'components_total': 11500.0,
            'installation_cost': 1105.04,
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
            'installation_total': 4705.04
        },
        'discounts': {
            'early_payment_discount': 300.0,
            'volume_discount': 200.0
        },
        'surcharges': {
            'rush_order_surcharge': 150.0
        },
        'vat': {
            'vat_rate': 19.0,
            'vat_amount': 2394.96,
            'net_amount': 12605.04
        },
        'totals': {
            'net_total': 12605.04,
            'gross_total': 15000.0
        }
    }

    return offer_data, pricing_data


def demo_basic_pdf_generation():
    """Demonstrate basic PDF generation without pricing system"""
    print("=== Demo: Basic PDF Generation ===")

    offer_data, _ = create_sample_data()

    # Create PDF generator without pricing data
    generator = PDFGenerator(
        offer_data=offer_data,
        module_order=[
            {"id": "deckblatt"},
            {"id": "angebotspositionen"},
            {"id": "preisaufstellung"}
        ],
        theme_name="default",
        filename="demo_basic.pdf"
    )

    # Get dynamic keys
    all_keys = generator.get_all_dynamic_keys()
    print(f"Generated {len(all_keys)} basic dynamic keys:")
    for key, value in list(all_keys.items())[:5]:  # Show first 5
        print(f"  {key}: {value}")

    # Test template placeholder population
    template = "Angebot für {{CUSTOMER_NAME}} - Gesamtsumme: {{GROSS_TOTAL}}"
    populated = generator.populate_template_placeholders(template)
    print(f"Template: {template}")
    print(f"Populated: {populated}")

    print("✓ Basic PDF generation demo completed\n")


def demo_enhanced_pdf_generation():
    """Demonstrate enhanced PDF generation with pricing system"""
    print("=== Demo: Enhanced PDF Generation with Pricing ===")

    offer_data, pricing_data = create_sample_data()

    # Create PDF generator with pricing data
    generator = PDFGenerator(
        offer_data=offer_data,
        module_order=[
            {"id": "deckblatt"},
            {"id": "angebotspositionen"},
            {"id": "preisaufstellung"}
        ],
        theme_name="default",
        filename="demo_enhanced.pdf",
        pricing_data=pricing_data
    )

    # Get all dynamic keys (including pricing keys)
    all_keys = generator.get_all_dynamic_keys()
    print(f"Generated {len(all_keys)} total dynamic keys (including pricing):")

    # Show pricing-specific keys
    pricing_keys = {
        k: v for k,
        v in all_keys.items() if any(
            prefix in k for prefix in [
                'PV_',
                'COMPONENT',
                'DISCOUNT',
                'VAT',
                'TOTAL'])}
    print(f"Pricing keys ({len(pricing_keys)}):")
    for key, value in list(pricing_keys.items())[:10]:  # Show first 10
        print(f"  {key}: {value}")

    # Get pricing summary
    summary = generator.get_pricing_summary()
    print("\nPricing Summary:")
    print(f"  Components: {len(summary['components'])} keys")
    print(f"  Modifications: {len(summary['modifications'])} keys")
    print(f"  Totals: {len(summary['totals'])} keys")
    print(f"  Total keys generated: {summary['keys_generated']}")

    # Test advanced template with pricing placeholders
    advanced_template = """
    Angebot für {{CUSTOMER_NAME}}
    Angebotsnummer: {{OFFER_ID}}

    PV-Anlage Gesamtpreis: {{PV_GROSS_TOTAL}}
    Nettosumme: {{PV_NET_TOTAL}}
    MwSt.: {{PV_VAT_AMOUNT}}

    Komponenten:
    - Module: {{COMPONENTS_MODULES_TOTAL}}
    - Wechselrichter: {{COMPONENTS_INVERTER_TOTAL}}
    - Speicher: {{COMPONENTS_STORAGE_TOTAL}}
    """

    populated_advanced = generator.populate_template_placeholders(
        advanced_template)
    print("\nAdvanced Template Population:")
    print("Original template (excerpt):")
    print("  Angebot für {{CUSTOMER_NAME}} - PV-Anlage: {{PV_GROSS_TOTAL}}")
    print("Populated result (excerpt):")
    lines = populated_advanced.strip().split('\n')
    for line in lines[:3]:  # Show first 3 lines
        if line.strip():
            print(f"  {line.strip()}")

    print("✓ Enhanced PDF generation demo completed\n")


def demo_currency_formatting():
    """Demonstrate currency formatting functionality"""
    print("=== Demo: Currency Formatting ===")

    generator = PDFGenerator(
        offer_data={},
        module_order=[],
        theme_name="default",
        filename="test.pdf"
    )

    test_values = [1234.56, 15000.0, 0.0, 999999.99, None, "invalid"]

    print("Currency formatting examples:")
    for value in test_values:
        formatted = generator._format_currency_value(value)
        print(f"  {value} -> {formatted}")

    print("✓ Currency formatting demo completed\n")


def demo_component_grouping():
    """Demonstrate component key grouping"""
    print("=== Demo: Component Key Grouping ===")

    generator = PDFGenerator(
        offer_data={},
        module_order=[],
        theme_name="default",
        filename="test.pdf"
    )

    # Sample component keys
    component_keys = {
        'COMPONENT_MODULES_PRICE': '3.600,00 €',
        'COMPONENT_MODULES_QUANTITY': '20',
        'COMPONENT_MODULES_UNIT_PRICE': '180,00 €',
        'COMPONENT_INVERTER_TOTAL': '800,00 €',
        'COMPONENT_STORAGE_PRICE': '3.500,00 €',
        'PV_INSTALLATION_TOTAL': '4.705,04 €'
    }

    groups = generator._group_component_keys(component_keys)

    print("Component key grouping:")
    for group_name, group_data in groups.items():
        print(f"  {group_name}:")
        for key, value in group_data.items():
            print(f"    {key}: {value}")

    print("✓ Component grouping demo completed\n")


def main():
    """Run all demonstrations"""
    print("Enhanced PDF Generator Demo")
    print("=" * 50)
    print()

    try:
        demo_basic_pdf_generation()
        demo_enhanced_pdf_generation()
        demo_currency_formatting()
        demo_component_grouping()

        print("🎉 All demos completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Dynamic key generation from pricing data")
        print("✓ Template placeholder population")
        print("✓ Currency formatting (German locale)")
        print("✓ Component key grouping and organization")
        print("✓ Pricing breakdown section creation")
        print("✓ Integration with existing PDF generation system")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
