"""
Comprehensive Application Tracing System using OpenTelemetry.

This module provides centralized tracing for the entire application to monitor:
- Performance metrics
- Error tracking
- User interactions
- Calculation flows
- Database operations
- PDF generation
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry.trace import Status, StatusCode
from functools import wraps
import logging
import time
from typing import Any, Callable, Dict, Optional
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppTracer:
    """Central tracing manager for the application."""
    
    def __init__(self, service_name: str = "bokuk2-solar-calculator", otlp_endpoint: str = "http://localhost:4318/v1/traces"):
        """
        Initialize the tracing system.
        
        Args:
            service_name: Name of the service for tracing
            otlp_endpoint: OTLP endpoint URL (AI Toolkit default: http://localhost:4318)
        """
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize OpenTelemetry tracing.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self._initialized:
            logger.info("Tracing already initialized")
            return True
            
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "2.5.0",
                "deployment.environment": "production"
            })
            
            # Set up tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            
            # Configure OTLP exporter
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            
            # Add span processor
            span_processor = BatchSpanProcessor(otlp_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            
            # Get tracer instance
            self.tracer = trace.get_tracer(__name__)
            
            # Instrument common libraries
            self._instrument_libraries()
            
            self._initialized = True
            logger.info(f"[OK] Tracing initialized: {self.service_name} -> {self.otlp_endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize tracing: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _instrument_libraries(self):
        """Automatically instrument common libraries."""
        try:
            # Instrument HTTP requests
            RequestsInstrumentor().instrument()
            
            # Instrument SQLite database
            SQLite3Instrumentor().instrument()
            
            logger.info("[OK] Libraries instrumented: requests, sqlite3")
        except Exception as e:
            logger.warning(f"[WARNING] Library instrumentation partial: {e}")
    
    def trace_function(self, operation_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
        """
        Decorator to trace function execution.
        
        Args:
            operation_name: Custom name for the operation (defaults to function name)
            attributes: Additional attributes to add to the span
            
        Usage:
            @app_tracer.trace_function("calculate_solar_output")
            def calculate(...):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self._initialized or not self.tracer:
                    # Tracing not initialized, execute function normally
                    return func(*args, **kwargs)
                
                span_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    # Add custom attributes
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, str(value))
                    
                    # Add function metadata
                    span.set_attribute("code.function", func.__name__)
                    span.set_attribute("code.filepath", func.__code__.co_filename)
                    
                    start_time = time.time()
                    
                    try:
                        # Execute function
                        result = func(*args, **kwargs)
                        
                        # Mark as successful
                        span.set_status(Status(StatusCode.OK))
                        
                        # Add performance metric
                        duration = time.time() - start_time
                        span.set_attribute("execution_time_seconds", duration)
                        
                        return result
                        
                    except Exception as e:
                        # Record error
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        
                        # Add error details
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        
                        # Re-raise exception
                        raise
            
            return wrapper
        return decorator
    
    def create_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Create a manual span context.
        
        Args:
            name: Name of the span
            attributes: Attributes to add to the span
            
        Usage:
            with app_tracer.create_span("database_query") as span:
                span.set_attribute("query", "SELECT * FROM products")
                result = execute_query()
        """
        if not self._initialized or not self.tracer:
            # Return dummy context manager
            from contextlib import nullcontext
            return nullcontext()
        
        span = self.tracer.start_span(name)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        
        return span
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Add an event to the current span.
        
        Args:
            name: Event name
            attributes: Event attributes
        """
        if not self._initialized:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes or {})
    
    def shutdown(self):
        """Shutdown tracing gracefully."""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
            logger.info("[OK] Tracing shutdown complete")


# Global tracer instance
app_tracer = AppTracer()


# Convenience decorators
def trace_calculation(func: Callable) -> Callable:
    """Trace calculation functions."""
    return app_tracer.trace_function(
        operation_name=f"calculation.{func.__name__}",
        attributes={"component": "calculations"}
    )(func)


def trace_database(func: Callable) -> Callable:
    """Trace database operations."""
    return app_tracer.trace_function(
        operation_name=f"database.{func.__name__}",
        attributes={"component": "database"}
    )(func)


def trace_pdf(func: Callable) -> Callable:
    """Trace PDF generation."""
    return app_tracer.trace_function(
        operation_name=f"pdf.{func.__name__}",
        attributes={"component": "pdf"}
    )(func)


def trace_ui(func: Callable) -> Callable:
    """Trace UI operations."""
    return app_tracer.trace_function(
        operation_name=f"ui.{func.__name__}",
        attributes={"component": "ui"}
    )(func)


def trace_api(func: Callable) -> Callable:
    """Trace API calls."""
    return app_tracer.trace_function(
        operation_name=f"api.{func.__name__}",
        attributes={"component": "api"}
    )(func)


# Module-level initialization
def initialize_tracing(enabled: bool = True) -> bool:
    """
    Initialize application tracing.
    
    Args:
        enabled: Whether to enable tracing
        
    Returns:
        bool: True if successful
    """
    if not enabled:
        logger.info("Tracing disabled")
        return False
    
    return app_tracer.initialize()


def shutdown_tracing():
    """Shutdown tracing system."""
    app_tracer.shutdown()


if __name__ == "__main__":
    # Test tracing
    initialize_tracing()
    
    @trace_calculation
    def test_calculation(x: float, y: float) -> float:
        """Test calculation function."""
        return x + y
    
    result = test_calculation(10, 20)
    print(f"Result: {result}")
    
    shutdown_tracing()
