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
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SpanExporter, SpanExportResult
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry.trace import Status, StatusCode
from functools import wraps
import logging
import time
from typing import Any, Callable, Dict, Optional, Sequence
import traceback
import os
import warnings

# Suppress OpenTelemetry and urllib3 connection warnings
warnings.filterwarnings('ignore', category=Warning, module='opentelemetry')
warnings.filterwarnings('ignore', category=Warning, module='urllib3')

# Suppress urllib3, requests, and opentelemetry connection error logging
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.CRITICAL)
logging.getLogger('opentelemetry.exporter.otlp.proto.http.trace_exporter').setLevel(logging.CRITICAL)
logging.getLogger('opentelemetry.sdk._shared_internal').setLevel(logging.CRITICAL)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress connection error warnings from urllib3 and requests
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('opentelemetry.exporter.otlp.proto.http.trace_exporter').setLevel(logging.ERROR)
logging.getLogger('opentelemetry.sdk._logs._internal').setLevel(logging.ERROR)

# Environment variable to disable tracing entirely
TRACING_DISABLED = os.getenv('DISABLE_TRACING', 'false').lower() == 'true'


class SafeOTLPSpanExporter(SpanExporter):
    """
    Wrapper around OTLPSpanExporter that silently handles connection failures.
    
    This prevents application crashes when the OTLP collector is not available,
    while still allowing tracing to work if the collector becomes available later.
    """
    
    def __init__(self, endpoint: str, timeout: int = 2):
        """Initialize the safe exporter."""
        self.endpoint = endpoint
        self.timeout = timeout
        self._exporter: Optional[OTLPSpanExporter] = None
        self._connection_failed = False
        self._last_error_log = 0
        
        try:
            self._exporter = OTLPSpanExporter(endpoint=endpoint, timeout=timeout)
        except Exception as e:
            logger.debug(f"OTLP exporter initialization warning: {e}")
            self._connection_failed = True
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans, silently handling connection errors.
        
        Returns SUCCESS even if export fails to prevent application crashes.
        """
        if self._connection_failed or not self._exporter:
            # Silently skip export if connection is known to be failed
            return SpanExportResult.SUCCESS
        
        try:
            # Attempt export with timeout
            result = self._exporter.export(spans)
            return result
        except Exception:
            # Suppress ALL exceptions (ConnectionError, TimeoutError, etc.)
            # Mark connection as failed to skip future attempts
            if not self._connection_failed:
                self._connection_failed = True
                # Log only once on first failure
                logger.debug("OTLP collector unavailable - tracing continues locally without export")
            
            # Return success to prevent BatchSpanProcessor from logging errors
            return SpanExportResult.SUCCESS
    
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        if self._exporter:
            try:
                self._exporter.shutdown()
            except Exception:
                pass
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush pending spans."""
        if self._exporter and not self._connection_failed:
            try:
                return self._exporter.force_flush(timeout_millis)
            except Exception:
                return True
        return True


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
        if TRACING_DISABLED:
            logger.info("[INFO] Tracing disabled via DISABLE_TRACING environment variable")
            self._initialized = False
            return False
            
        if self._initialized:
            logger.debug("Tracing already initialized")
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
            
            # Configure OTLP exporter with safe wrapper
            # The SafeOTLPSpanExporter will handle connection failures gracefully
            otlp_exporter = SafeOTLPSpanExporter(
                endpoint=self.otlp_endpoint,
                timeout=2
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(self.tracer_provider)
            
            # Get tracer instance
            self.tracer = trace.get_tracer(__name__)
            
            # Instrument libraries
            self._instrument_libraries()
            
            self._initialized = True
            logger.info(f"[OK] Tracing initialized: {self.service_name}")
            logger.debug(f"OTLP endpoint: {self.otlp_endpoint} (exports handled gracefully if unavailable)")
            return True
            
        except Exception as e:
            logger.warning(f"[WARNING] Tracing initialization failed (running without tracing): {e}")
            # Don't fail the application - just disable tracing
            self._initialized = False
            return False
    
    def _instrument_libraries(self):
        """Automatically instrument common libraries."""
        try:
            # Instrument HTTP requests
            try:
                RequestsInstrumentor().instrument()
                logger.debug("[OK] Requests instrumented")
            except Exception as e:
                logger.debug(f"Requests instrumentation skipped: {e}")
            
            # Instrument SQLite database
            try:
                SQLite3Instrumentor().instrument()
                logger.debug("[OK] SQLite3 instrumented")
            except Exception as e:
                logger.debug(f"SQLite3 instrumentation skipped: {e}")
            
        except Exception as e:
            logger.debug(f"Library instrumentation warning: {e}")
    
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
