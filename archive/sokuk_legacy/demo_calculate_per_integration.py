"""Demonstration of Calculate Per Integration

Shows how the enhanced calculate_per engine integrates with existing product features
and provides comprehensive pricing calculations.
"""


def demo_basic_calculations():
    """Demonstrate basic calculate_per calculations"""
    print("=== Basic Calculate Per Calculations ===")

    try:
        from product_db import calculate_price_by_method

        # Test cases
        test_cases = [
            {
                'name': 'PV Modules (per piece)',
                'base_price': 180.0,
                'quantity': 25,
                'calculate_per': 'Stück',
                'expected': 4500.0
            },
            {
                'name': 'DC Cable (per meter)',
                'base_price': 8.50,
                'quantity': 75.0,
                'calculate_per': 'Meter',
                'expected': 637.5
            },
            {
                'name': 'Installation Service (lump sum)',
                'base_price': 2500.0,
                'quantity': 3,  # Should be ignored
                'calculate_per': 'pauschal',
                'expected': 2500.0
            },
            {
                'name': 'Mounting System (per kWp)',
                'base_price': 120.0,
                'quantity': 25,  # 25 modules
                'calculate_per': 'kWp',
                'product_specs': {'capacity_w': 400.0},  # 25 * 400W = 10kWp
                'expected': 1200.0  # 120 * 10kWp
            }
        ]

        for test in test_cases:
            product_specs = test.get('product_specs')
            result = calculate_price_by_method(
                test['base_price'],
                test['quantity'],
                test['calculate_per'],
                product_specs
            )

            print(f"\n{test['name']}:")
            print(f"  Base Price: {test['base_price']}€")
            print(f"  Quantity: {test['quantity']}")
            print(f"  Method: {test['calculate_per']}")
            if product_specs:
                print(f"  Specs: {product_specs}")
            print(f"  Result: {result}€")
            print(f"  Expected: {test['expected']}€")
            print(
                "  ✓ Correct" if abs(
                    result -
                    test['expected']) < 0.01 else "  ✗ Error")

    except Exception as e:
        print(f"Error in basic calculations: {e}")


def demo_feature_integration():
    """Demonstrate feature-based pricing adjustments"""
    print("\n=== Feature Integration Demonstrations ===")

    try:
        from product_db import calculate_price_by_method

        # Premium PV module with multiple features
        print("\nPremium PV Module with Features:")
        product_specs = {
            'capacity_w': 450.0,
            'technology': 'HJT',           # +50€ premium
            'feature': 'Bifazial',         # +50€ premium
            'design': 'All-Black',         # +25€ premium
            'upgrade': 'Premium',          # +100€ premium
            'efficiency_percent': 22.5,    # +50€ for high efficiency
            'category': 'Modul'
        }

        base_price = 200.0
        quantity = 20

        result = calculate_price_by_method(
            base_price, quantity, "Stück", product_specs)

        print(f"  Base Price: {base_price}€ per module")
        print(f"  Quantity: {quantity} modules")
        print(f"  Technology: {product_specs['technology']} (+50€)")
        print(f"  Feature: {product_specs['feature']} (+50€)")
        print(f"  Design: {product_specs['design']} (+25€)")
        print(f"  Upgrade: {product_specs['upgrade']} (+100€)")
        print(f"  Efficiency: {product_specs['efficiency_percent']}% (+50€)")
        print("  Total adjustments per module: 275€")
        print("  Expected total: (200 + 275) × 20 = 9500€")
        print(f"  Actual result: {result}€")

        # Advanced inverter with features
        print("\nAdvanced Inverter with Features:")
        inverter_specs = {
            'power_kw': 10.0,
            'technology': 'String',        # Base technology
            'feature': 'Notstrom',         # +150€ emergency power
            'design': 'Outdoor',           # +75€ outdoor design
            'upgrade': 'Service Plus',     # +200€ service package
            'category': 'Wechselrichter'
        }

        inverter_result = calculate_price_by_method(
            1500.0, 1, "Stück", inverter_specs)

        print("  Base Price: 1500€")
        print(f"  Feature: {inverter_specs['feature']} (+150€)")
        print(f"  Design: {inverter_specs['design']} (+75€)")
        print(f"  Upgrade: {inverter_specs['upgrade']} (+200€)")
        print("  Expected total: 1500 + 150 + 75 + 200 = 1925€")
        print(f"  Actual result: {inverter_result}€")

    except Exception as e:
        print(f"Error in feature integration: {e}")


