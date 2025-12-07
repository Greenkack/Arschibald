"""
Controlling System Notification Manager

Manages notifications and warnings for quota thresholds.
Provides threshold configuration and notification generation.

Requirements: 21.1, 21.2, 21.4
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class NotificationType(Enum):
    """Types of notifications"""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ThresholdType(Enum):
    """Types of threshold checks"""
    ABOVE = "above"  # Trigger when quota is above threshold
    BELOW = "below"  # Trigger when quota is below threshold


@dataclass
class NotificationThreshold:
    """
    Configuration for a notification threshold.
    
    Requirements: 21.4
    """
    quota_name: str
    threshold_value: float  # Percentage value (0-100)
    threshold_type: ThresholdType
    notification_type: NotificationType
    message_template: str
    
    def check(self, quota_value: float) -> bool:
        """Check if threshold is triggered"""
        if self.threshold_type == ThresholdType.ABOVE:
            return quota_value > self.threshold_value
        else:  # BELOW
            return quota_value < self.threshold_value


@dataclass
class Notification:
    """
    A notification message.
    
    Requirements: 21.1, 21.2, 21.3
    """
    notification_type: NotificationType
    title: str
    message: str
    quota_name: str
    quota_value: float
    threshold_value: float
    employee_name: Optional[str] = None


class NotificationManager:
    """
    Manages notification thresholds and generates notifications.
    
    Requirements: 21.1, 21.2, 21.4
    """
    
    def __init__(self):
        """Initialize with default thresholds"""
        self.thresholds: List[NotificationThreshold] = []
        self._load_default_thresholds()
    
    def _load_default_thresholds(self):
        """Load default notification thresholds"""
        # Default thresholds for common quotas
        default_thresholds = [
            # Success notifications (above threshold)
            NotificationThreshold(
                quota_name="Abschlussquote",
                threshold_value=30.0,
                threshold_type=ThresholdType.ABOVE,
                notification_type=NotificationType.SUCCESS,
                message_template=(
                    "Hervorragende Leistung! Die Abschlussquote von "
                    "{quota_value:.1f}% liegt über dem Ziel von "
                    "{threshold_value:.1f}%."
                )
            ),
            NotificationThreshold(
                quota_name="Terminvereinbarungsquote",
                threshold_value=20.0,
                threshold_type=ThresholdType.ABOVE,
                notification_type=NotificationType.SUCCESS,
                message_template=(
                    "Sehr gut! Die Terminvereinbarungsquote von "
                    "{quota_value:.1f}% übertrifft das Ziel von "
                    "{threshold_value:.1f}%."
                )
            ),
            NotificationThreshold(
                quota_name="QC bestanden Quote",
                threshold_value=90.0,
                threshold_type=ThresholdType.ABOVE,
                notification_type=NotificationType.SUCCESS,
                message_template=(
                    "Exzellente Qualität! {quota_value:.1f}% der "
                    "Verkäufe haben die Qualitätskontrolle bestanden."
                )
            ),
            
            # Warning notifications (below threshold)
            NotificationThreshold(
                quota_name="Abschlussquote",
                threshold_value=15.0,
                threshold_type=ThresholdType.BELOW,
                notification_type=NotificationType.WARNING,
                message_template=(
                    "Achtung: Die Abschlussquote von {quota_value:.1f}% "
                    "liegt unter dem Mindestziel von {threshold_value:.1f}%."
                )
            ),
            NotificationThreshold(
                quota_name="Terminvereinbarungsquote",
                threshold_value=10.0,
                threshold_type=ThresholdType.BELOW,
                notification_type=NotificationType.WARNING,
                message_template=(
                    "Achtung: Die Terminvereinbarungsquote von "
                    "{quota_value:.1f}% liegt unter dem Mindestziel von "
                    "{threshold_value:.1f}%."
                )
            ),
            NotificationThreshold(
                quota_name="Termine-Anfahrquote",
                threshold_value=70.0,
                threshold_type=ThresholdType.BELOW,
                notification_type=NotificationType.WARNING,
                message_template=(
                    "Achtung: Nur {quota_value:.1f}% der terminierten "
                    "Kunden wurden angefahren. Ziel: {threshold_value:.1f}%."
                )
            ),
            
            # Info notifications for high negative quotas
            NotificationThreshold(
                quota_name="Nicht interessierte Kunden Quote",
                threshold_value=30.0,
                threshold_type=ThresholdType.ABOVE,
                notification_type=NotificationType.INFO,
                message_template=(
                    "Hinweis: {quota_value:.1f}% der Termine führten zu "
                    "Desinteresse. Überprüfen Sie die Zielgruppenansprache."
                )
            ),
            NotificationThreshold(
                quota_name="Zu teuer Quote",
                threshold_value=25.0,
                threshold_type=ThresholdType.ABOVE,
                notification_type=NotificationType.INFO,
                message_template=(
                    "Hinweis: {quota_value:.1f}% der Kunden fanden das "
                    "Angebot zu teuer. Prüfen Sie die Preisgestaltung."
                )
            ),
        ]
        
        self.thresholds = default_thresholds
    
    def add_threshold(
        self,
        quota_name: str,
        threshold_value: float,
        threshold_type: ThresholdType,
        notification_type: NotificationType,
        message_template: str
    ) -> NotificationThreshold:
        """
        Add a custom notification threshold.
        
        Requirements: 21.4
        
        Args:
            quota_name: Name of the quota to monitor
            threshold_value: Threshold percentage (0-100)
            threshold_type: Type of threshold (ABOVE or BELOW)
            notification_type: Type of notification to generate
            message_template: Message template with {quota_value} and
                            {threshold_value} placeholders
        
        Returns:
            The created NotificationThreshold
        """
        threshold = NotificationThreshold(
            quota_name=quota_name,
            threshold_value=threshold_value,
            threshold_type=threshold_type,
            notification_type=notification_type,
            message_template=message_template
        )
        self.thresholds.append(threshold)
        return threshold
    
    def remove_threshold(
        self,
        quota_name: str,
        threshold_value: float,
        threshold_type: ThresholdType
    ) -> bool:
        """
        Remove a notification threshold.
        
        Args:
            quota_name: Name of the quota
            threshold_value: Threshold percentage
            threshold_type: Type of threshold
        
        Returns:
            True if threshold was removed, False if not found
        """
        for i, threshold in enumerate(self.thresholds):
            if (threshold.quota_name == quota_name and
                threshold.threshold_value == threshold_value and
                threshold.threshold_type == threshold_type):
                self.thresholds.pop(i)
                return True
        return False
    
    def get_thresholds(
        self,
        quota_name: Optional[str] = None
    ) -> List[NotificationThreshold]:
        """
        Get all thresholds, optionally filtered by quota name.
        
        Args:
            quota_name: Optional quota name to filter by
        
        Returns:
            List of NotificationThreshold objects
        """
        if quota_name:
            return [
                t for t in self.thresholds
                if t.quota_name == quota_name
            ]
        return self.thresholds.copy()
    
    def check_quotas(
        self,
        quotas: Dict[str, float],
        employee_name: Optional[str] = None
    ) -> List[Notification]:
        """
        Check quotas against thresholds and generate notifications.
        
        Requirements: 21.1, 21.2
        
        Args:
            quotas: Dictionary of quota names to values (percentages)
            employee_name: Optional employee name for personalized messages
        
        Returns:
            List of Notification objects for triggered thresholds
        """
        notifications = []
        
        for quota_name, quota_value in quotas.items():
            # Find all thresholds for this quota
            relevant_thresholds = [
                t for t in self.thresholds
                if t.quota_name == quota_name
            ]
            
            for threshold in relevant_thresholds:
                if threshold.check(quota_value):
                    # Generate notification message
                    message = threshold.message_template.format(
                        quota_value=quota_value,
                        threshold_value=threshold.threshold_value
                    )
                    
                    # Create title based on notification type
                    if threshold.notification_type == NotificationType.SUCCESS:
                        title = "Ziel erreicht!"
                    elif (threshold.notification_type ==
                          NotificationType.WARNING):
                        title = "Warnung"
                    elif threshold.notification_type == NotificationType.INFO:
                        title = "Hinweis"
                    else:
                        title = "Benachrichtigung"
                    
                    notification = Notification(
                        notification_type=threshold.notification_type,
                        title=title,
                        message=message,
                        quota_name=quota_name,
                        quota_value=quota_value,
                        threshold_value=threshold.threshold_value,
                        employee_name=employee_name
                    )
                    notifications.append(notification)
        
        return notifications
    
    def format_notification_for_streamlit(
        self,
        notification: Notification
    ) -> Tuple[str, str, str]:
        """
        Format a notification for Streamlit display.
        
        Requirements: 21.5
        
        Args:
            notification: Notification object to format
        
        Returns:
            Tuple of (streamlit_type, title, message) where streamlit_type
            is one of: 'success', 'info', 'warning', 'error'
        """
        # Map notification type to Streamlit type
        streamlit_type = notification.notification_type.value
        
        # Add employee name to title if available
        title = notification.title
        if notification.employee_name:
            title = f"{title} - {notification.employee_name}"
        
        return (streamlit_type, title, notification.message)
    
    def get_notification_summary(
        self,
        notifications: List[Notification]
    ) -> Dict[str, int]:
        """
        Get a summary count of notifications by type.
        
        Args:
            notifications: List of Notification objects
        
        Returns:
            Dictionary with counts by notification type
        """
        summary = {
            "success": 0,
            "info": 0,
            "warning": 0,
            "error": 0
        }
        
        for notification in notifications:
            summary[notification.notification_type.value] += 1
        
        return summary
