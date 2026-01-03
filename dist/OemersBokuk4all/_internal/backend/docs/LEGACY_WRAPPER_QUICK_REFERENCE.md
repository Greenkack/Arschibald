# Legacy Wrapper Infrastructure - Quick Reference

## Quick Start

```python
from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors, validate_input
from backend.core.logging_decorator import log_service_call

class MyService(BaseService[MyLegacyModule]):
    def initialize(self):
        self._legacy_module = MyLegacyModule()
        self._set_initialized(True)
    
    def health_check(self):
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="OK"
        )
    
    @log_service_call(service_name="MyService")
    @handle_service_errors(service_name="MyService")
    def my_method(self, value: int) -> int:
        validate_input(value > 0, "Value must be positive")
        return self._legacy_module.process(value)
```

## Core Classes

### BaseService

```python
class MyService(BaseService[LegacyType]):
    def initialize(self) -> None:
        # Load legacy module
        self._legacy_module = LegacyModule()
        self._set_initialized(True)
    
    def health_check(self) -> HealthCheckResult:
        # Check service health
        return HealthCheckResult(status=ServiceStatus.HEALTHY)
```

**Key Methods:**
- `initialize()` - Initialize service
- `health_check()` - Check service health
- `register_dependency(name, dep)` - Register dependency
- `get_dependency(name)` - Get dependency
- `is_initialized` - Check if initialized
- `legacy_module` - Access wrapped module

### DependencyContainer

```python
from backend.core.dependency_container import get_container

container = get_container()

# Register singleton
container.register_singleton("db", database)

# Register factory
container.register_factory("calc", lambda: Calculator())

# Register lazy singleton
container.register_lazy_singleton("cache", create_cache)

# Resolve
db = container.resolve("db")
```

### Health Monitor

```python
from backend.core.service_health import get_health_monitor

monitor = get_health_monitor()

# Register service
monitor.register_service("my_service", service)

# Check health
health = monitor.check_service("my_service")

# Check all
all_health = monitor.check_all_services()

# Get report
report = monitor.get_system_report()
```

## Decorators

### @handle_service_errors

```python
@handle_service_errors(
    service_name="MyService",
    error_message="Operation failed",
    reraise=True
)
def my_method(self):
    # Automatically wraps exceptions
    pass
```

### @log_service_call

```python
@log_service_call(
    service_name="MyService",
    log_args=True,
    log_result=True,
    log_timing=True
)
def my_method(self, value):
    # Automatically logged
    return value * 2
```

### @log_performance

```python
@log_performance(
    threshold_seconds=1.0,
    service_name="MyService"
)
def slow_method(self):
    # Logs if exceeds threshold
    pass
```

### @log_exceptions

```python
@log_exceptions(
    service_name="MyService",
    reraise=True
)
def risky_method(self):
    # Logs exceptions
    pass
```

## Error Handling

### Validate Input

```python
from backend.core.error_wrapper import validate_input

validate_input(
    value > 0,
    "Value must be positive",
    service_name="MyService",
    field_name="value"
)
```

### Safe Execute

```python
from backend.core.error_wrapper import safe_execute

result = safe_execute(
    risky_function,
    arg1, arg2,
    service_name="MyService",
    operation="risky_op",
    default_return=None
)
```

### Error Context

```python
from backend.core.error_wrapper import ErrorContext

with ErrorContext(service_name="MyService", operation="complex"):
    # Code that might fail
    pass
```

## Exception Types

```python
from backend.core.error_wrapper import (
    ServiceError,           # Base exception
    InitializationError,    # Initialization failed
    DependencyError,        # Dependency issue
    ValidationError,        # Input validation failed
    ExecutionError          # Execution failed
)
```

## Health Check

### HealthCheckResult

```python
from backend.core.base_service import HealthCheckResult, ServiceStatus

result = HealthCheckResult(
    status=ServiceStatus.HEALTHY,  # or DEGRADED, UNHEALTHY
    message="Service is operational",
    details={"uptime": 100}
)

if result.is_healthy():
    print("All good!")
```

### HealthCheckInterface

