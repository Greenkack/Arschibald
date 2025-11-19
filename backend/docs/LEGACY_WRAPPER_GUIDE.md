# Legacy Code Wrapper Infrastructure Guide

## Overview

The Legacy Code Wrapper Infrastructure provides a comprehensive framework for wrapping existing Python code (legacy modules) into modern service classes with:

- **Dependency Injection**: Manage service dependencies cleanly
- **Health Checks**: Monitor service health and availability
- **Error Handling**: Consistent error handling and reporting
- **Logging**: Automatic method logging with timing and context
- **Type Safety**: Generic type support for wrapped modules

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Service Layer (New)                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │  Service A │  │  Service B │  │  Service C │       │
│  │  (Wrapper) │  │  (Wrapper) │  │  (Wrapper) │       │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│        │                │                │               │
│        └────────────────┴────────────────┘               │
│                         │                                 │
│              ┌──────────▼──────────┐                     │
│              │ Dependency Container │                     │
│              │   Health Monitor     │                     │
│              │   Error Handler      │                     │
│              └──────────┬──────────┘                     │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│              Legacy Code Layer (Existing)                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Module A   │  │ Module B   │  │ Module C   │       │
│  │ (Legacy)   │  │ (Legacy)   │  │ (Legacy)   │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. BaseService

Base class for all service wrappers.

```python
from backend.core.base_service import BaseService, ServiceStatus, HealthCheckResult

class MyService(BaseService[MyLegacyModule]):
    """Wrapper for legacy module"""
    
    def initialize(self) -> None:
        """Initialize service and load legacy module"""
        # Import and initialize legacy module
        from legacy import my_module
        self._legacy_module = my_module
        self._set_initialized(True)
    
    def health_check(self) -> HealthCheckResult:
        """Check service health"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        # Test legacy module
        try:
            self._legacy_module.test_connection()
            return HealthCheckResult(
                status=ServiceStatus.HEALTHY,
                message="Service operational"
            )
        except Exception as e:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}"
            )
```

### 2. Dependency Container

Manage service dependencies with dependency injection.

```python
from backend.core.dependency_container import DependencyContainer, get_container

# Create container
container = DependencyContainer()

# Register singleton
database = DatabaseConnection()
container.register_singleton("database", database)

# Register factory (creates new instance each time)
def create_calculator():
    return Calculator()

container.register_factory("calculator", create_calculator)

# Register lazy singleton (created on first access)
def create_cache():
    return CacheManager()

container.register_lazy_singleton("cache", create_cache)

# Resolve dependencies
db = container.resolve("database")
calc = container.resolve("calculator")

# Use global container
global_container = get_container()
```

### 3. Health Check System

Monitor service health and availability.

```python
from backend.core.service_health import (
    HealthCheckInterface, HealthStatus, HealthMonitor, get_health_monitor
)

class MyService(BaseService, HealthCheckInterface):
    """Service with health check interface"""
    
    def check_health(self) -> Dict[str, Any]:
        """HealthCheckInterface implementation"""
        return {
            "message": "Service is healthy",
            "details": {
                "uptime": self.get_uptime(),
                "requests_processed": self.request_count
            }
        }
    
    def get_health_status(self) -> HealthStatus:
        """Get current health status"""
        if self.is_operational():
            return HealthStatus.HEALTHY
        elif self.is_degraded():
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY

# Use health monitor
monitor = get_health_monitor()
monitor.register_service("my_service", my_service)

# Check specific service
health = monitor.check_service("my_service")
print(f"Status: {health.status.value}")

# Check all services
all_health = monitor.check_all_services()

# Get system report
report = monitor.get_system_report()
print(f"Overall status: {report['overall_status']}")
```

### 4. Error Handling

Consistent error handling with automatic wrapping and logging.