def demo_enhanced_product_pricing():
    """Demonstrate enhanced product pricing with detailed breakdown"""
    print("\n=== Enhanced Product Pricing Breakdown ===")

    try:
        from product_db import calculate_enhanced_product_pricing

        # Create a comprehensive product example
        premium_product = {
            'id': 1,
            'category': 'Modul',
            'model_name': 'SolarTech Premium HJT-450',
            'brand': 'SolarTech',
            'price_euro': 220.0,
            'calculate_per': 'Stück',
            'capacity_w': 450.0,
            'technology': 'HJT',
            'feature': 'Bifazial',
            'design': 'All-Black',
            'upgrade': 'Premium',
            'efficiency_percent': 22.8,
            'warranty_years': 30,
            'length_m': 2.1,
            'width_m': 1.05
        }

        quantity = 22  # For ~10kWp system
        system_context = {
            'system_capacity_kwp': 9.9,  # 22 × 450W = 9.9kWp
            'installation_area_m2': 50.0
        }

        result = calculate_enhanced_product_pricing(
            premium_product, quantity, system_context)

        if result['success']:
            print(f"\nProduct: {result['model_name']}")
            print(f"Category: {result['category']}")
            print(
                f"Base Price: {
                    result['base_price']}€ per {
                    result['calculation_method']}")
            print(f"Quantity: {result['quantity']}")
            print(f"Calculation Factor: {result['calculation_factor']}")

            print("\nFeature Adjustments:")
            for feature, adjustment in result['price_adjustments'].items():
                print(f"  {feature}: +{adjustment}€")

            print("\nCalculation Notes:")
            for note in result['calculation_notes']:
                print(f"  • {note}")

            print(f"\nFinal Total: {result['total_price']}€")

            if result['validation_warnings']:
                print("\nWarnings:")
                for warning in result['validation_warnings']:
                    print(f"  ⚠ {warning}")
        else:
            print(f"Error: {result['error']}")

    except Exception as e:
        print(f"Error in enhanced product pricing: {e}")


