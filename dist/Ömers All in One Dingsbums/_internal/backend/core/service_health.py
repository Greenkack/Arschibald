"""
Service Health Check Interface

This module provides interfaces and utilities for service health monitoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from enum import Enum


logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckInterface(ABC):
    """
    Interface for health check implementations.
    
    All services should implement this interface to provide
    standardized health monitoring.
    """
    
    @abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dictionary with health status and details
        """
        pass
    
    @abstractmethod
    def get_health_status(self) -> HealthStatus:
        """
        Get current health status.
        
        Returns:
            Current HealthStatus
        """
        pass


class HealthCheck:
    """
    Health check result container with metadata.
    """
    
    def __init__(
        self,
        service_name: str,
        status: HealthStatus,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        response_time_ms: Optional[float] = None
    ):
        """
        Initialize health check result.
        
        Args:
            service_name: Name of the service
            status: Health status
            message: Human-readable status message
            details: Additional details
            timestamp: Check timestamp
            response_time_ms: Response time in milliseconds
        """
        self.service_name = service_name
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or datetime.now()
        self.response_time_ms = response_time_ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "service_name": self.service_name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms
        }
    
    def is_healthy(self) -> bool:
        """Check if status is healthy"""
        return self.status == HealthStatus.HEALTHY
    
    def is_degraded(self) -> bool:
        """Check if status is degraded"""
        return self.status == HealthStatus.DEGRADED
    
    def is_unhealthy(self) -> bool:
        """Check if status is unhealthy"""
        return self.status == HealthStatus.UNHEALTHY


class HealthMonitor:
    """
    Health monitoring system for tracking service health over time.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize health monitor.
        
        Args:
            max_history: Maximum number of health checks to store per service
        """
        self.max_history = max_history
        self._health_history: Dict[str, List[HealthCheck]] = {}
        self._services: Dict[str, HealthCheckInterface] = {}
        logger.info("Health monitor initialized")
    
    def register_service(self, name: str, service: HealthCheckInterface) -> None:
        """
        Register a service for health monitoring.
        
        Args:
            name: Service identifier
            service: Service implementing HealthCheckInterface
        """
        self._services[name] = service
        self._health_history[name] = []
        logger.debug(f"Registered service for health monitoring: {name}")
    
    def check_service(self, name: str) -> HealthCheck:
        """
        Perform health check on a specific service.
        
        Args:
            name: Service identifier
            
        Returns:
            HealthCheck result
            
        Raises:
            KeyError: If service not registered
        """
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered for health monitoring")
        
        service = self._services[name]
        start_time = datetime.now()
        
        try:
            health_data = service.check_health()
            status = service.get_health_status()
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            health_check = HealthCheck(
                service_name=name,
                status=status,
                message=health_data.get("message", ""),
                details=health_data.get("details", {}),
                response_time_ms=response_time
            )
        except Exception as e:
            logger.error(f"Health check failed for service '{name}': {str(e)}")
            health_check = HealthCheck(
                service_name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__}
            )
        
        # Store in history
        self._add_to_history(name, health_check)
        
        return health_check
    
    def check_all_services(self) -> Dict[str, HealthCheck]:
        """
        Perform health check on all registered services.
        
        Returns:
            Dictionary mapping service names to HealthCheck results
        """
        results = {}
        for name in self._services.keys():
            results[name] = self.check_service(name)
        return results
    
    def get_service_history(self, name: str, limit: Optional[int] = None) -> List[HealthCheck]:
        """
        Get health check history for a service.
        
        Args:
            name: Service identifier
            limit: Maximum number of results to return
            
        Returns:
            List of HealthCheck results (most recent first)
        """
        if name not in self._health_history:
            return []
        
        history = self._health_history[name]
        if limit:
            return history[-limit:]
        return history
    
    def get_service_uptime(self, name: str, window: timedelta = timedelta(hours=24)) -> float:
        """
        Calculate service uptime percentage over a time window.
        
        Args:
            name: Service identifier
            window: Time window to calculate uptime
            
        Returns:
            Uptime percentage (0-100)
        """
        if name not in self._health_history:
            return 0.0
        
        cutoff_time = datetime.now() - window
        recent_checks = [
            check for check in self._health_history[name]
            if check.timestamp >= cutoff_time
        ]
        
        if not recent_checks:
            return 0.0
        
        healthy_checks = sum(1 for check in recent_checks if check.is_healthy())
        return (healthy_checks / len(recent_checks)) * 100
    
    def get_overall_health(self) -> HealthStatus:
        """
        Get overall system health status.
        
        Returns:
            Worst health status among all services
        """
        if not self._services:
            return HealthStatus.UNKNOWN
        
        results = self.check_all_services()
        
        # If any service is unhealthy, system is unhealthy
        if any(check.is_unhealthy() for check in results.values()):
            return HealthStatus.UNHEALTHY
        
        # If any service is degraded, system is degraded
        if any(check.is_degraded() for check in results.values()):
            return HealthStatus.DEGRADED
        
        # All services healthy
        return HealthStatus.HEALTHY
    
    def get_system_report(self) -> Dict[str, Any]:
        """
        Get comprehensive system health report.
        
        Returns:
            Dictionary with system health information
        """
        results = self.check_all_services()
        
        return {
            "overall_status": self.get_overall_health().value,
            "timestamp": datetime.now().isoformat(),
            "services": {
                name: check.to_dict()
                for name, check in results.items()
            },
            "summary": {
                "total_services": len(self._services),
                "healthy": sum(1 for c in results.values() if c.is_healthy()),
                "degraded": sum(1 for c in results.values() if c.is_degraded()),
                "unhealthy": sum(1 for c in results.values() if c.is_unhealthy())
            }
        }
    
    def _add_to_history(self, service_name: str, health_check: HealthCheck) -> None:
        """Add health check to history, maintaining max size"""
        if service_name not in self._health_history:
            self._health_history[service_name] = []
        
        history = self._health_history[service_name]
        history.append(health_check)
        
        # Trim history if needed
        if len(history) > self.max_history:
            self._health_history[service_name] = history[-self.max_history:]


# Global health monitor instance
_global_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """
    Get the global health monitor instance.
    
    Returns:
        Global HealthMonitor instance
    """
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = HealthMonitor()
    
    return _global_monitor
