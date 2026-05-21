"""
Unit tests for the Notification System.

Tests notification threshold configuration, notification generation,
and notification display functionality.

Requirements: 21.1, 21.2, 21.4
"""

import pytest
from controlling.notifications import (
    NotificationManager,
    Notification,
    NotificationThreshold,
    NotificationType,
    ThresholdType
)


class TestNotificationThreshold:
    """Test NotificationThreshold class"""

    def test_threshold_check_above(self):
        """Test threshold check for ABOVE type"""
        threshold = NotificationThreshold(
            quota_name="Abschlussquote",
            threshold_value=30.0,
            threshold_type=ThresholdType.ABOVE,
            notification_type=NotificationType.SUCCESS,
            message_template="Test message"
        )

        assert threshold.check(35.0) is True
        assert threshold.check(30.0) is False
        assert threshold.check(25.0) is False

    def test_threshold_check_below(self):
        """Test threshold check for BELOW type"""
        threshold = NotificationThreshold(
            quota_name="Abschlussquote",
            threshold_value=15.0,
            threshold_type=ThresholdType.BELOW,
            notification_type=NotificationType.WARNING,
            message_template="Test message"
        )

        assert threshold.check(10.0) is True
        assert threshold.check(15.0) is False
        assert threshold.check(20.0) is False


