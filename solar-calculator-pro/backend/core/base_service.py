"""
Base Service Wrapper Class

This module provides the foundation for wrapping legacy Python code
into modern service classes with dependency injection, health checks,
error handling, and logging.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
from datetime import datetime
import logging
from enum import Enum


# Configure logging
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """Health check result container"""
    
    def __init__(
        self,
        status: ServiceStatus,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

    
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.status == ServiceStatus.HEALTHY


T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """
    Base service wrapper class for legacy code integration.
    
    All service wrappers should inherit from this class to ensure
    consistent interface, error handling, logging, and health checks.
    
    Type parameter T represents the legacy module/class being wrapped.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize base service.
        
        Args:
            service_name: Unique identifier for this service
        """
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
        self._initialized = False
        self._legacy_module: Optional[T] = None
        self._dependencies: Dict[str, Any] = {}
        
        self.logger.info(f"Initializing service: {service_name}")
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the service and load legacy module.
        
        This method should:
        1. Load/import the legacy Python module
        2. Initialize any required dependencies
        3. Perform any necessary setup
        
        Raises:
            Exception: If initialization fails
        """
        pass
    
    @abstractmethod
    def health_check(self) -> HealthCheckResult:
        """
        Perform health check on the service.
        
        This method should verify:
        1. Service is initialized
        2. Dependencies are available
        3. Legacy module is functional
        
        Returns:
            HealthCheckResult: Current health status
        """
        pass
    
    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    def _set_initialized(self, value: bool = True) -> None:
        """Mark service as initialized"""
        self._initialized = value
        if value:
            self.logger.info(f"Service '{self.service_name}' initialized")
