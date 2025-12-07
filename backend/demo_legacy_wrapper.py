"""
Demo: Legacy Code Wrapper Infrastructure

This demo shows how to use the legacy code wrapper infrastructure
to wrap existing Python modules with modern service patterns.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add backend to path
backend_path = Path(__file__).parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from core.base_service import BaseService, ServiceStatus, HealthCheckResult
from core.dependency_container import get_container
from core.service_health import HealthCheckInterface, HealthStatus, get_health_monitor
from core.error_wrapper import handle_service_errors, validate_input
from core.logging_decorator import log_service_call, log_performance


# ============================================================================
# LEGACY CODE (Existing modules - unchanged)
# ============================================================================

class LegacyCalculator:
    """
    Legacy calculation module (existing code).
    This represents the old Streamlit code that we want to wrap.
    """
    
    def __init__(self):
        self.calculation_count = 0
    
    def calculate_solar_system_size(self, roof_area: float, efficiency: float) -> float:
        """Calculate solar system size in kWp"""
        self.calculation_count += 1
        return roof_area * efficiency * 0.15
    
    def calculate_annual_production(self, system_size: float, location_factor: float) -> float:
        """Calculate annual energy production in kWh"""
        self.calculation_count += 1
        return system_size * 1200 * location_factor
    
    def calculate_payback_period(self, total_cost: float, annual_savings: float) -> float:
        """Calculate payback period in years"""
        self.calculation_count += 1
        if annual_savings <= 0:
            raise ValueError("Annual savings must be positive")
        return total_cost / annual_savings


class LegacyDatabase:
    """
    Legacy database module (existing code).
    Simulates database operations.
    """
    
    def __init__(self):
        self.data = {}
        self.connected = True
    
    def save_calculation(self, calculation_id: str, data: dict) -> bool:
        """Save calculation to database"""
        if not self.connected:
            raise ConnectionError("Database not connected")
        self.data[calculation_id] = data
        return True
    
    def get_calculation(self, calculation_id: str) -> dict:
        """Retrieve calculation from database"""
        if not self.connected:
            raise ConnectionError("Database not connected")
        return self.data.get(calculation_id, {})


# ============================================================================
# SERVICE WRAPPERS (New code)
# ============================================================================

class CalculatorService(BaseService[LegacyCalculator], HealthCheckInterface):
    """
    Modern service wrapper for legacy calculator.
    
    Provides:
    - Dependency injection
    - Health checks
    - Error handling
    - Logging
    - Input validation
    """
    
    def __init__(self):
        super().__init__("CalculatorService")
        self._request_count = 0
    
    def initialize(self) -> None:
        """Initialize service and load legacy module"""
        try:
            # Load legacy module
            self._legacy_module = LegacyCalculator()
            
            # Register dependencies
            container = get_container()
            if container.has("database"):
                self.register_dependency("database", container.resolve("database"))
            
            self._set_initialized(True)
            self.logger.info("Calculator service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize calculator service: {str(e)}")
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
            test_result = self._legacy_module.calculate_solar_system_size(100, 0.2)
            
            if test_result > 0:
                return HealthCheckResult(
                    status=ServiceStatus.HEALTHY,
                    message="Service operational",
                    details={
                        "calculations_performed": self._legacy_module.calculation_count,
                        "requests_handled": self._request_count
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
    
    @log_service_call(service_name="CalculatorService", log_result=True, log_timing=True)
    @handle_service_errors(
        service_name="CalculatorService",
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
            service_name="CalculatorService",
            field_name="roof_area"
        )
        
        validate_input(
            0 < efficiency <= 1,
            "Efficiency must be between 0 and 1",
            service_name="CalculatorService",
            field_name="efficiency"
        )
        
        # Call legacy module
        self._request_count += 1
        result = self._legacy_module.calculate_solar_system_size(roof_area, efficiency)
        
        return result
    
    @log_service_call(service_name="CalculatorService", log_result=True)
    @handle_service_errors(
        service_name="CalculatorService",
        error_message="Production calculation failed"
    )
    def calculate_production(self, system_size: float, location_factor: float = 1.0) -> float:
        """
        Calculate annual energy production.
        
        Args:
            system_size: System size in kWp
            location_factor: Location adjustment factor (0.8-1.2)
            
        Returns:
            Annual production in kWh
        """
        validate_input(
            system_size > 0,
            "System size must be positive",
            service_name="CalculatorService",
            field_name="system_size"
        )
        
        validate_input(
            0.5 <= location_factor <= 1.5,
            "Location factor must be between 0.5 and 1.5",
            service_name="CalculatorService",
            field_name="location_factor"
        )
        
        self._request_count += 1
        result = self._legacy_module.calculate_annual_production(system_size, location_factor)
        
        return result
    
    @log_performance(threshold_seconds=0.1, service_name="CalculatorService")
    @handle_service_errors(
        service_name="CalculatorService",
        error_message="Payback calculation failed"
    )
    def calculate_payback(self, total_cost: float, annual_savings: float) -> float:
        """Calculate payback period"""
        validate_input(
            total_cost > 0,
            "Total cost must be positive",
            service_name="CalculatorService",
            field_name="total_cost"
        )
        
        validate_input(
            annual_savings > 0,
            "Annual savings must be positive",
            service_name="CalculatorService",
            field_name="annual_savings"
        )
        
        self._request_count += 1
        result = self._legacy_module.calculate_payback_period(total_cost, annual_savings)
        
        return result


class DatabaseService(BaseService[LegacyDatabase], HealthCheckInterface):
    """Service wrapper for legacy database"""
    
    def __init__(self):
        super().__init__("DatabaseService")
    
    def initialize(self) -> None:
        """Initialize database service"""
        self._legacy_module = LegacyDatabase()
        self._set_initialized(True)
        self.logger.info("Database service initialized")
    
    def health_check(self) -> HealthCheckResult:
        """Check database health"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        if self._legacy_module.connected:
            return HealthCheckResult(
                status=ServiceStatus.HEALTHY,
                message="Database connected",
                details={"records": len(self._legacy_module.data)}
            )
        else:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Database not connected"
            )
    
    def check_health(self) -> Dict[str, Any]:
        result = self.health_check()
        return {"message": result.message, "details": result.details}
    
    def get_health_status(self) -> HealthStatus:
        result = self.health_check()
        return HealthStatus.HEALTHY if result.is_healthy() else HealthStatus.UNHEALTHY
    
    @log_service_call(service_name="DatabaseService")
    @handle_service_errors(service_name="DatabaseService", error_message="Save failed")
    def save(self, calculation_id: str, data: dict) -> bool:
        """Save calculation"""
        validate_input(
            calculation_id,
            "Calculation ID is required",
            service_name="DatabaseService",
            field_name="calculation_id"
        )
        
        return self._legacy_module.save_calculation(calculation_id, data)
    
    @log_service_call(service_name="DatabaseService")
    @handle_service_errors(service_name="DatabaseService", error_message="Retrieve failed")
    def get(self, calculation_id: str) -> dict:
        """Retrieve calculation"""
        return self._legacy_module.get_calculation(calculation_id)


