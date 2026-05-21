"""
Demo: Form Input Dynamic Keys System

This demo shows how to use the Form Input Dynamic Keys system
to manage form inputs with dynamic keys, validation, and persistence.

Requirements: 14.7
Task: 223
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from services.form_input_key_service import (
    get_form_input_manager,
    FormInputType
)
from services.form_key_persistence import get_form_key_persistence


def demo_basic_usage():
    """Demo basic form input registration and usage"""
    print("=" * 60)
    print("DEMO 1: Basic Form Input Registration")
    print("=" * 60)

    manager = get_form_input_manager()

    # Register a simple text input
    text_input = manager.register_form_input(
        form_id="demo_form",
        field_name="username",
        input_type=FormInputType.TEXT,
        label="Username",
        default_value="",
        validation_rules={
            'required': True,
            'minLength': 3,
            'maxLength': 20
        }
    )

    print(f"\n✓ Registered text input")
    print(f"  Key: {text_input.key}")
    print(f"  Form ID: {text_input.form_id}")
    print(f"  Field Name: {text_input.field_name}")
    print(f"  Type: {text_input.input_type.value}")

    # Update value
    manager.update_input_value(text_input.key, "john_doe")
    print(f"\n✓ Updated value to: {manager.get_input_value(text_input.key)}")


def demo_solar_calculator_form():
    """Demo a complete solar calculator form"""
    print("\n" + "=" * 60)
    print("DEMO 2: Solar Calculator Form")
    print("=" * 60)

    manager = get_form_input_manager()

    # Register all solar calculator inputs
    inputs = [
        {
            'field_name': 'customer_name',
            'input_type': FormInputType.TEXT,
            'label': 'Customer Name',
            'default_value': '',
            'validation_rules': {'required': True, 'minLength': 2}
        },
        {
            'field_name': 'roof_area',
            'input_type': FormInputType.NUMBER,
            'label': 'Roof Area (m²)',
            'default_value': 50.0,
            'validation_rules': {'required': True, 'min': 10, 'max': 1000}
        },
        {
            'field_name': 'roof_type',
            'input_type': FormInputType.SELECT,
            'label': 'Roof Type',
            'default_value': 'flat',
            'validation_rules': {
                'required': True,
                'options': ['flat', 'gable', 'hip', 'shed']
            }
        },
        {
            'field_name': 'roof_angle',
            'input_type': FormInputType.SLIDER,
            'label': 'Roof Angle (degrees)',
            'default_value': 30,
            'validation_rules': {'min': 0, 'max': 90}
        },
        {
            'field_name': 'annual_consumption',
            'input_type': FormInputType.NUMBER,
            'label': 'Annual Consumption (kWh)',
            'default_value': 4000,
            'validation_rules': {'required': True, 'min': 0}
        },
        {
            'field_name': 'email',
            'input_type': FormInputType.EMAIL,
            'label': 'Email Address',
            'default_value': '',
            'validation_rules': {'required': True}
        }
    ]

    print("\n✓ Registering solar calculator inputs...")
    for input_config in inputs:
        manager.register_form_input(
            form_id="solar_calculator",
            **input_config
        )
        print(f"  - {input_config['label']}")

    # Get key mapping
    print("\n✓ Key Mapping:")
    mapping = manager.get_form_key_mapping("solar_calculator")
    for field_name, key in mapping.items():
        print(f"  {field_name}: {key[:40]}...")

    # Set form data
    print("\n✓ Setting form data...")
    form_data = {
        'customer_name': 'John Doe',
        'roof_area': 75.5,
        'roof_type': 'gable',
        'roof_angle': 35,
        'annual_consumption': 5000,
        'email': 'john.doe@example.com'
    }

    errors = manager.set_form_data("solar_calculator", form_data, validate=True)
    if errors:
        print(f"  ✗ Validation errors: {errors}")
    else:
        print("  ✓ All data set successfully")

    # Get form data
    print("\n✓ Current form data:")
    current_data = manager.get_form_data("solar_calculator")
    for field, value in current_data.items():
        print(f"  {field}: {value}")

    # Validate form
    print("\n✓ Validating form...")
    is_valid, errors = manager.validate_form("solar_calculator")
    if is_valid:
        print("  ✓ Form is valid")
    else:
        print(f"  ✗ Validation errors: {errors}")


def demo_validation():
    """Demo validation features"""
    print("\n" + "=" * 60)
    print("DEMO 3: Validation")
    print("=" * 60)

    manager = get_form_input_manager()

    # Register input with validation rules
    number_input = manager.register_form_input(
        form_id="validation_demo",
        field_name="age",
        input_type=FormInputType.NUMBER,
        label="Age",
        validation_rules={
            'required': True,
            'min': 18,
            'max': 120
        }
    )

    print("\n✓ Testing number validation (min: 18, max: 120)...")

    # Test valid value
    try:
        manager.update_input_value(number_input.key, 25, validate=True)
        print("  ✓ Value 25: Valid")
    except ValueError as e:
        print(f"  ✗ Value 25: {e}")

    # Test invalid value (too low)
    try:
        manager.update_input_value(number_input.key, 15, validate=True)
        print("  ✓ Value 15: Valid")
    except ValueError as e:
        print(f"  ✗ Value 15: {e}")

    # Test invalid value (too high)
    try:
        manager.update_input_value(number_input.key, 150, validate=True)
        print("  ✓ Value 150: Valid")
    except ValueError as e:
        print(f"  ✗ Value 150: {e}")

    # Email validation
    email_input = manager.register_form_input(
        form_id="validation_demo",
        field_name="email",
        input_type=FormInputType.EMAIL,
        label="Email"
    )

    print("\n✓ Testing email validation...")

    test_emails = [
        "valid@example.com",
        "invalid-email",
        "another.valid@test.co.uk"
    ]

    for email in test_emails:
        is_valid, error = email_input.validate_value(email)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {email}: {error if error else 'Valid'}")


def demo_persistence():
    """Demo persistence features"""
    print("\n" + "=" * 60)
    print("DEMO 4: Persistence")
    print("=" * 60)

    manager = get_form_input_manager()
    persistence = get_form_key_persistence("demo_form_keys.db")

    # Register and save input
    input_obj = manager.register_form_input(
        form_id="persist_demo",
        field_name="test_field",
        input_type=FormInputType.TEXT,
        label="Test Field",
        default_value="initial"
    )

    print("\n✓ Saving form input to database...")
    success = persistence.save_form_input(input_obj.to_dict())
    print(f"  {'✓' if success else '✗'} Save {'successful' if success else 'failed'}")

    # Load input
    print("\n✓ Loading form input from database...")
    loaded = persistence.load_form_input(input_obj.key)
    if loaded:
        print(f"  ✓ Loaded successfully")
        print(f"    Key: {loaded['key'][:40]}...")
        print(f"    Field: {loaded['field_name']}")
        print(f"    Value: {loaded['current_value']}")

    # Save form submission
    print("\n✓ Saving form submission...")
    submission_id = persistence.save_form_submission(
        form_id="persist_demo",
        data={'test_field': 'submitted value'},
        user_id="demo_user"
    )
    print(f"  ✓ Submission saved with ID: {submission_id}")

    # Load submissions
    print("\n✓ Loading form submissions...")
    submissions = persistence.load_form_submissions("persist_demo")
    print(f"  ✓ Found {len(submissions)} submission(s)")
    for sub in submissions:
        print(f"    - Submitted at: {sub['submitted_at']}")
        print(f"      Data: {sub['data']}")


def demo_value_history():
    """Demo value history tracking"""
    print("\n" + "=" * 60)
    print("DEMO 5: Value History")
    print("=" * 60)

    manager = get_form_input_manager()

    # Register input
    input_obj = manager.register_form_input(
        form_id="history_demo",
        field_name="tracked_field",
        input_type=FormInputType.NUMBER,
        label="Tracked Field",
        default_value=0
    )

    print("\n✓ Setting multiple values...")
    values = [10, 20, 30, 40, 50]
    for value in values:
        input_obj.set_value(value)
        print(f"  - Set value to: {value}")

    # Get history
    print("\n✓ Value history:")
    history = input_obj.get_value_history()
    for i, entry in enumerate(history, 1):
        print(f"  {i}. Value: {entry['value']} at {entry['timestamp']}")


def demo_form_schema():
    """Demo form schema export"""
    print("\n" + "=" * 60)
    print("DEMO 6: Form Schema Export")
    print("=" * 60)

    manager = get_form_input_manager()

    # Register a few inputs
    for i in range(3):
        manager.register_form_input(
            form_id="schema_demo",
            field_name=f"field_{i}",
            input_type=FormInputType.TEXT,
            label=f"Field {i}"
        )

    # Export schema
    print("\n✓ Exporting form schema...")
    schema = manager.export_form_schema("schema_demo")

    print(f"\n  Form ID: {schema['form_id']}")
    print(f"  Total Inputs: {schema['total_inputs']}")
    print(f"\n  Inputs:")
    for input_data in schema['inputs']:
        print(f"    - {input_data['label']} ({input_data['input_type']})")
        print(f"      Key: {input_data['key'][:40]}...")


def demo_statistics():
    """Demo statistics"""
    print("\n" + "=" * 60)
    print("DEMO 7: Statistics")
    print("=" * 60)

    manager = get_form_input_manager()

    # Get statistics
    stats = manager.get_statistics()

    print("\n✓ Manager Statistics:")
    print(f"  Total Inputs: {stats['total_inputs']}")
    print(f"  Total Forms: {stats['total_forms']}")

    if stats['inputs_by_type']:
        print(f"\n  Inputs by Type:")
        for input_type, count in stats['inputs_by_type'].items():
            print(f"    - {input_type}: {count}")

    if stats['inputs_by_form']:
        print(f"\n  Inputs by Form:")
        for form_id, count in stats['inputs_by_form'].items():
            print(f"    - {form_id}: {count}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("FORM INPUT DYNAMIC KEYS SYSTEM - DEMO")
    print("=" * 60)

    try:
        demo_basic_usage()
        demo_solar_calculator_form()
        demo_validation()
        demo_persistence()
        demo_value_history()
        demo_form_schema()
        demo_statistics()

        print("\n" + "=" * 60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
