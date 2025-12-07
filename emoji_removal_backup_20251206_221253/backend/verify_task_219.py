"""
Task 219 Verification Script

This script verifies that all components of Task 219 are properly implemented
and working correctly.
"""

import sys
from pathlib import Path
import importlib.util

# Load the module
spec = importlib.util.spec_from_file_location(
    "dynamic_keys",
    Path(__file__).parent / "core" / "dynamic_keys.py"
)
dynamic_keys = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dynamic_keys)

# Import classes
DynamicKeyMixin = dynamic_keys.DynamicKeyMixin
DynamicKeyIndex = dynamic_keys.DynamicKeyIndex
DynamicKeyValidator = dynamic_keys.DynamicKeyValidator
KeyPrefix = dynamic_keys.KeyPrefix
get_global_key_index = dynamic_keys.get_global_key_index
generate_hash_key = dynamic_keys.generate_hash_key


def verify_component(name, test_func):
    """Verify a component and print result"""
    try:
        test_func()
        print(f"✓ {name}")
        return True
    except Exception as e:
        print(f"✗ {name}: {e}")
        return False


def test_dynamic_key_mixin():
    """Test DynamicKeyMixin class"""
    mixin = DynamicKeyMixin()
    key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
    assert key is not None
    assert key.startswith("SOL_")
    assert mixin.get_dynamic_key() == key


def test_key_prefix_system():
    """Test KeyPrefix enum"""
    # Check all prefixes are valid
    for prefix in KeyPrefix:
        assert len(prefix.value) >= 2
        assert len(prefix.value) <= 4
        assert prefix.value.isupper()
    
    # Check uniqueness
    prefixes = [p.value for p in KeyPrefix]
    assert len(prefixes) == len(set(prefixes))


def test_dynamic_key_index():
    """Test DynamicKeyIndex class"""
    index = DynamicKeyIndex()
    key = "SOL_test_001"
    data = {"test": "data"}
    
    index.add(key, data)
    assert index.exists(key)
    assert index.get(key) == data
    
    index.remove(key)
    assert not index.exists(key)


def test_key_validation():
    """Test key validation"""
    assert DynamicKeyMixin.validate_key("SOL_20231116_143052_a1b2c3d4")
    assert not DynamicKeyMixin.validate_key("invalid_key")


def test_dynamic_key_validator():
    """Test DynamicKeyValidator class"""
    validator = DynamicKeyValidator()
    is_valid, error = validator.validate("SOL_20231116_143052_a1b2c3d4")
    assert is_valid is True
    assert error is None


def test_key_indexing():
    """Test fast lookup"""
    index = DynamicKeyIndex()
    
    # Add multiple items
    for i in range(100):
        key = f"SOL_{i:03d}"
        index.add(key, {"id": i})
    
    # Verify count
    assert index.count() == 100
    
    # Verify lookup
    data = index.get("SOL_050")
    assert data["id"] == 50
    
    # Verify prefix query
    solar_keys = index.get_keys_by_prefix("SOL")
    assert len(solar_keys) == 100
    
    index.clear()


def test_global_index():
    """Test global key index"""
    index1 = get_global_key_index()
    index2 = get_global_key_index()
    assert index1 is index2


def test_hash_key_generation():
    """Test hash-based key generation"""
    key1 = generate_hash_key("test_data")
    key2 = generate_hash_key("test_data")
    assert key1 == key2
    
    key3 = generate_hash_key("different_data")
    assert key1 != key3


def verify_files_exist():
    """Verify all required files exist"""
    base_path = Path(__file__).parent
    
    required_files = [
        "core/dynamic_keys.py",
        "tests/test_dynamic_keys.py",
        "test_dynamic_keys_standalone.py",
        "docs/DYNAMIC_KEY_SYSTEM.md",
        "docs/DYNAMIC_KEY_QUICK_REFERENCE.md",
        "examples/dynamic_key_examples.py",
        "demo_dynamic_keys.py",
        "TASK_219_COMPLETE.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✓ File exists: {file_path}")
        else:
            print(f"✗ File missing: {file_path}")
            all_exist = False
    
    return all_exist


def main():
    """Run all verifications"""
    print("=" * 60)
    print("Task 219: Dynamic Key System Infrastructure - Verification")
    print("=" * 60)
    print()
    
    print("Component Tests:")
    print("-" * 60)
    
    results = []
    results.append(verify_component("DynamicKeyMixin class", test_dynamic_key_mixin))
    results.append(verify_component("Key prefix system", test_key_prefix_system))
    results.append(verify_component("DynamicKeyIndex class", test_dynamic_key_index))
    results.append(verify_component("Key validation", test_key_validation))
    results.append(verify_component("DynamicKeyValidator class", test_dynamic_key_validator))
    results.append(verify_component("Key indexing for fast lookup", test_key_indexing))
    results.append(verify_component("Global key index", test_global_index))
    results.append(verify_component("Hash key generation", test_hash_key_generation))
    
    print()
    print("File Verification:")
    print("-" * 60)
    files_ok = verify_files_exist()
    
    print()
    print("=" * 60)
    
    if all(results) and files_ok:
        print("✓ ALL VERIFICATIONS PASSED")
        print()
        print("Task 219 is COMPLETE and ready for use!")
        print()
        print("Requirements Satisfied:")
        print("  ✓ Requirement 14.4: Dynamic key generation for all data types")
        print("  ✓ Requirement 14.7: Key indexing for fast lookup")
        print()
        print("Next Steps:")
        print("  - Integrate with database models")
        print("  - Use in API endpoints")
        print("  - Implement Task 220: PDF Byte Generation Core")
        print("  - Implement Task 221: Universal Data Model")
        return 0
    else:
        print("✗ SOME VERIFICATIONS FAILED")
        print()
        print("Please review the errors above and fix any issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
