"""
Universal Data Model Demonstration

This script demonstrates the capabilities of the UniversalDataModel class,
showing how it integrates dynamic keys, PDF generation, and German formatting.
"""

from decimal import Decimal
from datetime import datetime

from backend.core.universal_data import (
    SimpleDataModel,
    create_universal_model,
    format_dict_german
)
from backend.core.dynamic_keys import KeyPrefix


def demo_basic_usage():
    """Demonstrate basic usage of UniversalDataModel"""
    print("=" * 70)
    print("DEMO 1: Basic Usage")
    print("=" * 70)

    # Create a simple model
    model = SimpleDataModel(
        title="Solar System Calculation",
        system_size=10.5,
        cost=15000.0,
        efficiency=95.5,
        annual_production=12000.0
    )

    print(f"\nCreated model: {model}")
    print(f"Title: {model.title}")
    print(f"System Size: {model.get_data('system_size')}")
    print(f"Cost: {model.get_data('cost')}")


def demo_dynamic_keys():
    """Demonstrate dynamic key generation"""
    print("\n" + "=" * 70)
    print("DEMO 2: Dynamic Key Generation")
    print("=" * 70)

    model = SimpleDataModel(
        title="Solar Calculation",
        cost=15000.0
    )

    # Generate dynamic key
    key = model.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
    print(f"\nGenerated Key: {key}")

    # Get key metadata
    metadata = model.get_key_metadata()
    print(f"Key Metadata: {metadata}")

    # Validate key
    from backend.core.dynamic_keys import DynamicKeyMixin
    is_valid = DynamicKeyMixin.validate_key(key)
    print(f"Key Valid: {is_valid}")


def demo_german_formatting():
    """Demonstrate German number formatting"""
    print("\n" + "=" * 70)
    print("DEMO 3: German Number Formatting")
    print("=" * 70)

    model = SimpleDataModel(
        title="Price Calculation",
        base_price=1234.56,
        tax=234.56,
        total=1469.12,
        discount_percent=15.5
    )

    print("\nOriginal Values:")
    print(f"  Base Price: {model.get_data('base_price')}")
    print(f"  Tax: {model.get_data('tax')}")
    print(f"  Total: {model.get_data('total')}")

    print("\nGerman Formatted Values:")
    print(f"  Base Price: {model.get_formatted_value('base_price')}")
    print(f"  Tax: {model.get_formatted_value('tax')}")
    print(f"  Total: {model.get_formatted_value('total')}")

    print("\nFormatted as Currency:")
    formatted_total = model.get_formatted_value(
        'total', format_type='currency'
    )
    print(f"  Total: {formatted_total}")

    print("\nFormatted as Percent:")
    formatted_discount = model.get_formatted_value(
        'discount_percent', format_type='percent'
    )
    print(f"  Discount: {formatted_discount}")


def demo_locale_support():
    """Demonstrate locale support"""
    print("\n" + "=" * 70)
    print("DEMO 4: Locale Support")
    print("=" * 70)

    model = SimpleDataModel(
        title="Multi-Locale Data",
        price=1234.56,
        active=True
    )

    print("\nGerman Locale (de-DE):")
    print(f"  Price: {model.get_formatted_value('price', locale='de-DE')}")
    print(f"  Active: {model.get_formatted_value('active', locale='de-DE')}")

    print("\nEnglish Locale (en-US):")
    print(f"  Price: {model.get_formatted_value('price', locale='en-US')}")
    print(f"  Active: {model.get_formatted_value('active', locale='en-US')}")


def demo_datetime_formatting():
    """Demonstrate datetime formatting"""
    print("\n" + "=" * 70)
    print("DEMO 5: DateTime Formatting")
    print("=" * 70)

    now = datetime.now()
    model = SimpleDataModel(
        title="Time Data",
        created=now,
        modified=now
    )

    print("\nGerman Format:")
    print(f"  Created: {model.get_formatted_value('created', locale='de-DE')}")

    print("\nEnglish Format:")
    print(f"  Created: {model.get_formatted_value('created', locale='en-US')}")


def demo_all_formatted_values():
    """Demonstrate getting all formatted values"""
    print("\n" + "=" * 70)
    print("DEMO 6: All Formatted Values")
    print("=" * 70)

    model = SimpleDataModel(
        title="Complete Data",
        system_size=10.5,
        cost=15000.0,
        efficiency=95.5,
        active=True,
        created=datetime.now()
    )

    all_formatted = model.get_all_formatted_values(locale='de-DE')

    print("\nAll Formatted Values (German):")
    for key, value in all_formatted.items():
        if not key.startswith('_'):
            print(f"  {key}: {value}")


def demo_dict_conversion():
    """Demonstrate dictionary conversion"""
    print("\n" + "=" * 70)
    print("DEMO 7: Dictionary Conversion")
    print("=" * 70)

    model = SimpleDataModel(
        title="Solar System",
        cost=15000.0,
        size=10.5
    )
    model.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)

    print("\nStandard Dictionary:")
    standard_dict = model.to_dict(formatted=False)
    print(f"  Cost: {standard_dict['cost']}")
    print(f"  Size: {standard_dict['size']}")
    print(f"  Key: {standard_dict['_dynamic_key']}")

    print("\nFormatted Dictionary (German):")
    formatted_dict = model.to_dict(formatted=True, locale='de-DE')
    print(f"  Cost: {formatted_dict['cost']}")
    print(f"  Size: {formatted_dict['size']}")


