"""Pricing Audit and Logging System

Comprehensive audit trail for all pricing changes, logging for pricing calculations,
and error monitoring and alerting for pricing issues.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    PRICE_CALCULATION = "price_calculation"
    MARGIN_CHANGE = "margin_change"
    DISCOUNT_APPLIED = "discount_applied"
    SURCHARGE_APPLIED = "surcharge_applied"
    PRODUCT_PRICE_UPDATE = "product_price_update"
    VALIDATION_ERROR = "validation_error"
    CALCULATION_ERROR = "calculation_error"
    CACHE_OPERATION = "cache_operation"
    BUSINESS_RULE_VIOLATION = "business_rule_violation"
    SYSTEM_EVENT = "system_event"


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Represents an audit event"""
    event_type: AuditEventType
    severity: AuditSeverity
    message: str
    user_id: str | None = None
    session_id: str | None = None
    component: str = "pricing"
    operation: str = "unknown"

    # Event data
    before_data: dict[str, Any] | None = None
    after_data: dict[str, Any] | None = None
    context_data: dict[str, Any] | None = None

    # Metadata
    timestamp: datetime | None = None
    event_id: str | None = None
    correlation_id: str | None = None

    # Performance metrics
    duration_ms: float | None = None
    memory_usage_mb: float | None = None

    def __post_init__(self):
        if self.context_data is None:
            self.context_data = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert audit event to dictionary for storage"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "component": self.component,
            "operation": self.operation,
            "before_data": json.dumps(
                self.before_data) if self.before_data else None,
            "after_data": json.dumps(
                self.after_data) if self.after_data else None,
            "context_data": json.dumps(
                self.context_data),
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "duration_ms": self.duration_ms,
            "memory_usage_mb": self.memory_usage_mb}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditEvent:
        """Create audit event from dictionary"""
        return cls(
            event_type=AuditEventType(data["event_type"]),
            severity=AuditSeverity(data["severity"]),
            message=data["message"],
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            component=data.get("component", "pricing"),
            operation=data.get("operation", "unknown"),
            before_data=json.loads(data["before_data"]) if data.get("before_data") else None,
            after_data=json.loads(data["after_data"]) if data.get("after_data") else None,
            context_data=json.loads(data.get("context_data", "{}")),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_id=data.get("event_id"),
            correlation_id=data.get("correlation_id"),
            duration_ms=data.get("duration_ms"),
            memory_usage_mb=data.get("memory_usage_mb")
        )


@dataclass
class AuditQuery:
    """Query parameters for audit log search"""
    event_types: list[AuditEventType] | None = None
    severities: list[AuditSeverity] | None = None
    user_id: str | None = None
    session_id: str | None = None
    component: str | None = None
    operation: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    correlation_id: str | None = None
    limit: int = 1000
    offset: int = 0
    order_by: str = "timestamp"
    order_desc: bool = True


