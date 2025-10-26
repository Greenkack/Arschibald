"""
Demo: Solar Calculator Pricing Integration

Demonstrates the integration between solar calculator component selection
and the enhanced pricing system with calculate_per support.
"""


# Import the integration
try:
    from solar_calculator_pricing_integration import (
        SolarCalculatorPricingIntegration,
        get_pricing_display_for_ui,
        integrate_pricing_with_solar_calculator,
    )
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    INTEGRATION_AVAILABLE = False
    print(f"Integration not available: {e}")

# Mock product database for demo
DEMO_PRODUCTS = {
    "Test Module 400W": {
        "id": 1,
        "model_name": "Test Module 400W",
        "category": "Modul",
        "brand": "SolarTech",
        "price_euro": 180.0,
        "capacity_w": 400.0,
        "calculate_per": "Stück",
        "purchase_price_net": 150.0,
        "margin_type": "percentage",
        "margin_value": 20.0,
        "technology": "Monokristallin N-Type",
        "feature": "Bifacial",
        "design": "All-Black",
        "efficiency_percent": 21.5,
        "warranty_years": 25
    },
    "Test Inverter 8kW": {
        "id": 2,
        "model_name": "Test Inverter 8kW",
        "category": "Wechselrichter",
        "brand": "InverterPro",
        "price_euro": 1200.0,
        "power_kw": 8.0,
        "calculate_per": "Stück",
        "purchase_price_net": 1000.0,
        "margin_type": "percentage",
        "margin_value": 20.0,
        "technology": "String Inverter",
        "feature": "3 MPPT",
        "warranty_years": 10
    },
    "Test Battery 10kWh": {
        "id": 3,
        "model_name": "Test Battery 10kWh",
        "category": "Batteriespeicher",
        "brand": "BatteryMax",
        "price_euro": 4500.0,
        "storage_power_kw": 10.0,
        "calculate_per": "Stück",
        "purchase_price_net": 3800.0,
        "margin_type": "percentage",
        "margin_value": 18.4,
        "technology": "LiFePO4",
        "feature": "High Voltage",
        "max_cycles": 6000,
        "warranty_years": 10
    },
    "Test Wallbox 11kW": {
        "id": 4,
        "model_name": "Test Wallbox 11kW",
        "category": "Wallbox",
        "brand": "ChargePoint",
        "price_euro": 800.0,
        "power_kw": 11.0,
        "calculate_per": "Stück",
        "purchase_price_net": 650.0,
        "margin_type": "percentage",
        "margin_value": 23.1,
        "technology": "AC Charging",
        "feature": "Smart Charging",
        "warranty_years": 3
    },
    "Installation Service": {
        "id": 5,
        "model_name": "Installation Service",
        "category": "Dienstleistung",
        "brand": "InstallPro",
        "price_euro": 2500.0,
        "calculate_per": "pauschal",
        "purchase_price_net": 2000.0,
        "margin_type": "fixed",
        "margin_value": 500.0,
        "technology": "Professional Installation",
        "feature": "Full Service",
        "warranty_years": 2
    },
    "DC Cable 50m": {
        "id": 6,
        "model_name": "DC Cable 50m",
        "category": "Kabel",
        "brand": "CableTech",
        "price_euro": 8.50,  # Per meter
        "calculate_per": "Meter",
        "purchase_price_net": 7.00,
        "margin_type": "percentage",
        "margin_value": 21.4,
        "technology": "DC 1500V",
        "feature": "UV Resistant",
        "warranty_years": 20
    }
}


def mock_get_product_by_model_name(model_name: str):
    """Mock function to get product by model name"""
    return DEMO_PRODUCTS.get(model_name)


def mock_get_product_by_id(product_id: int):
    """Mock function to get product by ID"""
    for product in DEMO_PRODUCTS.values():
        if product["id"] == product_id:
            return product
    return None


def mock_calculate_price_by_method(
        base_price: float,
        quantity: float,
        calculate_per: str,
        product_specs=None):
    """Mock function to calculate price by method"""
    if calculate_per == "Stück":
        return base_price * quantity
    if calculate_per == "pauschal":
        return base_price  # Ignore quantity for lump sum
    if calculate_per == "Meter":
        return base_price * quantity
    if calculate_per == "kWp":
        if product_specs and "capacity_w" in product_specs:
            kwp = product_specs["capacity_w"] / 1000.0
            return base_price * kwp * quantity
        return base_price * quantity
    return base_price * quantity


