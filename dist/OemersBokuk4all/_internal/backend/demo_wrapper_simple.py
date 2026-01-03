"""
Simple Demo: Legacy Code Wrapper Infrastructure

This demo shows the core functionality without complex imports.
Run from the backend directory: python demo_wrapper_simple.py
"""

import logging
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

# Import only what we need (avoiding __init__.py)
from core.base_service import BaseService, ServiceStatus, HealthCheckResult
from core.dependency_container import DependencyContainer
from core.service_health import HealthCheckInterface, HealthStatus, HealthMonitor
from core.error_wrapper import handle_service_errors, validate_input, ValidationError
from core.logging_decorator import log_service_call


print("="*70)
print("LEGACY CODE WRAPPER INFRASTRUCTURE - SIMPLE DEMO")
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
print("\nNext steps:")
print("  1. Review docs/LEGACY_WRAPPER_GUIDE.md")
print("  2. Run tests: pytest tests/test_legacy_wrapper_infrastructure.py")
print("  3. Start wrapping your legacy modules!")
