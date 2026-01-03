"""
Dependency Injection Container

This module provides a simple dependency injection container for managing
service dependencies and lifecycle.
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar
import logging
from threading import Lock


logger = logging.getLogger(__name__)


T = TypeVar('T')


class DependencyContainer:
    """
    Simple dependency injection container.
    
    Supports:
    - Singleton registration
    - Factory registration
    - Lazy initialization
    - Thread-safe access
    """
    
    def __init__(self):
        """Initialize the dependency container"""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._lock = Lock()
        logger.info("Dependency container initialized")
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register a singleton instance.
        
        Args:
            name: Unique identifier for the dependency
            instance: The singleton instance
            
        Raises:
            ValueError: If name already registered
        """
        with self._lock:
            if name in self._singletons:
                raise ValueError(f"Singleton '{name}' already registered")
            
            self._singletons[name] = instance
            logger.debug(f"Registered singleton: {name}")
    
    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a factory function.
        
        The factory will be called each time the dependency is resolved.
        
        Args:
            name: Unique identifier for the dependency
            factory: Factory function that creates instances
            
        Raises:
            ValueError: If name already registered
        """
        with self._lock:
            if name in self._factories:
                raise ValueError(f"Factory '{name}' already registered")
            
            self._factories[name] = factory
            logger.debug(f"Registered factory: {name}")
    
    def register_lazy_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a lazy-initialized singleton.
        
        The factory will be called only once, on first access.
        
        Args:
            name: Unique identifier for the dependency
            factory: Factory function that creates the singleton
        """
        def lazy_factory():
            with self._lock:
                if name not in self._singletons:
                    instance = factory()
                    self._singletons[name] = instance
                    logger.debug(f"Lazy-initialized singleton: {name}")
                return self._singletons[name]
        
        self.register_factory(name, lazy_factory)
    
    def resolve(self, name: str) -> Any:
        """
        Resolve a dependency by name.
        
        Args:
            name: Dependency identifier
            
        Returns:
            The resolved dependency instance
            
        Raises:
            KeyError: If dependency not found
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Check factories
        if name in self._factories:
            return self._factories[name]()
        
        raise KeyError(f"Dependency '{name}' not found in container")
    
    def has(self, name: str) -> bool:
        """
        Check if dependency is registered.
        
        Args:
            name: Dependency identifier
            
        Returns:
            True if dependency exists
        """
        return name in self._singletons or name in self._factories
    
    def remove(self, name: str) -> None:
        """
        Remove a dependency from the container.
        
        Args:
            name: Dependency identifier
        """
        with self._lock:
            if name in self._singletons:
                del self._singletons[name]
                logger.debug(f"Removed singleton: {name}")
            
            if name in self._factories:
                del self._factories[name]
                logger.debug(f"Removed factory: {name}")
    
    def clear(self) -> None:
        """Clear all registered dependencies"""
        with self._lock:
            self._singletons.clear()
            self._factories.clear()
            logger.info("Dependency container cleared")
    
    def get_registered_names(self) -> list[str]:
        """
        Get list of all registered dependency names.
        
        Returns:
            List of dependency identifiers
        """
        return list(set(self._singletons.keys()) | set(self._factories.keys()))
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get container information.
        
        Returns:
            Dictionary with container metadata
        """
        return {
            "singletons": list(self._singletons.keys()),
            "factories": list(self._factories.keys()),
            "total_dependencies": len(self.get_registered_names())
        }


# Global container instance
_global_container: Optional[DependencyContainer] = None
_container_lock = Lock()


def get_container() -> DependencyContainer:
    """
    Get the global dependency container instance.
    
    Returns:
        Global DependencyContainer instance
    """
    global _global_container
    
    if _global_container is None:
        with _container_lock:
            if _global_container is None:
                _global_container = DependencyContainer()
    
    return _global_container


def reset_container() -> None:
    """Reset the global container (useful for testing)"""
    global _global_container
    
    with _container_lock:
        if _global_container is not None:
            _global_container.clear()
        _global_container = None
        logger.info("Global container reset")
