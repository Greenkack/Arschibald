"""
Tests for Dynamic Key System

This module contains comprehensive tests for the dynamic key system,
including key generation, storage, validation, namespacing, search,
filtering, and usage tracking.

Requirements: 4.1, 6.1
"""

import pytest
from datetime import datetime
import time

from backend.core.dynamic_keys import (
    DynamicKeyMixin,
    DynamicKeyIndex,
    KeyValueStore,
    KeyUsageTracker,
    KeyPrefix,
    KeyType,
    KeyNamespace,
    generate_hash_key
)
from backend.services.dynamic_key_service import DynamicKeyService


class TestDynamicKeyMixin:
    """Tests for DynamicKeyMixin"""
    
    def test_generate_dynamic_key(self):
        """Test basic key generation"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
        
        assert key is not None
        assert key.startswith("SOL_")
        assert mixin.get_dynamic_key() == key
    
    def test_generate_key_without_timestamp(self):
        """Test key generation without timestamp"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.USER,
            include_timestamp=False
        )
        
        assert key.startswith("USR_")
        # Should still have UUID
        assert len(key.split('_')) >= 2
    
    def test_generate_key_without_uuid(self):
        """Test key generation without UUID"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.PROJECT,
            include_uuid=False
        )
        
        assert key.startswith("PRJ_")
    
    def test_generate_key_with_custom_suffix(self):
        """Test key generation with custom suffix"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.DATA,
            custom_suffix="test"
        )
        
        assert key.endswith("_test")
    
    def test_validate_key(self):
        """Test key validation"""
        assert DynamicKeyMixin.validate_key("SOL_20231116_143052_a1b2c3d4")
        assert DynamicKeyMixin.validate_key("USR_12345")
        assert not DynamicKeyMixin.validate_key("invalid")
        assert not DynamicKeyMixin.validate_key("")
    
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
    
    def test_get_key_metadata(self):
        """Test key metadata retrieval"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
        metadata = mixin.get_key_metadata()
        
        assert metadata['prefix'] == "SOL"
        assert metadata['current_key'] == key
        assert 'key_age_seconds' in metadata


class TestKeyNamespace:
    """Tests for KeyNamespace"""
    
    def test_create_namespace(self):
        """Test namespace creation"""
        ns = KeyNamespace("test")
        assert ns.name == "test"
        assert ns.get_full_path() == "test"
    
    def test_add_child_namespace(self):
        """Test adding child namespace"""
        root = KeyNamespace("root")
        child = root.add_child("solar")
        
        assert child.name == "solar"
        assert child.parent == root
        assert child.get_full_path() == "root.solar"
    
    def test_add_key_to_namespace(self):
        """Test adding keys to namespace"""
        ns = KeyNamespace("test")
        ns.add_key("key1")
        ns.add_key("key2")
        
        assert ns.has_key("key1")
        assert ns.has_key("key2")
        assert ns.count_keys() == 2
    
    def test_remove_key_from_namespace(self):
        """Test removing keys from namespace"""
        ns = KeyNamespace("test")
        ns.add_key("key1")
        
        assert ns.remove_key("key1")
        assert not ns.has_key("key1")
        assert not ns.remove_key("key1")  # Already removed
    
    def test_get_all_keys_recursive(self):
        """Test getting all keys recursively"""
        root = KeyNamespace("root")
        child1 = root.add_child("child1")
        child2 = root.add_child("child2")
        
        root.add_key("root_key")
        child1.add_key("child1_key")
        child2.add_key("child2_key")
        
        all_keys = root.get_all_keys(recursive=True)
        assert len(all_keys) == 3
        assert "root_key" in all_keys
        assert "child1_key" in all_keys
        assert "child2_key" in all_keys


class TestKeyValueStore:
    """Tests for KeyValueStore"""
    
    def test_set_and_get_value(self):
        """Test basic set and get operations"""
        store = KeyValueStore()
        store.set("test_key", "test_value")
        
        assert store.get("test_key") == "test_value"
        assert store.exists("test_key")
    
    def test_set_with_type_validation(self):
        """Test setting value with type validation"""
        store = KeyValueStore()
        
        # Valid type
        store.set("int_key", 42, key_type=KeyType.INTEGER)
        assert store.get("int_key") == 42
        
        # Invalid type should raise error
        with pytest.raises(ValueError):
            store.set("int_key2", "not_an_int", key_type=KeyType.INTEGER)
    
    def test_set_with_namespace(self):
        """Test setting value with namespace"""
        store = KeyValueStore()
        store.set("key1", "value1", namespace="root.solar")
        
        ns = store.get_namespace("root.solar")
        assert ns is not None
        assert ns.has_key("key1")
    
    def test_set_with_metadata(self):
        """Test setting value with metadata"""
        store = KeyValueStore()
        metadata = {"description": "Test key", "version": 1}
        store.set("key1", "value1", metadata=metadata)
        
        retrieved_metadata = store.get_metadata("key1")
        assert retrieved_metadata == metadata
    
    def test_delete_value(self):
        """Test deleting values"""
        store = KeyValueStore()
        store.set("key1", "value1")
        
        assert store.delete("key1")
        assert not store.exists("key1")
        assert not store.delete("key1")  # Already deleted
    
    def test_search_by_pattern(self):
        """Test searching by pattern"""
        store = KeyValueStore()
        store.set("solar_key_1", "value1")
        store.set("solar_key_2", "value2")
        store.set("other_key", "value3")
        
        results = store.search(pattern="solar_.*")
        assert len(results) == 2
        assert "solar_key_1" in results
        assert "solar_key_2" in results
    
    def test_search_by_type(self):
        """Test searching by type"""
        store = KeyValueStore()
        store.set("int1", 42, key_type=KeyType.INTEGER)
        store.set("int2", 100, key_type=KeyType.INTEGER)
        store.set("str1", "text", key_type=KeyType.STRING)
        
        results = store.search(key_type=KeyType.INTEGER)
        assert len(results) == 2
        assert "int1" in results
        assert "int2" in results
    
    def test_search_by_namespace(self):
        """Test searching by namespace"""
        store = KeyValueStore()
        store.set("key1", "value1", namespace="root.solar")
        store.set("key2", "value2", namespace="root.solar")
        store.set("key3", "value3", namespace="root.other")
        
        results = store.search(namespace="root.solar")
        assert len(results) == 2
    
    def test_export_import(self):
        """Test export and import functionality"""
        store = KeyValueStore()
        store.set("key1", "value1", key_type=KeyType.STRING)
        store.set("key2", 42, key_type=KeyType.INTEGER)
        
        # Export
        data = store.export_to_dict()
        assert len(data) == 2
        
        # Import to new store
        new_store = KeyValueStore()
        new_store.import_from_dict(data)
        
        assert new_store.get("key1") == "value1"
        assert new_store.get("key2") == 42


class TestKeyUsageTracker:
    """Tests for KeyUsageTracker"""
    
    def test_record_access(self):
        """Test recording key access"""
        tracker = KeyUsageTracker()
        tracker.record_access("test_key")
        
        assert tracker.get_access_count("test_key") == 1
        assert tracker.get_last_access("test_key") is not None
    
    def test_multiple_accesses(self):
        """Test multiple accesses to same key"""
        tracker = KeyUsageTracker()
        
        for _ in range(5):
            tracker.record_access("test_key")
        
        assert tracker.get_access_count("test_key") == 5
    
    def test_access_history(self):
        """Test access history tracking"""
        tracker = KeyUsageTracker()
        
        for _ in range(3):
            tracker.record_access("test_key")
            time.sleep(0.01)  # Small delay
        
        history = tracker.get_access_history("test_key")
        assert len(history) == 3
    
    def test_most_accessed_keys(self):
        """Test getting most accessed keys"""
        tracker = KeyUsageTracker()
        
        tracker.record_access("key1")
        for _ in range(5):
            tracker.record_access("key2")
        for _ in range(3):
            tracker.record_access("key3")
        
        most_accessed = tracker.get_most_accessed(limit=2)
        assert len(most_accessed) == 2
        assert most_accessed[0][0] == "key2"
        assert most_accessed[0][1] == 5
    
    def test_recently_accessed_keys(self):
        """Test getting recently accessed keys"""
        tracker = KeyUsageTracker()
        
        tracker.record_access("key1")
        time.sleep(0.01)
        tracker.record_access("key2")
        time.sleep(0.01)
        tracker.record_access("key3")
        
        recent = tracker.get_recently_accessed(limit=2)
        assert len(recent) == 2
        assert recent[0][0] == "key3"  # Most recent
    
    def test_unused_keys(self):
        """Test getting unused keys"""
        tracker = KeyUsageTracker()
        
        tracker.record_access("key1")
        tracker.record_access("key2")
        
        all_keys = ["key1", "key2", "key3", "key4"]
        unused = tracker.get_unused_keys(all_keys)
        
        assert len(unused) == 2
        assert "key3" in unused
        assert "key4" in unused
    
    def test_reset_tracking(self):
        """Test resetting usage tracking"""
        tracker = KeyUsageTracker()
        
        tracker.record_access("key1")
        tracker.record_access("key2")
        
        # Reset specific key
        tracker.reset("key1")
        assert tracker.get_access_count("key1") == 0
        assert tracker.get_access_count("key2") == 1
        
        # Reset all
        tracker.reset()
        assert tracker.get_access_count("key2") == 0


class TestDynamicKeyService:
    """Tests for DynamicKeyService"""
    
    def test_generate_key(self):
        """Test key generation through service"""
        service = DynamicKeyService()
        key = service.generate_key(KeyPrefix.SOLAR_CALCULATION)
        
        assert key.startswith("SOL_")
    
    def test_set_and_get_value(self):
        """Test setting and getting values through service"""
        service = DynamicKeyService()
        
        service.set_value("test_key", "test_value")
        value = service.get_value("test_key")
        
        assert value == "test_value"
    
    def test_search_keys(self):
        """Test searching keys through service"""
        service = DynamicKeyService()
        
        service.set_value("solar_1", "value1")
        service.set_value("solar_2", "value2")
        service.set_value("other", "value3")
        
        results = service.search_keys(pattern="solar_.*")
        assert len(results) == 2
    
    def test_namespace_operations(self):
        """Test namespace operations through service"""
        service = DynamicKeyService()
        
        # Create namespace
        ns = service.create_namespace("root.solar.calculations")
        assert ns is not None
        
        # Add keys to namespace
        service.set_value("key1", "value1", namespace="root.solar.calculations")
        
        # Get keys from namespace
        keys = service.get_namespace_keys("root.solar.calculations")
        assert "key1" in keys
    
    def test_usage_tracking(self):
        """Test usage tracking through service"""
        service = DynamicKeyService()
        
        service.set_value("test_key", "test_value", track_usage=True)
        service.get_value("test_key", track_usage=True)
        service.get_value("test_key", track_usage=True)
        
        stats = service.get_usage_statistics("test_key")
        assert stats['access_count'] >= 2  # At least 2 gets
    
    def test_bulk_operations(self):
        """Test bulk operations through service"""
        service = DynamicKeyService()
        
        # Bulk set
        items = {"key1": "value1", "key2": "value2", "key3": "value3"}
        service.bulk_set(items)
        
        # Bulk get
        values = service.bulk_get(["key1", "key2"])
        assert len(values) == 2
        assert values["key1"] == "value1"
        
        # Bulk delete
        deleted = service.bulk_delete(["key1", "key2"])
        assert deleted == 2
    
    def test_export_import(self):
        """Test export and import through service"""
        service = DynamicKeyService()
        
        service.set_value("key1", "value1")
        service.set_value("key2", 42, key_type=KeyType.INTEGER)
        
        # Export
        data = service.export_configuration()
        assert len(data) == 2
        
        # Clear and import
        service.clear_all()
        service.import_configuration(data)
        
        assert service.get_value("key1") == "value1"
        assert service.get_value("key2") == 42
    
    def test_statistics(self):
        """Test getting comprehensive statistics"""
        service = DynamicKeyService()
        
        service.set_value("key1", "value1", namespace="root.test")
        service.set_value("key2", "value2", namespace="root.test")
        service.get_value("key1", track_usage=True)
        
        stats = service.get_statistics()
        
        assert 'store' in stats
        assert 'index' in stats
        assert 'usage' in stats
        assert stats['store']['total_keys'] >= 2


class TestKeyTypeValidation:
    """Tests for key type validation"""
    
    def test_string_type(self):
        """Test string type validation"""
        store = KeyValueStore()
        store.set("key", "value", key_type=KeyType.STRING)
        assert store.get("key") == "value"
    
    def test_integer_type(self):
        """Test integer type validation"""
        store = KeyValueStore()
        store.set("key", 42, key_type=KeyType.INTEGER)
        assert store.get("key") == 42
        
        with pytest.raises(ValueError):
            store.set("key2", "not_int", key_type=KeyType.INTEGER)
    
    def test_float_type(self):
        """Test float type validation"""
        store = KeyValueStore()
        store.set("key", 3.14, key_type=KeyType.FLOAT)
        assert store.get("key") == 3.14
    
    def test_boolean_type(self):
        """Test boolean type validation"""
        store = KeyValueStore()
        store.set("key", True, key_type=KeyType.BOOLEAN)
        assert store.get("key") is True
    
    def test_currency_type(self):
        """Test currency type validation"""
        store = KeyValueStore()
        store.set("key", 99.99, key_type=KeyType.CURRENCY)
        assert store.get("key") == 99.99
        
        with pytest.raises(ValueError):
            store.set("key2", -10, key_type=KeyType.CURRENCY)
    
    def test_percentage_type(self):
        """Test percentage type validation"""
        store = KeyValueStore()
        store.set("key", 85.5, key_type=KeyType.PERCENTAGE)
        assert store.get("key") == 85.5
        
        with pytest.raises(ValueError):
            store.set("key2", 150, key_type=KeyType.PERCENTAGE)


class TestHashKeyGeneration:
    """Tests for hash-based key generation"""
    
    def test_generate_hash_key(self):
        """Test hash key generation"""
        key1 = generate_hash_key("test_data", KeyPrefix.DATA)
        key2 = generate_hash_key("test_data", KeyPrefix.DATA)
        
        # Same data should produce same key
        assert key1 == key2
        assert key1.startswith("DAT_")
    
    def test_different_data_different_keys(self):
        """Test that different data produces different keys"""
        key1 = generate_hash_key("data1", KeyPrefix.DATA)
        key2 = generate_hash_key("data2", KeyPrefix.DATA)
        
        assert key1 != key2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
