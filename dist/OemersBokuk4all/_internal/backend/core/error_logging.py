"""
Error Logging System

Provides comprehensive error logging with rotation, formatting, and monitoring.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import traceback


class ErrorLogger:
    """Centralized error logging system"""
    
    def __init__(self, log_dir: str = "backend/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup loggers
        self.app_logger = self._setup_logger("app", "app.log")
        self.error_logger = self._setup_logger("error", "errors.log", level=logging.ERROR)
        self.access_logger = self._setup_logger("access", "access.log")
        self.security_logger = self._setup_logger("security", "security.log")
        
    def _setup_logger(
        self,
        name: str,
        filename: str,
        level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> logging.Logger:
        """Setup a logger with rotation"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers
        logger.handlers = []
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        # Also log to console in development
        if '--dev' in sys.argv or 'development' in sys.argv:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        request_path: Optional[str] = None
    ):
        """Log an error with context"""
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }
        
        if context:
            error_data["context"] = context
        
        if user_id:
            error_data["user_id"] = user_id
        
        if request_path:
            error_data["request_path"] = request_path
        
        self.error_logger.error(json.dumps(error_data, indent=2))
    
    def log_validation_error(
        self,
        field: str,
        message: str,
        value: Any = None,
        request_path: Optional[str] = None
    ):
        """Log a validation error"""
        validation_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "validation_error",
            "field": field,
            "message": message,
            "value": str(value) if value is not None else None,
            "request_path": request_path
        }
        
        self.app_logger.warning(json.dumps(validation_data))
    
    def log_security_event(
        self,
        event_type: str,
        message: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log a security-related event"""
        security_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "message": message,
        }
        
        if user_id:
            security_data["user_id"] = user_id
        
        if ip_address:
            security_data["ip_address"] = ip_address
        
        if details:
            security_data["details"] = details
        
        self.security_logger.warning(json.dumps(security_data, indent=2))
    
    def log_access(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log an API access"""
        access_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }
        
        if user_id:
            access_data["user_id"] = user_id
        
        if ip_address:
            access_data["ip_address"] = ip_address
        
        self.access_logger.info(json.dumps(access_data))
    
    def log_database_error(
        self,
        operation: str,
        table: Optional[str] = None,
        error: Optional[Exception] = None,
        query: Optional[str] = None
    ):
        """Log a database error"""
        db_error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "database_error",
            "operation": operation,
        }
        
        if table:
            db_error_data["table"] = table
        
        if error:
            db_error_data["error_type"] = type(error).__name__
            db_error_data["error_message"] = str(error)
        
        if query:
            # Sanitize query (remove sensitive data)
            db_error_data["query"] = self._sanitize_query(query)
        
        self.error_logger.error(json.dumps(db_error_data, indent=2))
    
    def log_external_service_error(
        self,
        service_name: str,
        endpoint: str,
        error: Exception,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        """Log an external service error"""
        service_error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "external_service_error",
            "service_name": service_name,
            "endpoint": endpoint,
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        
        if request_data:
            service_error_data["request_data"] = self._sanitize_data(request_data)
        
        if response_data:
            service_error_data["response_data"] = response_data
        
        self.error_logger.error(json.dumps(service_error_data, indent=2))
    
    def log_performance_issue(
        self,
        operation: str,
        duration_ms: float,
        threshold_ms: float,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log a performance issue"""
        perf_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "performance_issue",
            "operation": operation,
            "duration_ms": round(duration_ms, 2),
            "threshold_ms": threshold_ms,
            "exceeded_by_ms": round(duration_ms - threshold_ms, 2),
        }
        
        if details:
            perf_data["details"] = details
        
        self.app_logger.warning(json.dumps(perf_data, indent=2))
    
    def _sanitize_query(self, query: str) -> str:
        """Sanitize SQL query to remove sensitive data"""
        # Remove password values
        import re
        query = re.sub(r"password\s*=\s*'[^']*'", "password='***'", query, flags=re.IGNORECASE)
        query = re.sub(r'password\s*=\s*"[^"]*"', 'password="***"', query, flags=re.IGNORECASE)
        return query
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data to remove sensitive information"""
        sensitive_keys = ['password', 'token', 'secret', 'api_key', 'credit_card']
        sanitized = data.copy()
        
        for key in sanitized:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***"
        
        return sanitized
    
    def get_error_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for the last N hours"""
        # This would typically query a database or parse log files
        # For now, return a placeholder
        return {
            "period_hours": hours,
            "total_errors": 0,
            "error_types": {},
            "most_common_errors": []
        }


# Global error logger instance
error_logger = ErrorLogger()


def get_error_logger() -> ErrorLogger:
    """Get the global error logger instance"""
    return error_logger