# ============================================================================
# DEMO APPLICATION
# ============================================================================

def demo_basic_usage():
    """Demo: Basic service usage"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Service Usage")
    print("="*70)
    
    # Create and initialize service
    calc_service = CalculatorService()
    calc_service.initialize()
    
    print(f"\n Service initialized: {calc_service.service_name}")
    print(f"  Status: {'Initialized' if calc_service.is_initialized else 'Not initialized'}")
    
    # Use service
    print("\n→ Calculating system size...")
    system_size = calc_service.calculate_system_size(roof_area=50.0, efficiency=0.2)
    print(f"  System size: {system_size:.2f} kWp")
    
    print("\n→ Calculating annual production...")
    production = calc_service.calculate_production(system_size=system_size, location_factor=1.1)
    print(f"  Annual production: {production:.0f} kWh")
    
    print("\n→ Calculating payback period...")
    payback = calc_service.calculate_payback(total_cost=15000, annual_savings=1500)
    print(f"  Payback period: {payback:.1f} years")


def demo_dependency_injection():
    """Demo: Dependency injection"""
    print("\n" + "="*70)
    print("DEMO 2: Dependency Injection")
    print("="*70)
    
    # Setup container
    container = get_container()
    
    # Register database service
    db_service = DatabaseService()
    db_service.initialize()
    container.register_singleton("database", db_service)
    
    print("\n Registered database service in container")
    
    # Create calculator service with dependency
    calc_service = CalculatorService()
    calc_service.initialize()
    
    print(f" Calculator service has database dependency: {calc_service.has_dependency('database')}")
    
    # Use services together
    system_size = calc_service.calculate_system_size(50.0, 0.2)
    
    # Save to database
    db = calc_service.get_dependency("database")
    db.save("calc_001", {"system_size": system_size})
    
    print(f"\n→ Saved calculation to database")
    
    # Retrieve from database
    saved_data = db.get("calc_001")
    print(f"→ Retrieved from database: {saved_data}")


def demo_health_monitoring():
    """Demo: Health monitoring"""
    print("\n" + "="*70)
    print("DEMO 3: Health Monitoring")
    print("="*70)
    
    # Create services
    calc_service = CalculatorService()
    calc_service.initialize()
    
    db_service = DatabaseService()
    db_service.initialize()
    
    # Register with health monitor
    monitor = get_health_monitor()
    monitor.register_service("calculator", calc_service)
    monitor.register_service("database", db_service)
    
    print("\n Registered services with health monitor")
    
    # Check individual service
    print("\n→ Checking calculator service health...")
    health = monitor.check_service("calculator")
    print(f"  Status: {health.status.value}")
    print(f"  Message: {health.message}")
    print(f"  Details: {health.details}")
    
    # Check all services
    print("\n→ Checking all services...")
    all_health = monitor.check_all_services()
    for name, health in all_health.items():
        print(f"  {name}: {health.status.value}")
    
    # Get system report
    print("\n→ System health report:")
    report = monitor.get_system_report()
    print(f"  Overall status: {report['overall_status']}")
    print(f"  Total services: {report['summary']['total_services']}")
    print(f"  Healthy: {report['summary']['healthy']}")
    print(f"  Degraded: {report['summary']['degraded']}")
    print(f"  Unhealthy: {report['summary']['unhealthy']}")


def demo_error_handling():
    """Demo: Error handling"""
    print("\n" + "="*70)
    print("DEMO 4: Error Handling")
    print("="*70)
    
    calc_service = CalculatorService()
    calc_service.initialize()
    
    # Valid input
    print("\n→ Testing with valid input...")
    try:
        result = calc_service.calculate_system_size(50.0, 0.2)
        print(f"   Success: {result:.2f} kWp")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Invalid input (negative roof area)
    print("\n→ Testing with invalid input (negative roof area)...")
    try:
        result = calc_service.calculate_system_size(-50.0, 0.2)
        print(f"   Success: {result:.2f} kWp")
    except Exception as e:
        print(f"   Error caught: {type(e).__name__}: {e}")
    
    # Invalid input (efficiency out of range)
    print("\n→ Testing with invalid input (efficiency > 1)...")
    try:
        result = calc_service.calculate_system_size(50.0, 1.5)
        print(f"   Success: {result:.2f} kWp")
    except Exception as e:
        print(f"   Error caught: {type(e).__name__}: {e}")
    
    # Invalid calculation (zero savings)
    print("\n→ Testing with invalid calculation (zero savings)...")
    try:
        result = calc_service.calculate_payback(15000, 0)
        print(f"   Success: {result:.1f} years")
    except Exception as e:
        print(f"   Error caught: {type(e).__name__}: {e}")


def demo_complete_workflow():
    """Demo: Complete workflow"""
    print("\n" + "="*70)
    print("DEMO 5: Complete Workflow")
    print("="*70)
    
    # Setup
    container = get_container()
    monitor = get_health_monitor()
    
    # Initialize services
    print("\n→ Initializing services...")
    db_service = DatabaseService()
    db_service.initialize()
    container.register_singleton("database", db_service)
    
    calc_service = CalculatorService()
    calc_service.initialize()
    
    # Register for monitoring
    monitor.register_service("calculator", calc_service)
    monitor.register_service("database", db_service)
    
    print("   Services initialized and registered")
    
    # Perform calculations
    print("\n→ Performing solar calculations...")
    system_size = calc_service.calculate_system_size(roof_area=75.0, efficiency=0.22)
    production = calc_service.calculate_production(system_size=system_size, location_factor=1.05)
    payback = calc_service.calculate_payback(total_cost=20000, annual_savings=2000)
    
    print(f"  System size: {system_size:.2f} kWp")
    print(f"  Annual production: {production:.0f} kWh")
    print(f"  Payback period: {payback:.1f} years")
    
    # Save results
    print("\n→ Saving results to database...")
    calculation_data = {
        "system_size": system_size,
        "production": production,
        "payback": payback
    }
    db_service.save("calc_final", calculation_data)
    print("   Results saved")
    
    # Check health
    print("\n→ Final health check...")
    report = monitor.get_system_report()
    print(f"  Overall system status: {report['overall_status']}")
    print(f"  All services healthy: {report['summary']['healthy'] == report['summary']['total_services']}")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("LEGACY CODE WRAPPER INFRASTRUCTURE - DEMO")
    print("="*70)
    print("\nThis demo shows how to wrap legacy Python code with modern")
    print("service patterns including dependency injection, health checks,")
    print("error handling, and logging.")
    
    try:
        demo_basic_usage()
        demo_dependency_injection()
        demo_health_monitoring()
        demo_error_handling()
        demo_complete_workflow()
        
        print("\n" + "="*70)
        print(" ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nNext steps:")
        print("  1. Review backend/docs/LEGACY_WRAPPER_GUIDE.md")
        print("  2. Check backend/docs/LEGACY_WRAPPER_QUICK_REFERENCE.md")
        print("  3. Run tests: pytest backend/tests/test_legacy_wrapper_infrastructure.py")
        print("  4. Start wrapping your legacy modules!")
        
    except Exception as e:
        print(f"\n Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
