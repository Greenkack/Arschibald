"""
Notification API Endpoints

This module provides REST API endpoints for the notification system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db, get_current_user
from backend.services.notification_service import NotificationService
from backend.models.notification_schemas import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateResponse,
    BulkNotificationCreate,
    BulkMarkReadRequest,
    NotificationStatistics,
    NotificationType,
    NotificationChannel
)
from backend.models.user_schemas import UserResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ==================== Notification Endpoints ====================

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new notification.
    
    **Permissions**: Admin or notification for self
    """
    # Check permissions
    if notification_data.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create notifications for other users"
        )
    
    service = NotificationService(db)
    notification = service.create_notification(notification_data)
    return notification


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    category: Optional[str] = Query(None),
    notification_type: Optional[NotificationType] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get notifications for the current user.
    
    **Query Parameters**:
    - skip: Number of notifications to skip (pagination)
    - limit: Maximum number of notifications to return
    - unread_only: Filter to show only unread notifications
    - category: Filter by notification category
    - notification_type: Filter by notification type
    """
    service = NotificationService(db)
    notifications, total = service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        category=category,
        notification_type=notification_type
    )
    
    unread_count = service.get_unread_count(current_user.id)
    
    return NotificationListResponse(
        notifications=notifications,
        total=total,
        unread_count=unread_count,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get count of unread notifications"""
    service = NotificationService(db)
    count = service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.get("/statistics", response_model=NotificationStatistics)
def get_notification_statistics(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get notification statistics for the current user"""
    service = NotificationService(db)
    stats = service.get_statistics(current_user.id)
    return stats


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific notification"""
    service = NotificationService(db)
    notification = service.get_notification(notification_id, current_user.id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    update_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a notification (mark as read/archived)"""
    service = NotificationService(db)
    notification = service.update_notification(notification_id, current_user.id, update_data)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a notification"""
    service = NotificationService(db)
    success = service.delete_notification(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )


@router.post("/mark-all-read", response_model=dict)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Mark all notifications as read"""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.id)
    return {"marked_count": count}


@router.post("/bulk-mark-read", response_model=dict)
def bulk_mark_read(
    request: BulkMarkReadRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Mark multiple notifications as read"""
    service = NotificationService(db)
    count = 0
    
    for notification_id in request.notification_ids:
        notification = service.update_notification(
            notification_id,
            current_user.id,
            NotificationUpdate(is_read=True)
        )
        if notification:
            count += 1
    
    return {"marked_count": count}


# ==================== Bulk Operations ====================

@router.post("/bulk", response_model=List[NotificationResponse], status_code=status.HTTP_201_CREATED)
def create_bulk_notifications(
    bulk_data: BulkNotificationCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create notifications for multiple users.
    
    **Permissions**: Admin only
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create bulk notifications"
        )
    
    service = NotificationService(db)
    notifications = service.create_bulk_notifications(bulk_data)
    return notifications


# ==================== Notification Preferences ====================

@router.get("/preferences/me", response_model=NotificationPreferenceResponse)
def get_my_preferences(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get notification preferences for the current user"""
    service = NotificationService(db)
    preferences = service.get_user_preferences(current_user.id)
    
    if not preferences:
        # Return default preferences
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found. Use PUT to create."
        )
    
    return preferences


@router.put("/preferences/me", response_model=NotificationPreferenceResponse)
def update_my_preferences(
    preferences_data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create or update notification preferences"""
    service = NotificationService(db)
    preferences = service.create_or_update_preferences(current_user.id, preferences_data)
    return preferences


# ==================== Notification Templates (Admin) ====================

@router.post("/templates", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a notification template.
    
    **Permissions**: Admin only
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create templates"
        )
    
    service = NotificationService(db)
    template = service.create_template(template_data)
    return template


@router.get("/templates/{template_key}", response_model=NotificationTemplateResponse)
def get_template(
    template_key: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a notification template"""
    service = NotificationService(db)
    template = service.get_template(template_key)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template


@router.post("/from-template/{template_key}", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_from_template(
    template_key: str,
    variables: dict,
    user_id: Optional[int] = None,
    channels: Optional[List[NotificationChannel]] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a notification from a template.
    
    **Permissions**: Admin or notification for self
    """
    target_user_id = user_id if user_id else current_user.id
    
    if target_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create notifications for other users"
        )
    
    service = NotificationService(db)
    notification = service.create_from_template(
        template_key=template_key,
        user_id=target_user_id,
        variables=variables,
        channels=channels
    )
    return notification