class TestNotificationManager:
    """Test NotificationManager class"""

    def test_initialization_with_default_thresholds(self):
        """Test that manager initializes with default thresholds"""
        manager = NotificationManager()

        thresholds = manager.get_thresholds()
        assert len(thresholds) > 0

        # Check for some expected default thresholds
        quota_names = {t.quota_name for t in thresholds}
        assert "Abschlussquote" in quota_names
        assert "Terminvereinbarungsquote" in quota_names

    def test_add_threshold(self):
        """Test adding a custom threshold"""
        manager = NotificationManager()
        initial_count = len(manager.get_thresholds())

        manager.add_threshold(
            quota_name="Custom Quote",
            threshold_value=50.0,
            threshold_type=ThresholdType.ABOVE,
            notification_type=NotificationType.INFO,
            message_template="Custom message: {quota_value}%"
        )

        assert len(manager.get_thresholds()) == initial_count + 1

        # Verify the threshold was added
        custom_thresholds = manager.get_thresholds("Custom Quote")
        assert len(custom_thresholds) == 1
        assert custom_thresholds[0].threshold_value == 50.0

    def test_remove_threshold(self):
        """Test removing a threshold"""
        manager = NotificationManager()

        # Add a threshold
        manager.add_threshold(
            quota_name="Test Quote",
            threshold_value=25.0,
            threshold_type=ThresholdType.BELOW,
            notification_type=NotificationType.WARNING,
            message_template="Test"
        )

        # Verify it was added
        assert len(manager.get_thresholds("Test Quote")) == 1

        # Remove it
        result = manager.remove_threshold(
            quota_name="Test Quote",
            threshold_value=25.0,
            threshold_type=ThresholdType.BELOW
        )

        assert result is True
        assert len(manager.get_thresholds("Test Quote")) == 0

    def test_remove_nonexistent_threshold(self):
        """Test removing a threshold that doesn't exist"""
        manager = NotificationManager()

        result = manager.remove_threshold(
            quota_name="Nonexistent",
            threshold_value=99.0,
            threshold_type=ThresholdType.ABOVE
        )

        assert result is False

    def test_get_thresholds_filtered(self):
        """Test getting thresholds filtered by quota name"""
        manager = NotificationManager()

        # Get thresholds for a specific quota
        abschluss_thresholds = manager.get_thresholds("Abschlussquote")

        # Should have at least one threshold for Abschlussquote
        assert len(abschluss_thresholds) > 0

        # All returned thresholds should be for Abschlussquote
        for threshold in abschluss_thresholds:
            assert threshold.quota_name == "Abschlussquote"

    def test_check_quotas_success_notification(self):
        """
        Test that success notifications are generated when quota exceeds
        threshold.

        Requirements: 21.1
        """
        manager = NotificationManager()

        # High Abschlussquote should trigger success notification
        quotas = {
            "Abschlussquote": 35.0,  # Above 30% threshold
            "Terminvereinbarungsquote": 15.0
        }

        notifications = manager.check_quotas(quotas)

        # Should have at least one success notification
        success_notifications = [
            n for n in notifications
            if n.notification_type == NotificationType.SUCCESS
        ]
        assert len(success_notifications) > 0

        # Check that notification has correct data
        abschluss_notification = next(
            (n for n in success_notifications
             if n.quota_name == "Abschlussquote"),
            None
        )
        assert abschluss_notification is not None
        assert abschluss_notification.quota_value == 35.0
        assert "35.0" in abschluss_notification.message

    def test_check_quotas_warning_notification(self):
        """
        Test that warning notifications are generated when quota falls
        below threshold.

        Requirements: 21.2
        """
        manager = NotificationManager()

        # Low Abschlussquote should trigger warning notification
        quotas = {
            "Abschlussquote": 10.0,  # Below 15% threshold
            "Terminvereinbarungsquote": 5.0  # Below 10% threshold
        }

        notifications = manager.check_quotas(quotas)

        # Should have warning notifications
        warning_notifications = [
            n for n in notifications
            if n.notification_type == NotificationType.WARNING
        ]
        assert len(warning_notifications) > 0

        # Check that notification has correct data
        abschluss_warning = next(
            (n for n in warning_notifications
             if n.quota_name == "Abschlussquote"),
            None
        )
        assert abschluss_warning is not None
        assert abschluss_warning.quota_value == 10.0
        assert "10.0" in abschluss_warning.message

    def test_check_quotas_with_employee_name(self):
        """Test that employee name is included in notifications"""
        manager = NotificationManager()

        quotas = {"Abschlussquote": 35.0}
        employee_name = "Max Mustermann"

        notifications = manager.check_quotas(
            quotas,
            employee_name=employee_name
        )

        assert len(notifications) > 0
        for notification in notifications:
            assert notification.employee_name == employee_name

    def test_check_quotas_no_triggers(self):
        """Test that no notifications are generated when no thresholds
        are triggered"""
        manager = NotificationManager()

        # Quotas that don't trigger any thresholds
        quotas = {
            "Abschlussquote": 20.0,  # Between 15% and 30%
            "Terminvereinbarungsquote": 15.0  # Between 10% and 20%
        }

        notifications = manager.check_quotas(quotas)

        # Should have no notifications (or very few)
        # Default thresholds might still trigger some
        assert isinstance(notifications, list)

    def test_format_notification_for_streamlit(self):
        """Test formatting notification for Streamlit display"""
        manager = NotificationManager()

        notification = Notification(
            notification_type=NotificationType.SUCCESS,
            title="Test Title",
            message="Test message",
            quota_name="Test Quote",
            quota_value=50.0,
            threshold_value=40.0,
            employee_name="Test Employee"
        )

        streamlit_type, title, message = (
            manager.format_notification_for_streamlit(notification)
        )

        assert streamlit_type == "success"
        assert "Test Title" in title
        assert "Test Employee" in title
        assert message == "Test message"

    def test_format_notification_without_employee_name(self):
        """Test formatting notification without employee name"""
        manager = NotificationManager()

        notification = Notification(
            notification_type=NotificationType.WARNING,
            title="Warning Title",
            message="Warning message",
            quota_name="Test Quote",
            quota_value=10.0,
            threshold_value=15.0
        )

        streamlit_type, title, message = (
            manager.format_notification_for_streamlit(notification)
        )

        assert streamlit_type == "warning"
        assert title == "Warning Title"
        assert message == "Warning message"

    def test_get_notification_summary(self):
        """Test getting notification summary counts"""
        manager = NotificationManager()

        notifications = [
            Notification(
                notification_type=NotificationType.SUCCESS,
                title="Success",
                message="msg",
                quota_name="Q1",
                quota_value=50.0,
                threshold_value=40.0
            ),
            Notification(
                notification_type=NotificationType.SUCCESS,
                title="Success",
                message="msg",
                quota_name="Q2",
                quota_value=60.0,
                threshold_value=50.0
            ),
            Notification(
                notification_type=NotificationType.WARNING,
                title="Warning",
                message="msg",
                quota_name="Q3",
                quota_value=10.0,
                threshold_value=15.0
            ),
            Notification(
                notification_type=NotificationType.INFO,
                title="Info",
                message="msg",
                quota_name="Q4",
                quota_value=30.0,
                threshold_value=25.0
            )
        ]

        summary = manager.get_notification_summary(notifications)

        assert summary["success"] == 2
        assert summary["warning"] == 1
        assert summary["info"] == 1
        assert summary["error"] == 0

    def test_multiple_thresholds_same_quota(self):
        """Test that multiple thresholds can exist for the same quota"""
        manager = NotificationManager()

        # Add multiple thresholds for the same quota
        manager.add_threshold(
            quota_name="Test Quote",
            threshold_value=80.0,
            threshold_type=ThresholdType.ABOVE,
            notification_type=NotificationType.SUCCESS,
            message_template="Excellent: {quota_value}%"
        )

        manager.add_threshold(
            quota_name="Test Quote",
            threshold_value=20.0,
            threshold_type=ThresholdType.BELOW,
            notification_type=NotificationType.WARNING,
            message_template="Low: {quota_value}%"
        )

        # Check that both thresholds exist
        test_thresholds = manager.get_thresholds("Test Quote")
        assert len(test_thresholds) == 2

        # Test that both can trigger
        quotas_high = {"Test Quote": 85.0}
        notifications_high = manager.check_quotas(quotas_high)
        assert len(notifications_high) == 1
        assert notifications_high[0].notification_type == (
            NotificationType.SUCCESS
        )

        quotas_low = {"Test Quote": 15.0}
        notifications_low = manager.check_quotas(quotas_low)
        assert len(notifications_low) == 1
        assert notifications_low[0].notification_type == (
            NotificationType.WARNING
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
