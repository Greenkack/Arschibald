"""
Standalone tests for Dynamic Key System Infrastructure

This test file can be run independently without the full backend setup.
"""

import sys
from pathlib import Path

# Add core directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import directly from the module file
import importlib.util
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

import time


def test_basic_key_generation():
    """Test basic key generation"""
    print("Testing basic key generation...")
    
    mixin = DynamicKeyMixin()
    key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
    
    assert key is not None
    assert key.startswith("SOL_")
    assert mixin.get_dynamic_key() == key
    
    print(f"✓ Generated key: {key}")


def test_key_uniqueness():
    """Test that generated keys are unique"""
    print("\nTesting key uniqueness...")
    
    mixin1 = DynamicKeyMixin()
    mixin2 = DynamicKeyMixin()
    
    key1 = mixin1.generate_dynamic_key(KeyPrefix.DATA)
    time.sleep(0.01)
    key2 = mixin2.generate_dynamic_key(KeyPrefix.DATA)
    
    assert key1 != key2
    
    print(f"✓ Key 1: {key1}")
    print(f"✓ Key 2: {key2}")
    print("✓ Keys are unique")


def test_key_validation():
    """Test key validation"""
    print("\nTesting key validation...")
    
    valid_keys = [
        "SOL_20231116_143052_a1b2c3d4",
        "USR_12345",
        "PRJ_test_data"
    ]
    
    invalid_keys = [
        "invalid",
        "123_test",
        "sol_lowercase"
    ]
    
    for key in valid_keys:
        assert DynamicKeyMixin.validate_key(key), f"Key should be valid: {key}"
        print(f"✓ Valid: {key}")
    
    for key in invalid_keys:
        assert not DynamicKeyMixin.validate_key(key), f"Key should be invalid: {key}"
        print(f"✓ Invalid (as expected): {key}")


def test_index_operations():
    """Test index add, get, remove"""
    print("\nTesting index operations...")
    
    index = DynamicKeyIndex()
    key = "SOL_20231116_143052_a1b2c3d4"
    obj = {"data": "test", "power": 10.5}
    
    # Add
    index.add(key, obj)
    assert index.exists(key)
    print(f"✓ Added object with key: {key}")
    
    # Get
    retrieved = index.get(key)
    assert retrieved == obj
    print(f"✓ Retrieved object: {retrieved}")
    
    # Remove
    removed = index.remove(key)
    assert removed is True
    assert not index.exists(key)
    print("✓ Removed object")


def test_prefix_queries():
    """Test prefix-based queries"""
    print("\nTesting prefix-based queries...")
    
    index = DynamicKeyIndex()
    
    # Add multiple objects
    index.add("SOL_001", {"type": "solar1"})
    index.add("SOL_002", {"type": "solar2"})
    index.add("HP_001", {"type": "heatpump"})
    
    # Query by prefix
    solar_objects = index.get_by_prefix("SOL")
    assert len(solar_objects) == 2
    print(f"✓ Found {len(solar_objects)} solar objects")
    
    solar_keys = index.get_keys_by_prefix("SOL")
    assert len(solar_keys) == 2
    print(f"✓ Solar keys: {solar_keys}")
    
    # Count by prefix
    solar_count = index.count_by_prefix("SOL")
    hp_count = index.count_by_prefix("HP")
    assert solar_count == 2
    assert hp_count == 1
    print(f"✓ Counts - Solar: {solar_count}, Heat Pump: {hp_count}")
    
    # Cleanup
    index.clear()


def test_validator():
    """Test key validator"""
    print("\nTesting key validator...")
    
    validator = DynamicKeyValidator()
    
    # Valid key
    key = "SOL_20231116_143052_a1b2c3d4"
    is_valid, error = validator.validate(key)
    assert is_valid is True
    assert error is None
    print(f"✓ Valid key: {key}")
    
    # Invalid key
    key = "invalid_key"
    is_valid, error = validator.validate(key)
    assert is_valid is False
    assert error is not None
    print(f"✓ Invalid key detected: {key}")
    print(f"  Error: {error}")
    
    # Custom rules
    validator.set_rule('min_length', 15)
    short_key = "SOL_1"
    is_valid, error = validator.validate(short_key)
    assert is_valid is False
    print(f"✓ Custom rule applied: min_length=15")


def test_hash_key_generation():
    """Test hash-based key generation"""
    print("\nTesting hash-based key generation...")
    
    data = "test_data"
    key1 = generate_hash_key(data)
    key2 = generate_hash_key(data)
    
    assert key1 == key2
    print(f"✓ Deterministic hash key: {key1}")
    
    # Different data produces different keys
    key3 = generate_hash_key("different_data")
    assert key1 != key3
    print(f"✓ Different data produces different key: {key3}")


def test_key_metadata():
    """Test key metadata"""
    print("\nTesting key metadata...")
    
    mixin = DynamicKeyMixin()
    key = mixin.generate_dynamic_key(
        KeyPrefix.PROJECT,
        custom_suffix="important"
    )
    
    metadata = mixin.get_key_metadata()
    
    assert metadata['prefix'] == KeyPrefix.PROJECT.value
    assert metadata['custom_suffix'] == "important"
    assert 'key_age_seconds' in metadata
    
    print(f"✓ Key: {key}")
    print(f"✓ Metadata: {metadata}")


def test_key_components():
    """Test key component extraction"""
    print("\nTesting key component extraction...")
    
    key = "SOL_20231116_143052_a1b2c3d4_123"
    
    # Extract prefix
    prefix = DynamicKeyMixin.extract_prefix(key)
    assert prefix == "SOL"
    print(f"✓ Extracted prefix: {prefix}")
    
    # Extract components
    components = DynamicKeyMixin.extract_components(key)
    assert components['prefix'] == "SOL"
    assert 'date' in components
    assert 'uuid' in components
    print(f"✓ Extracted components: {components}")


def test_index_statistics():
    """Test index statistics"""
    print("\nTesting index statistics...")
    
    index = DynamicKeyIndex()
    index.clear()
    
    # Add various objects
    index.add("SOL_001", {"data": "1"}, {"meta": "data1"})
    index.add("SOL_002", {"data": "2"})
    index.add("HP_001", {"data": "3"}, {"meta": "data3"})
    
    stats = index.get_statistics()
    
    assert stats['total_keys'] == 3
    assert stats['total_prefixes'] == 2
    assert stats['keys_by_prefix']['SOL'] == 2
    assert stats['keys_by_prefix']['HP'] == 1
    assert stats['has_metadata'] == 2
    
    print(f"✓ Statistics: {stats}")
    
    # Cleanup
    index.clear()


def test_all_prefixes():
    """Test all KeyPrefix enum values"""
    print("\nTesting all key prefixes...")
    
    prefix_count = 0
    for prefix in KeyPrefix:
        # Check format
        assert len(prefix.value) >= 2
        assert len(prefix.value) <= 4
        assert prefix.value.isupper()
        assert prefix.value.isalpha()
        prefix_count += 1
    
    print(f"✓ Validated {prefix_count} prefixes")
    
    # Test uniqueness
    prefixes = [p.value for p in KeyPrefix]
    assert len(prefixes) == len(set(prefixes))
    print("✓ All prefixes are unique")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Dynamic Key System - Standalone Tests")
    print("=" * 60)
    
    try:
        test_basic_key_generation()
        test_key_uniqueness()
        test_key_validation()
        test_index_operations()
        test_prefix_queries()
        test_validator()
        test_hash_key_generation()
        test_key_metadata()
        test_key_components()
        test_index_statistics()
        test_all_prefixes()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