```python
from backend.core.service_health import HealthCheckInterface, HealthStatus

class MyService(BaseService, HealthCheckInterface):
    def check_health(self) -> Dict[str, Any]:
        return {"message": "OK", "details": {}}
    
    def get_health_status(self) -> HealthStatus:
        return HealthStatus.HEALTHY
```

## Logging

### MethodLogger Context

```python
from backend.core.logging_decorator import MethodLogger

with MethodLogger("MyService", "my_method", log_args=True):
    # Method implementation
    result = do_something()
```

## Common Patterns

### Service with Dependencies

```python
class MyService(BaseService):
    def initialize(self):
        # Get dependencies
        container = get_container()
        db = container.resolve("database")
        self.register_dependency("database", db)
        
        # Initialize legacy module
        self._legacy_module = LegacyModule(db)
        self._set_initialized(True)
```

### Service with Health Monitoring

```python
class MyService(BaseService, HealthCheckInterface):
    def initialize(self):
        self._legacy_module = LegacyModule()
        self._set_initialized(True)
        
        # Register with monitor
        monitor = get_health_monitor()
        monitor.register_service("my_service", self)
    
    def check_health(self):
        return {"message": "OK"}
    
    def get_health_status(self):
        return HealthStatus.HEALTHY
```

### Complete Service Method

```python
@log_service_call(service_name="MyService", log_result=True)
@handle_service_errors(service_name="MyService", error_message="Failed")
def process_data(self, data: dict) -> dict:
    # Validate
    validate_input(
        "value" in data,
        "Missing required field: value",
        service_name="MyService",
        field_name="value"
    )
    
    # Process with legacy module
    result = self._legacy_module.process(data)
    
    return result
```

## Testing

```python
import pytest
from backend.core.base_service import BaseService

class TestMyService:
    def test_initialization(self):
        service = MyService("test")
        service.initialize()
        assert service.is_initialized
    
    def test_health_check(self):
        service = MyService("test")
        service.initialize()
        health = service.health_check()
        assert health.is_healthy()
    
    def test_method_with_error(self):
        service = MyService("test")
        service.initialize()
        
        with pytest.raises(ValidationError):
            service.process_data({"invalid": "data"})
```

## Cheat Sheet

| Task | Code |
|------|------|
| Create service | `class MyService(BaseService[LegacyType])` |
| Initialize | `self._set_initialized(True)` |
| Set legacy module | `self._legacy_module = module` |
| Register dependency | `self.register_dependency("name", dep)` |
| Get dependency | `self.get_dependency("name")` |
| Health check | `return HealthCheckResult(status=ServiceStatus.HEALTHY)` |
| Validate input | `validate_input(condition, "message")` |
| Handle errors | `@handle_service_errors(service_name="MyService")` |
| Log calls | `@log_service_call(service_name="MyService")` |
| Log performance | `@log_performance(threshold_seconds=1.0)` |
| Safe execute | `safe_execute(func, default_return=None)` |
| Error context | `with ErrorContext(service_name="MyService"):` |
| Get container | `container = get_container()` |
| Register singleton | `container.register_singleton("name", instance)` |
| Resolve dependency | `dep = container.resolve("name")` |
| Get health monitor | `monitor = get_health_monitor()` |
| Register for monitoring | `monitor.register_service("name", service)` |
| Check service health | `health = monitor.check_service("name")` |
| System report | `report = monitor.get_system_report()` |

## File Structure

```
backend/
├── core/
│   ├── base_service.py           # BaseService class
│   ├── dependency_container.py   # DI container
│   ├── service_health.py         # Health check system
│   ├── error_wrapper.py          # Error handling
│   └── logging_decorator.py      # Logging decorators
├── tests/
│   └── test_legacy_wrapper_infrastructure.py
└── docs/
    ├── LEGACY_WRAPPER_GUIDE.md
    └── LEGACY_WRAPPER_QUICK_REFERENCE.md
```

## Next Steps

1. Read the [Full Guide](./LEGACY_WRAPPER_GUIDE.md)
2. Check [Examples](./SERVICE_EXAMPLES.md)
3. Review [Tests](../tests/test_legacy_wrapper_infrastructure.py)
