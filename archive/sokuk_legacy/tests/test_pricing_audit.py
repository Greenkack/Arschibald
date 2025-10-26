"""Tests for Pricing Audit and Logging System

Comprehensive tests for audit trail, logging functionality, and error monitoring.
"""

import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pricing.pricing_audit import (
    AuditEvent,
    AuditEventType,
    AuditQuery,
    AuditSeverity,
    PricingAuditLogger,
    PricingCalculationLogger,
    PricingMonitor,
    audit_price_calculation,
    audit_pricing_error,
    get_audit_logger,
    get_calculation_logger,
    get_pricing_monitor,
)
from pricing.pricing_errors import CalculationError, ValidationError


class TestAuditEvent:
    """Test AuditEvent class"""

    def test_audit_event_creation(self):
        """Test audit event creation"""
        event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Test calculation",
            user_id="user123",
            session_id="session456",
            component="pricing_engine",
            operation="calculate_price",
            context_data={"test": "data"},
            duration_ms=150.5
        )

        assert event.event_type == AuditEventType.PRICE_CALCULATION
        assert event.severity == AuditSeverity.INFO
        assert event.message == "Test calculation"
        assert event.user_id == "user123"
        assert event.session_id == "session456"
        assert event.duration_ms == 150.5
        assert event.context_data["test"] == "data"
        assert isinstance(event.timestamp, datetime)

    def test_audit_event_to_dict(self):
        """Test audit event serialization"""
        event = AuditEvent(
            event_type=AuditEventType.MARGIN_CHANGE,
            severity=AuditSeverity.WARNING,
            message="Margin changed",
            before_data={"margin": 20.0},
            after_data={"margin": 25.0}
        )

        event_dict = event.to_dict()

        assert event_dict["event_type"] == "margin_change"
        assert event_dict["severity"] == "warning"
        assert event_dict["message"] == "Margin changed"
        assert "before_data" in event_dict
        assert "after_data" in event_dict
        assert "timestamp" in event_dict

    def test_audit_event_from_dict(self):
        """Test audit event deserialization"""
        event_data = {
            "event_type": "price_calculation",
            "severity": "info",
            "message": "Test event",
            "user_id": "user123",
            "session_id": "session456",
            "component": "test_component",
            "operation": "test_operation",
            "before_data": '{"old": "value"}',
            "after_data": '{"new": "value"}',
            "context_data": '{"context": "data"}',
            "timestamp": "2024-01-01T12:00:00",
            "event_id": "test_event_123",
            "correlation_id": "corr_123",
            "duration_ms": 100.0,
            "memory_usage_mb": 50.0
        }

        event = AuditEvent.from_dict(event_data)

        assert event.event_type == AuditEventType.PRICE_CALCULATION
        assert event.severity == AuditSeverity.INFO
        assert event.message == "Test event"
        assert event.user_id == "user123"
        assert event.before_data["old"] == "value"
        assert event.after_data["new"] == "value"
        assert event.context_data["context"] == "data"


