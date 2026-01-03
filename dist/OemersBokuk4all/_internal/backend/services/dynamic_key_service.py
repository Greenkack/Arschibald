"""
Dynamic Key Service

This service provides high-level operations for managing dynamic keys,
including CRUD operations, search, filtering, and usage tracking.

Requirements: 4.1, 6.1
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.core.dynamic_keys import (
    DynamicKeyMixin,
    DynamicKeyIndex,
    KeyValueStore,
    KeyUsageTracker,
    KeyPrefix,
    KeyType,
    KeyNamespace,
    get_global_key_index,
    get_global_key_value_store,
    get_global_usage_tracker,
    generate_hash_key
)


class DynamicKeyService:
    """
    Service for managing dynamic keys with configuration storage,
    validation, namespacing, search, and usage tracking.
    """
    
    def __init__(self):
        """Initialize the service with global instances"""
        self.index = get_global_key_index()
        self.store = get_global_key_value_store()
        self.tracker = get_global_usage_tracker()
    
    # Key Generation Methods
    
    def generate_key(
        self,
        prefix: KeyPrefix,
        include_timestamp: bool = True,
        include_uuid: bool = True,
        custom_suffix: Optional[str] = None
    ) -> str:
        """
        Generate a new dynamic key.
        
        Args:
            prefix: Key prefix indicating data type
            include_timestamp: Whether to include timestamp
            include_uuid: Whether to include UUID
            custom_suffix: Optional custom suffix
            
        Returns:
            Generated dynamic key
        """
        mixin = DynamicKeyMixin()
        return mixin.generate_dynamic_key(
            prefix=prefix,
            include_timestamp=include_timestamp,
            include_uuid=include_uuid,
            custom_suffix=custom_suffix
        )
    
    def generate_hash_key_from_data(
        self,
        data: str,
        prefix: KeyPrefix = KeyPrefix.DATA
    ) -> str:
        """
        Generate a hash-based key from data.
        
        Args:
            data: Data to hash
            prefix: Key prefix
            
        Returns:
            Hash-based dynamic key
        """
        return generate_hash_key(data, prefix)
    
    # Key-Value Storage Methods
    
    def set_value(
        self,
        key: str,
        value: Any,
        key_type: Optional[KeyType] = None,
        namespace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        track_usage: bool = True
    ) -> None:
        """
        Store a key-value pair with optional typing and namespace.
        
        Args:
            key: Key to set
            value: Value to store
            key_type: Optional type specification
            namespace: Optional namespace path
            metadata: Optional metadata
            track_usage: Whether to track this operation
        """
        self.store.set(
            key=key,
            value=value,
            key_type=key_type,
            namespace=namespace,
            metadata=metadata
        )
        
        if track_usage:
            self.tracker.record_access(key)
    
    def get_value(
        self,
        key: str,
        default: Any = None,
        validate_type: bool = True,
        track_usage: bool = True
    ) -> Any:
        """
        Retrieve a value by key.
        
        Args:
            key: Key to retrieve
            default: Default value if not found
            validate_type: Whether to validate type
            track_usage: Whether to track this operation
            
        Returns:
            Stored value or default
        """
        if track_usage:
            self.tracker.record_access(key)
        
        return self.store.get(
            key=key,
            default=default,
            validate_type=validate_type
        )
    
    def delete_value(self, key: str) -> bool:
        """
        Delete a key-value pair.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.store.delete(key)
    
    def value_exists(self, key: str) -> bool:
        """
        Check if a key exists in the store.
        
        Args:
            key: Key to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.store.exists(key)
    
    # Namespace Methods
    
    def create_namespace(self, path: str) -> KeyNamespace:
        """
        Create a namespace.
        
        Args:
            path: Namespace path (e.g., "root.solar.calculations")
            
        Returns:
            Created or existing namespace
        """
        return self.store.create_namespace(path)
    
    def get_namespace(self, path: str) -> Optional[KeyNamespace]:
        """
        Get a namespace by path.
        
        Args:
            path: Namespace path
            
        Returns:
            KeyNamespace or None if not found
        """
        return self.store.get_namespace(path)
    
    def list_namespaces(self) -> List[str]:
        """
        List all namespace paths.
        
        Returns:
            List of namespace paths
        """
        return self.store.list_namespaces()
    
    def get_namespace_keys(
        self,
        namespace: str,
        recursive: bool = False
    ) -> List[str]:
        """
        Get all keys in a namespace.
        
        Args:
            namespace: Namespace path
            recursive: Whether to include child namespaces
            
        Returns:
            List of keys
        """
        ns = self.store.get_namespace(namespace)
        if ns:
            return ns.get_all_keys(recursive=recursive)
        return []
    
    # Search and Filter Methods
    
    def search_keys(
        self,
        pattern: Optional[str] = None,
        namespace: Optional[str] = None,
        key_type: Optional[KeyType] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        prefix: Optional[KeyPrefix] = None
    ) -> List[str]:
        """
        Search for keys matching criteria.
        
        Args:
            pattern: Regex pattern to match keys
            namespace: Namespace to search in
            key_type: Filter by key type
            metadata_filter: Filter by metadata values
            prefix: Filter by key prefix
            
        Returns:
            List of matching keys
        """
        # Start with store search
        keys = self.store.search(
            pattern=pattern,
            namespace=namespace,
            key_type=key_type,
            metadata_filter=metadata_filter
        )
        
        # Additional filter by prefix if specified
        if prefix:
            keys = [k for k in keys if k.startswith(prefix.value)]
        
        return keys
    
    def filter_by_prefix(self, prefix: KeyPrefix) -> List[str]:
        """
        Get all keys with a specific prefix.
        
        Args:
            prefix: Key prefix to filter by
            
        Returns:
            List of matching keys
        """
        return self.index.get_keys_by_prefix(prefix.value)
    
    def filter_by_type(self, key_type: KeyType) -> List[str]:
        """
        Get all keys of a specific type.
        
        Args:
            key_type: Key type to filter by
            
        Returns:
            List of matching keys
        """
        return self.store.search(key_type=key_type)
    
    def filter_by_namespace(
        self,
        namespace: str,
        recursive: bool = False
    ) -> List[str]:
        """
        Get all keys in a namespace.
        
        Args:
            namespace: Namespace path
            recursive: Whether to include child namespaces
            
        Returns:
            List of keys
        """
        return self.get_namespace_keys(namespace, recursive)
    
    # Usage Tracking Methods
    
    def get_usage_statistics(
        self,
        key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics for a key or all keys.
        
        Args:
            key: Optional specific key to get stats for
            
        Returns:
            Dictionary with usage statistics
        """
        return self.tracker.get_statistics(key)
    
    def get_most_accessed_keys(self, limit: int = 10) -> List[tuple[str, int]]:
        """
        Get the most frequently accessed keys.
        
        Args:
            limit: Number of keys to return
            
        Returns:
            List of (key, count) tuples
        """
        return self.tracker.get_most_accessed(limit)
    
    def get_recently_accessed_keys(
        self,
        limit: int = 10
    ) -> List[tuple[str, datetime]]:
        """
        Get the most recently accessed keys.
        
        Args:
            limit: Number of keys to return
            
        Returns:
            List of (key, datetime) tuples
        """
        return self.tracker.get_recently_accessed(limit)
    
    def get_unused_keys(self) -> List[str]:
        """
        Get keys that have never been accessed.
        
        Returns:
            List of unused keys
        """
        all_keys = self.store.get_all_keys()
        return self.tracker.get_unused_keys(all_keys)
    
    def reset_usage_tracking(self, key: Optional[str] = None) -> None:
        """
        Reset usage statistics.
        
        Args:
            key: Optional specific key to reset, or all if None
        """
        self.tracker.reset(key)
    
    # Index Methods
    
    def add_to_index(
        self,
        key: str,
        obj: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an object to the key index.
        
        Args:
            key: Dynamic key for the object
            obj: Object to index
            metadata: Optional metadata
        """
        self.index.add(key, obj, metadata)
    
    def get_from_index(self, key: str) -> Optional[Any]:
        """
        Get an object from the index by key.
        
        Args:
            key: Key to lookup
            
        Returns:
            Object or None if not found
        """
        return self.index.get(key)
    
    def remove_from_index(self, key: str) -> bool:
        """
        Remove an object from the index.
        
        Args:
            key: Key to remove
            
        Returns:
            True if removed, False if not found
        """
        return self.index.remove(key)
    
    def index_exists(self, key: str) -> bool:
        """
        Check if a key exists in the index.
        
        Args:
            key: Key to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.index.exists(key)
    
    # Metadata Methods
    
    def get_key_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a key.
        
        Args:
            key: Key to check
            
        Returns:
            Metadata dictionary or None
        """
        return self.store.get_metadata(key)
    
    def set_key_metadata(
        self,
        key: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Set metadata for a key.
        
        Args:
            key: Key to update
            metadata: Metadata to set
        """
        self.store.set_metadata(key, metadata)
    
    def get_key_type(self, key: str) -> Optional[KeyType]:
        """
        Get the type of a key.
        
        Args:
            key: Key to check
            
        Returns:
            KeyType or None if not specified
        """
        return self.store.get_type(key)
    
    # Bulk Operations
    
    def bulk_set(
        self,
        items: Dict[str, Any],
        key_type: Optional[KeyType] = None,
        namespace: Optional[str] = None
    ) -> None:
        """
        Set multiple key-value pairs at once.
        
        Args:
            items: Dictionary of key-value pairs
            key_type: Optional type for all items
            namespace: Optional namespace for all items
        """
        for key, value in items.items():
            self.set_value(
                key=key,
                value=value,
                key_type=key_type,
                namespace=namespace,
                track_usage=False
            )
    
    def bulk_get(
        self,
        keys: List[str],
        track_usage: bool = False
    ) -> Dict[str, Any]:
        """
        Get multiple values at once.
        
        Args:
            keys: List of keys to retrieve
            track_usage: Whether to track these operations
            
        Returns:
            Dictionary of key-value pairs
        """
        return {
            key: self.get_value(key, track_usage=track_usage)
            for key in keys
        }
    
    def bulk_delete(self, keys: List[str]) -> int:
        """
        Delete multiple keys at once.
        
        Args:
            keys: List of keys to delete
            
        Returns:
            Number of keys deleted
        """
        count = 0
        for key in keys:
            if self.delete_value(key):
                count += 1
        return count
    
    # Export/Import Methods
    
    def export_configuration(
        self,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export configuration to dictionary.
        
        Args:
            namespace: Optional namespace to export
            
        Returns:
            Dictionary with configuration data
        """
        return self.store.export_to_dict(namespace)
    
    def import_configuration(
        self,
        data: Dict[str, Any],
        namespace: Optional[str] = None
    ) -> None:
        """
        Import configuration from dictionary.
        
        Args:
            data: Dictionary with configuration data
            namespace: Optional namespace to import into
        """
        self.store.import_from_dict(data, namespace)
    
    # Statistics Methods
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the key system.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'store': {
                'total_keys': self.store.count(),
                'namespaces': len(self.store.list_namespaces()),
                'keys_by_namespace': {
                    ns: self.store.count(ns)
                    for ns in self.store.list_namespaces()
                }
            },
            'index': self.index.get_statistics(),
            'usage': self.tracker.get_statistics(),
            'most_accessed': self.get_most_accessed_keys(5),
            'recently_accessed': [
                (k, v.isoformat())
                for k, v in self.get_recently_accessed_keys(5)
            ],
            'unused_count': len(self.get_unused_keys())
        }
    
    def clear_all(self, namespace: Optional[str] = None) -> None:
        """
        Clear all data, optionally in a specific namespace.
        
        Args:
            namespace: Optional namespace to clear
        """
        if namespace:
            keys = self.get_namespace_keys(namespace, recursive=True)
            for key in keys:
                self.delete_value(key)
                self.remove_from_index(key)
        else:
            self.store.clear()
            self.index.clear()
            self.reset_usage_tracking()


# Global service instance
_global_dynamic_key_service = DynamicKeyService()


def get_dynamic_key_service() -> DynamicKeyService:
    """
    Get the global dynamic key service instance.
    
    Returns:
        Global DynamicKeyService instance
    """
    return _global_dynamic_key_service
