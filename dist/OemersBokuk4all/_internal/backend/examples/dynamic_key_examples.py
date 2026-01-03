"""
Dynamic Key System - Usage Examples

This module demonstrates practical usage of the Dynamic Key System
in various scenarios.
"""

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
from datetime import datetime
from typing import Dict, Any, List


# Example 1: Basic Model with Dynamic Keys
class SolarCalculation(DynamicKeyMixin):
    """Solar calculation with automatic key generation"""
    
    def __init__(self, power: float, modules: int, location: str):
        super().__init__()
        self.power = power
        self.modules = modules
        self.location = location
        self.created_at = datetime.now()
        
        # Generate key automatically
        self.key = self.generate_dynamic_key(
            KeyPrefix.SOLAR_CALCULATION,
            custom_suffix=location.lower().replace(' ', '_')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with key"""
        return {
            'key': self.key,
            'power': self.power,
            'modules': self.modules,
            'location': self.location,
            'created_at': self.created_at.isoformat()
        }


# Example 2: Service with Index Management
class SolarCalculationService:
    """Service for managing solar calculations with indexed access"""
    
    def __init__(self):
        self.index = DynamicKeyIndex()
        self.validator = DynamicKeyValidator()
    
    def create_calculation(
        self,
        power: float,
        modules: int,
        location: str
    ) -> SolarCalculation:
        """Create and index a new calculation"""
        calc = SolarCalculation(power, modules, location)
        
        # Add to index with metadata
        metadata = {
            'created_at': datetime.now().isoformat(),
            'location': location,
            'power_range': self._get_power_range(power)
        }
        
        self.index.add(calc.key, calc, metadata)
        
        return calc
    
    def get_calculation(self, key: str) -> SolarCalculation:
        """Retrieve calculation by key"""
        if not self.validator.validate(key)[0]:
            raise ValueError(f"Invalid key: {key}")
        
        return self.index.get(key)
    
    def get_calculations_by_location(self, location: str) -> List[SolarCalculation]:
        """Get all calculations for a location"""
        all_calcs = self.index.get_by_prefix(KeyPrefix.SOLAR_CALCULATION.value)
        return [
            calc for calc in all_calcs
            if calc.location.lower() == location.lower()
        ]
    
    def get_all_calculations(self) -> List[SolarCalculation]:
        """Get all solar calculations"""
        return self.index.get_by_prefix(KeyPrefix.SOLAR_CALCULATION.value)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        stats = self.index.get_statistics()
        solar_count = self.index.count_by_prefix(KeyPrefix.SOLAR_CALCULATION.value)
        
        return {
            'total_calculations': solar_count,
            'index_stats': stats
        }
    
    @staticmethod
    def _get_power_range(power: float) -> str:
        """Categorize power into ranges"""
        if power < 5:
            return 'small'
        elif power < 10:
            return 'medium'
        else:
            return 'large'


# Example 3: Multi-Type Data Manager
class DataManager:
    """Manager for multiple data types with unified key system"""
    
    def __init__(self):
        self.index = get_global_key_index()
    
    def add_solar_calculation(self, data: Dict[str, Any]) -> str:
        """Add solar calculation"""
        calc = SolarCalculation(
            data['power'],
            data['modules'],
            data['location']
        )
        self.index.add(calc.key, calc.to_dict())
        return calc.key
    
    def add_project(self, name: str, customer: str) -> str:
        """Add project"""
        mixin = DynamicKeyMixin()
        key = mixin.generate_dynamic_key(
            KeyPrefix.PROJECT,
            custom_suffix=name.lower().replace(' ', '_')
        )
        
        project_data = {
            'name': name,
            'customer': customer,
            'created_at': datetime.now().isoformat()
        }
        
        self.index.add(key, project_data)
        return key
    
    def add_customer(self, name: str, email: str) -> str:
        """Add customer with hash-based key"""
        # Use email hash for deterministic key
        key = generate_hash_key(email, KeyPrefix.CUSTOMER)
        
        customer_data = {
            'name': name,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        
        self.index.add(key, customer_data)
        return key
    
    def get_by_type(self, data_type: KeyPrefix) -> List[Any]:
        """Get all data of a specific type"""
        return self.index.get_by_prefix(data_type.value)
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of all data types"""
        summary = {}
        for prefix in self.index.get_all_prefixes():
            count = self.index.count_by_prefix(prefix)
            summary[prefix] = count
        return summary


# Example 4: Validation Service
class KeyValidationService:
    """Service for validating and managing keys"""
    
    def __init__(self):
        self.validator = DynamicKeyValidator()
        self._setup_rules()
    
    def _setup_rules(self):
        """Configure validation rules"""
        self.validator.set_rule('min_length', 10)
        self.validator.set_rule('max_length', 150)
        self.validator.set_rule('require_prefix', True)
    
    def validate_key(self, key: str, strict: bool = True) -> Dict[str, Any]:
        """Validate a key and return detailed results"""
        is_valid, error = self.validator.validate(key, strict)
        
        result = {
            'key': key,
            'is_valid': is_valid,
            'error': error
        }
        
        if is_valid:
            # Add additional info for valid keys
            result['prefix'] = DynamicKeyMixin.extract_prefix(key)
            result['components'] = DynamicKeyMixin.extract_components(key)
        
        return result
    
    def validate_batch(self, keys: List[str]) -> Dict[str, Any]:
        """Validate multiple keys"""
        results = []
        valid_count = 0
        invalid_count = 0
        
        for key in keys:
            result = self.validate_key(key)
            results.append(result)
            
            if result['is_valid']:
                valid_count += 1
            else:
                invalid_count += 1
        
        return {
            'total': len(keys),
            'valid': valid_count,
            'invalid': invalid_count,
            'results': results
        }
    
    def suggest_fix(self, invalid_key: str) -> str:
        """Suggest a fix for an invalid key"""
        # Try to extract components and rebuild
        parts = invalid_key.split('_')
        
        if len(parts) < 2:
            return f"DAT_{invalid_key}"
        
        # Ensure first part is uppercase
        prefix = parts[0].upper()
        
        # Rebuild key
        fixed_key = '_'.join([prefix] + parts[1:])
        
        return fixed_key


# Example 5: Caching with Keys
class CachedDataService:
    """Service demonstrating caching with dynamic keys"""
    
    def __init__(self):
        self.cache = DynamicKeyIndex()
        self.ttl_seconds = 3600  # 1 hour
    
    def cache_calculation(self, calc: SolarCalculation) -> str:
        """Cache a calculation result"""
        metadata = {
            'cached_at': datetime.now().isoformat(),
            'ttl_seconds': self.ttl_seconds
        }
        
        self.cache.add(calc.key, calc.to_dict(), metadata)
        return calc.key
    
    def get_cached(self, key: str) -> Dict[str, Any]:
        """Get cached data if not expired"""
        if not self.cache.exists(key):
            return None
        
        metadata = self.cache.get_metadata(key)
        if metadata:
            cached_at = datetime.fromisoformat(metadata['cached_at'])
            age = (datetime.now() - cached_at).total_seconds()
            
            if age > self.ttl_seconds:
                # Expired, remove from cache
                self.cache.remove(key)
                return None
        
        return self.cache.get(key)
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries"""
        removed_count = 0
        
        for key in list(self.cache._index.keys()):
            metadata = self.cache.get_metadata(key)
            if metadata:
                cached_at = datetime.fromisoformat(metadata['cached_at'])
                age = (datetime.now() - cached_at).total_seconds()
                
                if age > self.ttl_seconds:
                    self.cache.remove(key)
                    removed_count += 1
        
        return removed_count


# Example 6: Demonstration Functions
def demo_basic_usage():
    """Demonstrate basic key generation and usage"""
    print("=== Basic Usage Demo ===\n")
    
    # Create calculation
    calc = SolarCalculation(10.5, 30, "Berlin")
    print(f"Created calculation with key: {calc.key}")
    print(f"Data: {calc.to_dict()}\n")
    
    # Get key metadata
    metadata = calc.get_key_metadata()
    print(f"Key metadata: {metadata}\n")


def demo_service_usage():
    """Demonstrate service with index"""
    print("=== Service Usage Demo ===\n")
    
    service = SolarCalculationService()
    
    # Create multiple calculations
    calc1 = service.create_calculation(10.5, 30, "Berlin")
    calc2 = service.create_calculation(15.0, 45, "Munich")
    calc3 = service.create_calculation(8.5, 25, "Berlin")
    
    print(f"Created 3 calculations")
    print(f"Keys: {calc1.key}, {calc2.key}, {calc3.key}\n")
    
    # Retrieve by location
    berlin_calcs = service.get_calculations_by_location("Berlin")
    print(f"Berlin calculations: {len(berlin_calcs)}")
    
    # Get statistics
    stats = service.get_statistics()
    print(f"Statistics: {stats}\n")


def demo_multi_type():
    """Demonstrate multi-type data management"""
    print("=== Multi-Type Data Demo ===\n")
    
    manager = DataManager()
    
    # Add different types of data
    solar_key = manager.add_solar_calculation({
        'power': 10.5,
        'modules': 30,
        'location': 'Berlin'
    })
    
    project_key = manager.add_project("House Solar", "John Doe")
    customer_key = manager.add_customer("John Doe", "john@example.com")
    
    print(f"Solar key: {solar_key}")
    print(f"Project key: {project_key}")
    print(f"Customer key: {customer_key}\n")
    
    # Get summary
    summary = manager.get_summary()
    print(f"Data summary: {summary}\n")


def demo_validation():
    """Demonstrate key validation"""
    print("=== Validation Demo ===\n")
    
    validator_service = KeyValidationService()
    
    # Test various keys
    test_keys = [
        "SOL_20231116_143052_a1b2c3d4",
        "invalid_key",
        "HP_test",
        "PRJ_20231116_143052_a1b2c3d4_important"
    ]
    
    results = validator_service.validate_batch(test_keys)
    
    print(f"Validated {results['total']} keys")
    print(f"Valid: {results['valid']}, Invalid: {results['invalid']}\n")
    
    for result in results['results']:
        status = "" if result['is_valid'] else ""
        print(f"{status} {result['key']}")
        if not result['is_valid']:
            print(f"  Error: {result['error']}")
            fixed = validator_service.suggest_fix(result['key'])
            print(f"  Suggested fix: {fixed}")
    print()


def demo_caching():
    """Demonstrate caching with keys"""
    print("=== Caching Demo ===\n")
    
    cache_service = CachedDataService()
    
    # Create and cache calculation
    calc = SolarCalculation(10.5, 30, "Berlin")
    cache_service.cache_calculation(calc)
    
    print(f"Cached calculation: {calc.key}")
    
    # Retrieve from cache
    cached_data = cache_service.get_cached(calc.key)
    print(f"Retrieved from cache: {cached_data is not None}")
    print(f"Data: {cached_data}\n")


def run_all_demos():
    """Run all demonstration functions"""
    demo_basic_usage()
    demo_service_usage()
    demo_multi_type()
    demo_validation()
    demo_caching()
    
    print("=== All Demos Complete ===")


if __name__ == "__main__":
    run_all_demos()