class TestPricingAuditLogger:
    """Test PricingAuditLogger class"""

    def setup_method(self):
        """Setup test environment"""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"
        self.audit_logger = PricingAuditLogger(str(self.db_path))

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_database_initialization(self):
        """Test database initialization"""
        assert self.db_path.exists()

        # Check table structure
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert "audit_events" in tables

            # Check indexes
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            assert any("idx_event_type" in idx for idx in indexes)

    def test_log_event(self):
        """Test logging audit events"""
        event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Test calculation event",
            user_id="user123",
            context_data={"component_count": 5}
        )

        success = self.audit_logger.log_event(event)

        assert success
        assert event.event_id is not None

        # Verify event was stored
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM audit_events")
            count = cursor.fetchone()[0]
            assert count == 1

            cursor = conn.execute(
                "SELECT * FROM audit_events WHERE event_id = ?", (event.event_id,))
            row = cursor.fetchone()
            assert row is not None

    def test_query_events(self):
        """Test querying audit events"""
        # Log multiple events
        events = [
            AuditEvent(
                event_type=AuditEventType.PRICE_CALCULATION,
                severity=AuditSeverity.INFO,
                message="Calculation 1",
                user_id="user1"
            ),
            AuditEvent(
                event_type=AuditEventType.MARGIN_CHANGE,
                severity=AuditSeverity.WARNING,
                message="Margin change 1",
                user_id="user2"
            ),
            AuditEvent(
                event_type=AuditEventType.CALCULATION_ERROR,
                severity=AuditSeverity.ERROR,
                message="Error 1",
                user_id="user1"
            )
        ]

        for event in events:
            self.audit_logger.log_event(event)

        # Query all events
        query = AuditQuery()
        results = self.audit_logger.query_events(query)
        assert len(results) == 3

        # Query by event type
        query = AuditQuery(event_types=[AuditEventType.PRICE_CALCULATION])
        results = self.audit_logger.query_events(query)
        assert len(results) == 1
        assert results[0].event_type == AuditEventType.PRICE_CALCULATION

        # Query by severity
        query = AuditQuery(severities=[AuditSeverity.ERROR])
        results = self.audit_logger.query_events(query)
        assert len(results) == 1
        assert results[0].severity == AuditSeverity.ERROR

        # Query by user
        query = AuditQuery(user_id="user1")
        results = self.audit_logger.query_events(query)
        assert len(results) == 2
        assert all(r.user_id == "user1" for r in results)

    def test_query_events_with_time_range(self):
        """Test querying events with time range"""
        # Log event in the past
        past_event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Past event"
        )
        past_event.timestamp = datetime.now() - timedelta(hours=2)
        self.audit_logger.log_event(past_event)

        # Log current event
        current_event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Current event"
        )
        self.audit_logger.log_event(current_event)

        # Query events from last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        query = AuditQuery(start_time=one_hour_ago)
        results = self.audit_logger.query_events(query)

        assert len(results) == 1
        assert results[0].message == "Current event"

    def test_get_event_statistics(self):
        """Test getting event statistics"""
        # Log various events
        events = [
            AuditEvent(
                AuditEventType.PRICE_CALCULATION,
                AuditSeverity.INFO,
                "Calc 1",
                duration_ms=100),
            AuditEvent(
                AuditEventType.PRICE_CALCULATION,
                AuditSeverity.INFO,
                "Calc 2",
                duration_ms=200),
            AuditEvent(
                AuditEventType.CALCULATION_ERROR,
                AuditSeverity.ERROR,
                "Error 1"),
            AuditEvent(
                AuditEventType.MARGIN_CHANGE,
                AuditSeverity.WARNING,
                "Margin 1")]

        for event in events:
            self.audit_logger.log_event(event)

        stats = self.audit_logger.get_event_statistics(hours=24)

        assert stats["total_events"] == 4
        assert stats["events_by_type"]["price_calculation"] == 2
        assert stats["events_by_type"]["calculation_error"] == 1
        assert stats["events_by_severity"]["info"] == 2
        assert stats["events_by_severity"]["error"] == 1
        assert stats["error_count"] == 1
        assert stats["error_rate_percent"] == 25.0
        assert stats["average_duration_ms"] == 150.0  # (100 + 200) / 2

    def test_event_listeners(self):
        """Test event listeners"""
        received_events = []

        def test_listener(event):
            received_events.append(event)

        # Add listener
        self.audit_logger.add_event_listener(test_listener)

        # Log event
        event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Test event"
        )
        self.audit_logger.log_event(event)

        # Check listener was called
        assert len(received_events) == 1
        assert received_events[0].message == "Test event"

        # Remove listener
        self.audit_logger.remove_event_listener(test_listener)

        # Log another event
        self.audit_logger.log_event(AuditEvent(
            event_type=AuditEventType.MARGIN_CHANGE,
            severity=AuditSeverity.INFO,
            message="Another event"
        ))

        # Listener should not be called
        assert len(received_events) == 1


