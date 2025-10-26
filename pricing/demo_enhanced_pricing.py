"""Demo script for Enhanced Pricing System

Demonstrates the core functionality of the enhanced pricing system
with comprehensive product data and dynamic key generation.
"""

from pricing.enhanced_pricing_engine import PriceComponent, PricingEngine
from pricing.dynamic_key_manager import DynamicKeyManager, KeyCategory
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def demo_price_component():
    """Demonstrate PriceComponent with different calculate_per methods"""
    print("=== PriceComponent Demo ===")

    # PV Module (per piece)
    pv_module = PriceComponent(
        product_id=1,
        model_name="AlphaSolar 450W",
        category="Modul",
        brand="AlphaSolar",
        quantity=20,
        price_euro=180.0,
        calculate_per="Stück",
        capacity_w=450.0,
        warranty_years=25,
        technology="Monokristallin N-Type",
        efficiency_percent=21.8
    )

    print(f"PV Module: {pv_module.model_name}")
    print(f"  Unit Price: {pv_module.unit_price}€")
    print(f"  Quantity: {pv_module.quantity}")
    print(f"  Total Price: {pv_module.total_price}€")
    print(f"  Calculate Per: {pv_module.calculate_per}")
    print(f"  Dynamic Keys: {len(pv_module.dynamic_keys)} keys generated")

    # Cable (per meter)
    cable = PriceComponent(
        product_id=2,
        model_name="Solar Cable 6mm²",
        category="Kabel",
        brand="CableTech",
        quantity=50,  # 50 meters
        price_euro=2.5,  # per meter
        calculate_per="Meter",
        length_m=1.0
    )

    print(f"\nCable: {cable.model_name}")
    print(f"  Unit Price: {cable.unit_price}€/m")
    print(f"  Length: {cable.quantity}m")
    print(f"  Total Price: {cable.total_price}€")

    # Installation Service (lump sum)
    service = PriceComponent(
        product_id=3,
        model_name="Installation Service",
        category="Dienstleistung",
        brand="ServiceCorp",
        quantity=1,
        price_euro=1500.0,
        calculate_per="pauschal"
    )

    print(f"\nService: {service.model_name}")
    print(f"  Price: {service.unit_price}€ (lump sum)")
    print(f"  Total Price: {service.total_price}€")


def demo_dynamic_key_manager():
    """Demonstrate DynamicKeyManager functionality"""
    print("\n=== DynamicKeyManager Demo ===")

    key_manager = DynamicKeyManager()

    # Generate keys from pricing data
    pricing_data = {
        "base_price": 5000.0,
        "discount_amount": 250.0,
        "final_price": 4750.0,
        "vat_amount": 902.5,
        "component_count": 3
    }

    keys = key_manager.generate_keys(
        pricing_data,
        prefix="PV_",
        category=KeyCategory.PRICING)

    print("Generated Dynamic Keys:")
    for key, value in keys.items():
        print(f"  {key}: {value}")

    # Test PDF formatting
    pdf_keys = key_manager.format_for_pdf(keys)
    print("\nPDF-Formatted Keys:")
    for key, value in pdf_keys.items():
        print(f"  {key}: {value}")

    # Test safe key name creation
    test_names = [
        "Wärmepumpe Größe",
        "Price (€/kWh)",
        "5kW Inverter",
        "Special-Characters!@#"
    ]

    print("\nSafe Key Name Generation:")
    for name in test_names:
        safe_name = key_manager._create_safe_key_name(name)
        print(f"  '{name}' -> '{safe_name}'")


