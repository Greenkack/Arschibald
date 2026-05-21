"""
Dynamic Key System Infrastructure

This module provides a comprehensive system for generating, managing, and validating
dynamic keys for all data types in the application. It supports unique key generation,
key prefixes for different data types, validation, and fast lookup through indexing.

Requirements: 14.4, 14.7
"""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from uuid import uuid4
import hashlib
import re
from enum import Enum


class KeyPrefix(str, Enum):
    """Enumeration of key prefixes for different data types"""
    
    # Core entities
    USER = "USR"
    PROJECT = "PRJ"
    CUSTOMER = "CUS"
    
    # Solar calculator
    SOLAR_CALCULATION = "SOL"
    SOLAR_MODULE = "MOD"
    SOLAR_INVERTER = "INV"
    SOLAR_BATTERY = "BAT"
    
    # Heat pump
    HEATPUMP_CALCULATION = "HP"
    HEATPUMP_PRODUCT = "HPP"
    
    # Price matrix
    PRICE_MATRIX = "PMX"
    PRICE_CALCULATION = "PRC"
    PRODUCT = "PRD"
    
    # PDF
    PDF_DOCUMENT = "PDF"
    PDF_TEMPLATE = "TPL"
    
    # 3D Visualization
    VISUALIZATION_3D = "VIS"
    MODULE_PLACEMENT = "PLC"
    
    # CRM
    OFFER = "OFF"
    TASK = "TSK"
    NOTE = "NOT"
    EMAIL = "EML"
    CONTRACT = "CNT"
    
    # Configuration
    CONFIG = "CFG"
    SETTING = "SET"
    
    # Media
    IMAGE = "IMG"
    DOCUMENT = "DOC"
    CHART = "CHT"
    
    # Generic
    DATA = "DAT"
    TEMP = "TMP"


