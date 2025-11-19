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
