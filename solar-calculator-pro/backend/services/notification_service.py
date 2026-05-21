"""
Notification Service

This module provides the core notification service for creating, managing,
and delivering notifications across multiple channels.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging

from backend.models.notification_models import (
    Notification,
    NotificationAction,
    NotificationPreference,
    NotificationTemplate,
    NotificationType,
    NotificationChannel,
    NotificationPriority
)
from backend.models.notification_schemas import (
    NotificationCreate,
    NotificationUpdate,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    BulkNotificationCreate
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== Notification CRUD ====================

    def create_notification(
        self,
        notification_data: NotificationCreate
    ) -> Notification:
        """Create a new notification"""
        try:
            # Convert channels list to comma-separated string
            channels_str = ",".join([ch.value for ch in notification_data.channels])
            
            # Create notification
            notification = Notification(
                user_id=notification_data.user_id,
                type=notification_data.type,
                priority=notification_data.priority,
                title=notification_data.title,
                message=notification_data.message,
                category=notification_data.category,
                action_url=notification_data.action_url,
                action_label=notification_data.action_label,
                icon=notification_data.icon,
                channels=channels_str,
                expires_at=notification_data.expires_at
            )
            
            self.db.add(notification)
            self.db.flush()
            
            # Add actions if provided
            if notification_data.actions:
                for action_data in notification_data.actions:
                    action = NotificationAction(
                        notification_id=notification.id,
                        action_type=action_data.action_type,
                        label=action_data.label,
                        url=action_data.url
                    )
                    self.db.add(action)
            
            self.db.commit()
            self.db.refresh(notification)
            
            # Trigger delivery
            self._deliver_notification(notification)
            
            logger.info(f"Created notification {notification.id} for user {notification.user_id}")
            return notification
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise

    def get_notification(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """Get a notification by ID"""
        return self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()

    def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False,
        category: Optional[str] = None,
        notification_type: Optional[NotificationType] = None
    ) -> tuple[List[Notification], int]:
        """Get notifications for a user with filtering"""
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_archived == False
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        if category:
            query = query.filter(Notification.category == category)
        
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        # Filter out expired notifications
        query = query.filter(
            or_(
                Notification.expires_at == None,
                Notification.expires_at > datetime.utcnow()
            )
        )
        
        total = query.count()
        notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
        
        return notifications, total

    def update_notification(
        self,
        notification_id: int,
        user_id: int,
        update_data: NotificationUpdate
    ) -> Optional[Notification]:
        """Update a notification"""
        notification = self.get_notification(notification_id, user_id)
        if not notification:
            return None
        
        try:
            if update_data.is_read is not None:
                notification.is_read = update_data.is_read
                if update_data.is_read and not notification.read_at:
                    notification.read_at = datetime.utcnow()
            
            if update_data.is_archived is not None:
                notification.is_archived = update_data.is_archived
            
            self.db.commit()
            self.db.refresh(notification)
            
            logger.info(f"Updated notification {notification_id}")
            return notification
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating notification: {str(e)}")
            raise

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        notification = self.get_notification(notification_id, user_id)
        if not notification:
            return False
        
        try:
            self.db.delete(notification)
            self.db.commit()
            logger.info(f"Deleted notification {notification_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting notification: {str(e)}")
            raise

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        try:
            count = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            ).update({
                "is_read": True,
                "read_at": datetime.utcnow()
            })
            self.db.commit()
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking notifications as read: {str(e)}")
            raise

    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        return self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_archived == False,
                or_(
                    Notification.expires_at == None,
                    Notification.expires_at > datetime.utcnow()
                )
            )
        ).count()

    # ==================== Bulk Operations ====================

    def create_bulk_notifications(
        self,
        bulk_data: BulkNotificationCreate
    ) -> List[Notification]:
        """Create notifications for multiple users"""
        notifications = []
        
        try:
            for user_id in bulk_data.user_ids:
                notification_data = NotificationCreate(
                    user_id=user_id,
                    **bulk_data.notification.dict(),
                    channels=bulk_data.channels
                )
                notification = self.create_notification(notification_data)
                notifications.append(notification)
            
            logger.info(f"Created {len(notifications)} bulk notifications")
            return notifications
            
        except Exception as e:
            logger.error(f"Error creating bulk notifications: {str(e)}")
            raise

    # ==================== Notification Preferences ====================

    def get_user_preferences(self, user_id: int) -> Optional[NotificationPreference]:
        """Get notification preferences for a user"""
        return self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()

    def create_or_update_preferences(
        self,
        user_id: int,
        preferences_data: NotificationPreferenceUpdate
    ) -> NotificationPreference:
        """Create or update notification preferences"""
        preferences = self.get_user_preferences(user_id)
        
        try:
            if preferences:
                # Update existing
                for key, value in preferences_data.dict(exclude_unset=True).items():
                    if key == "enabled_types" and value is not None:
                        setattr(preferences, key, json.dumps([t.value for t in value]))
                    else:
                        setattr(preferences, key, value)
                preferences.updated_at = datetime.utcnow()
            else:
                # Create new
                enabled_types_json = None
                if preferences_data.enabled_types:
                    enabled_types_json = json.dumps([t.value for t in preferences_data.enabled_types])
                
                preferences = NotificationPreference(
                    user_id=user_id,
                    **preferences_data.dict(exclude={"enabled_types"}),
                    enabled_types=enabled_types_json
                )
                self.db.add(preferences)
            
            self.db.commit()
            self.db.refresh(preferences)
            
            logger.info(f"Updated preferences for user {user_id}")
            return preferences
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating preferences: {str(e)}")
            raise

    # ==================== Notification Templates ====================

    def create_template(self, template_data: NotificationTemplateCreate) -> NotificationTemplate:
        """Create a notification template"""
        try:
            channels_str = ",".join([ch.value for ch in template_data.default_channels])
            
            template = NotificationTemplate(
                **template_data.dict(exclude={"default_channels"}),
                default_channels=channels_str
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
            logger.info(f"Created notification template {template.template_key}")
            return template
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating template: {str(e)}")
            raise

    def get_template(self, template_key: str) -> Optional[NotificationTemplate]:
        """Get a notification template by key"""
        return self.db.query(NotificationTemplate).filter(
            NotificationTemplate.template_key == template_key,
            NotificationTemplate.is_active == True
        ).first()

    def create_from_template(
        self,
        template_key: str,
        user_id: int,
        variables: Dict[str, Any],
        channels: Optional[List[NotificationChannel]] = None
    ) -> Notification:
        """Create a notification from a template"""
        template = self.get_template(template_key)
        if not template:
            raise ValueError(f"Template {template_key} not found")
        
        # Replace variables in title and message
        title = template.title_template
        message = template.message_template
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            title = title.replace(placeholder, str(value))
            message = message.replace(placeholder, str(value))
        
        # Use template channels if not specified
        if not channels:
            channels = [NotificationChannel(ch) for ch in template.default_channels.split(",")]
        
        notification_data = NotificationCreate(
            user_id=user_id,
            type=template.type,
            priority=template.priority,
            title=title,
            message=message,
            category=template.category,
            icon=template.icon,
            channels=channels
        )
        
        return self.create_notification(notification_data)

    # ==================== Delivery Methods ====================

    def _deliver_notification(self, notification: Notification):
        """Deliver notification through configured channels"""
        channels = notification.channels.split(",")
        
        # Check user preferences
        preferences = self.get_user_preferences(notification.user_id)
        if preferences and not self._should_deliver(notification, preferences):
            logger.info(f"Notification {notification.id} blocked by user preferences")
            return
        
        for channel in channels:
            try:
                if channel == NotificationChannel.IN_APP.value:
                    self._deliver_in_app(notification)
                elif channel == NotificationChannel.DESKTOP.value:
                    self._deliver_desktop(notification)
                elif channel == NotificationChannel.EMAIL.value:
                    self._deliver_email(notification)
                elif channel == NotificationChannel.SMS.value:
                    self._deliver_sms(notification)
            except Exception as e:
                logger.error(f"Error delivering notification via {channel}: {str(e)}")

    def _should_deliver(self, notification: Notification, preferences: NotificationPreference) -> bool:
        """Check if notification should be delivered based on preferences"""
        # Check quiet hours
        if preferences.enable_quiet_hours:
            now = datetime.utcnow().time()
            start = datetime.strptime(preferences.quiet_hours_start, "%H:%M").time()
            end = datetime.strptime(preferences.quiet_hours_end, "%H:%M").time()
            
            if start <= now <= end:
                return False
        
        # Check enabled types
        if preferences.enabled_types:
            enabled_types = json.loads(preferences.enabled_types)
            if notification.type.value not in enabled_types:
                return False
        
        return True

    def _deliver_in_app(self, notification: Notification):
        """Mark notification as delivered in-app"""
        notification.sent_in_app = True
        self.db.commit()
        logger.debug(f"Delivered notification {notification.id} in-app")

    def _deliver_desktop(self, notification: Notification):
        """Deliver desktop notification (handled by Electron)"""
        notification.sent_desktop = True
        self.db.commit()
        logger.debug(f"Delivered notification {notification.id} to desktop")

    def _deliver_email(self, notification: Notification):
        """Deliver email notification"""
        # TODO: Implement email delivery
        notification.sent_email = True
        self.db.commit()
        logger.debug(f"Delivered notification {notification.id} via email")

    def _deliver_sms(self, notification: Notification):
        """Deliver SMS notification"""
        # TODO: Implement SMS delivery
        notification.sent_sms = True
        self.db.commit()
        logger.debug(f"Delivered notification {notification.id} via SMS")

    # ==================== Statistics ====================

    def get_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get notification statistics for a user"""
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).all()
        
        total = len(notifications)
        unread = sum(1 for n in notifications if not n.is_read)
        
        by_type = {}
        by_priority = {}
        by_channel = {}
        
        for notification in notifications:
            # By type
            type_key = notification.type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
            
            # By priority
            priority_key = notification.priority.value
            by_priority[priority_key] = by_priority.get(priority_key, 0) + 1
            
            # By channel
            for channel in notification.channels.split(","):
                by_channel[channel] = by_channel.get(channel, 0) + 1
        
        # Recent count (last 24 hours)
        recent_time = datetime.utcnow() - timedelta(hours=24)
        recent_count = sum(1 for n in notifications if n.created_at >= recent_time)
        
        return {
            "total_notifications": total,
            "unread_count": unread,
            "by_type": by_type,
            "by_priority": by_priority,
            "by_channel": by_channel,
            "recent_count": recent_count
        }
