"""
Tests for Legacy Code Wrapper Infrastructure

This module tests all components of the legacy code wrapper infrastructure:
- BaseService
- DependencyContainer
- HealthCheck system
- Error handling
- Logging decorators
"""

import pytest
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.core.base_service import BaseService, ServiceStatus, HealthCheckResult
from backend.core.dependency_container import DependencyContainer, get_container, reset_container
from backend.core.service_health import (
    HealthStatus, HealthCheck, HealthCheckInterface, HealthMonitor, get_health_monitor
)
from backend.core.error_wrapper import (
    ServiceError, InitializationError, DependencyError, ValidationError, ExecutionError,
    handle_service_errors, safe_execute, ErrorContext, validate_input
)
from backend.core.logging_decorator import (
    log_service_call, log_performance, log_exceptions, log_entry_exit, MethodLogger
)


# Test Service Implementation
class TestLegacyModule:
    """Mock legacy module for testing"""
    
    def calculate(self, value: int) -> int:
        return value * 2
    
    def failing_operation(self):
        raise ValueError("Legacy operation failed")


class TestService(BaseService[TestLegacyModule], HealthCheckInterface):
    """Test service implementation"""
    
    def initialize(self) -> None:
        """Initialize test service"""
        self._legacy_module = TestLegacyModule()
        self._set_initialized(True)
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is healthy"
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
    
    @handle_service_errors(service_name="TestService", error_message="Calculation failed")
    def calculate_with_error_handling(self, value: int) -> int:
        """Method with error handling decorator"""
        if self._legacy_module:
            return self._legacy_module.calculate(value)
        raise RuntimeError("Legacy module not available")
    
    @log_service_call(service_name="TestService", log_result=True)
    def calculate_with_logging(self, value: int) -> int:
        """Method with logging decorator"""
        if self._legacy_module:
            return self._legacy_module.calculate(value)
        return 0


# Tests for BaseService
class TestBaseService:
    """Tests for BaseService class"""
    
    def test_service_initialization(self):
        """Test service initialization"""
        service = TestService("test_service")
        
        assert service.service_name == "test_service"
        assert not service.is_initialized
        assert service.legacy_module is None
        
        service.initialize()
        
        assert service.is_initialized
        assert service.legacy_module is not None
    
    def test_dependency_management(self):
        """Test dependency registration and retrieval"""
        service = TestService("test_service")
        
        # Register dependency
        mock_db = {"connection": "test"}
        service.register_dependency("database", mock_db)
        
        assert service.has_dependency("database")
        assert service.get_dependency("database") == mock_db
        
        # Test missing dependency
        with pytest.raises(KeyError):
            service.get_dependency("nonexistent")
    
    def test_health_check(self):
        """Test health check functionality"""
        service = TestService("test_service")
        
        # Before initialization
        result = service.health_check()
        assert result.status == ServiceStatus.UNHEALTHY
        assert not result.is_healthy()
        
        # After initialization
        service.initialize()
        result = service.health_check()
        assert result.status == ServiceStatus.HEALTHY
        assert result.is_healthy()
    
    def test_service_info(self):
        """Test service information retrieval"""
        service = TestService("test_service")
        service.register_dependency("dep1", "value1")
        service.initialize()
        
        info = service.get_service_info()
        
        assert info["name"] == "test_service"
        assert info["initialized"] is True
        assert "dep1" in info["dependencies"]
        assert info["has_legacy_module"] is True


