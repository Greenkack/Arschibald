/**
 * Notification Center Component
 * 
 * Displays in-app notifications with filtering, actions, and real-time updates.
 */

import React, { useState, useEffect } from 'react';
import { Badge } from 'primereact/badge';
import { Button } from 'primereact/button';
import { OverlayPanel } from 'primereact/overlaypanel';
import { Divider } from 'primereact/divider';
import { ScrollPanel } from 'primereact/scrollpanel';
import { Dropdown } from 'primereact/dropdown';
import { Checkbox } from 'primereact/checkbox';
import './NotificationCenter.css';

interface Notification {
  id: number;
  type: string;
  priority: string;
  title: string;
  message: string;
  category?: string;
  action_url?: string;
  action_label?: string;
  icon?: string;
  is_read: boolean;
  created_at: string;
  actions?: NotificationAction[];
}

interface NotificationAction {
  id: number;
  action_type: string;
  label: string;
  url?: string;
  is_executed: boolean;
}

interface NotificationCenterProps {
  onNotificationClick?: (notification: Notification) => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  onNotificationClick
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  
  const overlayRef = React.useRef<OverlayPanel>(null);

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(() => {
      loadUnreadCount();
      if (overlayRef.current?.isVisible()) {
        loadNotifications();
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, [filter, categoryFilter]);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: '50',
        unread_only: filter === 'unread' ? 'true' : 'false'
      });
      
      if (categoryFilter) {
        params.append('category', categoryFilter);
      }
      
      const response = await fetch(`/api/v1/notifications?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications);
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await fetch('/api/v1/notifications/unread-count', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error loading unread count:', error);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      const response = await fetch(`/api/v1/notifications/${notificationId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ is_read: true })
      });
      
      if (response.ok) {
        loadNotifications();
        loadUnreadCount();
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const response = await fetch('/api/v1/notifications/mark-all-read', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        loadNotifications();
        loadUnreadCount();
      }
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const deleteNotification = async (notificationId: number) => {
    try {
      const response = await fetch(`/api/v1/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        loadNotifications();
        loadUnreadCount();
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsRead(notification.id);
    }
    
    if (onNotificationClick) {
      onNotificationClick(notification);
    }
    
    if (notification.action_url) {
      window.location.href = notification.action_url;
    }
  };

  const getNotificationIcon = (notification: Notification) => {
    if (notification.icon) {
      return notification.icon;
    }
    
    switch (notification.type) {
      case 'success':
        return 'pi-check-circle';
      case 'warning':
        return 'pi-exclamation-triangle';
      case 'error':
        return 'pi-times-circle';
      case 'calculation_complete':
        return 'pi-calculator';
      case 'pdf_generated':
        return 'pi-file-pdf';
      case 'project_updated':
        return 'pi-folder';
      default:
        return 'pi-info-circle';
    }
  };

  const getNotificationClass = (notification: Notification) => {
    const classes = ['notification-item'];
    
    if (!notification.is_read) {
      classes.push('unread');
    }
    
    classes.push(`priority-${notification.priority}`);
    classes.push(`type-${notification.type}`);
    
    return classes.join(' ');
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
  };

  const filterOptions = [
    { label: 'All Notifications', value: 'all' },
    { label: 'Unread Only', value: 'unread' }
  ];

  return (
    <div className="notification-center">
      <Button
        icon="pi pi-bell"
        className="p-button-rounded p-button-text notification-bell"
        onClick={(e) => {
          overlayRef.current?.toggle(e);
          loadNotifications();
        }}
        badge={unreadCount > 0 ? unreadCount.toString() : undefined}
        badgeClassName="p-badge-danger"
      />
      
      <OverlayPanel
        ref={overlayRef}
        className="notification-panel"
        style={{ width: '400px', maxHeight: '600px' }}
      >
        <div className="notification-header">
          <h3>Notifications</h3>
          <div className="notification-actions">
            <Button
              icon="pi pi-check"
              className="p-button-text p-button-sm"
              onClick={markAllAsRead}
              tooltip="Mark all as read"
              disabled={unreadCount === 0}
            />
            <Button
              icon="pi pi-cog"
              className="p-button-text p-button-sm"
              onClick={() => window.location.href = '/settings/notifications'}
              tooltip="Notification settings"
            />
          </div>
        </div>
        
        <Divider />
        
        <div className="notification-filters">
          <Dropdown
            value={filter}
            options={filterOptions}
            onChange={(e) => setFilter(e.value)}
            className="notification-filter-dropdown"
          />
        </div>
        
        <ScrollPanel style={{ width: '100%', height: '400px' }}>
          {loading ? (
            <div className="notification-loading">
              <i className="pi pi-spin pi-spinner" style={{ fontSize: '2rem' }} />
            </div>
          ) : notifications.length === 0 ? (
            <div className="notification-empty">
              <i className="pi pi-inbox" style={{ fontSize: '3rem', color: '#ccc' }} />
              <p>No notifications</p>
            </div>
          ) : (
            <div className="notification-list">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={getNotificationClass(notification)}
                  onClick={() => handleNotificationClick(notification)}
                >
                  <div className="notification-icon">
                    <i className={`pi ${getNotificationIcon(notification)}`} />
                  </div>
                  
                  <div className="notification-content">
                    <div className="notification-title">{notification.title}</div>
                    <div className="notification-message">{notification.message}</div>
                    <div className="notification-meta">
                      <span className="notification-time">
                        {formatTimestamp(notification.created_at)}
                      </span>
                      {notification.category && (
                        <span className="notification-category">
                          {notification.category}
                        </span>
                      )}
                    </div>
                    
                    {notification.actions && notification.actions.length > 0 && (
                      <div className="notification-actions-list">
                        {notification.actions.map((action) => (
                          <Button
                            key={action.id}
                            label={action.label}
                            className="p-button-sm p-button-outlined"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (action.url) {
                                window.location.href = action.url;
                              }
                            }}
                            disabled={action.is_executed}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="notification-controls">
                    <Button
                      icon="pi pi-times"
                      className="p-button-text p-button-sm p-button-rounded"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNotification(notification.id);
                      }}
                      tooltip="Delete"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollPanel>
        
        <Divider />
        
        <div className="notification-footer">
          <Button
            label="View All"
            className="p-button-text"
            onClick={() => window.location.href = '/notifications'}
          />
        </div>
      </OverlayPanel>
    </div>
  );
};