```python
from backend.core.error_wrapper import (
    handle_service_errors, safe_execute, ErrorContext, validate_input
)

class MyService(BaseService):
    
    @handle_service_errors(
        service_name="MyService",
        error_message="Calculation failed"
    )
    def calculate(self, value: int) -> int:
        """Method with automatic error handling"""
        validate_input(
            value > 0,
            "Value must be positive",
            service_name="MyService",
            field_name="value"
        )
        
        return self._legacy_module.calculate(value)
    
    def safe_operation(self):
        """Use safe_execute for optional operations"""
        result = safe_execute(
            self._legacy_module.optional_feature,
            service_name="MyService",
            operation="optional_feature",
            default_return=None
        )
        return result
    
    def with_context(self):
        """Use ErrorContext for block-level error handling"""
        with ErrorContext(service_name="MyService", operation="complex_op"):
            # Code that might raise errors
            self._legacy_module.complex_operation()
```

### 5. Logging Decorators

Automatic logging with timing, arguments, and results.

```python
from backend.core.logging_decorator import (
    log_service_call, log_performance, log_exceptions, MethodLogger
)

class MyService(BaseService):
    
    @log_service_call(
        service_name="MyService",
        log_args=True,
        log_result=True,
        log_timing=True
    )
    def calculate(self, value: int) -> int:
        """Automatically logged method"""
        return self._legacy_module.calculate(value)
    
    @log_performance(
        threshold_seconds=1.0,
        service_name="MyService"
    )
    def slow_operation(self):
        """Log if execution exceeds threshold"""
        return self._legacy_module.slow_operation()
    
    @log_exceptions(service_name="MyService")
    def risky_operation(self):
        """Log exceptions with full context"""
        return self._legacy_module.risky_operation()
    
    def with_context_logging(self):
        """Use MethodLogger for manual logging"""
        with MethodLogger("MyService", "complex_method", log_args=True):
            # Method implementation
            pass
```

## Complete Example

Here's a complete example wrapping a legacy solar calculator module:

```python
from typing import Dict, Any
from backend.core.base_service import BaseService, ServiceStatus, HealthCheckResult
from backend.core.service_health import HealthCheckInterface, HealthStatus
from backend.core.error_wrapper import handle_service_errors, validate_input
from backend.core.logging_decorator import log_service_call
from backend.core.dependency_container import get_container

# Legacy module (existing code)
class LegacySolarCalculator:
    def calculate_system_size(self, roof_area: float, efficiency: float) -> float:
        return roof_area * efficiency * 0.15
    
    def calculate_production(self, system_size: float, location: str) -> float:
        # Complex legacy calculation
        return system_size * 1200  # Simplified

# Service wrapper (new code)
class SolarCalculatorService(BaseService[LegacySolarCalculator], HealthCheckInterface):
    """
    Service wrapper for legacy solar calculator.
    
    Provides modern interface with error handling, logging, and health checks.
    """
    
    def __init__(self):
        super().__init__("SolarCalculatorService")
        self._calculation_count = 0
    
    def initialize(self) -> None:
        """Initialize service and load legacy module"""
        try:
            # Load legacy module
            self._legacy_module = LegacySolarCalculator()
            
            # Register dependencies
            container = get_container()
            if container.has("database"):
                self.register_dependency("database", container.resolve("database"))
            
            self._set_initialized(True)
            self.logger.info("Solar calculator service initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize: {str(e)}")
            raise
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        try:
            # Test basic functionality
            test_result = self._legacy_module.calculate_system_size(100, 0.2)
            
            if test_result > 0:
                return HealthCheckResult(
                    status=ServiceStatus.HEALTHY,
                    message="Service operational",
                    details={
                        "calculations_performed": self._calculation_count
                    }
                )
            else:
                return HealthCheckResult(
                    status=ServiceStatus.DEGRADED,
                    message="Service returning unexpected results"
                )
                
        except Exception as e:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}"
            )
    
    def check_health(self) -> Dict[str, Any]:
        """HealthCheckInterface implementation"""
        result = self.health_check()
        return {
            "message": result.message,
            "details": result.details
        }
    
    def get_health_status(self) -> HealthStatus:
        """Get health status"""
        result = self.health_check()
        if result.status == ServiceStatus.HEALTHY:
            return HealthStatus.HEALTHY
        elif result.status == ServiceStatus.DEGRADED:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY
    
    @log_service_call(service_name="SolarCalculatorService", log_result=True)
    @handle_service_errors(
        service_name="SolarCalculatorService",
        error_message="System size calculation failed"
    )
    def calculate_system_size(self, roof_area: float, efficiency: float) -> float:
        """
        Calculate solar system size.
        
        Args:
            roof_area: Roof area in square meters
            efficiency: Module efficiency (0-1)
            
        Returns:
            System size in kWp
        """
        # Validate inputs
        validate_input(
            roof_area > 0,
            "Roof area must be positive",
            service_name="SolarCalculatorService",
            field_name="roof_area"
        )
        
        validate_input(
            0 < efficiency <= 1,
            "Efficiency must be between 0 and 1",
            service_name="SolarCalculatorService",
            field_name="efficiency"
        )
        
        # Call legacy module
        result = self._legacy_module.calculate_system_size(roof_area, efficiency)
        self._calculation_count += 1
        
        return result
    
    @log_service_call(service_name="SolarCalculatorService", log_result=True)
    @handle_service_errors(
        service_name="SolarCalculatorService",
        error_message="Production calculation failed"
    )
    def calculate_production(self, system_size: float, location: str) -> float:
        """
        Calculate annual energy production.
        
        Args:
            system_size: System size in kWp
            location: Location identifier
            
        Returns:
            Annual production in kWh
        """
        validate_input(
            system_size > 0,
            "System size must be positive",
            service_name="SolarCalculatorService",
            field_name="system_size"
        )
        
        result = self._legacy_module.calculate_production(system_size, location)
        self._calculation_count += 1
        
        return result

# Usage
def main():
    # Create and initialize service
    service = SolarCalculatorService()
    service.initialize()
    
    # Register with health monitor
    from backend.core.service_health import get_health_monitor
    monitor = get_health_monitor()
    monitor.register_service("solar_calculator", service)
    
    # Use service
    system_size = service.calculate_system_size(roof_area=50.0, efficiency=0.2)
    production = service.calculate_production(system_size=system_size, location="Berlin")
    
    print(f"System size: {system_size} kWp")
    print(f"Annual production: {production} kWh")
    
    # Check health
    health = monitor.check_service("solar_calculator")
    print(f"Service health: {health.status.value}")

if __name__ == "__main__":
    main()
```