# Tests for DependencyContainer
class TestDependencyContainer:
    """Tests for DependencyContainer class"""
    
    def setup_method(self):
        """Reset container before each test"""
        reset_container()
    
    def test_singleton_registration(self):
        """Test singleton registration and resolution"""
        container = DependencyContainer()
        
        instance = {"value": 42}
        container.register_singleton("test_singleton", instance)
        
        assert container.has("test_singleton")
        assert container.resolve("test_singleton") is instance
    
    def test_factory_registration(self):
        """Test factory registration"""
        container = DependencyContainer()
        
        call_count = 0
        
        def factory():
            nonlocal call_count
            call_count += 1
            return {"count": call_count}
        
        container.register_factory("test_factory", factory)
        
        # Each resolution creates new instance
        instance1 = container.resolve("test_factory")
        instance2 = container.resolve("test_factory")
        
        assert instance1["count"] == 1
        assert instance2["count"] == 2
    
    def test_lazy_singleton(self):
        """Test lazy singleton initialization"""
        container = DependencyContainer()
        
        initialized = False
        
        def factory():
            nonlocal initialized
            initialized = True
            return {"initialized": True}
        
        container.register_lazy_singleton("lazy_singleton", factory)
        
        # Not initialized yet
        assert not initialized
        
        # First resolution initializes
        instance1 = container.resolve("lazy_singleton")
        assert initialized
        
        # Second resolution returns same instance
        instance2 = container.resolve("lazy_singleton")
        assert instance1 is instance2
    
    def test_duplicate_registration(self):
        """Test that duplicate registration raises error"""
        container = DependencyContainer()
        
        container.register_singleton("test", "value1")
        
        with pytest.raises(ValueError):
            container.register_singleton("test", "value2")
    
    def test_missing_dependency(self):
        """Test resolution of missing dependency"""
        container = DependencyContainer()
        
        with pytest.raises(KeyError):
            container.resolve("nonexistent")
    
    def test_global_container(self):
        """Test global container instance"""
        container1 = get_container()
        container2 = get_container()
        
        assert container1 is container2


# Tests for Health Check System
class TestHealthCheckSystem:
    """Tests for health check system"""
    
    def test_health_check_result(self):
        """Test HealthCheck result"""
        check = HealthCheck(
            service_name="test_service",
            status=HealthStatus.HEALTHY,
            message="All good",
            details={"uptime": 100}
        )
        
        assert check.is_healthy()
        assert not check.is_degraded()
        assert not check.is_unhealthy()
        
        result_dict = check.to_dict()
        assert result_dict["status"] == "healthy"
        assert result_dict["service_name"] == "test_service"
    
    def test_health_monitor_registration(self):
        """Test service registration in health monitor"""
        monitor = HealthMonitor()
        service = TestService("test_service")
        service.initialize()
        
        monitor.register_service("test_service", service)
        
        check = monitor.check_service("test_service")
        assert check.is_healthy()
    
    def test_health_monitor_all_services(self):
        """Test checking all services"""
        monitor = HealthMonitor()
        
        service1 = TestService("service1")
        service1.initialize()
        service2 = TestService("service2")
        service2.initialize()
        
        monitor.register_service("service1", service1)
        monitor.register_service("service2", service2)
        
        results = monitor.check_all_services()
        
        assert len(results) == 2
        assert results["service1"].is_healthy()
        assert results["service2"].is_healthy()
    
    def test_health_monitor_history(self):
        """Test health check history tracking"""
        monitor = HealthMonitor(max_history=5)
        service = TestService("test_service")
        service.initialize()
        
        monitor.register_service("test_service", service)
        
        # Perform multiple checks
        for _ in range(10):
            monitor.check_service("test_service")
        
        history = monitor.get_service_history("test_service")
        
        # Should only keep max_history items
        assert len(history) <= 5
    
    def test_system_health_report(self):
        """Test system health report generation"""
        monitor = HealthMonitor()
        
        service1 = TestService("service1")
        service1.initialize()
        service2 = TestService("service2")
        # Don't initialize service2
        
        monitor.register_service("service1", service1)
        monitor.register_service("service2", service2)
        
        report = monitor.get_system_report()
        
        assert report["overall_status"] == "unhealthy"
        assert report["summary"]["total_services"] == 2
        assert report["summary"]["healthy"] == 1
        assert report["summary"]["unhealthy"] == 1