class PricingAuditLogger:
    """Comprehensive audit logging system for pricing operations"""

    def __init__(self, db_path: str = "data/pricing_audit.db",
                 max_log_size_mb: int = 100, retention_days: int = 90):
        """Initialize audit logger

        Args:
            db_path: Path to audit database
            max_log_size_mb: Maximum log size in MB before rotation
            retention_days: Number of days to retain audit logs
        """
        self.db_path = Path(db_path)
        self.max_log_size_mb = max_log_size_mb
        self.retention_days = retention_days
        self.logger = logging.getLogger(f"{__name__}.PricingAuditLogger")

        # Thread safety
        self._lock = threading.Lock()

        # Initialize database
        self._init_database()

        # Setup log rotation
        self._setup_log_rotation()

        # Event listeners
        self._event_listeners: list[Callable[[AuditEvent], None]] = []

        # Performance tracking
        self._performance_metrics = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_severity": {},
            "average_duration_ms": 0.0
        }

    def _init_database(self):
        """Initialize audit database"""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT UNIQUE,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        component TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        before_data TEXT,
                        after_data TEXT,
                        context_data TEXT,
                        timestamp TEXT NOT NULL,
                        correlation_id TEXT,
                        duration_ms REAL,
                        memory_usage_mb REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indexes for performance
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)")
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_severity ON audit_events(severity)")
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_id ON audit_events(user_id)")
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_session_id ON audit_events(session_id)")
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_correlation_id ON audit_events(correlation_id)")

                conn.commit()

            self.logger.info(f"Initialized audit database: {self.db_path}")

        except Exception as e:
            self.logger.error(f"Failed to initialize audit database: {e}")
            raise

    def _setup_log_rotation(self):
        """Setup automatic log rotation"""
        try:
            # Check current database size
            if self.db_path.exists():
                size_mb = self.db_path.stat().st_size / (1024 * 1024)
                if size_mb > self.max_log_size_mb:
                    self._rotate_logs()

            # Schedule cleanup of old records
            self._cleanup_old_records()

        except Exception as e:
            self.logger.warning(f"Log rotation setup failed: {e}")

    def _rotate_logs(self):
        """Rotate audit logs when they get too large"""
        try:
            backup_path = self.db_path.with_suffix(
                f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")

            # Copy current database to backup
            import shutil
            shutil.copy2(self.db_path, backup_path)

            # Clear old records from main database
            cutoff_date = datetime.now() - timedelta(days=30)  # Keep last 30 days

            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute(
                    "DELETE FROM audit_events WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                conn.execute("VACUUM")  # Reclaim space
                conn.commit()

            self.logger.info(f"Rotated audit logs. Backup: {backup_path}")

        except Exception as e:
            self.logger.error(f"Log rotation failed: {e}")

    def _cleanup_old_records(self):
        """Clean up old audit records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)

            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    "DELETE FROM audit_events WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                deleted_count = cursor.rowcount
                conn.commit()

            if deleted_count > 0:
                self.logger.info(
                    f"Cleaned up {deleted_count} old audit records")

        except Exception as e:
            self.logger.warning(f"Cleanup of old records failed: {e}")

    def log_event(self, event: AuditEvent) -> bool:
        """Log an audit event

        Args:
            event: Audit event to log

        Returns:
            True if successful, False otherwise
        """
        try:
            with self._lock:
                # Generate event ID if not provided
                if not event.event_id:
                    event.event_id = f"{
                        event.event_type.value}_{
                        datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

                # Store in database
                with sqlite3.connect(str(self.db_path)) as conn:
                    event_data = event.to_dict()

                    conn.execute(
                        """
                        INSERT INTO audit_events (
                            event_id, event_type, severity, message, user_id, session_id,
                            component, operation, before_data, after_data, context_data,
                            timestamp, correlation_id, duration_ms, memory_usage_mb
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (event_data["event_id"],
                         event_data["event_type"],
                            event_data["severity"],
                            event_data["message"],
                            event_data["user_id"],
                            event_data["session_id"],
                            event_data["component"],
                            event_data["operation"],
                            event_data["before_data"],
                            event_data["after_data"],
                            event_data["context_data"],
                            event_data["timestamp"],
                            event_data["correlation_id"],
                            event_data["duration_ms"],
                            event_data["memory_usage_mb"]))
                    conn.commit()

                # Update performance metrics
                self._update_performance_metrics(event)

                # Notify listeners
                self._notify_listeners(event)

                # Log to standard logger based on severity
                self._log_to_standard_logger(event)

                return True

        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            return False

    def _update_performance_metrics(self, event: AuditEvent):
        """Update performance metrics"""
        self._performance_metrics["total_events"] += 1

        # Count by type
        event_type = event.event_type.value
        self._performance_metrics["events_by_type"][event_type] = (
            self._performance_metrics["events_by_type"].get(event_type, 0) + 1
        )

        # Count by severity
        severity = event.severity.value
        self._performance_metrics["events_by_severity"][severity] = (
            self._performance_metrics["events_by_severity"].get(severity, 0) + 1
        )

        # Update average duration
        if event.duration_ms is not None:
            current_avg = self._performance_metrics["average_duration_ms"]
            total_events = self._performance_metrics["total_events"]
            self._performance_metrics["average_duration_ms"] = (
                (current_avg * (total_events - 1) + event.duration_ms) / total_events
            )

    def _notify_listeners(self, event: AuditEvent):
        """Notify event listeners"""
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.warning(f"Event listener failed: {e}")

    def _log_to_standard_logger(self, event: AuditEvent):
        """Log event to standard Python logger"""
        log_message = f"[{event.event_type.value}] {event.message}"

        if event.severity == AuditSeverity.DEBUG:
            self.logger.debug(
                log_message, extra={
                    "audit_event": event.to_dict()})
        elif event.severity == AuditSeverity.INFO:
            self.logger.info(
                log_message, extra={
                    "audit_event": event.to_dict()})
        elif event.severity == AuditSeverity.WARNING:
            self.logger.warning(
                log_message, extra={
                    "audit_event": event.to_dict()})
        elif event.severity == AuditSeverity.ERROR:
            self.logger.error(
                log_message, extra={
                    "audit_event": event.to_dict()})
        elif event.severity == AuditSeverity.CRITICAL:
            self.logger.critical(
                log_message, extra={
                    "audit_event": event.to_dict()})

    def query_events(self, query: AuditQuery) -> list[AuditEvent]:
        """Query audit events

        Args:
            query: Query parameters

        Returns:
            List of matching audit events
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row

                # Build SQL query
                sql_parts = ["SELECT * FROM audit_events WHERE 1=1"]
                params = []

                if query.event_types:
                    placeholders = ",".join("?" * len(query.event_types))
                    sql_parts.append(f"AND event_type IN ({placeholders})")
                    params.extend([et.value for et in query.event_types])

                if query.severities:
                    placeholders = ",".join("?" * len(query.severities))
                    sql_parts.append(f"AND severity IN ({placeholders})")
                    params.extend([s.value for s in query.severities])

                if query.user_id:
                    sql_parts.append("AND user_id = ?")
                    params.append(query.user_id)

                if query.session_id:
                    sql_parts.append("AND session_id = ?")
                    params.append(query.session_id)

                if query.component:
                    sql_parts.append("AND component = ?")
                    params.append(query.component)

                if query.operation:
                    sql_parts.append("AND operation = ?")
                    params.append(query.operation)

                if query.start_time:
                    sql_parts.append("AND timestamp >= ?")
                    params.append(query.start_time.isoformat())

                if query.end_time:
                    sql_parts.append("AND timestamp <= ?")
                    params.append(query.end_time.isoformat())

                if query.correlation_id:
                    sql_parts.append("AND correlation_id = ?")
                    params.append(query.correlation_id)

                # Add ordering
                order_direction = "DESC" if query.order_desc else "ASC"
                sql_parts.append(
                    f"ORDER BY {
                        query.order_by} {order_direction}")

                # Add limit and offset
                sql_parts.append("LIMIT ? OFFSET ?")
                params.extend([query.limit, query.offset])

                sql = " ".join(sql_parts)

                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()

                # Convert to AuditEvent objects
                events = []
                for row in rows:
                    event_data = dict(row)
                    events.append(AuditEvent.from_dict(event_data))

                return events

        except Exception as e:
            self.logger.error(f"Failed to query audit events: {e}")
            return []

    def get_event_statistics(self, hours: int = 24) -> dict[str, Any]:
        """Get audit event statistics

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with statistics
        """
        try:
            start_time = datetime.now() - timedelta(hours=hours)

            with sqlite3.connect(str(self.db_path)) as conn:
                # Total events
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM audit_events WHERE timestamp >= ?",
                    (start_time.isoformat(),)
                )
                total_events = cursor.fetchone()[0]

                # Events by type
                cursor = conn.execute("""
                    SELECT event_type, COUNT(*) as count
                    FROM audit_events
                    WHERE timestamp >= ?
                    GROUP BY event_type
                """, (start_time.isoformat(),))
                events_by_type = dict(cursor.fetchall())

                # Events by severity
                cursor = conn.execute("""
                    SELECT severity, COUNT(*) as count
                    FROM audit_events
                    WHERE timestamp >= ?
                    GROUP BY severity
                """, (start_time.isoformat(),))
                events_by_severity = dict(cursor.fetchall())

                # Average duration
                cursor = conn.execute("""
                    SELECT AVG(duration_ms)
                    FROM audit_events
                    WHERE timestamp >= ? AND duration_ms IS NOT NULL
                """, (start_time.isoformat(),))
                avg_duration = cursor.fetchone()[0] or 0.0

                # Error rate
                cursor = conn.execute("""
                    SELECT COUNT(*)
                    FROM audit_events
                    WHERE timestamp >= ? AND severity IN ('error', 'critical')
                """, (start_time.isoformat(),))
                error_count = cursor.fetchone()[0]
                error_rate = (
                    error_count /
                    total_events *
                    100) if total_events > 0 else 0.0

                return {
                    "period_hours": hours,
                    "total_events": total_events,
                    "events_by_type": events_by_type,
                    "events_by_severity": events_by_severity,
                    "average_duration_ms": avg_duration,
                    "error_count": error_count,
                    "error_rate_percent": error_rate,
                    "performance_metrics": self._performance_metrics.copy()
                }

        except Exception as e:
            self.logger.error(f"Failed to get event statistics: {e}")
            return {"error": str(e)}

    def add_event_listener(self, listener: Callable[[AuditEvent], None]):
        """Add event listener for real-time notifications

        Args:
            listener: Function to call when events are logged
        """
        self._event_listeners.append(listener)

    def remove_event_listener(self, listener: Callable[[AuditEvent], None]):
        """Remove event listener

        Args:
            listener: Function to remove
        """
        if listener in self._event_listeners:
            self._event_listeners.remove(listener)


class PricingCalculationLogger:
    """Specialized logger for pricing calculations"""

    def __init__(self, audit_logger: PricingAuditLogger):
        """Initialize calculation logger

        Args:
            audit_logger: Audit logger instance
        """
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(f"{__name__}.PricingCalculationLogger")

    def log_calculation_start(self, calculation_data: dict[str, Any],
                              user_id: str = None, session_id: str = None,
                              correlation_id: str = None) -> str:
        """Log start of pricing calculation

        Args:
            calculation_data: Input data for calculation
            user_id: User performing calculation
            session_id: Session ID
            correlation_id: Correlation ID for tracking

        Returns:
            Event ID for correlation
        """
        event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Pricing calculation started",
            user_id=user_id,
            session_id=session_id,
            component="pricing_engine",
            operation="calculate_price",
            context_data={
                "component_count": len(
                    calculation_data.get(
                        "components",
                        [])),
                "has_modifications": bool(
                    calculation_data.get("modifications")),
                "system_type": calculation_data.get(
                    "system_type",
                    "unknown")},
            correlation_id=correlation_id)

        self.audit_logger.log_event(event)
        return event.event_id

    def log_calculation_complete(self,
                                 calculation_result: dict[str,
                                                          Any],
                                 duration_ms: float,
                                 user_id: str = None,
                                 session_id: str = None,
                                 correlation_id: str = None):
        """Log completion of pricing calculation

        Args:
            calculation_result: Result of calculation
            duration_ms: Calculation duration in milliseconds
            user_id: User performing calculation
            session_id: Session ID
            correlation_id: Correlation ID for tracking
        """
        event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Pricing calculation completed",
            user_id=user_id,
            session_id=session_id,
            component="pricing_engine",
            operation="calculate_price",
            after_data={
                "final_price_net": calculation_result.get("final_price_net"),
                "final_price_gross": calculation_result.get("final_price_gross"),
                "total_discounts": calculation_result.get("total_discounts"),
                "total_surcharges": calculation_result.get("total_surcharges")},
            duration_ms=duration_ms,
            correlation_id=correlation_id)

        self.audit_logger.log_event(event)

    def log_calculation_error(self,
                              error: Exception,
                              calculation_data: dict[str,
                                                     Any],
                              user_id: str = None,
                              session_id: str = None,
                              correlation_id: str = None):
        """Log pricing calculation error

        Args:
            error: Exception that occurred
            calculation_data: Input data that caused error
            user_id: User performing calculation
            session_id: Session ID
            correlation_id: Correlation ID for tracking
        """
        event = AuditEvent(
            event_type=AuditEventType.CALCULATION_ERROR,
            severity=AuditSeverity.ERROR,
            message=f"Pricing calculation failed: {str(error)}",
            user_id=user_id,
            session_id=session_id,
            component="pricing_engine",
            operation="calculate_price",
            context_data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "component_count": len(calculation_data.get("components", []))
            },
            correlation_id=correlation_id
        )

        self.audit_logger.log_event(event)

    def log_margin_change(self, product_id: int, old_margin: dict[str, Any],
                          new_margin: dict[str, Any], user_id: str = None,
                          session_id: str = None):
        """Log margin configuration change

        Args:
            product_id: Product ID
            old_margin: Previous margin configuration
            new_margin: New margin configuration
            user_id: User making change
            session_id: Session ID
        """
        event = AuditEvent(
            event_type=AuditEventType.MARGIN_CHANGE,
            severity=AuditSeverity.INFO,
            message=f"Margin changed for product {product_id}",
            user_id=user_id,
            session_id=session_id,
            component="margin_manager",
            operation="set_margin",
            before_data=old_margin,
            after_data=new_margin,
            context_data={"product_id": product_id}
        )

        self.audit_logger.log_event(event)

    def log_price_update(
            self,
            product_id: int,
            old_price: float,
            new_price: float,
            user_id: str = None,
            session_id: str = None):
        """Log product price update

        Args:
            product_id: Product ID
            old_price: Previous price
            new_price: New price
            user_id: User making change
            session_id: Session ID
        """
        event = AuditEvent(
            event_type=AuditEventType.PRODUCT_PRICE_UPDATE,
            severity=AuditSeverity.INFO,
            message=f"Price updated for product {product_id}: {old_price}€ → {new_price}€",
            user_id=user_id,
            session_id=session_id,
            component="product_manager",
            operation="update_price",
            before_data={
                "price": old_price},
            after_data={
                "price": new_price},
            context_data={
                "product_id": product_id,
                "price_change": new_price -
                old_price})

        self.audit_logger.log_event(event)


class PricingMonitor:
    """Real-time monitoring and alerting for pricing issues"""

    def __init__(self, audit_logger: PricingAuditLogger):
        """Initialize pricing monitor

        Args:
            audit_logger: Audit logger instance
        """
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(f"{__name__}.PricingMonitor")

        # Alert thresholds
        self.alert_thresholds = {
            "error_rate_percent": 5.0,  # Alert if error rate > 5%
            "avg_duration_ms": 5000.0,  # Alert if avg duration > 5 seconds
            "errors_per_hour": 10,  # Alert if > 10 errors per hour
            "calculation_failures_per_hour": 5  # Alert if > 5 calculation failures per hour
        }

        # Alert handlers
        self.alert_handlers: list[Callable[[str, dict[str, Any]], None]] = []

        # Add event listener for real-time monitoring
        self.audit_logger.add_event_listener(self._handle_audit_event)

        # Recent events for trend analysis
        self._recent_events: list[AuditEvent] = []
        self._max_recent_events = 1000

    def _handle_audit_event(self, event: AuditEvent):
        """Handle audit events for real-time monitoring"""
        # Store recent events
        self._recent_events.append(event)
        if len(self._recent_events) > self._max_recent_events:
            self._recent_events = self._recent_events[-self._max_recent_events:]

        # Check for immediate alerts
        if event.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            self._check_error_alerts(event)

        if event.event_type == AuditEventType.CALCULATION_ERROR:
            self._check_calculation_failure_alerts(event)

        if event.duration_ms and event.duration_ms > self.alert_thresholds["avg_duration_ms"]:
            self._send_alert(
                "High Duration Alert",
                {
                    "event_id": event.event_id,
                    "duration_ms": event.duration_ms,
                    "threshold_ms": self.alert_thresholds["avg_duration_ms"],
                    "operation": event.operation
                }
            )

    def _check_error_alerts(self, event: AuditEvent):
        """Check for error rate alerts"""
        # Count recent errors (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_errors = [
            e for e in self._recent_events if e.timestamp >= one_hour_ago and e.severity in [
                AuditSeverity.ERROR, AuditSeverity.CRITICAL]]

        if len(recent_errors) > self.alert_thresholds["errors_per_hour"]:
            self._send_alert(
                "High Error Rate Alert",
                {
                    "errors_last_hour": len(recent_errors),
                    "threshold": self.alert_thresholds["errors_per_hour"],
                    "latest_error": event.message
                }
            )

    def _check_calculation_failure_alerts(self, event: AuditEvent):
        """Check for calculation failure alerts"""
        # Count recent calculation failures (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_failures = [
            e for e in self._recent_events
            if e.timestamp >= one_hour_ago and e.event_type == AuditEventType.CALCULATION_ERROR
        ]

        if len(
                recent_failures) > self.alert_thresholds["calculation_failures_per_hour"]:
            self._send_alert("High Calculation Failure Rate Alert",
                             {"failures_last_hour": len(recent_failures),
                              "threshold": self.alert_thresholds["calculation_failures_per_hour"],
                              "latest_failure": event.message})

    def _send_alert(self, alert_type: str, alert_data: dict[str, Any]):
        """Send alert to registered handlers"""
        self.logger.warning(
            f"PRICING ALERT: {alert_type}", extra={
                "alert_data": alert_data})

        for handler in self.alert_handlers:
            try:
                handler(alert_type, alert_data)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")

    def add_alert_handler(
            self, handler: Callable[[str, dict[str, Any]], None]):
        """Add alert handler

        Args:
            handler: Function to call when alerts are triggered
        """
        self.alert_handlers.append(handler)

    def remove_alert_handler(
            self, handler: Callable[[str, dict[str, Any]], None]):
        """Remove alert handler

        Args:
            handler: Function to remove
        """
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)

    def get_health_status(self) -> dict[str, Any]:
        """Get current system health status

        Returns:
            Dictionary with health metrics
        """
        try:
            # Get recent statistics
            stats = self.audit_logger.get_event_statistics(hours=1)

            # Calculate health score (0-100)
            health_score = 100

            # Deduct for high error rate
            error_rate = stats.get("error_rate_percent", 0)
            if error_rate > self.alert_thresholds["error_rate_percent"]:
                health_score -= min(50, error_rate * 2)

            # Deduct for high average duration
            avg_duration = stats.get("average_duration_ms", 0)
            if avg_duration > self.alert_thresholds["avg_duration_ms"]:
                health_score -= min(30, (avg_duration / 1000) * 5)

            # Deduct for recent calculation failures
            recent_failures = len([
                e for e in self._recent_events[-100:]  # Last 100 events
                if e.event_type == AuditEventType.CALCULATION_ERROR
            ])
            if recent_failures > 5:
                health_score -= min(20, recent_failures * 2)

            health_score = max(0, health_score)

            # Determine status
            if health_score >= 90:
                status = "healthy"
            elif health_score >= 70:
                status = "warning"
            elif health_score >= 50:
                status = "degraded"
            else:
                status = "critical"

            return {
                "status": status,
                "health_score": health_score,
                "statistics": stats,
                "alert_thresholds": self.alert_thresholds,
                "recent_events_count": len(self._recent_events),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to get health status: {e}")
            return {
                "status": "unknown",
                "health_score": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global instances
_audit_logger_instance = None
_calculation_logger_instance = None
_monitor_instance = None


def get_audit_logger() -> PricingAuditLogger:
    """Get global audit logger instance"""
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = PricingAuditLogger()
    return _audit_logger_instance


def get_calculation_logger() -> PricingCalculationLogger:
    """Get global calculation logger instance"""
    global _calculation_logger_instance
    if _calculation_logger_instance is None:
        _calculation_logger_instance = PricingCalculationLogger(
            get_audit_logger())
    return _calculation_logger_instance


def get_pricing_monitor() -> PricingMonitor:
    """Get global pricing monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PricingMonitor(get_audit_logger())
    return _monitor_instance


# Convenience functions for common operations
def audit_price_calculation(calculation_data: dict[str,
                                                   Any],
                            result: dict[str,
                                         Any],
                            duration_ms: float,
                            user_id: str = None,
                            session_id: str = None):
    """Audit a complete price calculation

    Args:
        calculation_data: Input calculation data
        result: Calculation result
        duration_ms: Calculation duration
        user_id: User ID
        session_id: Session ID
    """
    logger = get_calculation_logger()
    correlation_id = f"calc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    logger.log_calculation_start(
        calculation_data,
        user_id,
        session_id,
        correlation_id)
    logger.log_calculation_complete(
        result,
        duration_ms,
        user_id,
        session_id,
        correlation_id)


def audit_pricing_error(error: Exception, context: dict[str, Any],
                        user_id: str = None, session_id: str = None):
    """Audit a pricing error

    Args:
        error: Exception that occurred
        context: Error context
        user_id: User ID
        session_id: Session ID
    """
    logger = get_calculation_logger()
    logger.log_calculation_error(error, context, user_id, session_id)
