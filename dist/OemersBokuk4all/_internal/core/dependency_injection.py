"""
Dependency Injection Container System

Provides service registration, resolution, and lifetime management.
Supports constructor injection, property injection, and auto-wiring.

Author: ARSCHIBALD Development Team
Date: 2025-12-14
"""

import threading
import inspect
from enum import Enum
from typing import Any, Optional, Callable, Type, TypeVar, Dict, List, Set
from dataclasses import dataclass, field
from datetime import datetime

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


T = TypeVar('T')


class ServiceLifetime(Enum):
    """Service lifetime modes"""
    SINGLETON = "singleton"  # One instance for entire app lifetime
    SCOPED = "scoped"  # One instance per scope/request
    TRANSIENT = "transient"  # New instance every time


@dataclass
class ServiceDescriptor:
    """Describes a registered service"""
    def __getstate__(self):
        return {k: v for k, v in self.__dict__.items() if k not in ['_implementation', '_factory']}
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self._implementation = None
        self._factory = None
    
    service_type: Type
    lifetime: ServiceLifetime
    _implementation: Optional[Type] = None
    _factory: Optional[Callable] = None
    _instance: Any = None
    dependencies: Dict[str, Type] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    resolution_count: int = 0
    
    @property
    def implementation(self) -> Optional[Type]:
        return self._implementation
    
    @property
    def factory(self) -> Optional[Callable]:
        return self._factory
    
    @property
    def instance(self) -> Any:
        return self._instance
    
    @instance.setter
    def instance(self, value: Any):
        self._instance = value