def demo_pdf_generation():
    """Demonstrate PDF generation"""
    print("\n" + "=" * 70)
    print("DEMO 8: PDF Generation")
    print("=" * 70)

    model = SimpleDataModel(
        title="Solar System Report",
        system_size=10.5,
        cost=15000.0,
        efficiency=95.5,
        annual_production=12000.0
    )

    try:
        # Generate PDF bytes
        pdf_bytes = model.to_pdf_bytes()
        print(f"\nGenerated PDF: {len(pdf_bytes)} bytes")

        # Generate base64
        pdf_base64 = model.to_pdf_base64()
        print(f"Base64 length: {len(pdf_base64)} characters")

        # Save to file
        output_file = "demo_universal_data_report.pdf"
        model.save_pdf(output_file)
        print(f"Saved PDF to: {output_file}")

    except ImportError:
        print("\nPDF generation requires reportlab package")
        print("Install with: pip install reportlab")


def demo_utility_functions():
    """Demonstrate utility functions"""
    print("\n" + "=" * 70)
    print("DEMO 9: Utility Functions")
    print("=" * 70)

    # Create model from dict
    data = {
        'cost': 15000.0,
        'size': 10.5,
        'name': 'Solar System'
    }

    model = create_universal_model(
        data,
        title="Solar Calculation",
        key_prefix=KeyPrefix.SOLAR_CALCULATION
    )

    print("\nCreated from dictionary:")
    print(f"  Title: {model.title}")
    print(f"  Key: {model.get_dynamic_key()}")
    print(f"  Cost (formatted): {model.get_formatted_value('cost')}")

    # Format dict German
    formatted_data = format_dict_german(data)
    print("\nFormatted dictionary:")
    for key, value in formatted_data.items():
        print(f"  {key}: {value}")


def demo_metadata():
    """Demonstrate metadata handling"""
    print("\n" + "=" * 70)
    print("DEMO 10: Metadata Handling")
    print("=" * 70)

    model = SimpleDataModel(
        title="Data with Metadata",
        value=1234.56
    )

    # Set metadata
    model.set_metadata('version', '1.0')
    model.set_metadata('author', 'System')
    model.set_metadata('created_by', 'Demo Script')

    print("\nMetadata:")
    print(f"  Version: {model.get_metadata('version')}")
    print(f"  Author: {model.get_metadata('author')}")
    print(f"  Created By: {model.get_metadata('created_by')}")

    # Get all data with metadata
    full_dict = model.to_dict(include_metadata=True)
    print(f"\nFull metadata: {full_dict['_metadata']}")


def demo_complete_workflow():
    """Demonstrate complete workflow"""
    print("\n" + "=" * 70)
    print("DEMO 11: Complete Workflow")
    print("=" * 70)

    # Step 1: Create model
    print("\n1. Creating model...")
    model = SimpleDataModel(
        title="Complete Solar System Analysis",
        system_size=10.5,
        module_count=30,
        cost=15000.0,
        efficiency=95.5,
        annual_production=12000.0,
        payback_period=8.5,
        co2_savings=7500.0
    )

    # Step 2: Generate dynamic key
    print("2. Generating dynamic key...")
    key = model.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
    print(f"   Key: {key}")

    # Step 3: Set metadata
    print("3. Setting metadata...")
    model.set_metadata('version', '1.0')
    model.set_metadata('calculation_date', datetime.now().isoformat())

    # Step 4: Get formatted values
    print("4. Getting formatted values...")
    print(f"   Cost: {model.get_formatted_value('cost', format_type='currency')}")  # noqa: E501
    print(f"   Efficiency: {model.get_formatted_value('efficiency', format_type='percent')}")  # noqa: E501
    print(f"   System Size: {model.get_formatted_value('system_size')} kWp")

    # Step 5: Export to dictionary
    print("5. Exporting to dictionary...")
    data_dict = model.to_dict(formatted=True, locale='de-DE')
    print(f"   Exported {len(data_dict)} fields")

    # Step 6: Generate PDF
    print("6. Generating PDF...")
    try:
        pdf_bytes = model.to_pdf_bytes()
        print(f"   Generated {len(pdf_bytes)} bytes")
    except ImportError:
        print("   PDF generation requires reportlab")

    print("\n Complete workflow finished successfully!")


def main():
    """Run all demonstrations"""
    print("\n")
    print("" + "=" * 68 + "")
    print("" + " " * 15 + "UNIVERSAL DATA MODEL DEMONSTRATION" + " " * 19 + "")  # noqa: E501
    print("" + "=" * 68 + "")

    demos = [
        demo_basic_usage,
        demo_dynamic_keys,
        demo_german_formatting,
        demo_locale_support,
        demo_datetime_formatting,
        demo_all_formatted_values,
        demo_dict_conversion,
        demo_pdf_generation,
        demo_utility_functions,
        demo_metadata,
        demo_complete_workflow
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\nError in {demo.__name__}: {e}")

    print("\n" + "=" * 70)
    print("All demonstrations completed!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