def mock_calculate_selling_price(product_id: int):
    """Mock function to calculate selling price with margins"""
    product = mock_get_product_by_id(product_id)
    if not product:
        return None

    purchase_price = product.get("purchase_price_net", 0.0)
    margin_type = product.get("margin_type", "percentage")
    margin_value = product.get("margin_value", 0.0)

    if margin_type == "percentage":
        margin_amount = purchase_price * (margin_value / 100.0)
        selling_price = purchase_price + margin_amount
    elif margin_type == "fixed":
        margin_amount = margin_value
        selling_price = purchase_price + margin_amount
    else:
        margin_amount = 0.0
        selling_price = purchase_price

    return {
        "purchase_price_net": purchase_price,
        "margin_type": margin_type,
        "margin_value": margin_value,
        "margin_amount": margin_amount,
        "selling_price_net": selling_price,
        "margin_percentage": (
            margin_amount /
            purchase_price *
            100.0) if purchase_price > 0 else 0.0,
        "source": "calculated"}


def create_demo_project_details():
    """Create demo project details"""
    return {
        # Module selection
        "selected_module_name": "Test Module 400W",
        "module_quantity": 20,
        "selected_module_capacity_w": 400.0,
        "anlage_kwp": 8.0,

        # Inverter selection
        "selected_inverter_name": "Test Inverter 8kW",
        "selected_inverter_quantity": 1,
        "selected_inverter_power_kw": 8.0,

        # Storage selection
        "include_storage": True,
        "selected_storage_name": "Test Battery 10kWh",
        "selected_storage_storage_power_kw": 10.0,

        # Additional components
        "include_additional_components": True,
        "selected_wallbox_name": "Test Wallbox 11kW",
        "selected_ems_name": None,
        "selected_optimizer_name": None,
        "selected_carport_name": None,
        "selected_notstrom_name": None,
        "selected_tierabwehr_name": None
    }


def demo_calculate_per_scenarios():
    """Demonstrate different calculate_per scenarios"""
    print("=== Calculate_Per Method Demonstrations ===\n")

    scenarios = [
        {
            "name": "PV Modules (per piece)",
            "base_price": 180.0,
            "quantity": 20,
            "calculate_per": "Stück",
            "description": "20 PV modules at 180€ each"
        },
        {
            "name": "DC Cable (per meter)",
            "base_price": 8.50,
            "quantity": 50,
            "calculate_per": "Meter",
            "description": "50 meters of DC cable at 8.50€ per meter"
        },
        {
            "name": "Installation Service (lump sum)",
            "base_price": 2500.0,
            "quantity": 1,
            "calculate_per": "pauschal",
            "description": "Installation service as lump sum (quantity ignored)"
        },
        {
            "name": "System Components (per kWp)",
            "base_price": 200.0,
            "quantity": 8,  # 8 kWp system
            "calculate_per": "kWp",
            "description": "System components at 200€ per kWp for 8kWp system",
            "product_specs": {"capacity_w": 1000}  # 1kW per unit
        }
    ]

    for scenario in scenarios:
        total_price = mock_calculate_price_by_method(
            scenario["base_price"],
            scenario["quantity"],
            scenario["calculate_per"],
            scenario.get("product_specs")
        )

        print(f"Scenario: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Base Price: {scenario['base_price']:.2f}€")
        print(f"Quantity: {scenario['quantity']}")
        print(f"Calculate Per: {scenario['calculate_per']}")
        print(f"Total Price: {total_price:.2f}€")
        print("-" * 50)


