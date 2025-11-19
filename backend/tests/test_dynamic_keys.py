"""
Tests for Dynamic Key System Infrastructure

This module contains comprehensive tests for the dynamic key generation,
validation, and indexing system.
"""

import pytest
from datetime import datetime
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.dynamic_keys import (
    DynamicKeyMixin,
    DynamicKeyIndex,
    DynamicKeyValidator,
    KeyPrefix,
    get_global_key_index,
    generate_hash_key
)


class TestDynamicKeyMixin:
    """Tests for DynamicKeyMixin class"""
    
    def test_generate_dynamic_key_basic(self):
        """Test basic key generation"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
        
        assert key is not None
        assert key.startswith("SOL_")
        assert mixin.get_dynamic_key() == key
    
    def test_generate_dynamic_key_with_timestamp(self):
        """Test key generation with timestamp"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.USER,
            include_timestamp=True
        )
        
        assert "USR_" in key
        # Check timestamp format (YYYYMMDD_HHMMSS)
        parts = key.split('_')
        assert len(parts) >= 3
        assert len(parts[1]) == 8  # Date part
        assert parts[1].isdigit()
    
    def test_generate_dynamic_key_with_uuid(self):
        """Test key generation with UUID"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.PROJECT,
            include_uuid=True
        )
        
        assert "PRJ_" in key
        # UUID should be 8 hex characters
        parts = key.split('_')
        uuid_part = [p for p in parts if len(p) == 8 and all(c in '0123456789abcdef' for c in p.lower())]
        assert len(uuid_part) > 0
    
    def test_generate_dynamic_key_with_custom_suffix(self):
        """Test key generation with custom suffix"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.PRODUCT,
            custom_suffix="special"
        )
        
        assert key.endswith("_special")
    
    def test_generate_dynamic_key_uniqueness(self):
        """Test that generated keys are unique"""
        mixin1 = DynamicKeyMixin()
        mixin2 = DynamicKeyMixin()
        
        key1 = mixin1.generate_dynamic_key(KeyPrefix.DATA)
        time.sleep(0.01)  # Small delay to ensure different timestamp
        key2 = mixin2.generate_dynamic_key(KeyPrefix.DATA)
        
        assert key1 != key2
    
    def test_set_dynamic_key(self):
        """Test manual key setting"""
        mixin = DynamicKeyMixin()
        test_key = "SOL_20231116_143052_a1b2c3d4"
        
        mixin.set_dynamic_key(test_key)
        assert mixin.get_dynamic_key() == test_key
    
    def test_set_dynamic_key_invalid(self):
        """Test that invalid keys are rejected"""
        mixin = DynamicKeyMixin()
        
        with pytest.raises(ValueError):
            mixin.set_dynamic_key("invalid_key", validate=True)
    
    def test_get_key_metadata(self):
        """Test key metadata retrieval"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.SOLAR_CALCULATION,
            custom_suffix="test"
        )
        
        metadata = mixin.get_key_metadata()
        
        assert metadata['current_key'] == key
        assert metadata['prefix'] == KeyPrefix.SOLAR_CALCULATION.value
        assert metadata['custom_suffix'] == "test"
        assert 'key_age_seconds' in metadata
    
    def test_validate_key_valid(self):
        """Test key validation with valid keys"""
        valid_keys = [
            "SOL_20231116_143052_a1b2c3d4",
            "USR_12345",
            "PRJ_test_data",
            "HP_20231116_a1b2c3d4_123"
        ]
        
        for key in valid_keys:
            assert DynamicKeyMixin.validate_key(key), f"Key should be valid: {key}"
    
    def test_validate_key_invalid(self):
        """Test key validation with invalid keys"""
        invalid_keys = [
            "invalid",
            "123_test",
            "sol_lowercase",
            "",
            "A_",
            "_test"
        ]
        
        for key in invalid_keys:
            assert not DynamicKeyMixin.validate_key(key), f"Key should be invalid: {key}"
    
    def test_extract_prefix(self):
        """Test prefix extraction"""
        key = "SOL_20231116_143052_a1b2c3d4"
        prefix = DynamicKeyMixin.extract_prefix(key)
        
        assert prefix == "SOL"
    
    def test_extract_components(self):
        """Test component extraction"""
        key = "SOL_20231116_143052_a1b2c3d4"
        components = DynamicKeyMixin.extract_components(key)
        
        assert components['prefix'] == "SOL"
        assert components['full_key'] == key
        assert 'date' in components
        assert 'uuid' in components
    
    def test_to_dict_with_key(self):
        """Test dictionary conversion with key"""
        mixin = DynamicKeyMixin()
        mixin.test_attr = "test_value"
        key = mixin.generate_dynamic_key(KeyPrefix.DATA)
        
        result = mixin.to_dict_with_key()
        
        assert result['dynamic_key'] == key
        assert 'key_metadata' in result
        assert 'key_created_at' in result


class TestDynamicKeyIndex:
    """Tests for DynamicKeyIndex class"""
    
    def test_add_and_get(self):
        """Test adding and retrieving objects"""
        index = DynamicKeyIndex()
        key = "SOL_20231116_143052_a1b2c3d4"
        obj = {"data": "test"}
        
        index.add(key, obj)
        retrieved = index.get(key)
        
        assert retrieved == obj
    
    def test_add_invalid_key(self):
        """Test that invalid keys are rejected"""
        index = DynamicKeyIndex()
        
        with pytest.raises(ValueError):
            index.add("invalid_key", {"data": "test"})
    
    def test_add_with_metadata(self):
        """Test adding objects with metadata"""
        index = DynamicKeyIndex()
        key = "SOL_20231116_143052_a1b2c3d4"
        obj = {"data": "test"}
        metadata = {"created_by": "user1", "version": 1}
        
        index.add(key, obj, metadata)
        retrieved_metadata = index.get_metadata(key)
        
        assert retrieved_metadata == metadata
    
    def test_remove(self):
        """Test removing objects"""
        index = DynamicKeyIndex()
        key = "SOL_20231116_143052_a1b2c3d4"
        obj = {"data": "test"}
        
        index.add(key, obj)
        assert index.exists(key)
        
        removed = index.remove(key)
        assert removed is True
        assert not index.exists(key)
    
    def test_remove_nonexistent(self):
        """Test removing non-existent key"""
        index = DynamicKeyIndex()
        removed = index.remove("SOL_nonexistent")
        
        assert removed is False
    
    def test_get_by_prefix(self):
        """Test retrieving objects by prefix"""
        index = DynamicKeyIndex()
        
        # Add multiple objects with different prefixes
        index.add("SOL_001", {"type": "solar1"})
        index.add("SOL_002", {"type": "solar2"})
        index.add("HP_001", {"type": "heatpump"})
        
        solar_objects = index.get_by_prefix("SOL")
        
        assert len(solar_objects) == 2
        assert all(obj["type"].startswith("solar") for obj in solar_objects)
    
    def test_get_keys_by_prefix(self):
        """Test retrieving keys by prefix"""
        index = DynamicKeyIndex()
        
        index.add("SOL_001", {"data": "1"})
        index.add("SOL_002", {"data": "2"})
        index.add("HP_001", {"data": "3"})
        
        solar_keys = index.get_keys_by_prefix("SOL")
        
        assert len(solar_keys) == 2
        assert all(key.startswith("SOL_") for key in solar_keys)
    
    def test_exists(self):
        """Test key existence check"""
        index = DynamicKeyIndex()
        key = "SOL_20231116_143052_a1b2c3d4"
        
        assert not index.exists(key)
        
        index.add(key, {"data": "test"})
        assert index.exists(key)
    
    def test_count(self):
        """Test counting indexed objects"""
        index = DynamicKeyIndex()
        
        assert index.count() == 0
        
        index.add("SOL_001", {"data": "1"})
        index.add("SOL_002", {"data": "2"})
        
        assert index.count() == 2
    
    def test_count_by_prefix(self):
        """Test counting by prefix"""
        index = DynamicKeyIndex()
        
        index.add("SOL_001", {"data": "1"})
        index.add("SOL_002", {"data": "2"})
        index.add("HP_001", {"data": "3"})
        
        assert index.count_by_prefix("SOL") == 2
        assert index.count_by_prefix("HP") == 1
        assert index.count_by_prefix("PRJ") == 0
    
    def test_get_all_prefixes(self):
        """Test getting all prefixes"""
        index = DynamicKeyIndex()
        
        index.add("SOL_001", {"data": "1"})
        index.add("HP_001", {"data": "2"})
        index.add("PRJ_001", {"data": "3"})
        
        prefixes = index.get_all_prefixes()
        
        assert len(prefixes) == 3
        assert "SOL" in prefixes
        assert "HP" in prefixes
        assert "PRJ" in prefixes
    
    def test_clear(self):
        """Test clearing the index"""
        index = DynamicKeyIndex()
        
        index.add("SOL_001", {"data": "1"})
        index.add("HP_001", {"data": "2"})
        
        assert index.count() == 2
        
        index.clear()
        
        assert index.count() == 0
        assert len(index.get_all_prefixes()) == 0
    
    def test_get_statistics(self):
        """Test getting index statistics"""
        index = DynamicKeyIndex()
        
        index.add("SOL_001", {"data": "1"}, {"meta": "data1"})
        index.add("SOL_002", {"data": "2"})
        index.add("HP_001", {"data": "3"}, {"meta": "data3"})
        
        stats = index.get_statistics()
        
        assert stats['total_keys'] == 3
        assert stats['total_prefixes'] == 2
        assert stats['keys_by_prefix']['SOL'] == 2
        assert stats['keys_by_prefix']['HP'] == 1
        assert stats['has_metadata'] == 2


class TestDynamicKeyValidator:
    """Tests for DynamicKeyValidator class"""
    
    def test_validate_valid_key(self):
        """Test validation of valid keys"""
        validator = DynamicKeyValidator()
        key = "SOL_20231116_143052_a1b2c3d4"
        
        is_valid, error = validator.validate(key)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_empty_key(self):
        """Test validation of empty key"""
        validator = DynamicKeyValidator()
        
        is_valid, error = validator.validate("")
        
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_too_short(self):
        """Test validation of too short key"""
        validator = DynamicKeyValidator()
        validator.set_rule('min_length', 10)
        
        is_valid, error = validator.validate("SOL_1")
        
        assert is_valid is False
        assert "short" in error.lower()
    
    def test_validate_too_long(self):
        """Test validation of too long key"""
        validator = DynamicKeyValidator()
        validator.set_rule('max_length', 20)
        
        long_key = "SOL_" + "x" * 50
        is_valid, error = validator.validate(long_key)
        
        assert is_valid is False
        assert "long" in error.lower()
    
    def test_validate_invalid_prefix(self):
        """Test validation of invalid prefix"""
        validator = DynamicKeyValidator()
        key = "INVALID_20231116_143052_a1b2c3d4"
        
        is_valid, error = validator.validate(key, strict=True)
        
        assert is_valid is False
        assert "prefix" in error.lower()
    
    def test_validate_custom_prefix_allowed(self):
        """Test validation with custom prefix allowed"""
        validator = DynamicKeyValidator()
        validator.set_rule('allow_custom_prefix', True)
        
        key = "CUSTOM_20231116_143052_a1b2c3d4"
        is_valid, error = validator.validate(key, strict=True)
        
        assert is_valid is True
    
    def test_set_and_get_rule(self):
        """Test setting and getting rules"""
        validator = DynamicKeyValidator()
        
        validator.set_rule('min_length', 15)
        assert validator.get_rule('min_length') == 15
        
        validator.set_rule('custom_rule', "test_value")
        assert validator.get_rule('custom_rule') == "test_value"


class TestGlobalKeyIndex:
    """Tests for global key index"""
    
    def test_get_global_key_index(self):
        """Test getting global key index"""
        index1 = get_global_key_index()
        index2 = get_global_key_index()
        
        # Should return same instance
        assert index1 is index2
    
    def test_global_index_persistence(self):
        """Test that global index persists across calls"""
        index = get_global_key_index()
        index.clear()  # Start fresh
        
        key = "SOL_test_global"
        obj = {"data": "global_test"}
        
        index.add(key, obj)
        
        # Get index again and verify data persists
        index2 = get_global_key_index()
        retrieved = index2.get(key)
        
        assert retrieved == obj
        
        # Cleanup
        index.clear()


class TestGenerateHashKey:
    """Tests for hash-based key generation"""
    
    def test_generate_hash_key_basic(self):
        """Test basic hash key generation"""
        data = "test_data"
        key = generate_hash_key(data)
        
        assert key.startswith("DAT_")
        assert len(key) > 10
    
    def test_generate_hash_key_with_prefix(self):
        """Test hash key generation with custom prefix"""
        data = "test_data"
        key = generate_hash_key(data, KeyPrefix.SOLAR_CALCULATION)
        
        assert key.startswith("SOL_")
    
    def test_generate_hash_key_deterministic(self):
        """Test that same data produces same hash key"""
        data = "test_data"
        key1 = generate_hash_key(data)
        key2 = generate_hash_key(data)
        
        assert key1 == key2
    
    def test_generate_hash_key_different_data(self):
        """Test that different data produces different keys"""
        key1 = generate_hash_key("data1")
        key2 = generate_hash_key("data2")
        
        assert key1 != key2


class TestKeyPrefix:
    """Tests for KeyPrefix enum"""
    
    def test_all_prefixes_valid(self):
        """Test that all enum prefixes are valid"""
        for prefix in KeyPrefix:
            # Check format (2-4 uppercase letters)
            assert len(prefix.value) >= 2
            assert len(prefix.value) <= 4
            assert prefix.value.isupper()
            assert prefix.value.isalpha()
    
    def test_prefix_uniqueness(self):
        """Test that all prefixes are unique"""
        prefixes = [p.value for p in KeyPrefix]
        assert len(prefixes) == len(set(prefixes))


class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_mixin_with_index(self):
        """Test using mixin with index"""
        index = DynamicKeyIndex()
        index.clear()
        
        # Create object with mixin
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
        
        # Add to index
        obj_data = mixin.to_dict_with_key()
        index.add(key, obj_data)
        
        # Retrieve and verify
        retrieved = index.get(key)
        assert retrieved['dynamic_key'] == key
        
        # Cleanup
        index.clear()
    
    def test_validator_with_mixin(self):
        """Test using validator with mixin-generated keys"""
        validator = DynamicKeyValidator()
        mixin = DynamicKeyMixin()
        
        key = mixin.generate_dynamic_key(KeyPrefix.PROJECT)
        is_valid, error = validator.validate(key)
        
        assert is_valid is True
        assert error is None
    
    def test_full_workflow(self):
        """Test complete workflow: generate, validate, index, retrieve"""
        # Setup
        index = DynamicKeyIndex()
        index.clear()
        validator = DynamicKeyValidator()
        
        # Generate key
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.SOLAR_CALCULATION,
            custom_suffix="workflow_test"
        )
        
        # Validate
        is_valid, error = validator.validate(key)
        assert is_valid is True
        
        # Index
        obj_data = {"calculation": "test", "result": 42}
        metadata = {"created_by": "test_user"}
        index.add(key, obj_data, metadata)
        
        # Retrieve
        retrieved_obj = index.get(key)
        retrieved_meta = index.get_metadata(key)
        
        assert retrieved_obj == obj_data
        assert retrieved_meta == metadata
        
        # Verify statistics
        stats = index.get_statistics()
        assert stats['total_keys'] >= 1
        
        # Cleanup
        index.clear()