# Tests for Error Handling
class TestErrorHandling:
    """Tests for error handling wrapper"""
    
    def test_service_error_creation(self):
        """Test ServiceError creation"""
        error = ServiceError(
            message="Test error",
            service_name="TestService",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        
        assert error.message == "Test error"
        assert error.service_name == "TestService"
        assert error.error_code == "TEST_ERROR"
        
        error_dict = error.to_dict()
        assert error_dict["error_code"] == "TEST_ERROR"
    
    def test_error_decorator(self):
        """Test error handling decorator"""
        service = TestService("test_service")
        service.initialize()
        
        # Should work normally
        result = service.calculate_with_error_handling(5)
        assert result == 10
        
        # Should wrap errors
        service._legacy_module = None
        with pytest.raises(ExecutionError):
            service.calculate_with_error_handling(5)
    
    def test_safe_execute(self):
        """Test safe_execute utility"""
        def failing_func():
            raise ValueError("Test error")
        
        result = safe_execute(
            failing_func,
            service_name="TestService",
            operation="test_op",
            default_return="default"
        )
        
        assert result == "default"
    
    def test_error_context(self):
        """Test ErrorContext context manager"""
        with pytest.raises(ExecutionError):
            with ErrorContext(service_name="TestService", operation="test_op"):
                raise ValueError("Test error")
    
    def test_validate_input(self):
        """Test input validation"""
        # Should pass
        validate_input(True, "Should not raise", service_name="TestService")
        
        # Should raise
        with pytest.raises(ValidationError):
            validate_input(False, "Should raise", service_name="TestService", field_name="test_field")


# Tests for Logging Decorators
class TestLoggingDecorators:
    """Tests for logging decorators"""
    
    def test_log_service_call(self, caplog):
        """Test service call logging"""
        service = TestService("test_service")
        service.initialize()
        
        with caplog.at_level(logging.INFO):
            result = service.calculate_with_logging(5)
        
        assert result == 10
        assert "Calling TestService.calculate_with_logging" in caplog.text
        assert "Completed TestService.calculate_with_logging" in caplog.text
    
    def test_log_performance(self, caplog):
        """Test performance logging"""
        @log_performance(threshold_seconds=0.001, service_name="TestService")
        def slow_function():
            import time
            time.sleep(0.01)
            return "done"
        
        with caplog.at_level(logging.WARNING):
            result = slow_function()
        
        assert result == "done"
        assert "Slow execution" in caplog.text
    
    def test_log_exceptions(self, caplog):
        """Test exception logging"""
        @log_exceptions(service_name="TestService")
        def failing_function():
            raise ValueError("Test error")
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                failing_function()
        
        assert "Exception in TestService.failing_function" in caplog.text
    
    def test_method_logger_context(self, caplog):
        """Test MethodLogger context manager"""
        with caplog.at_level(logging.INFO):
            with MethodLogger("TestService", "test_method"):
                pass
        
        assert "Starting TestService.test_method" in caplog.text
        assert "Completed TestService.test_method" in caplog.text


# Integration Tests
class TestIntegration:
    """Integration tests for the complete infrastructure"""
    
    def test_full_service_lifecycle(self):
        """Test complete service lifecycle"""
        # Create container
        container = DependencyContainer()
        
        # Register dependencies
        container.register_singleton("config", {"setting": "value"})
        
        # Create service
        service = TestService("integration_test")
        service.register_dependency("config", container.resolve("config"))
        
        # Initialize
        service.initialize()
        assert service.is_initialized
        
        # Health check
        health = service.health_check()
        assert health.is_healthy()
        
        # Use service
        result = service.calculate_with_error_handling(10)
        assert result == 20
    
    def test_health_monitoring_integration(self):
        """Test health monitoring with multiple services"""
        monitor = HealthMonitor()
        
        # Create and register services
        services = []
        for i in range(3):
            service = TestService(f"service_{i}")
            service.initialize()
            services.append(service)
            monitor.register_service(f"service_{i}", service)
        
        # Check overall health
        overall_status = monitor.get_overall_health()
        assert overall_status == HealthStatus.HEALTHY
        
        # Get system report
        report = monitor.get_system_report()
        assert report["summary"]["total_services"] == 3
        assert report["summary"]["healthy"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