class TestPricingCalculationLogger:
    """Test PricingCalculationLogger class"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"
        self.audit_logger = PricingAuditLogger(str(self.db_path))
        self.calc_logger = PricingCalculationLogger(self.audit_logger)

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_calculation_start(self):
        """Test logging calculation start"""
        calculation_data = {
            "components": [{"product_id": 123, "quantity": 5}],
            "modifications": {"discount_percent": 10.0},
            "system_type": "pv"
        }

        event_id = self.calc_logger.log_calculation_start(
            calculation_data,
            user_id="user123",
            session_id="session456"
        )

        assert event_id is not None

        # Verify event was logged
        query = AuditQuery(event_types=[AuditEventType.PRICE_CALCULATION])
        events = self.audit_logger.query_events(query)

        assert len(events) == 1
        assert events[0].message == "Pricing calculation started"
        assert events[0].user_id == "user123"
        assert events[0].context_data["component_count"] == 1
        assert events[0].context_data["has_modifications"]
        assert events[0].context_data["system_type"] == "pv"

    def test_log_calculation_complete(self):
        """Test logging calculation completion"""
        calculation_result = {
            "final_price_net": 1000.0,
            "final_price_gross": 1190.0,
            "total_discounts": 100.0,
            "total_surcharges": 50.0
        }

        self.calc_logger.log_calculation_complete(
            calculation_result,
            duration_ms=250.5,
            user_id="user123",
            correlation_id="calc_123"
        )

        # Verify event was logged
        query = AuditQuery(event_types=[AuditEventType.PRICE_CALCULATION])
        events = self.audit_logger.query_events(query)

        assert len(events) == 1
        assert events[0].message == "Pricing calculation completed"
        assert events[0].duration_ms == 250.5
        assert events[0].correlation_id == "calc_123"
        assert events[0].after_data["final_price_net"] == 1000.0

    def test_log_calculation_error(self):
        """Test logging calculation error"""
        error = CalculationError(
            "Test calculation error",
            calculation_step="validation")
        calculation_data = {
            "components": [{"product_id": 123, "quantity": 5}]
        }

        self.calc_logger.log_calculation_error(
            error,
            calculation_data,
            user_id="user123",
            correlation_id="calc_error_123"
        )

        # Verify event was logged
        query = AuditQuery(event_types=[AuditEventType.CALCULATION_ERROR])
        events = self.audit_logger.query_events(query)

        assert len(events) == 1
        assert "Test calculation error" in events[0].message
        assert events[0].severity == AuditSeverity.ERROR
        assert events[0].correlation_id == "calc_error_123"
        assert events[0].context_data["error_type"] == "CalculationError"

    def test_log_margin_change(self):
        """Test logging margin change"""
        old_margin = {"margin_type": "percentage", "margin_value": 20.0}
        new_margin = {"margin_type": "percentage", "margin_value": 25.0}

        self.calc_logger.log_margin_change(
            product_id=123,
            old_margin=old_margin,
            new_margin=new_margin,
            user_id="admin123"
        )

        # Verify event was logged
        query = AuditQuery(event_types=[AuditEventType.MARGIN_CHANGE])
        events = self.audit_logger.query_events(query)

        assert len(events) == 1
        assert "Margin changed for product 123" in events[0].message
        assert events[0].before_data == old_margin
        assert events[0].after_data == new_margin
        assert events[0].context_data["product_id"] == 123

    def test_log_price_update(self):
        """Test logging price update"""
        self.calc_logger.log_price_update(
            product_id=456,
            old_price=200.0,
            new_price=250.0,
            user_id="admin123"
        )

        # Verify event was logged
        query = AuditQuery(event_types=[AuditEventType.PRODUCT_PRICE_UPDATE])
        events = self.audit_logger.query_events(query)

        assert len(events) == 1
        assert "Price updated for product 456: 200.0€ → 250.0€" in events[0].message
        assert events[0].before_data["price"] == 200.0
        assert events[0].after_data["price"] == 250.0
        assert events[0].context_data["price_change"] == 50.0


class TestPricingMonitor:
    """Test PricingMonitor class"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"
        self.audit_logger = PricingAuditLogger(str(self.db_path))
        self.monitor = PricingMonitor(self.audit_logger)

        # Capture alerts
        self.alerts = []

        def capture_alert(alert_type, alert_data):
            self.alerts.append((alert_type, alert_data))

        self.monitor.add_alert_handler(capture_alert)

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_error_rate_alert(self):
        """Test error rate alerting"""
        # Generate multiple error events to trigger alert
        for i in range(12):  # More than threshold of 10
            event = AuditEvent(
                event_type=AuditEventType.CALCULATION_ERROR,
                severity=AuditSeverity.ERROR,
                message=f"Error {i}"
            )
            self.audit_logger.log_event(event)

        # Check that alert was triggered
        assert len(self.alerts) >= 1
        alert_type, alert_data = self.alerts[-1]
        assert "High Error Rate Alert" in alert_type
        assert alert_data["errors_last_hour"] > 10

    def test_high_duration_alert(self):
        """Test high duration alerting"""
        event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Slow calculation",
            duration_ms=6000.0  # More than 5000ms threshold
        )

        self.audit_logger.log_event(event)

        # Check that alert was triggered
        assert len(self.alerts) >= 1
        alert_type, alert_data = self.alerts[-1]
        assert "High Duration Alert" in alert_type
        assert alert_data["duration_ms"] == 6000.0

    def test_calculation_failure_alert(self):
        """Test calculation failure alerting"""
        # Generate multiple calculation failures
        for i in range(7):  # More than threshold of 5
            event = AuditEvent(
                event_type=AuditEventType.CALCULATION_ERROR,
                severity=AuditSeverity.ERROR,
                message=f"Calculation failure {i}"
            )
            self.audit_logger.log_event(event)

        # Check that alert was triggered
        assert len(self.alerts) >= 1
        alert_found = False
        for alert_type, alert_data in self.alerts:
            if "High Calculation Failure Rate Alert" in alert_type:
                assert alert_data["failures_last_hour"] > 5
                alert_found = True
                break
        assert alert_found

    def test_get_health_status(self):
        """Test health status calculation"""
        # Log some normal events
        for i in range(5):
            event = AuditEvent(
                event_type=AuditEventType.PRICE_CALCULATION,
                severity=AuditSeverity.INFO,
                message=f"Normal calculation {i}",
                duration_ms=100.0
            )
            self.audit_logger.log_event(event)

        health = self.monitor.get_health_status()

        assert health["status"] == "healthy"
        assert health["health_score"] >= 90
        assert "statistics" in health
        assert "timestamp" in health

    def test_degraded_health_status(self):
        """Test degraded health status"""
        # Log many errors to degrade health
        for i in range(10):
            event = AuditEvent(
                event_type=AuditEventType.CALCULATION_ERROR,
                severity=AuditSeverity.ERROR,
                message=f"Error {i}"
            )
            self.audit_logger.log_event(event)

        # Log some slow calculations
        for i in range(3):
            event = AuditEvent(
                event_type=AuditEventType.PRICE_CALCULATION,
                severity=AuditSeverity.INFO,
                message=f"Slow calculation {i}",
                duration_ms=8000.0  # Very slow
            )
            self.audit_logger.log_event(event)

        health = self.monitor.get_health_status()

        assert health["status"] in ["warning", "degraded", "critical"]
        assert health["health_score"] < 90

    def test_alert_handlers(self):
        """Test alert handler management"""
        alerts_received = []

        def test_handler(alert_type, alert_data):
            alerts_received.append((alert_type, alert_data))

        # Add handler
        self.monitor.add_alert_handler(test_handler)

        # Trigger alert
        event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Test",
            duration_ms=6000.0
        )
        self.audit_logger.log_event(event)

        # Check handler was called
        assert len(alerts_received) >= 1

        # Remove handler
        self.monitor.remove_alert_handler(test_handler)

        # Clear previous alerts
        alerts_received.clear()

        # Trigger another alert
        event = AuditEvent(
            event_type=AuditEventType.PRICE_CALCULATION,
            severity=AuditSeverity.INFO,
            message="Test 2",
            duration_ms=7000.0
        )
        self.audit_logger.log_event(event)

        # Handler should not be called
        assert len(alerts_received) == 0


