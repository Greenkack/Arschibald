"""Demo: PDF Pricing Integration

Demonstrates the enhanced PDF generation system with integrated pricing.
Shows how dynamic pricing keys are generated and used in PDF templates.
"""


# Import the PDF pricing integration modules
try:
    from pdf_pricing_integration import (
        EnhancedPDFGenerator,
        create_pricing_breakdown_section,
        generate_enhanced_pdf_with_pricing,
        update_pdf_placeholders_with_pricing,
    )
    from pdf_pricing_templates import (
        PricingTemplateConfig,
        PricingTemplateManager,
        create_combined_pricing_template,
        create_heatpump_pricing_template,
        create_pv_pricing_template,
    )
    from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory

    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    MODULES_AVAILABLE = False


def demo_dynamic_key_generation():
    """Demonstrate dynamic key generation for pricing data"""
    print("=== Dynamic Key Generation Demo ===")

    if not MODULES_AVAILABLE:
        print("Modules not available for demo")
        return

    # Sample pricing data
    pricing_data = {
        'pv_pricing': {
            'base_price': 12000.0,
            'components_total': 11500.0,
            'installation_cost': 500.0
        },
        'components': {
            'modules_total': 3600.0,
            'inverter_total': 800.0,
            'storage_total': 3500.0,
            'installation_total': 3600.0
        },
        'discounts': {
            'early_payment_discount': 300.0,
            'volume_discount': 200.0
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

    # Create key manager and generate keys
    key_manager = DynamicKeyManager()

    # Generate keys for different categories
    for category, data in pricing_data.items():
        if isinstance(data, dict):
            try:
                category_enum = getattr(KeyCategory, category.upper(), KeyCategory.PRICING)
            except AttributeError:
                category_enum = KeyCategory.PRICING

            keys = key_manager.generate_keys(
                data,
                prefix=category.upper(),
                category=category_enum
            )
            print(f"\n{category.title()} Keys Generated: {len(keys)}")
            for key, value in list(keys.items())[:3]:  # Show first 3 keys
                print(f"  {key}: {value}")

    # Format keys for PDF
    pdf_keys = key_manager.format_for_pdf(key_manager.get_all_keys())
    print(f"\nTotal PDF Keys Generated: {len(pdf_keys)}")

    # Show registry statistics
    stats = key_manager.get_registry_stats()
    print("\nRegistry Statistics:")
    print(f"  Total Keys: {stats['total_keys']}")
    print(f"  Categories: {list(stats['categories'].keys())}")
    print(f"  Conflicts Resolved: {stats['conflicts_resolved']}")


def demo_pricing_templates():
    """Demonstrate pricing template creation and rendering"""
    print("\n=== Pricing Templates Demo ===")

    if not MODULES_AVAILABLE:
        print("Modules not available for demo")
        return

    # Create template manager
    manager = PricingTemplateManager()

    # Demo PV template
    print("\n--- PV Template ---")
    pv_template = manager.create_template('pv')
    pv_placeholders = pv_template.placeholders
    print(f"PV Template Placeholders: {len(pv_placeholders)}")

    # Show some key placeholders
    key_examples = [
        'PV_MODULES_QUANTITY',
        'PV_NET_TOTAL',
        'PV_GROSS_TOTAL'
    ]
    for key in key_examples:
        if key in pv_placeholders:
            print(f"  {key}: {pv_placeholders[key]}")

    # Demo Heat Pump template
    print("\n--- Heat Pump Template ---")
    hp_template = manager.create_template('heatpump')
    hp_placeholders = hp_template.placeholders
    print(f"Heat Pump Template Placeholders: {len(hp_placeholders)}")

    # Show some key placeholders
    hp_examples = [
        'HP_UNIT_QUANTITY',
        'HP_BEG_SUBSIDY_AMOUNT',
        'HP_NET_TOTAL'
    ]
    for key in hp_examples:
        if key in hp_placeholders:
            print(f"  {key}: {hp_placeholders[key]}")

    # Demo Combined template
    print("\n--- Combined Template ---")
    combined_template = manager.create_template('combined')
    combined_placeholders = combined_template.placeholders
    print(f"Combined Template Placeholders: {len(combined_placeholders)}")

    # Show some combined placeholders
    combined_examples = [
        'COMBINED_NET_TOTAL',
        'SYNERGY_TOTAL_BENEFIT',
        'COMBINED_PACKAGE_DISCOUNT'
    ]
    for key in combined_examples:
        if key in combined_placeholders:
            print(f"  {key}: {combined_placeholders[key]}")


def demo_template_rendering():
    """Demonstrate template rendering with actual data"""
    print("\n=== Template Rendering Demo ===")

    if not MODULES_AVAILABLE:
        print("Modules not available for demo")
        return

    # Sample pricing data for rendering
    pricing_data = {
        'components': {
            'PV_MODULES_QUANTITY': 20,
            'PV_MODULES_UNIT_PRICE': 180.0,
            'PV_MODULES_TOTAL_PRICE': 3600.0,
            'PV_INVERTER_QUANTITY': 1,
            'PV_INVERTER_UNIT_PRICE': 800.0,
            'PV_NET_TOTAL': 12605.04,
            'PV_VAT_AMOUNT': 2394.96,
            'PV_GROSS_TOTAL': 15000.0
        }
    }

    # Create template manager and render PV template
    manager = PricingTemplateManager()
    rendered = manager.render_template('pv', pricing_data)

    print("Rendered PV Template Values:")
    rendered_count = 0
    for key, value in rendered.items():
        if value and value != "":  # Only show non-empty values
            print(f"  {key}: {value}")
            rendered_count += 1
            if rendered_count >= 10:  # Limit output
                break

    print(f"\nTotal rendered values: {len([v for v in rendered.values() if v])}")


def demo_enhanced_pdf_generator():
    """Demonstrate enhanced PDF generator with pricing integration"""
    print("\n=== Enhanced PDF Generator Demo ===")

    if not MODULES_AVAILABLE:
        print("Modules not available for demo")
        return

    # Sample project data
    project_data = {
        'customer_data': {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'email': 'max@example.com',
            'phone_mobile': '+49 123 456789'
        },
        'project_details': {
            'module_quantity': 20,
            'selected_module_capacity_w': 400,
            'anlage_kwp': 8.0
        },
        'selected_module': {
            'price_euro': 180.0,
            'model_name': 'Test Module 400W'
        },
        'selected_inverter': {
            'price_euro': 800.0,
            'model_name': 'Test Inverter 8kW'
        }
    }

    # Sample analysis results
    analysis_results = {
        'anlage_kwp': 8.0,
        'final_price': 15000.0,
        'total_investment_netto': 12605.04,
        'vat_amount': 2394.96,
        'annual_savings': 1200.0
    }

    # Sample company info
    company_info = {
        'name': 'Demo Solar GmbH',
        'street': 'Teststraße 123',
        'city': 'Teststadt',
        'phone': '+49 123 456789'
    }

    # Sample pricing data
    pricing_data = {
        'components': {
            'modules_total': 3600.0,
            'inverter_total': 800.0,
            'installation_total': 3600.0
        },
        'totals': {
            'net_total': 12605.04,
            'gross_total': 15000.0
        }
    }

    # Create enhanced PDF generator
    try:
        generator = EnhancedPDFGenerator(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            pricing_data=pricing_data
        )

        print("Enhanced PDF Generator created successfully")
        print(f"Generated pricing keys: {len(generator.pricing_keys)}")

        # Generate pricing breakdown
        breakdown = generator.generate_pricing_breakdown_data()
        print(f"Pricing breakdown sections: {list(breakdown.keys())}")

        # Get enhanced dynamic data
        enhanced_data = generator.get_enhanced_dynamic_data()
        print(f"Enhanced dynamic data keys: {len(enhanced_data)}")

        # Show some enhanced data examples
        print("\nSample Enhanced Data:")
        sample_keys = ['customer_name', 'company_name']
        for key in sample_keys:
            if key in enhanced_data:
                print(f"  {key}: {enhanced_data[key]}")

        # Show pricing keys
        pricing_keys = [k for k in enhanced_data.keys() if any(
            prefix in k for prefix in ['PRICING', 'COMPONENT', 'TOTAL']
        )]
        if pricing_keys:
            print(f"\nPricing keys in enhanced data: {len(pricing_keys)}")
            for key in pricing_keys[:5]:  # Show first 5
                print(f"  {key}: {enhanced_data[key]}")

    except Exception as e:
        print(f"Error creating enhanced PDF generator: {e}")


def demo_pricing_breakdown_section():
    """Demonstrate pricing breakdown section creation"""
    print("\n=== Pricing Breakdown Section Demo ===")

    if not MODULES_AVAILABLE:
        print("Modules not available for demo")
        return

    # Sample pricing data
    pricing_data = {
        'components': {
            'modules': 3600.0,
            'inverter': 800.0,
            'storage': 3500.0,
            'installation': 3600.0
        },
        'discounts': {
            'early_payment': 300.0,
            'volume': 200.0
        },
        'vat': {
            'rate': 19.0,
            'amount': 2394.96
        },
        'totals': {
            'net': 12605.04,
            'gross': 15000.0
        }
    }

    try:
        section_data = create_pricing_breakdown_section(pricing_data)

        print("Pricing Breakdown Section created:")
        print(f"  Title: {section_data.get('title', 'N/A')}")
        print(f"  Keys: {len(section_data.get('keys', {}))}")
        print(f"  Categories: {list(section_data.get('categories', {}).keys())}")

        # Show some keys
        keys = section_data.get('keys', {})
        if keys:
            print("\nSample Keys:")
            for key, value in list(keys.items())[:5]:
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error creating pricing breakdown section: {e}")


def main():
    """Run all demos"""
    print("PDF Pricing Integration Demo")
    print("=" * 50)

    if not MODULES_AVAILABLE:
        print("Required modules not available. Please ensure all pricing modules are installed.")
        return

    try:
        demo_dynamic_key_generation()
        demo_pricing_templates()
        demo_template_rendering()
        demo_enhanced_pdf_generator()
        demo_pricing_breakdown_section()

        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Dynamic pricing key generation")
        print("✓ PDF template creation for PV, heat pump, and combined systems")
        print("✓ Template rendering with actual pricing data")
        print("✓ Enhanced PDF generator with pricing integration")
        print("✓ Pricing breakdown section creation")
        print("✓ German number formatting for currency values")

    except Exception as e:
        print(f"\nDemo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