def demo_system_pricing():
    """Demonstrate complete system pricing with mixed calculation methods"""
    print("\n=== Complete System Pricing ===")

    try:

        # Define system components with different calculation methods
        components = [
            {
                'product_data': {
                    'id': 1,
                    'category': 'Modul',
                    'model_name': 'SolarTech ST-400',
                    'brand': 'SolarTech',
                    'price_euro': 180.0,
                    'calculate_per': 'Stück',
                    'capacity_w': 400.0,
                    'technology': 'Monokristallin',
                    'feature': 'Halbzellen',
                    'design': 'All-Black',
                    'efficiency_percent': 20.5
                },
                'quantity': 25
            },
            {
                'product_data': {
                    'id': 2,
                    'category': 'Wechselrichter',
                    'model_name': 'InverterPro IP-8000',
                    'brand': 'InverterPro',
                    'price_euro': 1200.0,
                    'calculate_per': 'Stück',
                    'power_kw': 8.0,
                    'technology': 'String',
                    'feature': 'WiFi'
                },
                'quantity': 1
            },
            {
                'product_data': {
                    'id': 3,
                    'category': 'Kabel',
                    'model_name': 'CableTech DC-6mm',
                    'brand': 'CableTech',
                    'price_euro': 8.50,
                    'calculate_per': 'Meter'
                },
                'quantity': 80.0
            },
            {
                'product_data': {
                    'id': 4,
                    'category': 'Montagesystem',
                    'model_name': 'MountTech Roof System',
                    'brand': 'MountTech',
                    'price_euro': 120.0,
                    'calculate_per': 'kWp'
                },
                'quantity': 1
            },
            {
                'product_data': {
                    'id': 5,
                    'category': 'Dienstleistung',
                    'model_name': 'Professional Installation',
                    'brand': 'InstallPro',
                    'price_euro': 2800.0,
                    'calculate_per': 'pauschal',
                    'labor_hours': 18.0
                },
                'quantity': 1
            }
        ]

        system_context = {
            'system_capacity_kwp': 10.0,  # 25 × 400W = 10kWp
            'installation_area_m2': 60.0,
            'labor_hours': 18.0
        }

        print("System Configuration:")
        print(f"  Total Capacity: {system_context['system_capacity_kwp']}kWp")
        print(
            f"  Installation Area: {
                system_context['installation_area_m2']}m²")
        print(f"  Labor Hours: {system_context['labor_hours']}h")

        print("\nComponents:")
        total_manual = 0.0

        for i, comp in enumerate(components, 1):
            product = comp['product_data']
            quantity = comp['quantity']

            # Calculate individual component pricing
            from product_db import calculate_enhanced_product_pricing
            comp_result = calculate_enhanced_product_pricing(
                product, quantity, system_context)

            if comp_result['success']:
                print(f"\n{i}. {product['model_name']}")
                print(f"   Category: {product['category']}")
                print(f"   Method: {product['calculate_per']}")
                print(
                    f"   Base: {
                        product['price_euro']}€ × {quantity} = {
                        product['price_euro'] *
                        quantity}€")

                if comp_result['price_adjustments']:
                    adj_total = sum(comp_result['price_adjustments'].values())
                    if comp_result['calculation_method'] == 'Stück':
                        adj_total *= quantity
                    print(f"   Adjustments: +{adj_total}€")

                print(f"   Total: {comp_result['total_price']}€")
                total_manual += comp_result['total_price']

        print(f"\nManual Total: {total_manual}€")

    except Exception as e:
        print(f"Error in system pricing: {e}")


def demo_validation():
    """Demonstrate integration validation"""
    print("\n=== Integration Validation ===")

    try:
        from product_db import validate_calculate_per_integration

        result = validate_calculate_per_integration()

        if result['success']:
            print("✓ Enhanced pricing engine available")
            print(
                f"✓ Supported calculation methods: {
                    ', '.join(
                        result['supported_methods'])}")

            print("\nValidation Tests:")
            for test in result['test_results']:
                status = "✓" if test.get('passed', False) else "✗"
                print(f"  {status} {test['test']}")
                if 'expected' in test and 'actual' in test:
                    print(
                        f"    Expected: {
                            test['expected']}, Got: {
                            test['actual']}")
                if 'error' in test:
                    print(f"    Error: {test['error']}")

            summary = result['summary']
            print("\nSummary:")
            print(f"  Total Tests: {summary['total_tests']}")
            print(f"  Passed: {summary['passed_tests']}")
            print(f"  Failed: {summary['failed_tests']}")
            print(f"  Success Rate: {summary['success_rate']:.1f}%")

        else:
            print(f"✗ Validation failed: {result['error']}")
            if result.get('fallback_available'):
                print("  Fallback calculation available")

    except Exception as e:
        print(f"Error in validation: {e}")


def main():
    """Run all demonstrations"""
    print("Calculate Per Integration Demonstration")
    print("=" * 50)

    try:
        demo_basic_calculations()
        demo_feature_integration()
        demo_enhanced_product_pricing()
        demo_system_pricing()
        demo_validation()

        print("\n" + "=" * 50)
        print("Demonstration completed successfully!")

    except Exception as e:
        print(f"\nDemonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
