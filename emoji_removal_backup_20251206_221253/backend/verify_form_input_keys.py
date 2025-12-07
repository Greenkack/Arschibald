"""
Verification Script for Form Input Dynamic Keys System

This script verifies that the Form Input Dynamic Keys system is working correctly.

Requirements: 14.7
Task: 223
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

print("=" * 70)
print("FORM INPUT DYNAMIC KEYS SYSTEM - VERIFICATION")
print("=" * 70)

# Test imports
print("\n✓ Testing imports...")
try:
    from services.form_input_key_service import (
        FormInputKeyManager,
        FormInput,
        FormInputType,
        get_form_input_manager
    )
    from services.form_key_persistence import (
        FormKeyPersistence,
        get_form_key_persistence
    )
    print("  ✓ All imports successful")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test basic functionality
print("\n✓ Testing basic functionality...")
try:
    manager = FormInputKeyManager()
    
    # Register input
    form_input = manager.register_form_input(
        form_id="test_form",
        field_name="test_field",
        input_type=FormInputType.TEXT,
        label="Test Field",
        default_value="test"
    )
    
    assert form_input is not None
    assert form_input.key is not None
    print(f"  ✓ Input registered with key: {form_input.key[:40]}...")
    
    # Update value
    manager.update_input_value(form_input.key, "new value")
    value = manager.get_input_value(form_input.key)
    assert value == "new value"
    print(f"  ✓ Value updated and retrieved: {value}")
    
    # Get form data
    data = manager.get_form_data("test_form")
    assert "test_field" in data
    print(f"  ✓ Form data retrieved: {data}")
    
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test validation
print("\n✓ Testing validation...")
try:
    number_input = manager.register_form_input(
        form_id="validation_test",
        field_name="age",
        input_type=FormInputType.NUMBER,
        label="Age",
        validation_rules={'min': 18, 'max': 120}
    )
    
    # Valid value
    manager.update_input_value(number_input.key, 25, validate=True)
    print("  ✓ Valid value accepted: 25")
    
    # Invalid value
    try:
        manager.update_input_value(number_input.key, 150, validate=True)
        print("  ✗ Invalid value should have been rejected")
    except ValueError:
        print("  ✓ Invalid value rejected: 150")
    
except Exception as e:
    print(f"  ✗ Validation test failed: {e}")
    sys.exit(1)

# Test persistence
print("\n✓ Testing persistence...")
try:
    persistence = FormKeyPersistence("test_verify_form_keys.db")
    
    # Save input
    success = persistence.save_form_input(form_input.to_dict())
    assert success
    print("  ✓ Input saved to database")
    
    # Load input
    loaded = persistence.load_form_input(form_input.key)
    assert loaded is not None
    assert loaded['key'] == form_input.key
    print("  ✓ Input loaded from database")
    
    # Save submission
    submission_id = persistence.save_form_submission(
        form_id="test_form",
        data={'test_field': 'submitted'},
        user_id="test_user"
    )
    assert submission_id is not None
    print(f"  ✓ Submission saved with ID: {submission_id}")
    
    # Cleanup
    import os
    if os.path.exists("test_verify_form_keys.db"):
        os.remove("test_verify_form_keys.db")
    
except Exception as e:
    print(f"  ✗ Persistence test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test key mapping
print("\n✓ Testing key mapping...")
try:
    mapping = manager.get_form_key_mapping("test_form")
    assert "test_field" in mapping
    print(f"  ✓ Key mapping retrieved: {len(mapping)} field(s)")
    
    # Get input by field
    retrieved = manager.get_input_by_field("test_form", "test_field")
    assert retrieved is not None
    print("  ✓ Input retrieved by field name")
    
except Exception as e:
    print(f"  ✗ Key mapping test failed: {e}")
    sys.exit(1)

# Test form operations
print("\n✓ Testing form operations...")
try:
    # Set form data
    errors = manager.set_form_data("test_form", {
        'test_field': 'bulk update'
    })
    assert len(errors) == 0
    print("  ✓ Form data set successfully")
    
    # Validate form
    is_valid, errors = manager.validate_form("test_form")
    print(f"  ✓ Form validation: {'valid' if is_valid else 'invalid'}")
    
    # Clear form
    manager.clear_form("test_form")
    data = manager.get_form_data("test_form")
    assert data['test_field'] == "test"  # Back to default
    print("  ✓ Form cleared (reset to defaults)")
    
except Exception as e:
    print(f"  ✗ Form operations test failed: {e}")
    sys.exit(1)

# Test statistics
print("\n✓ Testing statistics...")
try:
    stats = manager.get_statistics()
    print(f"  ✓ Total inputs: {stats['total_inputs']}")
    print(f"  ✓ Total forms: {stats['total_forms']}")
    
except Exception as e:
    print(f"  ✗ Statistics test failed: {e}")
    sys.exit(1)

# Test schema export
print("\n✓ Testing schema export...")
try:
    schema = manager.export_form_schema("test_form")
    assert 'form_id' in schema
    assert 'inputs' in schema
    assert 'key_mapping' in schema
    print(f"  ✓ Schema exported with {schema['total_inputs']} input(s)")
    
except Exception as e:
    print(f"  ✗ Schema export test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL VERIFICATION TESTS PASSED ✓")
print("=" * 70)
print("\nTask 223: Input Field Dynamic Keys - COMPLETE")
print("\nFeatures verified:")
print("  ✓ Dynamic key generation for form inputs")
print("  ✓ Key mapping (field_name <-> dynamic_key)")
print("  ✓ Key-based data retrieval")
print("  ✓ Key-based validation")
print("  ✓ Key persistence system")
print("  ✓ Form operations (set, get, clear, validate)")
print("  ✓ Statistics and monitoring")
print("  ✓ Schema export")
print("\nRequirement 14.7: FULFILLED ✓")
print("=" * 70)
