"""
Standalone Demo: Legacy Code Wrapper Infrastructure

This demo imports modules directly to avoid __init__.py issues.
"""

import logging
import sys
from pathlib import Path

# Setup path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

# Direct imports (bypassing __init__.py)
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load our modules
base_service = load_module("base_service", backend_dir / "core" / "base_service.py")
dependency_container = load_module("dependency_container", backend_dir / "core" / "dependency_container.py")
service_health = load_module("service_health", backend_dir / "core" / "service_health.py")
error_wrapper = load_module("error_wrapper", backend_dir / "core" / "error_wrapper.py")
logging_decorator = load_module("logging_decorator", backend_dir / "core" / "logging_decorator.py")

# Extract classes
BaseService = base_service.BaseService
ServiceStatus = base_service.ServiceStatus
HealthCheckResult = base_service.HealthCheckResult
DependencyContainer = dependency_container.DependencyContainer
HealthCheckInterface = service_health.HealthCheckInterface
HealthStatus = service_health.HealthStatus
HealthMonitor = service_health.HealthMonitor
handle_service_errors = error_wrapper.handle_service_errors
validate_input = error_wrapper.validate_input
ValidationError = error_wrapper.ValidationError
log_service_call = logging_decorator.log_service_call

print("="*70)
print("LEGACY CODE WRAPPER INFRASTRUCTURE - STANDALONE DEMO")
print("="*70)

# ============================================================================
# LEGACY CODE (Simulated existing module)
# ============================================================================

class LegacyCalculator:
    """Simulates existing legacy code"""
    def calculate(self, value: int) -> int:
        return value * 2

# ============================================================================
# SERVICE WRAPPER (New code)
# ============================================================================

class CalculatorService(BaseService, HealthCheckInterface):
    """Modern service wrapper"""
    
    def __init__(self):
        super().__init__("CalculatorService")
    
    def initialize(self):
        self._legacy_module = LegacyCalculator()
        self._set_initialized(True)
        print(" Service initialized")
    
    def health_check(self):
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Not initialized"
            )
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service operational"
        )
    
    def check_health(self):
        result = self.health_check()
        return {"message": result.message}
    
    def get_health_status(self):
        result = self.health_check()
        return HealthStatus.HEALTHY if result.is_healthy() else HealthStatus.UNHEALTHY
    
    @log_service_call(service_name="CalculatorService", log_result=True)
    @handle_service_errors(service_name="CalculatorService")
    def calculate(self, value: int) -> int:
        validate_input(
            value > 0,
            "Value must be positive",
            service_name="CalculatorService"
        )
        return self._legacy_module.calculate(value)

# ============================================================================
# DEMO
# ============================================================================

print("\n1. Creating and initializing service...")
service = CalculatorService()
service.initialize()

print("\n2. Checking service health...")
health = service.health_check()
print(f"   Status: {health.status.value}")
print(f"   Message: {health.message}")

print("\n3. Using service with valid input...")
result = service.calculate(5)
print(f"   Result: {result}")

print("\n4. Testing error handling with invalid input...")
try:
    result = service.calculate(-5)
except ValidationError as e:
    print(f"    Error caught: {e.message}")

print("\n5. Testing dependency container...")
container = DependencyContainer()
container.register_singleton("calculator", service)
retrieved = container.resolve("calculator")
print(f"    Service retrieved from container: {retrieved.service_name}")

print("\n6. Testing health monitor...")
monitor = HealthMonitor()
monitor.register_service("calculator", service)
health_check = monitor.check_service("calculator")
print(f"    Health check: {health_check.status.value}")

report = monitor.get_system_report()
print(f"    System status: {report['overall_status']}")

print("\n" + "="*70)
print(" DEMO COMPLETED SUCCESSFULLY")
print("="*70)
print("\nThe legacy code wrapper infrastructure provides:")
print("  • BaseService - Base class for service wrappers")
print("  • DependencyContainer - Dependency injection")
print("  • HealthMonitor - Service health monitoring")
print("  • Error handling - Automatic error wrapping")
print("  • Logging decorators - Automatic method logging")
print("\nKey files created:")
print("  • backend/core/base_service.py")
print("  • backend/core/dependency_container.py")
print("  • backend/core/service_health.py")
print("  • backend/core/error_wrapper.py")
print("  • backend/core/logging_decorator.py")
print("\nDocumentation:")
print("  • backend/docs/LEGACY_WRAPPER_GUIDE.md")
print("  • backend/docs/LEGACY_WRAPPER_QUICK_REFERENCE.md")
print("\nTests:")
print("  • backend/tests/test_legacy_wrapper_infrastructure.py")
print("  • Run: pytest backend/tests/test_legacy_wrapper_infrastructure.py -v")