class DIContainer:
    """Dependency Injection Container"""
    
    def __getstate__(self):
        return {
            '_services': {k: v for k, v in self._services.items()},
            '_scoped_instances': {},
            '_resolution_count': self._resolution_count
        }
    
    def __setstate__(self, state):
        self.__init__()
        self._services = state.get('_services', {})
        self._resolution_count = state.get('_resolution_count', 0)
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}
        self._lock = threading.RLock()
        self._resolution_count = 0
        self._resolution_stack: List[Type] = []
    
    def register(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        dependencies: Optional[Dict[str, Type]] = None
    ) -> 'DIContainer':
        """
        Register a service
        
        Args:
            service_type: Service type (interface/abstract class)
            implementation: Implementation type (None = use service_type)
            factory: Factory function to create instances
            lifetime: Service lifetime (SINGLETON, SCOPED, TRANSIENT)
            dependencies: Manual dependency mapping
        
        Returns:
            Self for chaining
        """
        if implementation is None and factory is None:
            implementation = service_type
        
        descriptor = ServiceDescriptor(
            service_type=service_type,
            lifetime=lifetime,
            _implementation=implementation,
            _factory=factory,
            dependencies=dependencies or {}
        )
        
        with self._lock:
            self._services[service_type] = descriptor
        
        logger.info(
            "service_registered",
            service=service_type.__name__,
            lifetime=lifetime.value
        )
        
        return self
    
    def register_singleton(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        instance: Optional[T] = None
    ) -> 'DIContainer':
        """Register singleton service"""
        if instance is not None:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                lifetime=ServiceLifetime.SINGLETON,
                _instance=instance
            )
            with self._lock:
                self._services[service_type] = descriptor
        else:
            self.register(
                service_type=service_type,
                implementation=implementation,
                lifetime=ServiceLifetime.SINGLETON
            )
        return self
    
    def register_scoped(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None
    ) -> 'DIContainer':
        """Register scoped service"""
        return self.register(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SCOPED
        )
    
    def register_transient(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None
    ) -> 'DIContainer':
        """Register transient service"""
        return self.register(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT
        )
    
    def resolve(
        self,
        service_type: Type[T],
        scope_id: Optional[str] = None
    ) -> T:
        """
        Resolve a service instance
        
        Args:
            service_type: Service type to resolve
            scope_id: Scope identifier for SCOPED services
        
        Returns:
            Service instance
        
        Raises:
            ValueError: If service not registered or circular dependency detected
        """
        with self._lock:
            if service_type not in self._services:
                raise ValueError(f"Service {service_type.__name__} not registered")
            
            # Circular dependency detection
            if service_type in self._resolution_stack:
                cycle = ' -> '.join(t.__name__ for t in self._resolution_stack)
                raise ValueError(
                    f"Circular dependency detected: {cycle} -> {service_type.__name__}"
                )
            
            self._resolution_stack.append(service_type)
            
            try:
                descriptor = self._services[service_type]
                descriptor.resolution_count += 1
                self._resolution_count += 1
                
                # SINGLETON: Return cached instance
                if descriptor.lifetime == ServiceLifetime.SINGLETON:
                    if descriptor.instance is None:
                        descriptor.instance = self._create_instance(descriptor)
                    return descriptor.instance
                
                # SCOPED: Return scoped instance
                elif descriptor.lifetime == ServiceLifetime.SCOPED:
                    if scope_id is None:
                        scope_id = "default"
                    
                    if scope_id not in self._scoped_instances:
                        self._scoped_instances[scope_id] = {}
                    
                    if service_type not in self._scoped_instances[scope_id]:
                        self._scoped_instances[scope_id][service_type] = (
                            self._create_instance(descriptor)
                        )
                    
                    return self._scoped_instances[scope_id][service_type]
                
                # TRANSIENT: Always create new
                else:
                    return self._create_instance(descriptor)
            
            finally:
                self._resolution_stack.pop()
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create service instance"""
        # Use factory if provided
        if descriptor.factory is not None:
            return descriptor.factory()
        
        # Use implementation
        impl = descriptor.implementation
        if impl is None:
            raise ValueError(f"No implementation for {descriptor.service_type.__name__}")
        
        # Auto-wire constructor dependencies
        return self._auto_wire(impl)
    
    def _auto_wire(self, impl_type: Type) -> Any:
        """Auto-wire constructor dependencies"""
        sig = inspect.signature(impl_type.__init__)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Get type annotation
            if param.annotation == inspect.Parameter.empty:
                continue
            
            param_type = param.annotation
            
            # Try to resolve dependency
            try:
                params[param_name] = self.resolve(param_type)
            except ValueError:
                # If dependency not registered and has default, use default
                if param.default != inspect.Parameter.empty:
                    params[param_name] = param.default
                else:
                    raise ValueError(
                        f"Cannot resolve dependency {param_name}: {param_type.__name__} "
                        f"for {impl_type.__name__}"
                    )
        
        return impl_type(**params)
    
    def clear_scope(self, scope_id: str):
        """Clear scoped instances for given scope"""
        with self._lock:
            if scope_id in self._scoped_instances:
                del self._scoped_instances[scope_id]
                logger.info("scope_cleared", scope_id=scope_id)
    
    def get_registered_services(self) -> List[str]:
        """Get list of registered service names"""
        with self._lock:
            return [s.__name__ for s in self._services.keys()]
    
    def get_stats(self) -> dict[str, Any]:
        """Get container statistics"""
        with self._lock:
            total_services = len(self._services)
            singleton_count = sum(
                1 for d in self._services.values()
                if d.lifetime == ServiceLifetime.SINGLETON
            )
            scoped_count = sum(
                1 for d in self._services.values()
                if d.lifetime == ServiceLifetime.SCOPED
            )
            transient_count = sum(
                1 for d in self._services.values()
                if d.lifetime == ServiceLifetime.TRANSIENT
            )
            
            # Resolution stats
            top_resolved = sorted(
                self._services.values(),
                key=lambda d: d.resolution_count,
                reverse=True
            )[:5]
            
            return {
                'total_services': total_services,
                'singleton_count': singleton_count,
                'scoped_count': scoped_count,
                'transient_count': transient_count,
                'total_resolutions': self._resolution_count,
                'active_scopes': len(self._scoped_instances),
                'top_resolved': [
                    {
                        'service': d.service_type.__name__,
                        'count': d.resolution_count,
                        'lifetime': d.lifetime.value
                    }
                    for d in top_resolved
                ],
                'status': 'ok'
            }
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if service is registered"""
        return service_type in self._services


# Decorators

def injectable(cls: Type[T]) -> Type[T]:
    """Mark class as injectable"""
    cls.__injectable__ = True
    return cls


def singleton(cls: Type[T]) -> Type[T]:
    """Mark class as singleton and auto-register"""
    cls.__injectable__ = True
    cls.__lifetime__ = ServiceLifetime.SINGLETON
    
    # Auto-register on module import
    container = get_di_container()
    container.register_singleton(cls)
    
    return cls


def scoped(cls: Type[T]) -> Type[T]:
    """Mark class as scoped and auto-register"""
    cls.__injectable__ = True
    cls.__lifetime__ = ServiceLifetime.SCOPED
    
    container = get_di_container()
    container.register_scoped(cls)
    
    return cls


def transient(cls: Type[T]) -> Type[T]:
    """Mark class as transient and auto-register"""
    cls.__injectable__ = True
    cls.__lifetime__ = ServiceLifetime.TRANSIENT
    
    container = get_di_container()
    container.register_transient(cls)
    
    return cls


# Global instance
_di_container: Optional[DIContainer] = None
_container_lock = threading.Lock()


def get_di_container() -> DIContainer:
    """Get global DI container instance"""
    global _di_container
    
    if _di_container is None:
        with _container_lock:
            if _di_container is None:
                _di_container = DIContainer()
    
    return _di_container


def resolve(service_type: Type[T], scope_id: Optional[str] = None) -> T:
    """Resolve service from global container"""
    container = get_di_container()
    return container.resolve(service_type, scope_id)