## Best Practices

### 1. Service Initialization

- Always call `initialize()` after creating a service
- Handle initialization errors gracefully
- Register all dependencies during initialization
- Use `_set_initialized(True)` to mark successful initialization

### 2. Health Checks

- Implement meaningful health checks that test actual functionality
- Include relevant details in health check results
- Use appropriate status levels (HEALTHY, DEGRADED, UNHEALTHY)
- Register services with the health monitor for centralized monitoring

### 3. Error Handling

- Use `@handle_service_errors` decorator for automatic error wrapping
- Validate inputs with `validate_input()` before processing
- Use `safe_execute()` for optional operations that shouldn't fail the entire request
- Provide meaningful error messages and error codes

### 4. Logging

- Use `@log_service_call` for important public methods
- Use `@log_performance` for operations that might be slow
- Use `@log_exceptions` for risky operations
- Keep log messages concise and informative

### 5. Dependency Management

- Register all dependencies in the container
- Use lazy singletons for expensive resources
- Use factories for stateful objects that need fresh instances
- Document required dependencies in service docstrings

## Testing

The infrastructure includes comprehensive tests. Run them with:

```bash
cd backend
pytest tests/test_legacy_wrapper_infrastructure.py -v
```

## Migration Checklist

When wrapping a legacy module:

- [ ] Create service class inheriting from `BaseService`
- [ ] Implement `initialize()` method
- [ ] Implement `health_check()` method
- [ ] Implement `HealthCheckInterface` if using health monitoring
- [ ] Add error handling decorators to public methods
- [ ] Add logging decorators to important methods
- [ ] Validate all inputs
- [ ] Register dependencies
- [ ] Write tests for the service wrapper
- [ ] Document the service API
- [ ] Register with health monitor
- [ ] Add to dependency container

## Next Steps

1. Review the [API Documentation](./API_DOCUMENTATION.md)
2. See [Service Examples](./SERVICE_EXAMPLES.md) for more patterns
3. Check [Testing Guide](./TESTING_GUIDE.md) for testing strategies
4. Read [Performance Guide](./PERFORMANCE_GUIDE.md) for optimization tips