class DynamicKeyMixin:
    """
    Mixin class that provides dynamic key generation capabilities to any model.
    
    This mixin adds methods for generating unique keys, managing key metadata,
    and providing key-based access to data.
    """
    
    def __init__(self):
        """Initialize the mixin with key tracking"""
        self._dynamic_key: Optional[str] = None
        self._key_metadata: Dict[str, Any] = {}
        self._key_created_at: Optional[datetime] = None
    
    def generate_dynamic_key(
        self,
        prefix: KeyPrefix = KeyPrefix.DATA,
        include_timestamp: bool = True,
        include_uuid: bool = True,
        custom_suffix: Optional[str] = None
    ) -> str:
        """
        Generate a unique dynamic key with specified components.
        
        Args:
            prefix: Key prefix indicating data type
            include_timestamp: Whether to include timestamp in key
            include_uuid: Whether to include UUID in key
            custom_suffix: Optional custom suffix to append
            
        Returns:
            Generated dynamic key string
            
        Example:
            >>> mixin = DynamicKeyMixin()
            >>> key = mixin.generate_dynamic_key(KeyPrefix.SOLAR_CALCULATION)
            >>> print(key)
            'SOL_20231116_143052_a1b2c3d4_e5f6'
        """
        components = [prefix.value]
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            components.append(timestamp)
        
        if include_uuid:
            # Use short UUID (first 8 chars of hex)
            short_uuid = uuid4().hex[:8]
            components.append(short_uuid)
        
        # Add entity ID if available
        if hasattr(self, 'id') and self.id is not None:
            components.append(str(self.id))
        
        if custom_suffix:
            components.append(custom_suffix)
        
        key = "_".join(components)
        
        # Store key and metadata
        self._dynamic_key = key
        self._key_created_at = datetime.now()
        self._key_metadata = {
            'prefix': prefix.value,
            'created_at': self._key_created_at.isoformat(),
            'has_timestamp': include_timestamp,
            'has_uuid': include_uuid,
            'custom_suffix': custom_suffix
        }
        
        return key
    
    def get_dynamic_key(self) -> Optional[str]:
        """
        Get the current dynamic key.
        
        Returns:
            Current dynamic key or None if not generated
        """
        return self._dynamic_key
    
    def set_dynamic_key(self, key: str, validate: bool = True) -> None:
        """
        Set a dynamic key manually.
        
        Args:
            key: Key string to set
            validate: Whether to validate the key format
            
        Raises:
            ValueError: If validation fails
        """
        if validate and not self.validate_key(key):
            raise ValueError(f"Invalid key format: {key}")
        
        self._dynamic_key = key
        self._key_created_at = datetime.now()
    
    def get_key_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the dynamic key.
        
        Returns:
            Dictionary containing key metadata
        """
        return {
            **self._key_metadata,
            'current_key': self._dynamic_key,
            'key_age_seconds': (
                (datetime.now() - self._key_created_at).total_seconds()
                if self._key_created_at else None
            )
        }
    
    @staticmethod
    def validate_key(key: str) -> bool:
        """
        Validate a dynamic key format.
        
        Args:
            key: Key string to validate
            
        Returns:
            True if key is valid, False otherwise
            
        Example:
            >>> DynamicKeyMixin.validate_key("SOL_20231116_143052_a1b2c3d4")
            True
            >>> DynamicKeyMixin.validate_key("invalid_key")
            False
        """
        # Pattern: PREFIX_[TIMESTAMP]_[UUID]_[ID]_[SUFFIX]
        # At minimum: PREFIX_something
        pattern = r'^[A-Z]{2,4}(_[a-zA-Z0-9]+)+$'
        return bool(re.match(pattern, key))
    
    @staticmethod
    def extract_prefix(key: str) -> Optional[str]:
        """
        Extract the prefix from a dynamic key.
        
        Args:
            key: Key string to parse
            
        Returns:
            Prefix string or None if invalid
        """
        if not key:
            return None
        
        parts = key.split('_')
        return parts[0] if parts else None
    
    @staticmethod
    def extract_components(key: str) -> Dict[str, str]:
        """
        Extract all components from a dynamic key.
        
        Args:
            key: Key string to parse
            
        Returns:
            Dictionary with extracted components
        """
        if not key:
            return {}
        
        parts = key.split('_')
        components = {
            'prefix': parts[0] if len(parts) > 0 else None,
            'full_key': key,
            'parts': parts
        }
        
        # Try to identify timestamp (YYYYMMDD format)
        for i, part in enumerate(parts):
            if len(part) == 8 and part.isdigit():
                components['date'] = part
                components['date_index'] = i
                break
        
        # Try to identify UUID (8 hex chars)
        for i, part in enumerate(parts):
            if len(part) == 8 and all(c in '0123456789abcdef' for c in part.lower()):
                components['uuid'] = part
                components['uuid_index'] = i
                break
        
        return components
    
    def to_dict_with_key(self) -> Dict[str, Any]:
        """
        Convert object to dictionary including dynamic key.
        
        Returns:
            Dictionary representation with key metadata
        """
        base_dict = {}
        
        # Get base attributes
        if hasattr(self, '__dict__'):
            base_dict = {
                k: v for k, v in self.__dict__.items()
                if not k.startswith('_')
            }
        
        # Add key information
        return {
            **base_dict,
            'dynamic_key': self._dynamic_key,
            'key_metadata': self._key_metadata,
            'key_created_at': self._key_created_at.isoformat() if self._key_created_at else None
        }


class DynamicKeyIndex:
    """
    Index system for fast lookup of objects by their dynamic keys.
    
    This class provides O(1) lookup performance for key-based access
    and supports prefix-based queries for finding related objects.
    """
    
    def __init__(self):
        """Initialize the key index"""
        self._index: Dict[str, Any] = {}
        self._prefix_index: Dict[str, Set[str]] = {}
        self._metadata_index: Dict[str, Dict[str, Any]] = {}
    
    def add(self, key: str, obj: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an object to the index.
        
        Args:
            key: Dynamic key for the object
            obj: Object to index
            metadata: Optional metadata to store with the key
        """
        if not DynamicKeyMixin.validate_key(key):
            raise ValueError(f"Invalid key format: {key}")
        
        # Add to main index
        self._index[key] = obj
        
        # Add to prefix index
        prefix = DynamicKeyMixin.extract_prefix(key)
        if prefix:
            if prefix not in self._prefix_index:
                self._prefix_index[prefix] = set()
            self._prefix_index[prefix].add(key)
        
        # Add metadata
        if metadata:
            self._metadata_index[key] = metadata
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get an object by its dynamic key.
        
        Args:
            key: Dynamic key to lookup
            
        Returns:
            Object associated with key or None if not found
        """
        return self._index.get(key)
    
    def remove(self, key: str) -> bool:
        """
        Remove an object from the index.
        
        Args:
            key: Dynamic key to remove
            
        Returns:
            True if removed, False if not found
        """
        if key not in self._index:
            return False
        
        # Remove from main index
        del self._index[key]
        
        # Remove from prefix index
        prefix = DynamicKeyMixin.extract_prefix(key)
        if prefix and prefix in self._prefix_index:
            self._prefix_index[prefix].discard(key)
            if not self._prefix_index[prefix]:
                del self._prefix_index[prefix]
        
        # Remove metadata
        if key in self._metadata_index:
            del self._metadata_index[key]
        
        return True
    
    def get_by_prefix(self, prefix: str) -> List[Any]:
        """
        Get all objects with a specific prefix.
        
        Args:
            prefix: Key prefix to search for
            
        Returns:
            List of objects with matching prefix
        """
        if prefix not in self._prefix_index:
            return []
        
        keys = self._prefix_index[prefix]
        return [self._index[key] for key in keys if key in self._index]
    
    def get_keys_by_prefix(self, prefix: str) -> List[str]:
        """
        Get all keys with a specific prefix.
        
        Args:
            prefix: Key prefix to search for
            
        Returns:
            List of keys with matching prefix
        """
        return list(self._prefix_index.get(prefix, set()))
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the index.
        
        Args:
            key: Dynamic key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return key in self._index
    
    def count(self) -> int:
        """
        Get total number of indexed objects.
        
        Returns:
            Count of indexed objects
        """
        return len(self._index)
    
    def count_by_prefix(self, prefix: str) -> int:
        """
        Get count of objects with specific prefix.
        
        Args:
            prefix: Key prefix to count
            
        Returns:
            Count of objects with matching prefix
        """
        return len(self._prefix_index.get(prefix, set()))
    
    def get_all_prefixes(self) -> List[str]:
        """
        Get list of all prefixes in the index.
        
        Returns:
            List of unique prefixes
        """
        return list(self._prefix_index.keys())
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific key.
        
        Args:
            key: Dynamic key to lookup
            
        Returns:
            Metadata dictionary or None if not found
        """
        return self._metadata_index.get(key)
    
    def clear(self) -> None:
        """Clear all entries from the index"""
        self._index.clear()
        self._prefix_index.clear()
        self._metadata_index.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            'total_keys': len(self._index),
            'total_prefixes': len(self._prefix_index),
            'keys_by_prefix': {
                prefix: len(keys)
                for prefix, keys in self._prefix_index.items()
            },
            'has_metadata': len(self._metadata_index)
        }