class TestGlobalInstances:
    """Test global instance functions"""

    def test_get_audit_logger(self):
        """Test global audit logger instance"""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()

        assert logger1 is logger2  # Should be the same instance
        assert isinstance(logger1, PricingAuditLogger)

    def test_get_calculation_logger(self):
        """Test global calculation logger instance"""
        logger1 = get_calculation_logger()
        logger2 = get_calculation_logger()

        assert logger1 is logger2  # Should be the same instance
        assert isinstance(logger1, PricingCalculationLogger)

    def test_get_pricing_monitor(self):
        """Test global pricing monitor instance"""
        monitor1 = get_pricing_monitor()
        monitor2 = get_pricing_monitor()

        assert monitor1 is monitor2  # Should be the same instance
        assert isinstance(monitor1, PricingMonitor)


class TestConvenienceFunctions:
    """Test convenience functions"""

    def setup_method(self):
        """Setup test environment"""
        # Mock the global instances to avoid database creation
        self.mock_audit_logger = Mock()
        self.mock_calc_logger = Mock()

        with patch('pricing.pricing_audit.get_calculation_logger', return_value=self.mock_calc_logger):
            pass

    @patch('pricing.pricing_audit.get_calculation_logger')
    def test_audit_price_calculation(self, mock_get_logger):
        """Test audit_price_calculation convenience function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        calculation_data = {"components": [{"product_id": 123, "quantity": 5}]}
        result = {"final_price_net": 1000.0}

        audit_price_calculation(
            calculation_data=calculation_data,
            result=result,
            duration_ms=150.0,
            user_id="user123",
            session_id="session456"
        )

        # Verify logger methods were called
        mock_logger.log_calculation_start.assert_called_once()
        mock_logger.log_calculation_complete.assert_called_once()

        # Check arguments
        start_call = mock_logger.log_calculation_start.call_args
        assert start_call[0][0] == calculation_data
        assert start_call[0][1] == "user123"
        assert start_call[0][2] == "session456"

        complete_call = mock_logger.log_calculation_complete.call_args
        assert complete_call[0][0] == result
        assert complete_call[0][1] == 150.0

    @patch('pricing.pricing_audit.get_calculation_logger')
    def test_audit_pricing_error(self, mock_get_logger):
        """Test audit_pricing_error convenience function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        error = ValidationError("Test error")
        context = {"test": "context"}

        audit_pricing_error(
            error=error,
            context=context,
            user_id="user123",
            session_id="session456"
        )

        # Verify logger method was called
        mock_logger.log_calculation_error.assert_called_once_with(
            error, context, "user123", "session456"
        )