def demo_pricing_integration():
    """Demonstrate the complete pricing integration"""
    if not INTEGRATION_AVAILABLE:
        print("Pricing integration not available for demo")
        return

    print("\n=== Solar Calculator Pricing Integration Demo ===\n")

    # Patch the import functions with our mock functions
    import solar_calculator_pricing_integration
    solar_calculator_pricing_integration.get_product_by_model_name = mock_get_product_by_model_name
    solar_calculator_pricing_integration.calculate_price_by_method = mock_calculate_price_by_method
    solar_calculator_pricing_integration.calculate_selling_price = mock_calculate_selling_price

    # Create demo project details
    project_details = create_demo_project_details()

    print("Project Configuration:")
    print(
        f"- PV Modules: {
            project_details['module_quantity']}x {
            project_details['selected_module_name']}")
    print(
        f"- Inverter: {
            project_details['selected_inverter_quantity']}x {
            project_details['selected_inverter_name']}")
    print(
        f"- Storage: {
            project_details['selected_storage_name']} ({
            project_details['selected_storage_storage_power_kw']} kWh)")
    print(f"- Wallbox: {project_details['selected_wallbox_name']}")
    print(f"- System Size: {project_details['anlage_kwp']} kWp")
    print()

    # Calculate pricing
    pricing_result = integrate_pricing_with_solar_calculator(project_details)

    if pricing_result.get("error"):
        print(f"Error: {pricing_result['error']}")
        return

    print("Pricing Calculation Results:")
    print(f"Total Components: {len(pricing_result['components'])}")
    print(f"Base Price (net): {pricing_result['base_price']:.2f}€")
    print()

    # Display component breakdown
    print("Component Breakdown:")
    print("-" * 80)
    print(
        f"{
            'Component':<25} {
            'Qty':<5} {
                'Method':<10} {
                    'Unit Price':<12} {
                        'Total Price':<12}")
    print("-" * 80)

    for comp in pricing_result["components"]:
        print(
            f"{
                comp['model_name']:<25} {
                comp['quantity']:<5} {
                comp['calculate_per']:<10} " f"{
                    comp['unit_price']:<12.2f} {
                        comp['total_price']:<12.2f}")

    print("-" * 80)
    print(f"{'TOTAL':<52} {pricing_result['base_price']:<12.2f}")
    print()

    # Display some dynamic keys
    print("Sample Dynamic Keys (for PDF integration):")
    dynamic_keys = pricing_result.get("dynamic_keys", {})
    key_samples = [
        "PV_MODULE_TOTAL_PRICE",
        "INVERTER_TOTAL_PRICE",
        "STORAGE_TOTAL_PRICE",
        "WALLBOX_TOTAL_PRICE",
        "PV_SYSTEM_BASE_PRICE"
    ]

    for key in key_samples:
        if key in dynamic_keys:
            print(f"  {key}: {dynamic_keys[key]}")

    print(f"\nTotal Dynamic Keys Generated: {len(dynamic_keys)}")

    # Display formatted pricing for UI
    print("\n=== UI Display Format ===")
    display_data = get_pricing_display_for_ui(project_details)

    if not display_data.get("error"):
        print(f"Formatted Total: {display_data['formatted_total']}")
        print("\nComponent Display Format:")
        for comp in display_data["display_components"]:
            print(
                f"  {
                    comp['name']} ({
                    comp['type']}): {
                    comp['formatted_total_price']}")


def demo_margin_calculations():
    """Demonstrate margin calculations"""
    print("\n=== Margin Calculation Demonstrations ===\n")

    margin_examples = [
        {
            "product": "Test Module 400W",
            "purchase_price": 150.0,
            "margin_type": "percentage",
            "margin_value": 20.0
        },
        {
            "product": "Installation Service",
            "purchase_price": 2000.0,
            "margin_type": "fixed",
            "margin_value": 500.0
        },
        {
            "product": "Test Battery 10kWh",
            "purchase_price": 3800.0,
            "margin_type": "percentage",
            "margin_value": 18.4
        }
    ]

    print(
        f"{
            'Product':<20} {
            'Purchase':<10} {
                'Margin Type':<12} {
                    'Margin':<10} {
                        'Selling':<10} {
                            'Margin %':<10}")
    print("-" * 80)

    for example in margin_examples:
        # Find product ID
        product_id = None
        for product in DEMO_PRODUCTS.values():
            if product["model_name"] == example["product"]:
                product_id = product["id"]
                break

        if product_id:
            margin_info = mock_calculate_selling_price(product_id)
            if margin_info:
                print(
                    f"{
                        example['product']:<20} {
                        margin_info['purchase_price_net']:<10.2f} " f"{
                        margin_info['margin_type']:<12} {
                        margin_info['margin_value']:<10.2f} " f"{
                        margin_info['selling_price_net']:<10.2f} {
                            margin_info['margin_percentage']:<10.1f}")


def main():
    """Run all demonstrations"""
    print("Solar Calculator Pricing Integration Demo")
    print("=" * 50)

    # Demo calculate_per methods
    demo_calculate_per_scenarios()

    # Demo margin calculations
    demo_margin_calculations()

    # Demo complete integration
    demo_pricing_integration()

    print("\n=== Demo Complete ===")
    print("\nKey Features Demonstrated:")
    print("✓ Calculate_per support (Stück, Meter, pauschal, kWp)")
    print("✓ Real-time pricing calculations")
    print("✓ Profit margin integration")
    print("✓ Dynamic key generation for PDF")
    print("✓ Component-based pricing breakdown")
    print("✓ German currency formatting")
    print("✓ Integration with solar calculator")


if __name__ == "__main__":
    main()