class DynamicKeyValidator:
    """
    Validator for dynamic keys with configurable rules.
    """
    
    def __init__(self):
        """Initialize validator with default rules"""
        self.rules: Dict[str, Any] = {
            'min_length': 5,
            'max_length': 100,
            'allowed_prefixes': [p.value for p in KeyPrefix],
            'require_prefix': True,
            'allow_custom_prefix': False
        }
    
    def validate(self, key: str, strict: bool = True) -> tuple[bool, Optional[str]]:
        """
        Validate a dynamic key against configured rules.
        
        Args:
            key: Key to validate
            strict: Whether to apply strict validation
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not key:
            return False, "Key cannot be empty"
        
        # Length check
        if len(key) < self.rules['min_length']:
            return False, f"Key too short (min: {self.rules['min_length']})"
        
        if len(key) > self.rules['max_length']:
            return False, f"Key too long (max: {self.rules['max_length']})"
        
        # Format check
        if not DynamicKeyMixin.validate_key(key):
            return False, "Invalid key format"
        
        # Prefix check
        if self.rules['require_prefix']:
            prefix = DynamicKeyMixin.extract_prefix(key)
            if not prefix:
                return False, "Key must have a prefix"
            
            if strict and not self.rules['allow_custom_prefix']:
                if prefix not in self.rules['allowed_prefixes']:
                    return False, f"Invalid prefix: {prefix}"
        
        return True, None
    
    def set_rule(self, rule_name: str, value: Any) -> None:
        """
        Set a validation rule.
        
        Args:
            rule_name: Name of the rule to set
            value: Value for the rule
        """
        self.rules[rule_name] = value
    
    def get_rule(self, rule_name: str) -> Any:
        """
        Get a validation rule value.
        
        Args:
            rule_name: Name of the rule to get
            
        Returns:
            Rule value or None if not found
        """
        return self.rules.get(rule_name)


# Global key index instance
_global_key_index = DynamicKeyIndex()


def get_global_key_index() -> DynamicKeyIndex:
    """
    Get the global key index instance.
    
    Returns:
        Global DynamicKeyIndex instance
    """
    return _global_key_index


def generate_hash_key(data: str, prefix: KeyPrefix = KeyPrefix.DATA) -> str:
    """
    Generate a hash-based dynamic key from data.
    
    Args:
        data: Data to hash
        prefix: Key prefix to use
        
    Returns:
        Hash-based dynamic key
    """
    hash_obj = hashlib.sha256(data.encode())
    hash_hex = hash_obj.hexdigest()[:16]  # Use first 16 chars
    return f"{prefix.value}_{hash_hex}"


class KeyType(str, Enum):
    """Enumeration of key value types for validation and typing"""
    
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    BINARY = "binary"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    EMAIL = "email"
    URL = "url"


class KeyNamespace:
    """
    Namespace system for organizing keys hierarchically.
    
    Namespaces provide logical grouping of keys and prevent naming conflicts.
    """
    
    def __init__(self, name: str, parent: Optional['KeyNamespace'] = None):
        """
        Initialize a key namespace.
        
        Args:
            name: Namespace name
            parent: Optional parent namespace for hierarchy
        """
        self.name = name
        self.parent = parent
        self.children: Dict[str, 'KeyNamespace'] = {}
        self.keys: Set[str] = set()
        self.metadata: Dict[str, Any] = {}
    
    def get_full_path(self) -> str:
        """
        Get the full hierarchical path of this namespace.
        
        Returns:
            Full namespace path (e.g., "root.solar.calculations")
        """
        if self.parent:
            return f"{self.parent.get_full_path()}.{self.name}"
        return self.name
    
    def add_child(self, name: str) -> 'KeyNamespace':
        """
        Add a child namespace.
        
        Args:
            name: Child namespace name
            
        Returns:
            Created child namespace
        """
        if name not in self.children:
            self.children[name] = KeyNamespace(name, parent=self)
        return self.children[name]
    
    def get_child(self, name: str) -> Optional['KeyNamespace']:
        """
        Get a child namespace by name.
        
        Args:
            name: Child namespace name
            
        Returns:
            Child namespace or None if not found
        """
        return self.children.get(name)
    
    def add_key(self, key: str) -> None:
        """
        Add a key to this namespace.
        
        Args:
            key: Key to add
        """
        self.keys.add(key)
    
    def remove_key(self, key: str) -> bool:
        """
        Remove a key from this namespace.
        
        Args:
            key: Key to remove
            
        Returns:
            True if removed, False if not found
        """
        if key in self.keys:
            self.keys.discard(key)
            return True
        return False
    
    def has_key(self, key: str) -> bool:
        """
        Check if a key exists in this namespace.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return key in self.keys
    
    def get_all_keys(self, recursive: bool = False) -> List[str]:
        """
        Get all keys in this namespace.
        
        Args:
            recursive: Whether to include keys from child namespaces
            
        Returns:
            List of keys
        """
        keys = list(self.keys)
        
        if recursive:
            for child in self.children.values():
                keys.extend(child.get_all_keys(recursive=True))
        
        return keys
    
    def count_keys(self, recursive: bool = False) -> int:
        """
        Count keys in this namespace.
        
        Args:
            recursive: Whether to include keys from child namespaces
            
        Returns:
            Number of keys
        """
        count = len(self.keys)
        
        if recursive:
            for child in self.children.values():
                count += child.count_keys(recursive=True)
        
        return count
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert namespace to dictionary representation.
        
        Returns:
            Dictionary with namespace structure
        """
        return {
            'name': self.name,
            'full_path': self.get_full_path(),
            'keys': list(self.keys),
            'key_count': len(self.keys),
            'children': {
                name: child.to_dict()
                for name, child in self.children.items()
            },
            'metadata': self.metadata
        }


class KeyValueStore:
    """
    Key-value configuration storage with typing and validation.
    
    This class provides a typed key-value store with support for
    namespaces, validation, and metadata.
    """
    
    def __init__(self):
        """Initialize the key-value store"""
        self._store: Dict[str, Any] = {}
        self._types: Dict[str, KeyType] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._namespaces: Dict[str, KeyNamespace] = {}
        self._root_namespace = KeyNamespace("root")
        self._namespaces["root"] = self._root_namespace
    
    def set(
        self,
        key: str,
        value: Any,
        key_type: Optional[KeyType] = None,
        namespace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set a key-value pair with optional typing and namespace.
        
        Args:
            key: Key to set
            value: Value to store
            key_type: Optional type specification
            namespace: Optional namespace path
            metadata: Optional metadata for the key
            
        Raises:
            ValueError: If value doesn't match specified type
        """
        # Validate type if specified
        if key_type:
            if not self._validate_type(value, key_type):
                raise ValueError(f"Value does not match type {key_type}")
            self._types[key] = key_type
        
        # Store value
        self._store[key] = value
        
        # Store metadata
        if metadata:
            self._metadata[key] = metadata
        
        # Add to namespace
        if namespace:
            ns = self._get_or_create_namespace(namespace)
            ns.add_key(key)
        else:
            self._root_namespace.add_key(key)
    
    def get(
        self,
        key: str,
        default: Any = None,
        validate_type: bool = True
    ) -> Any:
        """
        Get a value by key.
        
        Args:
            key: Key to retrieve
            default: Default value if key not found
            validate_type: Whether to validate type on retrieval
            
        Returns:
            Stored value or default
        """
        if key not in self._store:
            return default
        
        value = self._store[key]
        
        # Validate type if requested and type is defined
        if validate_type and key in self._types:
            if not self._validate_type(value, self._types[key]):
                raise ValueError(f"Stored value does not match expected type {self._types[key]}")
        
        return value
    
    def delete(self, key: str) -> bool:
        """
        Delete a key-value pair.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted, False if not found
        """
        if key not in self._store:
            return False
        
        # Remove from store
        del self._store[key]
        
        # Remove type
        if key in self._types:
            del self._types[key]
        
        # Remove metadata
        if key in self._metadata:
            del self._metadata[key]
        
        # Remove from namespaces
        for ns in self._namespaces.values():
            ns.remove_key(key)
        
        return True
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return key in self._store
    
    def get_type(self, key: str) -> Optional[KeyType]:
        """
        Get the type of a key.
        
        Args:
            key: Key to check
            
        Returns:
            KeyType or None if not specified
        """
        return self._types.get(key)
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a key.
        
        Args:
            key: Key to check
            
        Returns:
            Metadata dictionary or None
        """
        return self._metadata.get(key)
    
    def set_metadata(self, key: str, metadata: Dict[str, Any]) -> None:
        """
        Set metadata for a key.
        
        Args:
            key: Key to update
            metadata: Metadata to set
        """
        if key in self._store:
            self._metadata[key] = metadata
    
    def search(
        self,
        pattern: Optional[str] = None,
        namespace: Optional[str] = None,
        key_type: Optional[KeyType] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Search for keys matching criteria.
        
        Args:
            pattern: Regex pattern to match keys
            namespace: Namespace to search in
            key_type: Filter by key type
            metadata_filter: Filter by metadata values
            
        Returns:
            List of matching keys
        """
        keys = list(self._store.keys())
        
        # Filter by namespace
        if namespace:
            ns = self._get_namespace(namespace)
            if ns:
                keys = [k for k in keys if ns.has_key(k)]
            else:
                return []
        
        # Filter by pattern
        if pattern:
            regex = re.compile(pattern)
            keys = [k for k in keys if regex.search(k)]
        
        # Filter by type
        if key_type:
            keys = [k for k in keys if self._types.get(k) == key_type]
        
        # Filter by metadata
        if metadata_filter:
            keys = [
                k for k in keys
                if k in self._metadata and
                all(
                    self._metadata[k].get(mk) == mv
                    for mk, mv in metadata_filter.items()
                )
            ]
        
        return keys
    
    def get_all_keys(self, namespace: Optional[str] = None) -> List[str]:
        """
        Get all keys, optionally filtered by namespace.
        
        Args:
            namespace: Optional namespace to filter by
            
        Returns:
            List of keys
        """
        if namespace:
            ns = self._get_namespace(namespace)
            return ns.get_all_keys(recursive=True) if ns else []
        return list(self._store.keys())
    
    def get_namespace(self, path: str) -> Optional[KeyNamespace]:
        """
        Get a namespace by path.
        
        Args:
            path: Namespace path (e.g., "root.solar.calculations")
            
        Returns:
            KeyNamespace or None if not found
        """
        return self._get_namespace(path)
    
    def create_namespace(self, path: str) -> KeyNamespace:
        """
        Create a namespace by path.
        
        Args:
            path: Namespace path (e.g., "root.solar.calculations")
            
        Returns:
            Created or existing namespace
        """
        return self._get_or_create_namespace(path)
    
    def list_namespaces(self) -> List[str]:
        """
        List all namespace paths.
        
        Returns:
            List of namespace paths
        """
        return list(self._namespaces.keys())
    
    def count(self, namespace: Optional[str] = None) -> int:
        """
        Count keys, optionally in a specific namespace.
        
        Args:
            namespace: Optional namespace to count in
            
        Returns:
            Number of keys
        """
        if namespace:
            ns = self._get_namespace(namespace)
            return ns.count_keys(recursive=True) if ns else 0
        return len(self._store)
    
    def clear(self, namespace: Optional[str] = None) -> None:
        """
        Clear all keys, optionally in a specific namespace.
        
        Args:
            namespace: Optional namespace to clear
        """
        if namespace:
            ns = self._get_namespace(namespace)
            if ns:
                keys_to_delete = ns.get_all_keys(recursive=True)
                for key in keys_to_delete:
                    self.delete(key)
        else:
            self._store.clear()
            self._types.clear()
            self._metadata.clear()
            self._namespaces.clear()
            self._root_namespace = KeyNamespace("root")
            self._namespaces["root"] = self._root_namespace
    
    def export_to_dict(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Export store to dictionary.
        
        Args:
            namespace: Optional namespace to export
            
        Returns:
            Dictionary with store data
        """
        keys = self.get_all_keys(namespace)
        
        return {
            key: {
                'value': self._store[key],
                'type': self._types.get(key).value if key in self._types else None,
                'metadata': self._metadata.get(key, {})
            }
            for key in keys
        }
    
    def import_from_dict(self, data: Dict[str, Any], namespace: Optional[str] = None) -> None:
        """
        Import store from dictionary.
        
        Args:
            data: Dictionary with store data
            namespace: Optional namespace to import into
        """
        for key, value_data in data.items():
            key_type = KeyType(value_data['type']) if value_data.get('type') else None
            self.set(
                key=key,
                value=value_data['value'],
                key_type=key_type,
                namespace=namespace,
                metadata=value_data.get('metadata')
            )
    
    def _validate_type(self, value: Any, key_type: KeyType) -> bool:
        """
        Validate that a value matches a key type.
        
        Args:
            value: Value to validate
            key_type: Expected type
            
        Returns:
            True if valid, False otherwise
        """
        if key_type == KeyType.STRING:
            return isinstance(value, str)
        elif key_type == KeyType.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)
        elif key_type == KeyType.FLOAT:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif key_type == KeyType.BOOLEAN:
            return isinstance(value, bool)
        elif key_type == KeyType.DATE:
            return isinstance(value, datetime) or (
                isinstance(value, str) and self._is_valid_date(value)
            )
        elif key_type == KeyType.DATETIME:
            return isinstance(value, datetime) or (
                isinstance(value, str) and self._is_valid_datetime(value)
            )
        elif key_type == KeyType.JSON:
            return isinstance(value, (dict, list))
        elif key_type == KeyType.BINARY:
            return isinstance(value, bytes)
        elif key_type == KeyType.CURRENCY:
            return isinstance(value, (int, float)) and value >= 0
        elif key_type == KeyType.PERCENTAGE:
            return isinstance(value, (int, float)) and 0 <= value <= 100
        elif key_type == KeyType.EMAIL:
            return isinstance(value, str) and '@' in value
        elif key_type == KeyType.URL:
            return isinstance(value, str) and (
                value.startswith('http://') or value.startswith('https://')
            )
        return True
    
    def _is_valid_date(self, value: str) -> bool:
        """Check if string is a valid date"""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _is_valid_datetime(self, value: str) -> bool:
        """Check if string is a valid datetime"""
        try:
            datetime.fromisoformat(value)
            return True
        except ValueError:
            return False
    
    def _get_namespace(self, path: str) -> Optional[KeyNamespace]:
        """Get namespace by path"""
        if path in self._namespaces:
            return self._namespaces[path]
        
        # Try to navigate from root
        parts = path.split('.')
        current = self._root_namespace
        
        for part in parts[1:] if parts[0] == 'root' else parts:
            current = current.get_child(part)
            if not current:
                return None
        
        return current
    
    def _get_or_create_namespace(self, path: str) -> KeyNamespace:
        """Get or create namespace by path"""
        if path in self._namespaces:
            return self._namespaces[path]
        
        # Create namespace hierarchy
        parts = path.split('.')
        current = self._root_namespace
        current_path = "root"
        
        for part in parts[1:] if parts[0] == 'root' else parts:
            current = current.add_child(part)
            current_path = f"{current_path}.{part}"
            self._namespaces[current_path] = current
        
        return current


class KeyUsageTracker:
    """
    Track usage statistics for dynamic keys.
    
    This class monitors key access patterns, frequency, and timing
    to provide insights into key usage.
    """
    
    def __init__(self):
        """Initialize the usage tracker"""
        self._access_count: Dict[str, int] = {}
        self._last_access: Dict[str, datetime] = {}
        self._first_access: Dict[str, datetime] = {}
        self._access_history: Dict[str, List[datetime]] = {}
        self._max_history_size = 100
    
    def record_access(self, key: str) -> None:
        """
        Record an access to a key.
        
        Args:
            key: Key that was accessed
        """
        now = datetime.now()
        
        # Increment access count
        self._access_count[key] = self._access_count.get(key, 0) + 1
        
        # Update last access
        self._last_access[key] = now
        
        # Set first access if not set
        if key not in self._first_access:
            self._first_access[key] = now
        
        # Add to history
        if key not in self._access_history:
            self._access_history[key] = []
        
        self._access_history[key].append(now)
        
        # Trim history if too large
        if len(self._access_history[key]) > self._max_history_size:
            self._access_history[key] = self._access_history[key][-self._max_history_size:]
    
    def get_access_count(self, key: str) -> int:
        """
        Get the number of times a key has been accessed.
        
        Args:
            key: Key to check
            
        Returns:
            Access count
        """
        return self._access_count.get(key, 0)
    
    def get_last_access(self, key: str) -> Optional[datetime]:
        """
        Get the last access time for a key.
        
        Args:
            key: Key to check
            
        Returns:
            Last access datetime or None
        """
        return self._last_access.get(key)
    
    def get_first_access(self, key: str) -> Optional[datetime]:
        """
        Get the first access time for a key.
        
        Args:
            key: Key to check
            
        Returns:
            First access datetime or None
        """
        return self._first_access.get(key)
    
    def get_access_history(self, key: str, limit: Optional[int] = None) -> List[datetime]:
        """
        Get access history for a key.
        
        Args:
            key: Key to check
            limit: Optional limit on number of entries
            
        Returns:
            List of access datetimes
        """
        history = self._access_history.get(key, [])
        if limit:
            return history[-limit:]
        return history
    
    def get_most_accessed(self, limit: int = 10) -> List[tuple[str, int]]:
        """
        Get the most frequently accessed keys.
        
        Args:
            limit: Number of keys to return
            
        Returns:
            List of (key, count) tuples
        """
        sorted_keys = sorted(
            self._access_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_keys[:limit]
    
    def get_recently_accessed(self, limit: int = 10) -> List[tuple[str, datetime]]:
        """
        Get the most recently accessed keys.
        
        Args:
            limit: Number of keys to return
            
        Returns:
            List of (key, datetime) tuples
        """
        sorted_keys = sorted(
            self._last_access.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_keys[:limit]
    
    def get_unused_keys(self, keys: List[str]) -> List[str]:
        """
        Get keys that have never been accessed.
        
        Args:
            keys: List of keys to check
            
        Returns:
            List of unused keys
        """
        return [k for k in keys if k not in self._access_count]
    
    def get_statistics(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics.
        
        Args:
            key: Optional specific key to get stats for
            
        Returns:
            Dictionary with statistics
        """
        if key:
            if key not in self._access_count:
                return {'key': key, 'accessed': False}
            
            first = self._first_access[key]
            last = self._last_access[key]
            duration = (last - first).total_seconds()
            count = self._access_count[key]
            
            return {
                'key': key,
                'accessed': True,
                'access_count': count,
                'first_access': first.isoformat(),
                'last_access': last.isoformat(),
                'duration_seconds': duration,
                'average_frequency': count / max(duration / 3600, 1),  # per hour
                'history_size': len(self._access_history.get(key, []))
            }
        else:
            total_accesses = sum(self._access_count.values())
            total_keys = len(self._access_count)
            
            return {
                'total_keys_accessed': total_keys,
                'total_accesses': total_accesses,
                'average_accesses_per_key': total_accesses / max(total_keys, 1),
                'most_accessed': self.get_most_accessed(5),
                'recently_accessed': [
                    (k, v.isoformat())
                    for k, v in self.get_recently_accessed(5)
                ]
            }
    
    def reset(self, key: Optional[str] = None) -> None:
        """
        Reset usage statistics.
        
        Args:
            key: Optional specific key to reset, or all if None
        """
        if key:
            self._access_count.pop(key, None)
            self._last_access.pop(key, None)
            self._first_access.pop(key, None)
            self._access_history.pop(key, None)
        else:
            self._access_count.clear()
            self._last_access.clear()
            self._first_access.clear()
            self._access_history.clear()


# Global instances
_global_key_value_store = KeyValueStore()
_global_usage_tracker = KeyUsageTracker()


def get_global_key_value_store() -> KeyValueStore:
    """
    Get the global key-value store instance.
    
    Returns:
        Global KeyValueStore instance
    """
    return _global_key_value_store


def get_global_usage_tracker() -> KeyUsageTracker:
    """
    Get the global usage tracker instance.
    
    Returns:
        Global KeyUsageTracker instance
    """
    return _global_usage_tracker