class TestAuditQuery:
    """Test AuditQuery class"""

    def test_audit_query_defaults(self):
        """Test AuditQuery default values"""
        query = AuditQuery()

        assert query.event_types is None
        assert query.severities is None
        assert query.user_id is None
        assert query.limit == 1000
        assert query.offset == 0
        assert query.order_by == "timestamp"
        assert query.order_desc

    def test_audit_query_custom_values(self):
        """Test AuditQuery with custom values"""
        query = AuditQuery(
            event_types=[AuditEventType.PRICE_CALCULATION],
            severities=[AuditSeverity.ERROR],
            user_id="user123",
            limit=50,
            offset=10,
            order_by="severity",
            order_desc=False
        )

        assert query.event_types == [AuditEventType.PRICE_CALCULATION]
        assert query.severities == [AuditSeverity.ERROR]
        assert query.user_id == "user123"
        assert query.limit == 50
        assert query.offset == 10
        assert query.order_by == "severity"
        assert query.order_desc == False


class TestIntegration:
    """Integration tests for audit system"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"

        # Create fresh instances for integration testing
        self.audit_logger = PricingAuditLogger(str(self.db_path))
        self.calc_logger = PricingCalculationLogger(self.audit_logger)
        self.monitor = PricingMonitor(self.audit_logger)

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_calculation_audit_workflow(self):
        """Test complete calculation audit workflow"""
        # Simulate a complete pricing calculation with audit
        calculation_data = {
            "components": [
                {"product_id": 123, "quantity": 10},
                {"product_id": 456, "quantity": 1}
            ],
            "modifications": {"discount_percent": 5.0},
            "system_type": "pv"
        }

        # Start calculation
        correlation_id = "test_calc_123"
        event_id = self.calc_logger.log_calculation_start(
            calculation_data,
            user_id="user123",
            session_id="session456",
            correlation_id=correlation_id
        )

        # Simulate calculation completion
        result = {
            "final_price_net": 2000.0,
            "final_price_gross": 2380.0,
            "total_discounts": 100.0,
            "total_surcharges": 0.0
        }

        self.calc_logger.log_calculation_complete(
            result,
            duration_ms=250.0,
            user_id="user123",
            session_id="session456",
            correlation_id=correlation_id
        )

        # Verify events were logged
        query = AuditQuery(correlation_id=correlation_id)
        events = self.audit_logger.query_events(query)

        assert len(events) == 2
        # Most recent first
        assert events[0].message == "Pricing calculation completed"
        assert events[1].message == "Pricing calculation started"
        assert all(e.correlation_id == correlation_id for e in events)
        assert all(e.user_id == "user123" for e in events)

    def test_error_monitoring_integration(self):
        """Test error monitoring integration"""
        alerts_received = []

        def capture_alerts(alert_type, alert_data):
            alerts_received.append((alert_type, alert_data))

        self.monitor.add_alert_handler(capture_alerts)

        # Generate calculation errors
        for i in range(8):
            error = CalculationError(f"Test error {i}")
            self.calc_logger.log_calculation_error(
                error,
                {"components": []},
                user_id="user123"
            )

        # Check that alerts were generated
        assert len(alerts_received) >= 1

        # Verify health status reflects the errors
        health = self.monitor.get_health_status()
        assert health["status"] in ["warning", "degraded", "critical"]
        assert health["statistics"]["error_count"] >= 8


if __name__ == "__main__":
    pytest.main([__file__])