def demo_pricing_engine():
    """Demonstrate PricingEngine with mock data"""
    print("\n=== PricingEngine Demo ===")

    # Create PV pricing engine
    engine = PricingEngine("pv")

    # Mock component data (simulating database products)
    mock_components = [
        {
            "product_id": 1,
            "quantity": 20,
            # This would normally come from database
            "_mock_product": {
                "id": 1,
                "category": "Modul",
                "model_name": "AlphaSolar 450W",
                "brand": "AlphaSolar",
                "price_euro": 180.0,
                "calculate_per": "Stück",
                "capacity_w": 450.0,
                "warranty_years": 25,
                "technology": "Monokristallin",
                "efficiency_percent": 21.8
            }
        },
        {
            "product_id": 2,
            "quantity": 1,
            "_mock_product": {
                "id": 2,
                "category": "Wechselrichter",
                "model_name": "PowerMax 5K",
                "brand": "InvertCorp",
                "price_euro": 800.0,
                "calculate_per": "Stück",
                "power_kw": 5.0,
                "warranty_years": 10,
                "efficiency_percent": 97.5
            }
        }
    ]

    # Simulate pricing calculation (without database)
    total_price = 0.0
    components = []

    for comp_data in mock_components:
        mock_product = comp_data["_mock_product"]
        price_comp = PriceComponent(
            product_id=mock_product["id"],
            model_name=mock_product["model_name"],
            category=mock_product["category"],
            brand=mock_product["brand"],
            quantity=comp_data["quantity"],
            price_euro=mock_product["price_euro"],
            calculate_per=mock_product.get("calculate_per"),
            capacity_w=mock_product.get("capacity_w"),
            power_kw=mock_product.get("power_kw"),
            warranty_years=mock_product.get("warranty_years"),
            technology=mock_product.get("technology"),
            efficiency_percent=mock_product.get("efficiency_percent")
        )
        components.append(price_comp)
        total_price += price_comp.total_price

    print("Base Price Calculation:")
    print(f"  Total Components: {len(components)}")
    print(f"  Base Price: {total_price}€")

    # Test modifications
    modifications = {
        "discount_percent": 5.0,
        "accessories_cost": 200.0,
        "surcharge_fixed": 100.0
    }

    mod_result = engine.apply_modifications(total_price, modifications)

    print("\nWith Modifications:")
    print(f"  Original Price: {mod_result['original_price']}€")
    print(f"  Accessories: +{mod_result['accessories_cost']}€")
    print(f"  Discount (5%): -{mod_result['discount_percent_amount']}€")
    print(f"  Surcharge: +{mod_result['surcharge_fixed']}€")
    print(f"  Final Price: {mod_result['final_price']}€")

    # Show some dynamic keys
    print("\nSample Dynamic Keys:")
    for key, value in list(mod_result['dynamic_keys'].items())[:5]:
        print(f"  {key}: {value}")


def demo_validation():
    """Demonstrate input validation"""
    print("\n=== Validation Demo ===")

    engine = PricingEngine("pv")

    # Valid data
    valid_data = {
        "components": [
            {"product_id": 1, "quantity": 10},
            {"model_name": "Test Product", "quantity": 5}
        ],
        "modifications": {
            "discount_percent": 5.0,
            "surcharge_fixed": 100.0
        }
    }

    print(f"Valid data validation: {engine.validate_pricing_data(valid_data)}")

    # Invalid data examples
    invalid_examples = [
        {"modifications": {}},  # Missing components
        {"components": [{"quantity": 5}]},  # Missing product identifier
        # Negative quantity
        {"components": [{"product_id": 1, "quantity": -5}]},
        {
            "components": [{"product_id": 1, "quantity": 1}],
            "modifications": {"discount_percent": "invalid"}
        }  # Invalid modification type
    ]

    for i, invalid_data in enumerate(invalid_examples, 1):
        result = engine.validate_pricing_data(invalid_data)
        print(f"Invalid example {i} validation: {result}")


if __name__ == "__main__":
    print("Enhanced Pricing System Demo")
    print("=" * 50)

    try:
        demo_price_component()
        demo_dynamic_key_manager()
        demo_pricing_engine()
        demo_validation()

        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ PriceComponent with all calculate_per methods")
        print("✓ Dynamic key generation and PDF formatting")
        print("✓ Complex pricing formula calculations")
        print("✓ Input validation and error handling")
        print("✓ Support for comprehensive product data")

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
